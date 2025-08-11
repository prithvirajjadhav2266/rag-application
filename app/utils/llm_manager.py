import openai
import json
import logging
from typing import List, Dict, Any, Optional
from config import Config

class LLMManager:
    """Manage LLM API calls for RAG functionality."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key
        
        # Initialize client for newer OpenAI library versions
        self.client = openai.OpenAI(api_key=api_key)
        
        logging.info(f"LLM Manager initialized with model: {model}")
    
    def generate_response(self, query: str, context_chunks: List[Dict[str, Any]], 
                         max_tokens: int = 1500, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate response using RAG approach."""
        try:
            # Prepare context from retrieved chunks
            context = self._prepare_context(context_chunks)
            
            # Create prompt
            prompt = self._create_rag_prompt(query, context)
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract response
            answer = response.choices[0].message.content
            
            # Prepare response with metadata
            result = {
                'answer': answer,
                'sources': self._extract_sources(context_chunks),
                'tokens_used': response.usage.total_tokens,
                'model': self.model,
                'context_chunks_count': len(context_chunks)
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Error generating LLM response: {str(e)}")
            return {
                'answer': f"Sorry, I encountered an error: {str(e)}",
                'sources': [],
                'tokens_used': 0,
                'model': self.model,
                'context_chunks_count': 0,
                'error': str(e)
            }
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for RHP document analysis."""
        return """You are an expert financial analyst specializing in IPO Red Herring Prospectus (RHP) documents. 
        Your role is to analyze and answer questions about company financials, business models, risks, and other 
        information contained in RHP documents.

        Guidelines:
        1. Provide accurate, detailed answers based only on the provided context
        2. If information is not available in the context, clearly state that
        3. When discussing financial data, include specific numbers when available
        4. Highlight key risks and opportunities mentioned in the document
        5. Structure your responses clearly with bullet points or sections when appropriate
        6. Always cite which part of the document your information comes from
        7. Be objective and balanced in your analysis
        
        Remember: You are analyzing official regulatory filings, so accuracy is crucial."""
    
    def _create_rag_prompt(self, query: str, context: str) -> str:
        """Create RAG prompt combining query and context."""
        return f"""Based on the following context from the Red Herring Prospectus document, please answer the question.

Context:
{context}

Question: {query}

Please provide a comprehensive answer based on the information available in the context. If the information is not sufficient to answer completely, please indicate what additional information would be needed."""
    
    def _prepare_context(self, context_chunks: List[Dict[str, Any]]) -> str:
        """Prepare context string from retrieved chunks."""
        if not context_chunks:
            return "No relevant context found in the document."
        
        context_parts = []
        for i, chunk in enumerate(context_chunks):
            chunk_text = chunk.get('text', '').strip()
            score = chunk.get('score', 0)
            doc_metadata = chunk.get('document_metadata', {})
            filename = doc_metadata.get('filename', 'Unknown')
            
            context_part = f"[Source {i+1} - {filename} (Relevance: {score:.2f})]:\n{chunk_text}\n"
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _extract_sources(self, context_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract source information from context chunks."""
        sources = []
        for chunk in context_chunks:
            doc_metadata = chunk.get('document_metadata', {})
            sources.append({
                'filename': doc_metadata.get('filename', 'Unknown'),
                'company_name': doc_metadata.get('company_name', 'Unknown'),
                'document_type': doc_metadata.get('document_type', 'Unknown'),
                'relevance_score': chunk.get('score', 0),
                'chunk_preview': chunk.get('text', '')[:200] + "..." if len(chunk.get('text', '')) > 200 else chunk.get('text', '')
            })
        return sources
    
    def analyze_financial_data(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial data using LLM."""
        try:
            # Prepare financial data summary
            summary = self._prepare_financial_summary(financial_data)
            
            prompt = f"""Analyze the following financial data from an IPO Red Herring Prospectus:

{summary}

Please provide:
1. Key financial highlights and trends
2. Strengths and areas of concern
3. Comparison with industry standards (if possible to infer)
4. Investment considerations
5. Key metrics to watch

Structure your analysis professionally as if for an investor."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior financial analyst providing investment analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3  # Lower temperature for financial analysis
            )
            
            analysis = response.choices[0].message.content
            
            return {
                'analysis': analysis,
                'tokens_used': response.usage.total_tokens,
                'model': self.model
            }
            
        except Exception as e:
            logging.error(f"Error analyzing financial data: {str(e)}")
            return {
                'analysis': f"Error analyzing financial data: {str(e)}",
                'tokens_used': 0,
                'model': self.model,
                'error': str(e)
            }
    
    def _prepare_financial_summary(self, financial_data: Dict[str, Any]) -> str:
        """Prepare financial data summary for LLM analysis."""
        summary_parts = []
        
        # Income statement data
        income_data = financial_data.get('income_statement', [])
        if income_data:
            summary_parts.append("Income Statement Data:")
            for item in income_data:
                summary_parts.append(f"- {item['metric'].title()}: {item['value']} ({item.get('year', 'N/A')})")
        
        # Growth rates
        growth_rates = financial_data.get('growth_rates', {})
        if growth_rates:
            summary_parts.append("\nGrowth Rates:")
            for metric, rate in growth_rates.items():
                summary_parts.append(f"- {metric.title()}: {rate}%")
        
        # Key metrics summary
        key_metrics = financial_data.get('key_metrics', {})
        if key_metrics:
            summary_parts.append("\nKey Metrics by Year:")
            for metric, values in key_metrics.items():
                summary_parts.append(f"- {metric.title()}:")
                for value_data in values:
                    summary_parts.append(f"  - {value_data.get('year', 'N/A')}: {value_data['value']}")
        
        return "\n".join(summary_parts) if summary_parts else "No financial data available for analysis."
    
    def generate_document_summary(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive summary of the RHP document."""
        try:
            # Extract key information
            metadata = document_data.get('metadata', {})
            structured_content = document_data.get('structured_content', {})
            
            # Prepare document overview
            overview = f"""Document: {metadata.get('filename', 'Unknown')}
Company: {metadata.get('company_name', 'Unknown')}
Industry: {metadata.get('industry', 'Unknown')}
IPO Size: {metadata.get('ipo_size', 'Unknown')}
Document Type: {metadata.get('document_type', 'Unknown')}

Sections: {len(structured_content.get('sections', []))}
Tables: {metadata.get('table_count', 0)}
Paragraphs: {metadata.get('paragraph_count', 0)}
"""
            
            # Get first few sections for context
            sections_preview = []
            for section in structured_content.get('sections', [])[:5]:
                content_preview = ' '.join(section['content'][:2])[:300]
                sections_preview.append(f"- {section['title']}: {content_preview}...")
            
            sections_text = "\n".join(sections_preview)
            
            prompt = f"""Analyze this Red Herring Prospectus document and provide a comprehensive summary:

{overview}

Key Sections Preview:
{sections_text}

Please provide:
1. Executive Summary (2-3 sentences)
2. Business Overview
3. Key Financial Highlights
4. Major Risk Factors
5. Investment Highlights
6. Key Information for Investors

Keep the summary professional and investor-focused."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.5
            )
            
            summary = response.choices[0].message.content
            
            return {
                'summary': summary,
                'tokens_used': response.usage.total_tokens,
                'model': self.model
            }
            
        except Exception as e:
            logging.error(f"Error generating document summary: {str(e)}")
            return {
                'summary': f"Error generating summary: {str(e)}",
                'tokens_used': 0,
                'model': self.model,
                'error': str(e)
            }
    
    def validate_api_key(self) -> bool:
        """Validate if the API key is working."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logging.error(f"API key validation failed: {str(e)}")
            return False