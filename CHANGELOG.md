# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [2.0.0] - 2024-11-26

### Adicionado
- **Integração com Google Drive**:
  - Autenticação OAuth 2.0 segura
  - Navegação de pastas do Google Drive
  - Seleção intuitiva de pastas
  - Download automático de arquivos para processamento
  - Upload automático de resultados na mesma pasta
  - Suporte para desconexão e reconexão
- **Novo formato de saída**: Documento do Word 97-2003 (.doc)
- **Módulo google_drive_integration.py**: Gerenciamento completo de operações do Google Drive
- **Interface de abas**: Upload Local vs Google Drive
- **Documentação completa**: GOOGLE_DRIVE_SETUP.md com guia passo a passo
- **Arquivo de exemplo**: credentials.json.example para facilitar configuração
- **Segurança aprimorada**: credentials.json e token.pickle adicionados ao .gitignore

### Melhorado
- Interface da barra lateral reorganizada com seção dedicada ao Google Drive
- Feedback visual aprimorado durante download e upload de arquivos
- Mensagens de erro mais descritivas para problemas de autenticação
- Estatísticas de processamento exibidas para arquivos do Google Drive

### Dependências
- google-auth>=2.23.0
- google-auth-oauthlib>=1.1.0
- google-auth-httplib2>=0.1.1
- google-api-python-client>=2.100.0

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

