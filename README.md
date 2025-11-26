# 🔍 OCR Vision – Skyone LAB

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.30+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<div align="center">
  <img src="https://ghbranding.com.br/wp-content/uploads/2024/01/hero-skyone.svg" alt="Skyone Logo" width="400"/>
</div>

---

## 🎯 Sobre o Projeto

**OCR Vision** é uma solução de visão computacional desenvolvida pelo **Skyone LAB** para extrair e interpretar textos de documentos, imagens e PDFs com máxima acurácia utilizando Inteligência Artificial.

### Propósito

Esta tecnologia foi desenvolvida para:

- **Impulsionar automações** no Skyone Studio
- **Alimentar agentes de IA** com dados estruturados e confiáveis
- **Digitalizar documentos** de forma inteligente e precisa
- **Processar informações** em múltiplos formatos e idiomas

---

## 🚀 Principais Funcionalidades

- ✅ **Múltiplos Provedores de IA**: Ollama (local), OpenAI e Google Gemini
- ✅ **Integração com Google Drive**: Processe arquivos diretamente da nuvem
- ✅ **Processamento em Lote**: Múltiplos arquivos simultaneamente
- ✅ **Formatos Suportados**: PNG, JPG, JPEG, TIFF, BMP e PDF
- ✅ **Pré-processamento Inteligente**: Melhoria automática de imagem
- ✅ **Formatos de Saída**: Markdown, Texto, JSON, Estruturado, Chave-Valor, Tabela, Word 97-2003
- ✅ **Formato Minuta**: Geração de documentos no padrão de peças processuais
- ✅ **Interface Moderna**: UI intuitiva e responsiva
- ✅ **Salvamento Automático**: Resultados salvos diretamente no Google Drive

---

## 📋 Pré-requisitos

- Python 3.8 ou superior
- [Ollama](https://ollama.ai/) instalado (para uso local)
- Chave de API da OpenAI (opcional)
- Chave de API do Google Gemini (opcional)

---

## 🔧 Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/Ollama-OCR.git
cd Ollama-OCR

# 2. Instale as dependências
pip install -r requirements.txt

# 3. (Opcional) Instale modelos Ollama locais
ollama pull llava:7b
ollama pull llama3.2-vision:11b
```

---

## 🎯 Como Usar

### Iniciar a Aplicação

```bash
streamlit run src/ollama_ocr/app.py
```

A aplicação abrirá automaticamente em `http://localhost:8501`

### Fluxo de Uso

1. **Selecione o Provedor de API** (Ollama, OpenAI ou Google Gemini)
2. **Escolha o Modelo** de IA
3. **Configure o Processamento**:
   - Formato de saída desejado
   - Tipo de prompt (Manual ou Automático)
   - Idioma do documento
   - Processamento paralelo e pré-processamento
4. **Faça Upload dos Arquivos** e processe
5. **Visualize e Baixe** os resultados em múltiplos formatos

---

## 📝 Formatos de Saída

- **Markdown**: Texto formatado com estrutura hierárquica
- **Texto**: Texto puro sem formatação
- **JSON**: Estrutura hierárquica em formato JSON
- **Estruturado**: Preserva tabelas e listas estruturadas
- **Chave-Valor**: Pares chave-valor extraídos
- **Tabela**: Dados tabulares em formato estruturado
- **Formato Minuta**: Documentos no padrão de peças processuais (.doc)

---

## 🔑 Configuração de API Keys

### OpenAI
1. Obtenha sua API key em: https://platform.openai.com/api-keys
2. Insira a key no campo "Chave da API" quando selecionar OpenAI

### Google Gemini
1. Obtenha sua API key em: https://makersuite.google.com/app/apikey
2. Insira a key no campo "Chave da API" quando selecionar Google Gemini

---

## ☁️ Integração com Google Drive

O OCR Vision agora suporta processamento direto de arquivos do Google Drive!

### 🎯 Funcionalidades

- **Navegação de Pastas**: Navegue pelas pastas do seu Google Drive
- **Seleção Intuitiva**: Selecione a pasta com os arquivos para processar
- **Download Automático**: Arquivos são baixados temporariamente para processamento
- **Upload Automático**: Resultados são salvos automaticamente na mesma pasta
- **Segurança**: Autenticação OAuth 2.0 segura

### 📖 Como Configurar

Para usar a integração com Google Drive, siga o guia completo de configuração:

👉 **[GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md)**

### 🚀 Início Rápido

1. Configure as credenciais do Google Drive (veja guia acima)
2. Inicie o aplicativo
3. Na barra lateral, clique em **"🔐 Conectar ao Google Drive"**
4. Autorize o acesso
5. Navegue e selecione uma pasta
6. Vá para a aba **"☁️ Google Drive"**
7. Clique em **"🚀 Processar Arquivos do Google Drive"**

Os resultados serão salvos automaticamente na mesma pasta!

---

## 🏗️ Estrutura do Projeto

```
OCR-LAB/
├── src/
│   └── ollama_ocr/
│       ├── app.py           # Interface Streamlit
│       └── ocr_processor.py # Lógica de processamento OCR
├── requirements.txt         # Dependências Python
└── README.md
```

---

## 🏢 Desenvolvido por

<div align="center">
  <strong>Skyone LAB</strong>
  <br/>
  <em>Impulsionando automações e alimentando agentes de IA com dados estruturados e confiáveis.</em>
</div>

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## 🤝 Suporte

Para suporte, dúvidas ou sugestões, entre em contato com a equipe do **Skyone LAB**.

---

<div align="center">
  <p>Desenvolvido com ❤️ pela equipe Skyone LAB</p>
</div>
