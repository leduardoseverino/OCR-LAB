import streamlit as st
from ocr_processor import OCRProcessor
import tempfile
import os
from PIL import Image
import json
import subprocess
from io import BytesIO
import requests
import time
from datetime import timedelta, datetime
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

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
    
    max_retries = 3
    for attempt in range(max_retries):
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
            elif response.status_code in [500, 502, 503, 504] and attempt < max_retries - 1:
                # Retry on server errors
                time.sleep(2 ** attempt)
                continue
            else:
                return []
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                st.warning(f"Erro ao buscar modelos da OpenAI após {max_retries} tentativas: {str(e)}")
                return []
        except Exception as e:
            st.warning(f"Erro ao buscar modelos da OpenAI: {str(e)}")
            return []
    return []

def get_gemini_models(api_key):
    """Get available models from Google Gemini API"""
    if not api_key:
        return []
    
    max_retries = 3
    for attempt in range(max_retries):
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
            elif response.status_code in [500, 502, 503, 504] and attempt < max_retries - 1:
                # Retry on server errors
                time.sleep(2 ** attempt)
                continue
            else:
                return []
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                st.warning(f"Erro ao buscar modelos do Gemini após {max_retries} tentativas: {str(e)}")
                return []
        except Exception as e:
            st.warning(f"Erro ao buscar modelos do Gemini: {str(e)}")
            return []
    return []

def process_single_image(processor, image_path, format_type, enable_preprocessing, custom_prompt, language, status_text, timer_text):
    """Process a single image and return the result"""
    try:
        start_time = time.time()
        
        # Create progress callback
        def update_progress(current, total, message):
            elapsed = time.time() - start_time
            timer_text.metric("⏱️ Tempo Decorrido", f"{elapsed:.1f}s")
            status_text.text(message)
        
        # Set progress callback
        processor.progress_callback = update_progress
        
        # Process the image
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

def process_batch_images(processor, image_paths, format_type, enable_preprocessing, custom_prompt, language, status_text, timer_text):
    """Process multiple images and return results"""
    try:
        start_time = time.time()
        
        # Create progress callback
        def update_progress(current, total, message):
            elapsed = time.time() - start_time
            avg_time = elapsed / current if current > 0 else 0
            estimated_total = avg_time * total
            remaining = estimated_total - elapsed
            
            timer_text.metric(
                "⏱️ Tempo Decorrido", 
                f"{elapsed:.1f}s",
                delta=f"~{remaining:.1f}s restantes" if remaining > 0 else None
            )
            status_text.text(message)
        
        # Set progress callback
        processor.progress_callback = update_progress
        
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

