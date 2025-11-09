# 🚀 Início Rápido

## Instalação em 3 Passos

### Windows
```bash
# 1. Execute o script de setup
setup.bat

# 2. Ative o ambiente virtual
venv\Scripts\activate

# 3. Inicie a aplicação
streamlit run src\ollama_ocr\app.py
```

### Linux/Mac
```bash
# 1. Execute o script de setup
chmod +x setup.sh
./setup.sh

# 2. Ative o ambiente virtual
source venv/bin/activate

# 3. Inicie a aplicação
streamlit run src/ollama_ocr/app.py
```

## Uso Básico

### 1. Ollama Local (Sem API Key)

1. Instale Ollama: https://ollama.ai/
2. Baixe um modelo de visão:
   ```bash
   ollama pull llava:34b
   ```
3. Na aplicação, selecione "Ollama (Local)"
4. Escolha o modelo instalado

### 2. OpenAI

1. Obtenha API key: https://platform.openai.com/api-keys
2. Na aplicação:
   - Selecione "OpenAI"
   - Cole sua API key
   - Escolha o modelo (ex: gpt-4o)

### 3. Google Gemini

1. Obtenha API key: https://makersuite.google.com/app/apikey
2. Na aplicação:
   - Selecione "Google Gemini"
   - Cole sua API key
   - Escolha o modelo (ex: gemini-2.0-flash-exp)

## Primeiro Processamento

1. **Configure**:
   - Escolha o provedor e modelo
   - Selecione formato de saída (ex: markdown)
   - Insira um prompt (ex: "Extraia todo o texto desta imagem")

2. **Upload**:
   - Arraste um arquivo (PNG, JPG, PDF)
   - Veja o preview na coluna direita

3. **Processe**:
   - Clique em "🚀 Processar Arquivo"
   - Aguarde a extração
   - Baixe os resultados

## Exemplos de Prompts

### Extração Simples
```
Extraia todo o texto visível nesta imagem mantendo a formatação original.
```

### Documento Estruturado
```
Extraia o conteúdo deste documento preservando:
- Títulos e subtítulos
- Listas e numerações
- Tabelas (se houver)
- Formatação de parágrafos
```

### Formulário
```
Extraia os campos e valores deste formulário no formato chave-valor.
```

### Tabela
```
Extraia os dados desta tabela mantendo a estrutura de linhas e colunas.
```

## Dicas

- ✅ Use **pré-processamento** para imagens de baixa qualidade
- ✅ **Processamento paralelo** acelera múltiplos arquivos
- ✅ Prompts **específicos** geram melhores resultados
- ✅ Para PDFs, cada página é processada separadamente
- ✅ Teste diferentes **formatos de saída** para seu caso de uso

## Problemas Comuns

### "Ollama não encontrado"
- Instale Ollama: https://ollama.ai/
- Verifique se está rodando: `ollama list`

### "API Key inválida"
- Verifique se copiou a key completa
- Confirme que a key tem permissões corretas

### "Modelo não disponível"
- OpenAI/Gemini: Verifique sua conta
- Ollama: Execute `ollama pull <modelo>`

## Próximos Passos

- 📖 Leia o [README.md](README.md) completo
- 🤝 Veja como [contribuir](CONTRIBUTING.md)
- 🐛 Reporte [issues](https://github.com/seu-usuario/Ollama-OCR/issues)

