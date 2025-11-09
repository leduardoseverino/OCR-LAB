#!/bin/bash

# Setup script for OCR Vision - Skyone LAB

echo "🚀 Configurando OCR Vision - Skyone LAB..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo "📦 Criando ambiente virtual..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Ativando ambiente virtual..."
source venv/bin/activate

# Install dependencies
echo "📥 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Criando diretórios..."
mkdir -p input output

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "Para iniciar a aplicação:"
echo "  1. Ative o ambiente virtual: source venv/bin/activate"
echo "  2. Execute: streamlit run src/ollama_ocr/app.py"
echo ""

