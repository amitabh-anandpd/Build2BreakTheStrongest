"""
agents/content_extractor.py
Extracts text, metadata, and structure from PDF files
"""

import PyPDF2
import re
from typing import Dict, List
from pathlib import Path


class ContentExtractor:
    """Extracts and structures content from PDF documents"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def extract(self, pdf_path: str) -> Dict:
        """
        Extract text and metadata from PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dict containing text, metadata, and citations
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        if pdf_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported format: {pdf_path.suffix}")
        
        # Extract text and metadata
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract metadata
            metadata = pdf_reader.metadata or {}
            
            # Extract text from all pages
            text_parts = []
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    text_parts.append(f"[Page {page_num}]\n{text}")
            
            full_text = "\n\n".join(text_parts)
        
        # Generate citations
        citations = self._extract_citations(metadata, pdf_path.name)
        
        # Extract key sections
        sections = self._identify_sections(full_text)
        
        return {
            'text': full_text,
            'metadata': {
                'title': metadata.get('/Title', pdf_path.stem),
                'author': metadata.get('/Author', 'Unknown'),
                'subject': metadata.get('/Subject', ''),
                'num_pages': len(pdf_reader.pages)
            },
            'citations': citations,
            'sections': sections,
            'filename': pdf_path.name
        }
    
    def _extract_citations(self, metadata: Dict, filename: str) -> List[Dict]:
        """Generate citation information from PDF metadata"""
        citations = []
        
        # Primary citation
        citation = {
            'type': 'document',
            'title': metadata.get('/Title', filename),
            'author': metadata.get('/Author', 'Unknown'),
            'source': filename
        }
        citations.append(citation)
        
        return citations
    
    def _identify_sections(self, text: str) -> List[Dict]:
        """Identify major sections in the document"""
        sections = []
        
        # Look for common section headers
        section_patterns = [
            r'^#+\s+(.+)$',  # Markdown headers
            r'^([A-Z][A-Za-z\s]{2,30}):$',  # Title case headers with colon
            r'^(\d+\.)\s+([A-Z].+)$',  # Numbered sections
            r'^([A-Z\s]{5,30})$',  # ALL CAPS headers
        ]
        
        lines = text.split('\n')
        current_section = None
        section_text = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check if line matches section pattern
            is_header = False
            for pattern in section_patterns:
                if re.match(pattern, line):
                    # Save previous section
                    if current_section:
                        sections.append({
                            'title': current_section,
                            'text': '\n'.join(section_text),
                            'start_line': i - len(section_text)
                        })
                    
                    current_section = line
                    section_text = []
                    is_header = True
                    break
            
            if not is_header and current_section:
                section_text.append(line)
        
        # Add final section
        if current_section:
            sections.append({
                'title': current_section,
                'text': '\n'.join(section_text),
                'start_line': len(lines) - len(section_text)
            })
        
        return sections if sections else [{'title': 'Main Content', 'text': text, 'start_line': 0}]