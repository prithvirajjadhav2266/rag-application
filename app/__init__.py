from flask import Flask
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os

def create_app():
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize configuration
    Config.init_app(app)
    
    # Configure logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/rag_app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('RAG Application startup')
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    from app.api import api
    app.register_blueprint(api, url_prefix='/api')
    
    return app