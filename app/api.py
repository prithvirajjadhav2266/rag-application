from flask import Blueprint, request, jsonify, current_app
import os
import json
from werkzeug.utils import secure_filename
import logging
from datetime import datetime
import uuid

# Delay imports to avoid circular imports
def get_document_processor():
    from app.utils.document_processor import DocumentProcessor
    return DocumentProcessor

def get_vector_database():
    from app.utils.vector_db import VectorDatabase
    return VectorDatabase

def get_llm_manager():
    from app.utils.llm_manager import LLMManager
    return LLMManager

def get_financial_processor():
    from app.utils.financial_processor import FinancialDataProcessor
    return FinancialDataProcessor

api = Blueprint('api', __name__)

# Initialize processors
def get_processors():
    """Get initialized processor instances."""
    DocumentProcessor = get_document_processor()
    VectorDatabase = get_vector_database()
    LLMManager = get_llm_manager()
    FinancialDataProcessor = get_financial_processor()
    
    doc_processor = DocumentProcessor(
        current_app.config['UPLOAD_FOLDER'],
        current_app.config['METADATA_DIR']
    )
    
    vector_db = VectorDatabase(
        current_app.config['FAISS_INDEX_PATH'],
        current_app.config['EMBEDDING_MODEL']
    )
    
    llm_manager = None
    if current_app.config.get('OPENAI_API_KEY'):
        llm_manager = LLMManager(
            current_app.config['OPENAI_API_KEY'],
            current_app.config['LLM_MODEL']
        )
    
    financial_processor = FinancialDataProcessor(
        current_app.config['PLOTS_DIR']
    )
    
    return doc_processor, vector_db, llm_manager, financial_processor

@api.route('/health', methods=['GET'])
def health_check():
    """API health check."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': current_app.config.get('APP_VERSION', '1.0.0')
    })

@api.route('/upload', methods=['POST'])
def upload_and_process():
    """Upload and process document via API."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file type
        if not (file.filename.lower().endswith('.docx') or file.filename.lower().endswith('.doc')):
            return jsonify({'error': 'Invalid file type. Only .docx and .doc files are supported'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        file.save(file_path)
        
        # Process document
        doc_processor, vector_db, llm_manager, financial_processor = get_processors()
        
        # Extract document content
        document_data = doc_processor.process_document(file_path)
        
        # Add to vector database
        vector_db.add_document(document_data, file_id)
        
        # Extract financial data
        financial_data = financial_processor.extract_financial_tables(
            document_data.get('text_content', '')
        )
        
        # Generate summary if LLM is available
        summary = None
        if llm_manager:
            summary_result = llm_manager.generate_document_summary(document_data)
            summary = summary_result.get('summary')
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': filename,
            'document_summary': {
                'word_count': len(document_data.get('text_content', '').split()),
                'table_count': len(document_data.get('tables', [])),
                'company_name': document_data.get('metadata', {}).get('company_name'),
                'document_type': document_data.get('metadata', {}).get('document_type'),
                'has_financial_data': bool(financial_data.get('income_statement'))
            },
            'ai_summary': summary,
            'processing_timestamp': document_data.get('processing_timestamp')
        })
        
    except Exception as e:
        logging.error(f"Upload processing error: {str(e)}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@api.route('/query', methods=['POST'])
def query_documents():
    """Query documents using RAG."""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        k = data.get('k', 5)  # Number of results
        
        doc_processor, vector_db, llm_manager, financial_processor = get_processors()
        
        if not llm_manager:
            return jsonify({'error': 'LLM service not configured'}), 500
        
        # Search for relevant chunks
        search_results = vector_db.search(query, k=k)
        
        if not search_results:
            return jsonify({
                'answer': 'No relevant information found in the uploaded documents.',
                'sources': [],
                'context_chunks': 0
            })
        
        # Generate response using LLM
        response = llm_manager.generate_response(query, search_results)
        
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"Query processing error: {str(e)}")
        return jsonify({'error': f'Query failed: {str(e)}'}), 500

