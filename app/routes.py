from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
import os
from werkzeug.utils import secure_filename
import logging

main = Blueprint('main', __name__)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@main.route('/upload', methods=['GET', 'POST'])
def upload_document():
    """Upload and process RHP document."""
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                flash(f'File {filename} uploaded successfully!', 'success')
                return redirect(url_for('main.document_details', filename=filename))
                
            except Exception as e:
                flash(f'Error uploading file: {str(e)}', 'error')
                logging.error(f"Upload error: {str(e)}")
        else:
            flash('Invalid file type. Please upload a .docx or .doc file.', 'error')
    
    return render_template('upload.html')

@main.route('/documents')
def list_documents():
    """List all uploaded documents."""
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        documents = []
        
        if os.path.exists(upload_folder):
            for filename in os.listdir(upload_folder):
                if allowed_file(filename):
                    file_path = os.path.join(upload_folder, filename)
                    file_stats = os.stat(file_path)
                    
                    documents.append({
                        'filename': filename,
                        'size': file_stats.st_size,
                        'modified': file_stats.st_mtime
                    })
        
        return render_template('documents.html', documents=documents)
        
    except Exception as e:
        flash(f'Error listing documents: {str(e)}', 'error')
        return render_template('documents.html', documents=[])

@main.route('/document/<filename>')
def document_details(filename):
    """Show document details and analysis."""
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            flash('Document not found', 'error')
            return redirect(url_for('main.list_documents'))
        
        # This will be enhanced with actual document processing
        document_info = {
            'filename': filename,
            'path': file_path,
            'size': os.path.getsize(file_path),
            'status': 'Ready for processing'
        }
        
        return render_template('document_details.html', document=document_info)
        
    except Exception as e:
        flash(f'Error loading document: {str(e)}', 'error')
        return redirect(url_for('main.list_documents'))

@main.route('/chat')
def chat_interface():
    """RAG chat interface."""
    return render_template('chat.html')

@main.route('/analytics')
def analytics_dashboard():
    """Financial analytics dashboard."""
    return render_template('analytics.html')

@main.route('/settings')
def settings():
    """Application settings."""
    return render_template('settings.html')