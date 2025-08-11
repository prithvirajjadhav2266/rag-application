#!/bin/bash

echo "RHP RAG Application Setup Script"
echo "================================="

# Check Python version
python_version=$(python3 --version 2>&1)
echo "Detected Python: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
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

# Install ML/AI dependencies (may take longer)
echo "Installing AI/ML dependencies..."
pip install --timeout=600 sentence-transformers>=2.0.0
pip install --timeout=600 faiss-cpu>=1.7.0

# Copy environment file
echo "Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Please edit .env file with your OpenAI API key and other configuration"
fi

# Create directories
echo "Creating necessary directories..."
mkdir -p data/{documents,plots,metadata,faiss_index}
mkdir -p logs

# Set permissions
chmod +x run.py

echo ""
echo "Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your OpenAI API key"
echo "2. Run the application: python run.py"
echo "3. Open your browser to http://localhost:5000"
echo ""
echo "For development:"
echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "  python run.py"
echo ""
echo "For production:"
echo "  pip install gunicorn"
echo "  gunicorn -w 4 -b 0.0.0.0:5000 run:app"