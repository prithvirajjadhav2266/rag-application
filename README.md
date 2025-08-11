# RHP RAG Application

A comprehensive Retrieval-Augmented Generation (RAG) application for analyzing Red Herring Prospectus (RHP) documents. This application uses AI to extract insights, visualize financial data, and provide intelligent Q&A capabilities for IPO document analysis.

## 🚀 Features

### Core Capabilities
- **Document Processing**: Upload and process Word documents (.docx, .doc) with support for tables, images, and complex formatting
- **AI-Powered Analysis**: Get intelligent insights using advanced LLM models and RAG technology
- **Financial Visualization**: Automatically generate plots and charts from financial data
- **Metadata Extraction**: Extract company information, financial metrics, and document metadata
- **RAG Chat Interface**: Interactive Q&A system for document analysis
- **Vector Database**: FAISS-based similarity search for relevant content retrieval

### Specific Features for RHP Documents
- Company information extraction (name, industry, IPO size, listing date)
- Financial statement analysis (revenue, profit, assets, liabilities)
- Lead manager identification
- Risk factor analysis
- Automatic table classification (financial statements, shareholding patterns, etc.)
- Growth rate calculations and trend analysis

## 🛠️ Technology Stack

- **Backend**: Flask (Python web framework)
- **Document Processing**: python-docx, docx2txt, docx2python
- **Vector Database**: FAISS for similarity search
- **AI/LLM**: OpenAI API (configurable for other providers)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Visualization**: Plotly, Matplotlib
- **Frontend**: Bootstrap 5, JavaScript, Chart.js
- **Data Processing**: Pandas, NumPy

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key (or compatible LLM API)
- 4GB+ RAM recommended
- Modern web browser

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/prithvirajjadhav2266/rag-application.git
cd rag-application
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your configuration
```

### 5. Configure Environment Variables
Edit the `.env` file with your settings:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here

# File Upload Configuration
UPLOAD_FOLDER=data/documents
MAX_CONTENT_LENGTH=100MB

# FAISS Configuration
FAISS_INDEX_PATH=data/faiss_index
EMBEDDING_MODEL=all-MiniLM-L6-v2

# LLM Configuration
LLM_MODEL=gpt-3.5-turbo
MAX_TOKENS=1500
TEMPERATURE=0.7
```

### 6. Initialize Directory Structure
The application will automatically create necessary directories, but you can create them manually:
```bash
mkdir -p data/{documents,plots,metadata,faiss_index}
mkdir -p logs
```

## 🚀 Running the Application

### Development Mode
```bash
python run.py
```

### Production Mode
```bash
# Using Gunicorn (install first: pip install gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

The application will be available at `http://localhost:5000`

## 📖 Usage Guide

### 1. Upload Documents
1. Navigate to the **Upload** page
2. Drag and drop or select a Word document (.docx or .doc)
3. Configure processing options:
   - Extract financial data and generate visualizations
   - Generate AI-powered document summary
   - Add to vector database for RAG queries
4. Click "Upload and Process"

### 2. RAG Chat Interface
1. Go to the **RAG Chat** page
2. Ask questions about your uploaded documents:
   - "What is the company's revenue trend?"
   - "What are the main risk factors?"
   - "What is the IPO size and price range?"
   - "Who are the key management team members?"
3. View context sources and relevance scores

### 3. Financial Analytics
1. Visit the **Analytics** page
2. Select a document from the dropdown
3. View:
   - Financial summary and growth rates
   - AI-generated financial analysis
   - Interactive plots and charts
   - Detailed financial data tables

### 4. Document Management
1. Go to the **Documents** page
2. View all uploaded documents
3. Access document details and metadata
4. Delete documents if needed

## 🔌 API Endpoints

### Document Management
- `POST /api/upload` - Upload and process document
- `GET /api/documents` - List all documents
- `GET /api/document/{file_id}/metadata` - Get document metadata
- `DELETE /api/document/{file_id}` - Delete document

### RAG and Analysis
- `POST /api/query` - Query documents using RAG
- `GET /api/financial-analysis/{file_id}` - Get financial analysis
- `GET /api/plots/{filename}` - Serve generated plots

### System
- `GET /api/health` - Health check
- `GET /api/stats` - Application statistics

### Example API Usage

#### Upload Document
```bash
curl -X POST -F "file=@document.docx" http://localhost:5000/api/upload
```

#### Query Document
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"query": "What is the company revenue?", "k": 5}' \
     http://localhost:5000/api/query
```

## 🔧 Configuration Options

### LLM Configuration
- **Model Selection**: Configure different LLM models (GPT-3.5, GPT-4, Claude, etc.)
- **Token Limits**: Adjust maximum tokens per request
- **Temperature**: Control response creativity (0.0-1.0)

### Vector Database
- **Embedding Model**: Change sentence transformer model
- **Chunk Size**: Adjust text chunk size for processing
- **Similarity Threshold**: Set minimum relevance score

### File Processing
- **Upload Limits**: Configure maximum file size
- **Supported Formats**: Currently supports .docx and .doc
- **Processing Options**: Enable/disable specific features

## 🏗️ Architecture

```
rag-application/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py            # Web routes
│   ├── api.py               # API endpoints
│   ├── templates/           # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── upload.html
│   │   ├── chat.html
│   │   ├── analytics.html
│   │   └── documents.html
│   └── utils/
│       ├── document_processor.py    # Document processing
│       ├── vector_db.py            # FAISS vector database
│       ├── llm_manager.py          # LLM integration
│       └── financial_processor.py  # Financial analysis
├── data/
│   ├── documents/          # Uploaded documents
│   ├── faiss_index/        # Vector database files
│   ├── plots/              # Generated visualizations
│   └── metadata/           # Document metadata
├── logs/                   # Application logs
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── run.py                # Application entry point
└── README.md             # This file
```

## 🐛 Troubleshooting

### Common Issues

#### 1. API Key Errors
```
Error: OpenAI API key not configured
```
**Solution**: Ensure `OPENAI_API_KEY` is set in your `.env` file

#### 2. Document Processing Fails
```
Error processing document: No module named 'docx'
```
**Solution**: Install dependencies: `pip install python-docx`

#### 3. Vector Database Issues
```
Error: FAISS index not found
```
**Solution**: The index is created automatically. Ensure write permissions to `data/faiss_index/`

#### 4. Memory Issues
```
MemoryError: Unable to allocate array
```
**Solution**: Increase available RAM or reduce chunk size in configuration

### Performance Optimization

1. **Large Documents**: For documents >50MB, consider increasing chunk size
2. **Multiple Documents**: Use batch processing for better performance
3. **Memory Usage**: Monitor RAM usage with many large documents
4. **API Limits**: Implement rate limiting for production use

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing powerful LLM APIs
- Facebook AI Research for FAISS
- Hugging Face for Sentence Transformers
- The Flask and Python communities

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation

## 🔮 Future Enhancements

- [ ] Support for PDF documents
- [ ] Multi-language support
- [ ] Advanced financial metrics calculation
- [ ] Integration with more LLM providers
- [ ] Real-time collaboration features
- [ ] Advanced visualization options
- [ ] Mobile-responsive design improvements
- [ ] Batch document processing
- [ ] Document comparison features
- [ ] Export functionality for analysis reports

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Author**: Prithviraj Jadhav
