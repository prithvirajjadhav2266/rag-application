import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'data/documents'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'docx', 'doc'}
    
    # FAISS Configuration
    FAISS_INDEX_PATH = os.environ.get('FAISS_INDEX_PATH') or 'data/faiss_index'
    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL') or 'all-MiniLM-L6-v2'
    
    # LLM Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    LLM_MODEL = os.environ.get('LLM_MODEL') or 'gpt-3.5-turbo'
    MAX_TOKENS = int(os.environ.get('MAX_TOKENS', 1500))
    TEMPERATURE = float(os.environ.get('TEMPERATURE', 0.7))
    
    # Application Configuration
    APP_NAME = os.environ.get('APP_NAME') or 'RHP RAG Application'
    APP_VERSION = os.environ.get('APP_VERSION') or '1.0.0'
    
    # Paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    PLOTS_DIR = os.path.join(DATA_DIR, 'plots')
    METADATA_DIR = os.path.join(DATA_DIR, 'metadata')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        # Create directories if they don't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.FAISS_INDEX_PATH, exist_ok=True)
        os.makedirs(Config.PLOTS_DIR, exist_ok=True)
        os.makedirs(Config.METADATA_DIR, exist_ok=True)
        os.makedirs(Config.LOGS_DIR, exist_ok=True)