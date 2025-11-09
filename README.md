# OCR Vision – Skyone LAB

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.30+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Uma tecnologia de visão computacional e IA criada pelo Skyone LAB para extrair e interpretar textos de documentos, imagens e PDFs com máxima acurácia.

Projetado para impulsionar automações no Skyone Studio e alimentar agentes de IA com dados estruturados e confiáveis.

---

## 📸 Screenshots

![OCR Vision Interface](logo_file.jpg)

*Interface moderna com layout de duas colunas para upload e visualização*

## 🚀 Características

- **Múltiplos Provedores de IA**: Suporte para Ollama (local), OpenAI e Google Gemini
- **Processamento em Lote**: Processe múltiplos arquivos simultaneamente
- **Formatos Variados**: Suporte para PNG, JPG, JPEG, TIFF, BMP e PDF
- **Pré-processamento Inteligente**: Melhoria automática de imagem para melhor acurácia
- **Múltiplos Formatos de Saída**: Markdown, texto, JSON, estruturado, key-value e tabela
- **Interface Moderna**: UI intuitiva com tema Anthropic Light inspirado
- **Visualização em Tempo Real**: Preview dos arquivos antes do processamento

## 📋 Pré-requisitos

- Python 3.8 ou superior
- [Ollama](https://ollama.ai/) instalado (para uso local)
- Chave de API da OpenAI (opcional)
- Chave de API do Google Gemini (opcional)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/Ollama-OCR.git
cd Ollama-OCR
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. (Opcional) Para usar Ollama localmente, instale modelos de visão:
```bash
ollama pull llava:34b
ollama pull llama3.2-vision:latest
```

## 🎯 Como Usar

### Iniciar a Aplicação

```bash
streamlit run src/ollama_ocr/app.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`

### Uso Básico

1. **Escolha o Provedor de API**:
   - **Ollama (Local)**: Use modelos locais sem necessidade de API key
   - **OpenAI**: Insira sua API key para acessar modelos GPT-4
   - **Google Gemini**: Insira sua API key para acessar modelos Gemini

2. **Selecione o Modelo**: 
   - Para Ollama: modelos instalados localmente
   - Para OpenAI/Gemini: modelos disponíveis após inserir API key

3. **Configure o Processamento**:
   - Escolha o formato de saída
   - Insira um prompt personalizado (obrigatório)
   - Defina o idioma do documento
   - Ajuste processamento paralelo e pré-processamento

4. **Faça Upload dos Arquivos**:
   - Arraste arquivos para a área de upload
   - Visualize preview na coluna direita
   - Clique em "Processar Arquivo"

5. **Obtenha os Resultados**:
   - Visualize o texto extraído
   - Baixe os resultados em diferentes formatos

## 🏗️ Estrutura do Projeto

```
Ollama-OCR/
├── .streamlit/
│   └── config.toml          # Configuração do tema Streamlit
├── src/
│   └── ollama_ocr/
│       ├── __init__.py
│       ├── app.py           # Interface Streamlit
│       └── ocr_processor.py # Lógica de processamento OCR
├── input/                   # Pasta para arquivos de entrada (gitignored)
├── output/                  # Pasta para resultados (gitignored)
├── requirements.txt         # Dependências Python
├── .gitignore
└── README.md
```

## 🔑 Configuração de API Keys

### OpenAI
1. Obtenha sua API key em: https://platform.openai.com/api-keys
2. Insira a key no campo "Chave da API" quando selecionar OpenAI

### Google Gemini
1. Obtenha sua API key em: https://makersuite.google.com/app/apikey
2. Insira a key no campo "Chave da API" quando selecionar Google Gemini

## 🎨 Personalização

### Tema
O tema pode ser personalizado editando `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF7A59"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F7F7F7"
textColor = "#1F1F1F"
font = "sans serif"
```

## 📝 Formatos de Saída

- **Markdown**: Texto formatado com headers, listas e ênfases
- **Text**: Texto puro sem formatação
- **JSON**: Estrutura hierárquica em formato JSON
- **Structured**: Preserva tabelas e listas estruturadas
- **Key-Value**: Pares chave-valor extraídos
- **Table**: Dados tabulares em formato estruturado

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🏢 Desenvolvido por

**Skyone LAB**

Uma tecnologia desenvolvida para impulsionar automações e alimentar agentes de IA com dados estruturados e confiáveis.

## 🐛 Problemas e Suporte

Encontrou um bug ou tem uma sugestão? Abra uma [issue](https://github.com/seu-usuario/Ollama-OCR/issues).

## 🙏 Agradecimentos

- [Ollama](https://ollama.ai/) - Modelos de IA locais
- [Streamlit](https://streamlit.io/) - Framework de UI
- [OpenAI](https://openai.com/) - Modelos GPT
- [Google Gemini](https://deepmind.google/technologies/gemini/) - Modelos Gemini

