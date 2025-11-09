import streamlit as st
from ocr_processor import OCRProcessor
import tempfile
import os
from PIL import Image
import json
import subprocess
from io import BytesIO
import requests

# Page configuration
st.set_page_config(
    page_title="OCR with Ollama",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Anthropic Light Inspired Theme
st.markdown("""
    <style>
    .stApp {
        max-width: 100%;
        padding: 1rem;
        background-color: #FFFFFF;
    }
    .main {
        background-color: #FFFFFF;
    }
    .stButton button {
        background-color: #FF7A59;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton button:hover {
        background-color: #E66A49;
        box-shadow: 0 2px 8px rgba(255, 122, 89, 0.3);
    }
    .stSelectbox {
        margin-bottom: 1rem;
    }
    .stTextArea textarea {
        border: 1px solid #E0E0E0;
        border-radius: 6px;
        font-family: 'Courier New', monospace;
    }
    .stTextInput input {
        border: 1px solid #E0E0E0;
        border-radius: 6px;
    }
    .stImage {
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #F0F0F0;
    }
    h1 {
        color: #1F1F1F;
        font-weight: 600;
    }
    h2, h3 {
        color: #2F2F2F;
        font-weight: 500;
    }
    .sidebar .sidebar-content {
        background-color: #F7F7F7;
    }
    </style>
""", unsafe_allow_html=True)

DEFAULT_MODELS = [
    "llava:7b",
    "llama3.2-vision:11b",
    "granite3.2-vision",
    "moondream",
    "minicpm-v",
]

def get_available_models():
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
        models = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line or line.startswith("NAME"):
                continue
            models.append(line.split()[0])
        return models
    except Exception:
        return []

def get_openai_models(api_key):
    """Get available vision models from OpenAI API"""
    if not api_key:
        return []
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            # Get all available models (not just vision-specific)
            all_models = []
            for model in models_data.get("data", []):
                model_id = model.get("id", "")
                # Include all GPT models
                if model_id.startswith("gpt-"):
                    all_models.append(model_id)
            
            # Sort and return unique models
            all_models = sorted(set(all_models), reverse=True)
            return all_models if all_models else []
        else:
            return []
    except Exception as e:
        st.warning(f"Erro ao buscar modelos da OpenAI: {str(e)}")
        return []

def get_gemini_models(api_key):
    """Get available models from Google Gemini API"""
    if not api_key:
        return []
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            gemini_models = []
            for model in models_data.get("models", []):
                model_name = model.get("name", "")
                # Extract model ID from full name (e.g., "models/gemini-pro" -> "gemini-pro")
                if "/" in model_name:
                    model_id = model_name.split("/")[-1]
                    # Only include models that support vision
                    if "vision" in model_id.lower() or "gemini-1.5" in model_id or "gemini-2" in model_id:
                        gemini_models.append(model_id)
            
            return sorted(set(gemini_models), reverse=True) if gemini_models else []
        else:
            return []
    except Exception as e:
        st.warning(f"Erro ao buscar modelos do Gemini: {str(e)}")
        return []

def process_single_image(processor, image_path, format_type, enable_preprocessing, custom_prompt, language):
    """Process a single image and return the result"""
    try:
        result = processor.process_image(
            image_path=image_path,
            format_type=format_type,
            preprocess=enable_preprocessing,
            custom_prompt=custom_prompt,
            language=language
        )
        return result
    except Exception as e:
        return f"Error processing image: {str(e)}"

def process_batch_images(processor, image_paths, format_type, enable_preprocessing, custom_prompt, language):
    """Process multiple images and return results"""
    try:
        results = processor.process_batch(
            input_path=image_paths,
            format_type=format_type,
            preprocess=enable_preprocessing,
            custom_prompt=custom_prompt,
            language=language
        )
        return results
    except Exception as e:
        return {"error": str(e)}

def main():
    st.title("OCR Vision – Skyone LAB")
    st.markdown("""
    <div style='text-align: left; margin-bottom: 2rem;'>
        <p style='font-size: 0.9rem; color: black; margin-bottom: 0.5rem;'>
            Uma tecnologia de visão computacional e IA criada pelo Skyone LAB para extrair e interpretar textos de documentos, imagens e PDFs com máxima acurácia.
        </p>
        <p style='font-size: 0.9rem; color: black;'>
            Projetado para impulsionar automações no Skyone Studio e alimentar agentes de IA com dados estruturados e confiáveis.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar controls
    with st.sidebar:
        st.markdown("<style>.sidebar .sidebar-content { font-size: 11pt; }</style>", unsafe_allow_html=True)
        st.header("🎮 Controles")
        
        # API Provider Selection
        api_provider = st.selectbox(
            "🔌 Provedor de API",
            ["Ollama (Local)", "OpenAI", "Google Gemini"],
            help="Escolha o provedor de API de visão"
        )
        
        # API Key input for external providers
        api_key = None
        if api_provider in ["OpenAI", "Google Gemini"]:
            api_key = st.text_input(
                "🔑 Chave da API *",
                type="password",
                help=f"Insira sua chave de API do {api_provider}"
            )
        
        # Model selection based on provider
        if api_provider == "Ollama (Local)":
            available_models = get_available_models()
            if not available_models:
                st.warning("Não foi possível buscar modelos do Ollama. Usando lista padrão.")
                available_models = DEFAULT_MODELS
            selected_model = st.selectbox(
                "🤖 Selecionar Modelo de Visão",
                available_models,
                index=0,
            )
        elif api_provider == "OpenAI":
            # Get OpenAI models dynamically if API key is provided
            openai_models = get_openai_models(api_key)
            if openai_models:
                selected_model = st.selectbox(
                    "🤖 Selecionar Modelo de Visão",
                    openai_models,
                    index=0,
                    help="Modelos disponíveis na sua conta OpenAI"
                )
            else:
                st.warning("⚠️ Insira a API Key da OpenAI para ver os modelos disponíveis.")
                selected_model = None
        else:  # Google Gemini
            # Get Gemini models dynamically if API key is provided
            gemini_models = get_gemini_models(api_key)
            if gemini_models:
                selected_model = st.selectbox(
                    "🤖 Selecionar Modelo de Visão",
                    gemini_models,
                    index=0,
                    help="Modelos disponíveis na sua conta Google Gemini"
                )
            else:
                st.warning("⚠️ Insira a API Key do Google Gemini para ver os modelos disponíveis.")
                selected_model = None
        
        format_type = st.selectbox(
            "📄 Formato de Saída",
            ["markdown", "text", "json", "structured", "key_value", "table"],
            help="Escolha como deseja formatar o texto extraído"
        )
        
        # Custom prompt input (required)
        custom_prompt_input = st.text_area(
            "📝 Prompt Personalizado *",
            value="",
            placeholder="Digite seu prompt aqui (obrigatório)",
            help="Insira um prompt personalizado para extração de texto. Este campo é obrigatório."
        )

        language = st.text_input(
            "🌍 Idioma",
            value="pt-br",
            help="Insira o idioma do texto na imagem (ex: pt-br para Português, en para Inglês)."
        )

        max_workers = st.slider(
            "🔄 Processamento Paralelo",
            min_value=1,
            max_value=8,
            value=2,
            help="Número de imagens a processar em paralelo (para processamento em lote)"
        )

        enable_preprocessing = st.checkbox(
            "🔍 Pré-processamento",
            value=True,
            help="Aplicar aprimoramento e pré-processamento de imagem"
        )
        
        # Model info box
        if selected_model == "llava:7b":
            st.info("LLaVA 7B: Modelo de visão-linguagem eficiente otimizado para processamento em tempo real")
        elif selected_model == "llama3.2-vision:11b":
            st.info("Llama 3.2 Vision: Modelo avançado com alta precisão para extração de texto complexo")
        elif selected_model == "granite3.2-vision":
            st.info("Granite 3.2 Vision: Modelo robusto para análise detalhada de documentos")
        elif selected_model == "moondream":
            st.info("Moondream: Modelo leve projetado para dispositivos de borda")
        
    
    # Validate that custom prompt is provided
    custom_prompt = custom_prompt_input.strip() if custom_prompt_input.strip() != "" else None

    # Map provider name to internal format
    provider_map = {
        "Ollama (Local)": "ollama",
        "OpenAI": "openai",
        "Google Gemini": "gemini"
    }
    
    # Initialize OCR Processor with API provider and key
    try:
        processor = OCRProcessor(
            model_name=selected_model, 
            max_workers=max_workers,
            api_provider=provider_map[api_provider],
            api_key=api_key
        )
    except ValueError as e:
        st.error(f"⚠️ Configuration Error: {str(e)}")
        st.stop()

    # Two-column layout: Upload | Preview
    col_upload, col_preview = st.columns([1, 1])
    
    with col_upload:
        with st.container(border=True):
            st.subheader("📤 Upload de Arquivos")
            uploaded_files = st.file_uploader(
                "Arraste seus arquivos aqui",
                type=['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'pdf'],
                accept_multiple_files=True,
                help="Formatos suportados: PNG, JPG, JPEG, TIFF, BMP, PDF"
            )
    
    with col_preview:
        with st.container(border=True):
            st.subheader("👁️ Visualização")
            if uploaded_files:
                st.caption(f"{len(uploaded_files)} arquivo(s) carregado(s)")
                for uploaded_file in uploaded_files:
                    try:
                        if uploaded_file.name.lower().endswith('.pdf'):
                            # Show PDF icon and info
                            st.markdown(f"""
                            <div style='text-align: center; padding: 2rem; border: 2px dashed #E0E0E0; border-radius: 8px;'>
                                <div style='font-size: 48px; margin-bottom: 1rem;'>📄</div>
                                <div style='font-size: 14px; color: #666;'>{uploaded_file.name}</div>
                                <div style='font-size: 12px; color: #999; margin-top: 0.5rem;'>Arquivo PDF</div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            # Reset file pointer to beginning before displaying
                            uploaded_file.seek(0)
                            image = Image.open(uploaded_file)
                            st.image(image, caption=uploaded_file.name, use_container_width=True)
                    except Exception as e:
                        st.error(f"Erro ao exibir {uploaded_file.name}: {e}")
            else:
                st.info("Nenhum arquivo carregado ainda.")

    if uploaded_files:
        # Create a temporary directory for uploaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            image_paths = []

            # Save uploaded files and collect paths
            for uploaded_file in uploaded_files:
                # Reset file pointer before reading
                uploaded_file.seek(0)
                temp_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())
                image_paths.append(temp_path)

            # Process button
            if st.button("🚀 Processar Arquivo"):
                # Validate custom prompt
                if not custom_prompt:
                    st.error("⚠️ Prompt Personalizado é obrigatório. Por favor, insira um prompt antes de processar.")
                    st.stop()
                
                with st.spinner("Processing file..."):
                    if len(image_paths) == 1:
                        # Single image processing
                        result = process_single_image(
                            processor, 
                            image_paths[0], 
                            format_type,
                            enable_preprocessing,
                            custom_prompt,
                            language
                        )
                        st.subheader("📝 Extracted Text")
                        st.markdown(result)
                        
                        # Download button for single result
                        st.download_button(
                            "📥 Download Result",
                            result,
                            file_name=f"ocr_result.{format_type}",
                            mime="text/plain"
                        )
                    else:
                        # Batch processing
                        results = process_batch_images(
                            processor,
                            image_paths,
                            format_type,
                            enable_preprocessing,
                            custom_prompt,
                            language
                        )
                        
                        # Display statistics
                        st.subheader("📊 Processing Statistics")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Images", results['statistics']['total'])
                        with col2:
                            st.metric("Successful", results['statistics']['successful'])
                        with col3:
                            st.metric("Failed", results['statistics']['failed'])

                        # Display results
                        st.subheader("📝 Extracted Text")
                        for file_path, text in results['results'].items():
                            with st.expander(f"Result: {os.path.basename(file_path)}"):
                                st.markdown(text)

                        # Display errors if any
                        if results['errors']:
                            st.error("⚠️ Some files had errors:")
                            for file_path, error in results['errors'].items():
                                st.warning(f"{os.path.basename(file_path)}: {error}")

                        # Download all results as JSON
                        if st.button("📥 Download All Results"):
                            json_results = json.dumps(results, indent=2)
                            st.download_button(
                                "📥 Download Results JSON",
                                json_results,
                                file_name="ocr_results.json",
                                mime="application/json"
                            )

if __name__ == "__main__":
    main()