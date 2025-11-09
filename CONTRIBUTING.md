# Contribuindo para OCR Vision - Skyone LAB

Obrigado por considerar contribuir para o OCR Vision! 🎉

## Como Contribuir

### Reportando Bugs

Se você encontrou um bug, por favor abra uma issue incluindo:

- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs atual
- Screenshots (se aplicável)
- Versão do Python e sistema operacional

### Sugerindo Melhorias

Para sugerir novas funcionalidades:

1. Verifique se já não existe uma issue similar
2. Abra uma nova issue com o label "enhancement"
3. Descreva claramente a funcionalidade e seu caso de uso

### Pull Requests

1. **Fork** o repositório
2. **Clone** seu fork localmente
3. **Crie uma branch** para sua feature:
   ```bash
   git checkout -b feature/minha-feature
   ```
4. **Faça suas alterações** seguindo o guia de estilo
5. **Teste** suas alterações
6. **Commit** com mensagens claras:
   ```bash
   git commit -m "feat: adiciona suporte para novo formato"
   ```
7. **Push** para seu fork:
   ```bash
   git push origin feature/minha-feature
   ```
8. Abra um **Pull Request** descrevendo suas mudanças

## Guia de Estilo

### Python

- Siga PEP 8
- Use type hints quando possível
- Docstrings para funções e classes
- Máximo de 100 caracteres por linha

### Commits

Use conventional commits:

- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Documentação
- `style:` - Formatação
- `refactor:` - Refatoração
- `test:` - Testes
- `chore:` - Manutenção

### Código

```python
def process_image(image_path: str, format_type: str = "markdown") -> str:
    """
    Processa uma imagem e extrai texto.
    
    Args:
        image_path: Caminho para a imagem
        format_type: Formato de saída desejado
        
    Returns:
        Texto extraído no formato especificado
    """
    # Implementação
    pass
```

## Ambiente de Desenvolvimento

1. Clone o repositório
2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Instale dependências de desenvolvimento:
   ```bash
   pip install -r requirements.txt
   ```

## Testando

Antes de enviar um PR, teste:

1. Funcionalidade com Ollama local
2. Funcionalidade com OpenAI (se tiver API key)
3. Funcionalidade com Gemini (se tiver API key)
4. Upload de diferentes formatos (PNG, JPG, PDF)
5. Processamento em lote

## Dúvidas?

Sinta-se à vontade para abrir uma issue com suas dúvidas!

