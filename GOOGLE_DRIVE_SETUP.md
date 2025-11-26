# Configuração do Google Drive para OCR Vision

Este guia explica como configurar a integração com o Google Drive para processar arquivos diretamente da nuvem.

## 📋 Pré-requisitos

- Conta Google
- Acesso ao Google Cloud Console
- Python 3.8 ou superior

## 🔧 Configuração Passo a Passo

### 1. Criar um Projeto no Google Cloud Console

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Clique em **"Selecionar um projeto"** no topo da página
3. Clique em **"Novo Projeto"**
4. Digite um nome para o projeto (ex: "OCR Vision")
5. Clique em **"Criar"**

### 2. Ativar a Google Drive API

1. No menu lateral, vá para **"APIs e Serviços"** > **"Biblioteca"**
2. Pesquise por **"Google Drive API"**
3. Clique na API e depois em **"Ativar"**

### 3. Configurar a Tela de Consentimento OAuth

1. No menu lateral, vá para **"APIs e Serviços"** > **"Tela de consentimento OAuth"**
2. Selecione **"Externo"** como tipo de usuário
3. Clique em **"Criar"**
4. Preencha as informações obrigatórias:
   - **Nome do aplicativo**: OCR Vision
   - **E-mail de suporte do usuário**: seu e-mail
   - **E-mail do desenvolvedor**: seu e-mail
5. Clique em **"Salvar e continuar"**
6. Em **"Escopos"**, clique em **"Adicionar ou remover escopos"**
7. Adicione o escopo: `https://www.googleapis.com/auth/drive`
8. Clique em **"Salvar e continuar"**
9. Em **"Usuários de teste"**, adicione seu e-mail do Google
10. Clique em **"Salvar e continuar"**

### 4. Criar Credenciais OAuth 2.0

1. No menu lateral, vá para **"APIs e Serviços"** > **"Credenciais"**
2. Clique em **"+ Criar Credenciais"** > **"ID do cliente OAuth"**
3. Selecione **"Aplicativo para computador"** como tipo de aplicativo
4. Digite um nome (ex: "OCR Vision Desktop")
5. Clique em **"Criar"**
6. Clique em **"Fazer download do JSON"** (ícone de download)
7. Renomeie o arquivo baixado para **`credentials.json`**
8. Mova o arquivo `credentials.json` para a raiz do projeto OCR-LAB

### 5. Instalar Dependências

Execute o comando para instalar as novas dependências:

```bash
pip install -r requirements.txt
```

## 🚀 Como Usar

### 1. Iniciar o Aplicativo

```bash
cd src/ollama_ocr
streamlit run app.py
```

### 2. Conectar ao Google Drive

1. Na barra lateral, procure a seção **"☁️ Google Drive"**
2. Clique em **"🔐 Conectar ao Google Drive"**
3. Uma janela do navegador será aberta
4. Faça login com sua conta Google
5. Autorize o aplicativo a acessar seu Google Drive
6. Após a autorização, você será redirecionado de volta

### 3. Selecionar uma Pasta

1. Após conectar, você verá a lista de pastas do seu Google Drive
2. Navegue pelas pastas clicando nos botões **"📁 Nome da Pasta"**
3. Clique no botão **"✅"** ao lado da pasta que deseja processar
4. A pasta selecionada será exibida na barra lateral

### 4. Processar Arquivos

1. Vá para a aba **"☁️ Google Drive"** na área principal
2. Você verá a lista de arquivos na pasta selecionada
3. Configure as opções de processamento (modelo, formato, prompt, etc.)
4. Clique em **"🚀 Processar Arquivos do Google Drive"**

### 5. Resultados

- Os arquivos serão baixados temporariamente
- Processados com OCR
- Os resultados serão salvos automaticamente na mesma pasta do Google Drive
- Os nomes dos arquivos de resultado terão o sufixo `_resultado`

## 📁 Estrutura de Arquivos

```
OCR-LAB/
├── credentials.json          # Credenciais OAuth (não commitar!)
├── token.pickle             # Token de autenticação (gerado automaticamente)
├── src/
│   └── ollama_ocr/
│       ├── app.py
│       ├── ocr_processor.py
│       └── google_drive_integration.py
└── requirements.txt
```

## 🔒 Segurança

### Arquivos Sensíveis

Adicione os seguintes arquivos ao `.gitignore`:

```
credentials.json
token.pickle
```

**IMPORTANTE**: Nunca compartilhe ou faça commit dos arquivos `credentials.json` ou `token.pickle`!

### Revogar Acesso

Para revogar o acesso do aplicativo:

1. Vá para [myaccount.google.com/permissions](https://myaccount.google.com/permissions)
2. Encontre "OCR Vision" na lista
3. Clique em **"Remover acesso"**

Ou simplesmente clique no botão **"🚪 Desconectar"** na barra lateral do aplicativo.

## 🐛 Solução de Problemas

### Erro: "Credentials file not found"

**Solução**: Certifique-se de que o arquivo `credentials.json` está na raiz do projeto.

### Erro: "Authentication failed"

**Solução**: 
1. Delete o arquivo `token.pickle`
2. Tente conectar novamente
3. Certifique-se de que seu e-mail está na lista de usuários de teste

### Erro: "Access blocked: This app's request is invalid"

**Solução**:
1. Verifique se a Google Drive API está ativada
2. Verifique se o escopo correto foi adicionado na tela de consentimento
3. Certifique-se de que o tipo de aplicativo é "Aplicativo para computador"

### Arquivos não aparecem na pasta

**Solução**:
- Certifique-se de que os arquivos são dos tipos suportados: PNG, JPG, JPEG, PDF, TIFF, BMP
- Clique no botão **"🔄 Atualizar"** na barra lateral

## 📊 Formatos Suportados

### Entrada (Google Drive)
- Imagens: PNG, JPG, JPEG, TIFF, BMP
- Documentos: PDF

### Saída (Salvos no Google Drive)
- Texto: `.txt`
- JSON: `.json`
- Word 97-2003: `.doc`
- Word: `.docx`

## 💡 Dicas

1. **Organização**: Crie pastas específicas no Google Drive para processar arquivos em lote
2. **Backup**: Os resultados são salvos na mesma pasta dos arquivos originais
3. **Performance**: Para muitos arquivos, considere usar processamento paralelo (ajuste na barra lateral)
4. **Custos**: Se usar APIs pagas (OpenAI, Gemini), monitore os tokens usados nas estatísticas

## 📞 Suporte

Para problemas ou dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação da [Google Drive API](https://developers.google.com/drive/api/guides/about-sdk)

---

**Desenvolvido por Skyone LAB** 🚀

