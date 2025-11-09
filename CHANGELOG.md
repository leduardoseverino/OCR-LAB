# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2024-11-09

### Adicionado
- Interface Streamlit moderna com tema Anthropic Light
- Suporte para múltiplos provedores de IA:
  - Ollama (modelos locais)
  - OpenAI (GPT-4o, GPT-4o-mini, GPT-4-turbo)
  - Google Gemini (Gemini 2.0 Flash)
- Listagem dinâmica de modelos via API para OpenAI e Gemini
- Layout de duas colunas (Upload | Visualização)
- Preview de arquivos antes do processamento
- Suporte para múltiplos formatos:
  - Imagens: PNG, JPG, JPEG, TIFF, BMP
  - Documentos: PDF
- Múltiplos formatos de saída:
  - Markdown
  - Texto puro
  - JSON
  - Estruturado
  - Key-Value
  - Tabela
- Processamento em lote de múltiplos arquivos
- Pré-processamento inteligente de imagens
- Processamento paralelo configurável
- Suporte multilíngue (padrão: pt-br)
- Prompt personalizado obrigatório
- Download de resultados
- Containers com bordas para melhor organização visual

### Alterado
- Interface traduzida para português brasileiro
- Tema customizado baseado no Anthropic Light
- Tamanho de fonte dos controles ajustado para 11pt

### Corrigido
- Visualização de arquivos PDF com ícone apropriado
- Reposicionamento de ponteiro de arquivo para leitura correta
- Avisos de depreciação do Streamlit (use_column_width → use_container_width)

## [0.1.0] - 2024-XX-XX

### Adicionado
- Versão inicial do projeto
- Suporte básico para Ollama

