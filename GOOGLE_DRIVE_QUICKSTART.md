# 🚀 Google Drive - Guia Rápido

## ⚡ Início Rápido (5 minutos)

### 1️⃣ Obter Credenciais

1. Acesse: https://console.cloud.google.com/
2. Crie um novo projeto
3. Ative a **Google Drive API**
4. Configure a **Tela de Consentimento OAuth**
5. Crie credenciais **OAuth 2.0** tipo "Aplicativo para computador"
6. Baixe o arquivo JSON e renomeie para `credentials.json`
7. Coloque na raiz do projeto: `/OCR-LAB/credentials.json`

### 2️⃣ Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3️⃣ Iniciar Aplicativo

```bash
cd src/ollama_ocr
streamlit run app.py
```

### 4️⃣ Conectar ao Google Drive

1. Na barra lateral, clique em **"🔐 Conectar ao Google Drive"**
2. Faça login com sua conta Google
3. Autorize o acesso

### 5️⃣ Processar Arquivos

1. Navegue e selecione uma pasta
2. Vá para a aba **"☁️ Google Drive"**
3. Configure o modelo e formato de saída
4. Clique em **"🚀 Processar Arquivos do Google Drive"**

**Pronto!** Os resultados serão salvos automaticamente na mesma pasta do Google Drive.

---

## 📋 Checklist de Configuração

- [ ] Projeto criado no Google Cloud Console
- [ ] Google Drive API ativada
- [ ] Tela de Consentimento OAuth configurada
- [ ] Credenciais OAuth 2.0 criadas
- [ ] Arquivo `credentials.json` na raiz do projeto
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Aplicativo iniciado (`streamlit run app.py`)
- [ ] Conectado ao Google Drive
- [ ] Pasta selecionada
- [ ] Primeiro processamento realizado com sucesso

---

## 🎯 Fluxo de Trabalho

```
┌─────────────────────────────────────────────────────────────┐
│  1. Conectar ao Google Drive                                │
│     └─> Autenticação OAuth 2.0                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Navegar e Selecionar Pasta                              │
│     └─> Visualizar arquivos disponíveis                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Configurar Processamento                                │
│     ├─> Escolher modelo (Ollama/OpenAI/Gemini)            │
│     ├─> Selecionar formato de saída                        │
│     └─> Definir prompt (Manual/Automático)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Processar                                               │
│     ├─> Download automático dos arquivos                   │
│     ├─> Processamento OCR com IA                           │
│     └─> Upload automático dos resultados                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  5. Resultados Salvos no Google Drive                       │
│     └─> Mesma pasta dos arquivos originais                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 💡 Dicas Importantes

### ✅ Boas Práticas

- **Organize suas pastas**: Crie pastas específicas para cada tipo de documento
- **Use nomes descritivos**: Facilita identificar os resultados
- **Verifique o formato**: Escolha o formato de saída adequado para seu uso
- **Monitore tokens**: Se usar APIs pagas, acompanhe o consumo

### ⚠️ Evite

- **Não commite** `credentials.json` ou `token.pickle`
- **Não compartilhe** suas credenciais
- **Não processe** pastas com muitos arquivos de uma vez (comece com poucos)
- **Não feche** o navegador durante a autenticação

### 🔒 Segurança

- Suas credenciais ficam **apenas no seu computador**
- O token de acesso é armazenado localmente em `token.pickle`
- Para revogar acesso: https://myaccount.google.com/permissions
- Ou clique em **"🚪 Desconectar"** na barra lateral

---

## 🐛 Problemas Comuns

### "Credentials file not found"
**Solução**: Certifique-se de que `credentials.json` está na raiz do projeto

### "Authentication failed"
**Solução**: Delete `token.pickle` e tente conectar novamente

### "No files found"
**Solução**: Verifique se há arquivos PNG, JPG, JPEG, PDF, TIFF ou BMP na pasta

### "Upload failed"
**Solução**: Verifique sua conexão com a internet e permissões da pasta

---

## 📚 Documentação Completa

Para configuração detalhada, consulte: **[GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md)**

---

## 🎉 Pronto para Começar!

Agora você pode processar documentos diretamente do Google Drive com OCR Vision!

**Desenvolvido por Skyone LAB** 🚀

