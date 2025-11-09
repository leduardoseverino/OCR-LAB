@echo off
REM Setup script for OCR Vision - Skyone LAB (Windows)

echo 🚀 Configurando OCR Vision - Skyone LAB...

REM Check Python version
python --version
if errorlevel 1 (
    echo ❌ Python não encontrado. Por favor, instale Python 3.8 ou superior.
    pause
    exit /b 1
)

REM Create virtual environment
echo 📦 Criando ambiente virtual...
python -m venv venv

REM Activate virtual environment
echo 🔌 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Instalando dependências...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create necessary directories
echo 📁 Criando diretórios...
if not exist "input" mkdir input
if not exist "output" mkdir output

echo.
echo ✅ Instalação concluída!
echo.
echo Para iniciar a aplicação:
echo   1. Ative o ambiente virtual: venv\Scripts\activate.bat
echo   2. Execute: streamlit run src\ollama_ocr\app.py
echo.
pause