def create_structured_docx(title, content_dict, model_name, format_type, language, elapsed_time=None, is_batch=False):
    """Create a structured DOCX document with professional formatting"""
    doc = Document()
    
    # Title
    title_para = doc.add_heading(title, 0)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add metadata section
    doc.add_heading('Informações do Processamento', level=1)
    
    # Create metadata table
    metadata_table = doc.add_table(rows=5 if elapsed_time else 4, cols=2)
    metadata_table.style = 'Light Grid Accent 1'
    
    # Fill metadata
    row_idx = 0
    cells = metadata_table.rows[row_idx].cells
    cells[0].text = 'Data e Hora'
    cells[1].text = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    row_idx += 1
    cells = metadata_table.rows[row_idx].cells
    cells[0].text = 'Modelo Utilizado'
    cells[1].text = model_name
    
    row_idx += 1
    cells = metadata_table.rows[row_idx].cells
    cells[0].text = 'Formato de Saída'
    cells[1].text = format_type
    
    row_idx += 1
    cells = metadata_table.rows[row_idx].cells
    cells[0].text = 'Idioma'
    cells[1].text = language
    
    if elapsed_time:
        row_idx += 1
        cells = metadata_table.rows[row_idx].cells
        cells[0].text = 'Tempo de Processamento'
        cells[1].text = f'{elapsed_time:.2f} segundos'
    
    # Add spacing
    doc.add_paragraph()
    
    # Add results section
    doc.add_heading('Resultados Extraídos', level=1)
    
    if is_batch:
        # For batch processing, iterate through multiple results
        for idx, (file_name, text) in enumerate(content_dict.items(), 1):
            # Add file header
            doc.add_heading(f'{idx}. {file_name}', level=2)
            
            # Add separator line
            p = doc.add_paragraph()
            p.add_run('─' * 80)
            run = p.runs[0]
            run.font.color.rgb = RGBColor(200, 200, 200)
            
            # Add content with formatting
            content_para = doc.add_paragraph()
            run = content_para.add_run(text)
            run.font.size = Pt(11)
            run.font.name = 'Calibri'
            
            # Add spacing between files
            doc.add_paragraph()
    else:
        # For single file processing
        # Add separator line
        p = doc.add_paragraph()
        p.add_run('─' * 80)
        run = p.runs[0]
        run.font.color.rgb = RGBColor(200, 200, 200)
        
        # Add content with formatting
        content_para = doc.add_paragraph()
        run = content_para.add_run(content_dict)
        run.font.size = Pt(11)
        run.font.name = 'Calibri'
    
    # Add footer
    doc.add_page_break()
    footer_section = doc.sections[0]
    footer = footer_section.footer
    footer_para = footer.paragraphs[0]
    footer_para.text = f'Gerado por OCR Vision – Skyone LAB | {datetime.now().strftime("%d/%m/%Y %H:%M")}'
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer_para.runs[0]
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(128, 128, 128)
    
    return doc

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
            ["Google Gemini", "Ollama (Local)", "OpenAI"],
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
            help="Insira um prompt personalizado para extração de texto. Este campo é obrigatório.",
            height=200
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
        
        # Exchange rate info
        st.divider()
        st.caption("💱 Taxa de Câmbio: USD 1.00 = R$ 6.10")
        st.caption("📊 Custos calculados automaticamente para cada processamento")
        
    
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

    # Upload container
    with st.container(border=True):
        st.subheader("📤 Upload de Arquivos")
        uploaded_files = st.file_uploader(
            "Arraste seus arquivos aqui",
            type=['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'pdf'],
            accept_multiple_files=True,
            help="Formatos suportados: PNG, JPG, JPEG, TIFF, BMP, PDF"
        )
        
        # Botão de processar dentro do box de upload
        if uploaded_files:
            st.divider()
            if st.button("🚀 Processar Arquivo", key="process_button", use_container_width=True):
                st.session_state['process_clicked'] = True

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

            # Process button (verifica se foi clicado via session_state)
            if st.session_state.get('process_clicked', False):
                # Reset flag
                st.session_state['process_clicked'] = False
                # Validate custom prompt
                if not custom_prompt:
                    st.error("⚠️ Prompt Personalizado é obrigatório. Por favor, insira um prompt antes de processar.")
                    st.stop()
                
                # Show number of files being processed
                if len(image_paths) > 1:
                    st.info(f"📂 Processando {len(image_paths)} arquivos em modo lote...")
                else:
                    st.info(f"📄 Processando 1 arquivo...")
                
                # Reset usage stats before processing
                try:
                    processor.reset_usage_stats()
                except Exception as e:
                    st.warning(f"Aviso ao resetar estatísticas: {e}")
                
                # Create timer and status components
                timer_container = st.empty()
                status_text = st.empty()
                
                start_time = time.time()
                
                if len(image_paths) == 1:
                    # Single image processing
                    status_text.text("Iniciando processamento...")
                    result = process_single_image(
                        processor, 
                        image_paths[0], 
                        format_type,
                        enable_preprocessing,
                        custom_prompt,
                        language,
                        status_text,
                        timer_container
                    )
                    
                    # Show final time
                    elapsed_time = time.time() - start_time
                    timer_container.empty()
                    status_text.empty()
                    
                    # Get usage statistics
                    try:
                        usage_stats = processor.get_usage_stats()
                    except Exception as e:
                        st.warning(f"Aviso ao obter estatísticas: {e}")
                        usage_stats = {
                            'input_tokens': 0,
                            'output_tokens': 0,
                            'estimated_cost_brl': 0,
                            'estimated_cost_usd': 0
                        }
                    
                    st.success(f"✅ Processamento concluído em {elapsed_time:.2f}s!")
                    
                    # Display usage statistics in a separate block
                    with st.container(border=True):
                        st.subheader("📊 Estatísticas de Uso")
                        st.markdown('<div style="font-size: 11pt;">', unsafe_allow_html=True)
                        col1, col2, col3, col4, col5 = st.columns(5)
                        with col1:
                            st.metric("⏱️ Tempo", f"{elapsed_time:.2f}s")
                        with col2:
                            st.metric("📥 Tokens Entrada", f"{usage_stats.get('input_tokens', 0):,}")
                        with col3:
                            st.metric("📤 Tokens Saída", f"{usage_stats.get('output_tokens', 0):,}")
                        with col4:
                            cost_brl = usage_stats.get('estimated_cost_brl', 0)
                            if cost_brl > 0:
                                st.metric("💰 Custo (BRL)", f"R$ {cost_brl:.4f}")
                            else:
                                st.metric("💰 Custo", "Gratuito")
                        with col5:
                            cost_usd = usage_stats.get('estimated_cost_usd', 0)
                            if cost_usd > 0:
                                st.metric("💵 Custo (USD)", f"${cost_usd:.4f}")
                            else:
                                st.metric("💵 USD", "-")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Get raw result
                    try:
                        if hasattr(processor, 'get_raw_result'):
                            raw_result = processor.get_raw_result() or result
                        else:
                            raw_result = result
                    except (AttributeError, Exception):
                        raw_result = result
                    
                    # Display results in the selected format in a separate block
                    st.subheader(f"📝 Resultado Processado ({format_type.upper()})")
                    with st.container(border=True):
                        st.markdown('<div style="font-size: 11pt;">', unsafe_allow_html=True)
                        if format_type == "json":
                            try:
                                json_data = json.loads(result)
                                st.json(json_data)
                            except:
                                st.code(result, language="json")
                        elif format_type == "text":
                            st.text(result)
                        elif format_type in ["structured", "key_value", "table"]:
                            st.markdown(result)
                        else:  # markdown
                            st.markdown(result)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Download options for single result in a separate block
                    st.subheader("📥 Opções de Download")
                    with st.container(border=True):
                        st.markdown('<div style="font-size: 11pt;">', unsafe_allow_html=True)
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.download_button(
                                "📥 Download TXT",
                                result,
                                file_name=f"ocr_result.txt",
                                mime="text/plain",
                                key="download_txt_single"
                            )
                        
                        with col2:
                            # Create structured DOCX
                            doc = create_structured_docx(
                                title='Resultado do OCR',
                                content_dict=result,
                                model_name=selected_model,
                                format_type=format_type,
                                language=language,
                                elapsed_time=elapsed_time,
                                is_batch=False
                            )
                            docx_buffer = BytesIO()
                            doc.save(docx_buffer)
                            docx_buffer.seek(0)
                            st.download_button(
                                "📥 Download DOCX",
                                docx_buffer.getvalue(),
                                file_name="ocr_result.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key="download_docx_single"
                            )
                        
                        with col3:
                            # DOC format with structured content
                            doc = create_structured_docx(
                                title='Resultado do OCR',
                                content_dict=result,
                                model_name=selected_model,
                                format_type=format_type,
                                language=language,
                                elapsed_time=elapsed_time,
                                is_batch=False
                            )
                            doc_buffer = BytesIO()
                            doc.save(doc_buffer)
                            doc_buffer.seek(0)
                            st.download_button(
                                "📥 Download DOC",
                                doc_buffer.getvalue(),
                                file_name="ocr_result.doc",
                                mime="application/msword",
                                key="download_doc_single"
                            )
                        
                        with col4:
                            # Raw result - exactly as LLM processed
                            st.download_button(
                                "📥 Download RAW",
                                raw_result,
                                file_name="ocr_result_raw.txt",
                                mime="text/plain",
                                help="Resultado exatamente como processado pela LLM, sem formatação",
                                key="download_raw_single"
                            )
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    # Batch processing
                    status_text.text("Iniciando processamento em lote...")
                    try:
                        results = process_batch_images(
                            processor,
                            image_paths,
                            format_type,
                            enable_preprocessing,
                            custom_prompt,
                            language,
                            status_text,
                            timer_container
                        )
                    except Exception as e:
                        st.error(f"❌ Erro no processamento em lote: {str(e)}")
                        st.exception(e)
                        st.stop()
                    
                    # Show final time
                    elapsed_time = time.time() - start_time
                    timer_container.empty()
                    status_text.empty()
                    
                    # Get usage statistics
                    try:
                        usage_stats = processor.get_usage_stats()
                    except Exception as e:
                        st.warning(f"Aviso ao obter estatísticas: {e}")
                        usage_stats = {
                            'input_tokens': 0,
                            'output_tokens': 0,
                            'estimated_cost_brl': 0,
                            'estimated_cost_usd': 0
                        }
                    
                    st.success(f"✅ Processamento em lote concluído em {elapsed_time:.2f}s!")
                    
                    # Display processing and usage statistics side by side
                    col_stat1, col_stat2 = st.columns(2)
                    
                    with col_stat1:
                        with st.container(border=True):
                            st.subheader("📊 Estatísticas de Processamento")
                            st.markdown('<div style="font-size: 11pt;">', unsafe_allow_html=True)
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total de Imagens", results.get('statistics', {}).get('total', 0))
                            with col2:
                                st.metric("Sucesso", results.get('statistics', {}).get('successful', 0))
                            with col3:
                                st.metric("Falhas", results.get('statistics', {}).get('failed', 0))
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col_stat2:
                        with st.container(border=True):
                            st.subheader("💡 Estatísticas de Uso")
                            st.markdown('<div style="font-size: 11pt;">', unsafe_allow_html=True)
                            col1, col2, col3, col4, col5 = st.columns(5)
                            with col1:
                                st.metric("⏱️ Tempo Total", f"{elapsed_time:.2f}s")
                            with col2:
                                st.metric("📥 Tokens Entrada", f"{usage_stats.get('input_tokens', 0):,}")
                            with col3:
                                st.metric("📤 Tokens Saída", f"{usage_stats.get('output_tokens', 0):,}")
                            with col4:
                                cost_brl = usage_stats.get('estimated_cost_brl', 0)
                                if cost_brl > 0:
                                    st.metric("💰 Custo (BRL)", f"R$ {cost_brl:.4f}")
                                else:
                                    st.metric("💰 Custo", "Gratuito")
                            with col5:
                                cost_usd = usage_stats.get('estimated_cost_usd', 0)
                                if cost_usd > 0:
                                    st.metric("💵 Custo (USD)", f"${cost_usd:.4f}")
                                else:
                                    st.metric("💵 USD", "-")
                            st.markdown('</div>', unsafe_allow_html=True)

                    # Display errors if any
                    if results.get('errors'):
                        st.error("⚠️ Arquivos com erros:")
                        for file_path, error in results['errors'].items():
                            st.warning(f"❌ {os.path.basename(file_path)}: {error}")

                    # Display results in the selected format
                    if results.get('results'):
                        st.subheader(f"📝 Resultados Processados ({format_type.upper()})")
                        for file_path, text in results['results'].items():
                            # Check if this is actually an error message
                            if text.startswith("Error processing image:"):
                                with st.expander(f"❌ {os.path.basename(file_path)} (Erro)", expanded=False):
                                    st.error(text)
                            else:
                                with st.expander(f"✅ {os.path.basename(file_path)}", expanded=False):
                                    with st.container(border=True):
                                        st.markdown('<div style="font-size: 11pt;">', unsafe_allow_html=True)
                                        if format_type == "json":
                                            try:
                                                json_data = json.loads(text)
                                                st.json(json_data)
                                            except:
                                                st.code(text, language="json")
                                        elif format_type == "text":
                                            st.text(text)
                                        elif format_type in ["structured", "key_value", "table"]:
                                            st.markdown(text)
                                        else:  # markdown
                                            st.markdown(text)
                                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ Nenhum resultado foi gerado.")

                    # Get raw results
                    try:
                        if hasattr(processor, 'get_raw_results'):
                            raw_results_dict = processor.get_raw_results()
                        else:
                            raw_results_dict = {}
                    except (AttributeError, Exception):
                        raw_results_dict = {}
                    
                    # Download all results in different formats in a separate block
                    st.subheader("📥 Opções de Download")
                    with st.container(border=True):
                        st.markdown('<div style="font-size: 11pt;">', unsafe_allow_html=True)
                        if results.get('results'):
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                # JSON format
                                json_results = json.dumps(results, indent=2, ensure_ascii=False)
                                st.download_button(
                                    "📥 Download JSON",
                                    json_results,
                                    file_name="ocr_results.json",
                                    mime="application/json",
                                    key="download_json_batch"
                                )
                            
                            with col2:
                                # DOCX format - structured batch results
                                try:
                                    batch_content = {os.path.basename(fp): text for fp, text in results['results'].items()}
                                    doc = create_structured_docx(
                                        title='Resultados do OCR (Lote)',
                                        content_dict=batch_content,
                                        model_name=selected_model,
                                        format_type=format_type,
                                        language=language,
                                        elapsed_time=elapsed_time,
                                        is_batch=True
                                    )
                                    docx_buffer = BytesIO()
                                    doc.save(docx_buffer)
                                    docx_buffer.seek(0)
                                    st.download_button(
                                        "📥 Download DOCX",
                                        docx_buffer.getvalue(),
                                        file_name="ocr_results.docx",
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                        key="download_docx_batch"
                                    )
                                except Exception as e:
                                    st.error(f"Erro ao gerar DOCX: {e}")
                            
                            with col3:
                                # DOC format - structured batch results
                                try:
                                    batch_content = {os.path.basename(fp): text for fp, text in results['results'].items()}
                                    doc = create_structured_docx(
                                        title='Resultados do OCR (Lote)',
                                        content_dict=batch_content,
                                        model_name=selected_model,
                                        format_type=format_type,
                                        language=language,
                                        elapsed_time=elapsed_time,
                                        is_batch=True
                                    )
                                    doc_buffer = BytesIO()
                                    doc.save(doc_buffer)
                                    doc_buffer.seek(0)
                                    st.download_button(
                                        "📥 Download DOC",
                                        doc_buffer.getvalue(),
                                        file_name="ocr_results.doc",
                                        mime="application/msword",
                                        key="download_doc_batch"
                                    )
                                except Exception as e:
                                    st.error(f"Erro ao gerar DOC: {e}")
                            
                            with col4:
                                # RAW format - exactly as LLM processed
                                try:
                                    # Combine all raw results
                                    raw_content = []
                                    for fp, text in results['results'].items():
                                        file_name = os.path.basename(fp)
                                        raw_text = raw_results_dict.get(fp, text)  # Fallback to formatted if raw not available
                                        raw_content.append(f"=== {file_name} ===\n{raw_text}\n\n")
                                    
                                    raw_all = "\n".join(raw_content)
                                    st.download_button(
                                        "📥 Download RAW",
                                        raw_all,
                                        file_name="ocr_results_raw.txt",
                                        mime="text/plain",
                                        help="Resultados exatamente como processados pela LLM, sem formatação",
                                        key="download_raw_batch"
                                    )
                                except Exception as e:
                                    st.error(f"Erro ao gerar RAW: {e}")
                        else:
                            st.info("📝 Nenhum resultado disponível para download.")
                        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()