@api.route('/financial-analysis/<file_id>', methods=['GET'])
def financial_analysis(file_id):
    """Get financial analysis for a document."""
    try:
        doc_processor, vector_db, llm_manager, financial_processor = get_processors()
        
        # Get document chunks
        chunks = vector_db.get_document_chunks(file_id)
        if not chunks:
            return jsonify({'error': 'Document not found'}), 404
        
        # Reconstruct document text
        document_text = ' '.join([chunk['text'] for chunk in chunks])
        
        # Extract financial data
        financial_data = financial_processor.extract_financial_tables(document_text)
        
        # Generate financial summary
        financial_summary = financial_processor.generate_financial_summary(financial_data)
        
        # Create plots
        plots = []
        try:
            revenue_plot = financial_processor.create_revenue_trend_plot(financial_data)
            if revenue_plot:
                plots.append({
                    'type': 'revenue_trend',
                    'filename': revenue_plot,
                    'title': 'Revenue Trend Analysis'
                })
            
            dashboard_plot = financial_processor.create_financial_dashboard(financial_data)
            if dashboard_plot:
                plots.append({
                    'type': 'financial_dashboard',
                    'filename': dashboard_plot,
                    'title': 'Financial Dashboard'
                })
        except Exception as plot_error:
            logging.warning(f"Plot generation failed: {str(plot_error)}")
        
        # Generate AI analysis if available
        ai_analysis = None
        if llm_manager and financial_data.get('income_statement'):
            analysis_result = llm_manager.analyze_financial_data(financial_summary)
            ai_analysis = analysis_result.get('analysis')
        
        return jsonify({
            'financial_data': financial_data,
            'financial_summary': financial_summary,
            'plots': plots,
            'ai_analysis': ai_analysis
        })
        
    except Exception as e:
        logging.error(f"Financial analysis error: {str(e)}")
        return jsonify({'error': f'Financial analysis failed: {str(e)}'}), 500

@api.route('/documents', methods=['GET'])
def list_documents():
    """List all processed documents."""
    try:
        doc_processor, vector_db, llm_manager, financial_processor = get_processors()
        
        documents = vector_db.get_documents()
        
        return jsonify({
            'documents': documents,
            'total_count': len(documents)
        })
        
    except Exception as e:
        logging.error(f"Document listing error: {str(e)}")
        return jsonify({'error': f'Failed to list documents: {str(e)}'}), 500

@api.route('/document/<file_id>/metadata', methods=['GET'])
def get_document_metadata(file_id):
    """Get detailed metadata for a document."""
    try:
        doc_processor, vector_db, llm_manager, financial_processor = get_processors()
        
        # Get document chunks to verify existence
        chunks = vector_db.get_document_chunks(file_id)
        if not chunks:
            return jsonify({'error': 'Document not found'}), 404
        
        # Get document metadata
        documents = vector_db.get_documents()
        document_meta = next((doc for doc in documents if doc['file_id'] == file_id), None)
        
        if not document_meta:
            return jsonify({'error': 'Document metadata not found'}), 404
        
        # Load detailed metadata from file if available
        metadata_file = os.path.join(
            current_app.config['METADATA_DIR'],
            f"{document_meta['filename'].split('.')[0]}_metadata.json"
        )
        
        detailed_metadata = {}
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                detailed_metadata = json.load(f)
        
        return jsonify({
            'document_metadata': document_meta,
            'detailed_metadata': detailed_metadata,
            'chunk_count': len(chunks)
        })
        
    except Exception as e:
        logging.error(f"Metadata retrieval error: {str(e)}")
        return jsonify({'error': f'Failed to get metadata: {str(e)}'}), 500

@api.route('/document/<file_id>', methods=['DELETE'])
def delete_document(file_id):
    """Delete a document and its data."""
    try:
        doc_processor, vector_db, llm_manager, financial_processor = get_processors()
        
        # Delete from vector database
        success = vector_db.delete_document(file_id)
        
        if not success:
            return jsonify({'error': 'Document not found or deletion failed'}), 404
        
        return jsonify({
            'success': True,
            'message': f'Document {file_id} deleted successfully'
        })
        
    except Exception as e:
        logging.error(f"Document deletion error: {str(e)}")
        return jsonify({'error': f'Failed to delete document: {str(e)}'}), 500

@api.route('/stats', methods=['GET'])
def get_stats():
    """Get application statistics."""
    try:
        doc_processor, vector_db, llm_manager, financial_processor = get_processors()
        
        db_stats = vector_db.get_stats()
        
        # Check LLM availability
        llm_available = False
        if llm_manager:
            llm_available = llm_manager.validate_api_key()
        
        return jsonify({
            'database_stats': db_stats,
            'llm_available': llm_available,
            'llm_model': current_app.config.get('LLM_MODEL'),
            'embedding_model': current_app.config.get('EMBEDDING_MODEL'),
            'app_version': current_app.config.get('APP_VERSION')
        })
        
    except Exception as e:
        logging.error(f"Stats retrieval error: {str(e)}")
        return jsonify({'error': f'Failed to get stats: {str(e)}'}), 500

@api.route('/plots/<filename>')
def serve_plot(filename):
    """Serve generated plot files."""
    try:
        plot_path = os.path.join(current_app.config['PLOTS_DIR'], filename)
        if not os.path.exists(plot_path):
            return jsonify({'error': 'Plot not found'}), 404
        
        # Read and return the HTML plot file
        with open(plot_path, 'r', encoding='utf-8') as f:
            plot_content = f.read()
        
        return plot_content, 200, {'Content-Type': 'text/html'}
        
    except Exception as e:
        logging.error(f"Plot serving error: {str(e)}")
        return jsonify({'error': f'Failed to serve plot: {str(e)}'}), 500