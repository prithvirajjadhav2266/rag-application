@echo off
echo RHP RAG Application Setup Script
echo =================================

REM Check Python version
python --version
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install --timeout=300 flask>=2.0.0
pip install --timeout=300 python-docx>=0.8.0
pip install --timeout=300 python-dotenv>=0.19.0
pip install --timeout=300 werkzeug>=2.0.0
pip install --timeout=300 openai>=1.0.0
pip install --timeout=300 pandas>=1.5.0
pip install --timeout=300 numpy>=1.20.0
pip install --timeout=300 matplotlib>=3.5.0
pip install --timeout=300 plotly>=5.0.0
pip install --timeout=300 beautifulsoup4>=4.10.0
pip install --timeout=300 lxml>=4.6.0
pip install --timeout=300 pillow>=8.0.0
pip install --timeout=300 openpyxl>=3.0.0

REM Install ML/AI dependencies
echo Installing AI/ML dependencies...
pip install --timeout=600 sentence-transformers>=2.0.0
pip install --timeout=600 faiss-cpu>=1.7.0

REM Copy environment file
echo Setting up environment configuration...
if not exist .env (
    copy .env.example .env
    echo Please edit .env file with your OpenAI API key and other configuration
)

REM Create directories
echo Creating necessary directories...
mkdir data\documents 2>nul
mkdir data\plots 2>nul
mkdir data\metadata 2>nul
mkdir data\faiss_index 2>nul
mkdir logs 2>nul

echo.
echo Setup completed successfully!
echo.
echo Next steps:
echo 1. Edit .env file with your OpenAI API key
echo 2. Run the application: python run.py
echo 3. Open your browser to http://localhost:5000
echo.
echo For development:
echo   venv\Scripts\activate
echo   python run.py
echo.
pause