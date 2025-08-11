#!/usr/bin/env python3
"""
Demo script for the RHP RAG Application API
This script demonstrates how to use the application's API endpoints.
"""

import requests
import json
import time
import sys

class RAGApplicationDemo:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
    
    def health_check(self):
        """Check if the application is running."""
        try:
            response = requests.get(f"{self.api_url}/health")
            if response.status_code == 200:
                print("✓ Application is running")
                return True
            else:
                print("✗ Application is not responding correctly")
                return False
        except requests.ConnectionError:
            print("✗ Cannot connect to application. Make sure it's running on", self.base_url)
            return False
    
    def get_stats(self):
        """Get application statistics."""
        try:
            response = requests.get(f"{self.api_url}/stats")
            if response.status_code == 200:
                stats = response.json()
                print("\n📊 Application Statistics:")
                print("-" * 30)
                
                db_stats = stats.get('database_stats', {})
                print(f"Documents: {db_stats.get('total_documents', 0)}")
                print(f"Text Chunks: {db_stats.get('total_chunks', 0)}")
                print(f"Index Size: {db_stats.get('index_size', 0)}")
                print(f"LLM Available: {'Yes' if stats.get('llm_available') else 'No'}")
                print(f"Model: {stats.get('llm_model', 'N/A')}")
                
                return True
            else:
                print("✗ Failed to get statistics")
                return False
        except Exception as e:
            print(f"✗ Error getting statistics: {e}")
            return False
    
    def list_documents(self):
        """List all uploaded documents."""
        try:
            response = requests.get(f"{self.api_url}/documents")
            if response.status_code == 200:
                data = response.json()
                documents = data.get('documents', [])
                
                print(f"\n📁 Documents ({len(documents)} total):")
                print("-" * 40)
                
                if documents:
                    for doc in documents:
                        print(f"• {doc.get('filename', 'Unknown')}")
                        print(f"  Company: {doc.get('company_name', 'Unknown')}")
                        print(f"  Chunks: {doc.get('chunk_count', 0)}")
                        print()
                else:
                    print("No documents uploaded yet")
                
                return documents
            else:
                print("✗ Failed to list documents")
                return []
        except Exception as e:
            print(f"✗ Error listing documents: {e}")
            return []
    
    def upload_sample_document(self, file_path):
        """Upload a sample document (if file exists)."""
        try:
            import os
            if not os.path.exists(file_path):
                print(f"Sample file not found: {file_path}")
                return False
            
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.api_url}/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✓ Document uploaded successfully: {result.get('filename')}")
                    return result.get('file_id')
                else:
                    print(f"✗ Upload failed: {result.get('error')}")
                    return False
            else:
                print(f"✗ Upload failed with status: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error uploading document: {e}")
            return False
    
    def query_document(self, query, k=3):
        """Query documents using RAG."""
        try:
            data = {
                'query': query,
                'k': k
            }
            response = requests.post(
                f"{self.api_url}/query",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n🤖 RAG Query: '{query}'")
                print("-" * 50)
                print("Answer:", result.get('answer', 'No answer provided'))
                
                sources = result.get('sources', [])
                if sources:
                    print(f"\n📚 Sources ({len(sources)}):")
                    for i, source in enumerate(sources, 1):
                        print(f"{i}. {source.get('filename', 'Unknown')} "
                              f"(Relevance: {source.get('relevance_score', 0):.2f})")
                
                print(f"\nTokens Used: {result.get('tokens_used', 0)}")
                return True
            else:
                print(f"✗ Query failed with status: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error querying documents: {e}")
            return False
    
    def run_demo(self):
        """Run the complete demo."""
        print("RHP RAG Application API Demo")
        print("=" * 40)
        
        # Health check
        if not self.health_check():
            return False
        
        # Get statistics
        self.get_stats()
        
        # List documents
        documents = self.list_documents()
        
        # Sample queries if documents exist
        if documents:
            print("\n🔍 Sample Queries:")
            print("-" * 20)
            
            sample_queries = [
                "What is the company's revenue?",
                "What are the main risk factors?",
                "Who are the key management team members?",
                "What is the IPO size?"
            ]
            
            for query in sample_queries[:2]:  # Run first 2 queries
                time.sleep(1)  # Rate limiting
                self.query_document(query)
        
        print("\n✓ Demo completed!")
        print("\nTo interact with the application:")
        print(f"• Web Interface: {self.base_url}")
        print(f"• API Documentation: {self.base_url}/api/health")
        return True

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='RHP RAG Application Demo')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='Base URL of the application (default: http://localhost:5000)')
    parser.add_argument('--query', help='Single query to test')
    parser.add_argument('--upload', help='Path to document to upload')
    
    args = parser.parse_args()
    
    demo = RAGApplicationDemo(args.url)
    
    if args.query:
        # Single query mode
        if demo.health_check():
            demo.query_document(args.query)
    elif args.upload:
        # Upload mode
        if demo.health_check():
            demo.upload_sample_document(args.upload)
    else:
        # Full demo mode
        demo.run_demo()

if __name__ == "__main__":
    main()