import os
import json
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional, Tuple
import logging

class VectorDatabase:
    """FAISS-based vector database for document embeddings."""
    
    def __init__(self, index_path: str, embedding_model: str = 'all-MiniLM-L6-v2'):
        self.index_path = index_path
        self.embedding_model_name = embedding_model
        self.embedding_model = SentenceTransformer(embedding_model)
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize FAISS index
        self.index = None
        self.documents = []  # Store document metadata
        self.chunks = []     # Store text chunks
        
        # Create index directory
        os.makedirs(index_path, exist_ok=True)
        
        # Load existing index if available
        self.load_index()
        
        logging.info(f"Vector database initialized with model: {embedding_model}")
    
    def load_index(self) -> bool:
        """Load existing FAISS index and metadata."""
        try:
            index_file = os.path.join(self.index_path, 'faiss_index.bin')
            metadata_file = os.path.join(self.index_path, 'metadata.pkl')
            chunks_file = os.path.join(self.index_path, 'chunks.pkl')
            
            if all(os.path.exists(f) for f in [index_file, metadata_file, chunks_file]):
                # Load FAISS index
                self.index = faiss.read_index(index_file)
                
                # Load metadata
                with open(metadata_file, 'rb') as f:
                    self.documents = pickle.load(f)
                
                # Load chunks
                with open(chunks_file, 'rb') as f:
                    self.chunks = pickle.load(f)
                
                logging.info(f"Loaded existing index with {len(self.chunks)} chunks")
                return True
            else:
                # Create new index
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
                logging.info("Created new FAISS index")
                return False
                
        except Exception as e:
            logging.error(f"Error loading index: {str(e)}")
            self.index = faiss.IndexFlatIP(self.dimension)
            return False
    
    def save_index(self) -> bool:
        """Save FAISS index and metadata to disk."""
        try:
            index_file = os.path.join(self.index_path, 'faiss_index.bin')
            metadata_file = os.path.join(self.index_path, 'metadata.pkl')
            chunks_file = os.path.join(self.index_path, 'chunks.pkl')
            
            # Save FAISS index
            faiss.write_index(self.index, index_file)
            
            # Save metadata
            with open(metadata_file, 'wb') as f:
                pickle.dump(self.documents, f)
            
            # Save chunks
            with open(chunks_file, 'wb') as f:
                pickle.dump(self.chunks, f)
            
            logging.info(f"Saved index with {len(self.chunks)} chunks")
            return True
            
        except Exception as e:
            logging.error(f"Error saving index: {str(e)}")
            return False
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > start + chunk_size // 2:  # Ensure reasonable chunk size
                    chunk = text[start:start + break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks
    
    def add_document(self, document_data: Dict[str, Any], file_id: str) -> bool:
        """Add a document to the vector database."""
        try:
            # Extract text content
            text_content = document_data.get('text_content', '')
            
            # Also include structured content
            structured_content = document_data.get('structured_content', {})
            for section in structured_content.get('sections', []):
                text_content += f"\n\nSection: {section['title']}\n"
                text_content += '\n'.join(section['content'])
            
            # Add table content as text
            tables = document_data.get('tables', [])
            for table in tables:
                if table.get('type') == 'financial_statement':
                    table_text = f"\nFinancial Table ({table['type']}):\n"
                    for row in table.get('data', []):
                        table_text += ' | '.join(row) + '\n'
                    text_content += table_text
            
            # Chunk the text
            chunks = self.chunk_text(text_content)
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(chunks, convert_to_tensor=False)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add to FAISS index
            self.index.add(embeddings.astype('float32'))
            
            # Store metadata
            document_metadata = {
                'file_id': file_id,
                'filename': document_data.get('metadata', {}).get('filename', 'unknown'),
                'company_name': document_data.get('metadata', {}).get('company_name'),
                'document_type': document_data.get('metadata', {}).get('document_type', 'unknown'),
                'processing_timestamp': document_data.get('processing_timestamp'),
                'chunk_count': len(chunks)
            }
            
            # Store chunks with metadata
            start_idx = len(self.chunks)
            for i, chunk in enumerate(chunks):
                self.chunks.append({
                    'text': chunk,
                    'document_id': file_id,
                    'chunk_id': start_idx + i,
                    'document_metadata': document_metadata
                })
            
            self.documents.append(document_metadata)
            
            # Save updated index
            self.save_index()
            
            logging.info(f"Added document {file_id} with {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logging.error(f"Error adding document to vector database: {str(e)}")
            return False
    
    def search(self, query: str, k: int = 5, score_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Search for relevant document chunks."""
        try:
            if self.index.ntotal == 0:
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query], convert_to_tensor=False)
            faiss.normalize_L2(query_embedding)
            
            # Search in FAISS index
            scores, indices = self.index.search(query_embedding.astype('float32'), k)
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and score >= score_threshold:  # Valid index and above threshold
                    chunk_data = self.chunks[idx].copy()
                    chunk_data['score'] = float(score)
                    results.append(chunk_data)
            
            return results
            
        except Exception as e:
            logging.error(f"Error searching vector database: {str(e)}")
            return []
    
    def get_document_chunks(self, file_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document."""
        return [chunk for chunk in self.chunks if chunk['document_id'] == file_id]
    
    def get_documents(self) -> List[Dict[str, Any]]:
        """Get list of all documents in the database."""
        return self.documents.copy()
    
    def delete_document(self, file_id: str) -> bool:
        """Delete a document and its chunks from the database."""
        try:
            # Find chunks to delete
            chunks_to_keep = []
            chunks_to_remove = []
            
            for i, chunk in enumerate(self.chunks):
                if chunk['document_id'] == file_id:
                    chunks_to_remove.append(i)
                else:
                    chunks_to_keep.append(chunk)
            
            if not chunks_to_remove:
                logging.warning(f"No chunks found for document {file_id}")
                return False
            
            # Remove document from documents list
            self.documents = [doc for doc in self.documents if doc['file_id'] != file_id]
            
            # Rebuild the index without the removed chunks
            self.chunks = chunks_to_keep
            
            if self.chunks:
                # Re-encode all remaining chunks
                all_texts = [chunk['text'] for chunk in self.chunks]
                embeddings = self.embedding_model.encode(all_texts, convert_to_tensor=False)
                faiss.normalize_L2(embeddings)
                
                # Create new index
                self.index = faiss.IndexFlatIP(self.dimension)
                self.index.add(embeddings.astype('float32'))
            else:
                # Create empty index
                self.index = faiss.IndexFlatIP(self.dimension)
            
            # Save updated index
            self.save_index()
            
            logging.info(f"Deleted document {file_id} and {len(chunks_to_remove)} chunks")
            return True
            
        except Exception as e:
            logging.error(f"Error deleting document from vector database: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        return {
            'total_documents': len(self.documents),
            'total_chunks': len(self.chunks),
            'index_size': self.index.ntotal if self.index else 0,
            'embedding_dimension': self.dimension,
            'model_name': self.embedding_model_name
        }
    
    def clear_database(self) -> bool:
        """Clear all data from the database."""
        try:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.documents = []
            self.chunks = []
            self.save_index()
            logging.info("Cleared vector database")
            return True
        except Exception as e:
            logging.error(f"Error clearing database: {str(e)}")
            return False