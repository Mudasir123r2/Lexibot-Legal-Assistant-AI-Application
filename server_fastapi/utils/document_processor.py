"""
Document Processing Utilities
Handles text extraction, chunking, and preprocessing for legal documents.
Supports OCR for scanned/image-based PDFs.
"""

from typing import List, Dict, Any, Optional
import re
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# OCR dependencies (optional - will fallback if not available)
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    
    # Configure direct paths for Windows (bypass PATH issues)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    POPPLER_PATH = r'C:\poppler\Library\bin'
    
    OCR_AVAILABLE = True
    logger.info("✅ OCR support enabled (pytesseract + pdf2image)")
except ImportError as e:
    OCR_AVAILABLE = False
    POPPLER_PATH = None
    logger.warning(f"⚠️ OCR support disabled. Install: pip install pytesseract pdf2image pillow")


class DocumentProcessor:
    """
    Process legal documents for RAG pipeline.
    
    Features:
    - Extract text from PDF/DOCX files
    - Clean and normalize text
    - Split into chunks for embedding
    - Extract metadata
    """
    
    def __init__(self, chunk_size: int = 2000, chunk_overlap: int = 400, use_ocr: bool = True):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Target size for text chunks (in characters)
            chunk_overlap: Overlap between chunks to maintain context
            use_ocr: Enable OCR for image-based PDFs (default: True)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.use_ocr = use_ocr and OCR_AVAILABLE
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file. Falls back to OCR for image-based PDFs.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(pdf_path)
            text = ""
            page_count = len(reader.pages)
            
            # Extract from all pages (including first page with barcode and case details)
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # For scanned image PDFs: check if average chars/page is too low
            # Threshold: < 40 chars/page average indicates scanned images
            chars_extracted = len(text.strip())
            avg_chars_per_page = chars_extracted / page_count if page_count > 0 else 0
            
            if avg_chars_per_page < 40 and self.use_ocr:
                logger.warning(f"Low text density ({chars_extracted} chars / {page_count} pages = {avg_chars_per_page:.1f} chars/page) in {pdf_path}, trying OCR...")
                ocr_text = self._extract_text_with_ocr(pdf_path)
                if len(ocr_text) > len(text):
                    logger.info(f"✅ OCR extracted {len(ocr_text)} characters from {page_count}-page {pdf_path}")
                    return ocr_text
            
            logger.info(f"Extracted {len(text)} characters from {page_count} pages ({avg_chars_per_page:.1f} chars/page) in {pdf_path}")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
            # Try OCR as last resort
            if self.use_ocr:
                try:
                    return self._extract_text_with_ocr(pdf_path)
                except:
                    pass
            return ""
    
    def _extract_text_with_ocr(self, pdf_path: str) -> str:
        """
        Extract text from PDF using OCR (for scanned/image-based PDFs).
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text via OCR
        """
        if not OCR_AVAILABLE:
            logger.warning("OCR requested but libraries not available")
            return ""
        
        try:
            # Convert PDF pages to images
            logger.info(f"Converting PDF to images for OCR: {pdf_path}")
            images = convert_from_path(pdf_path, dpi=300, fmt='jpeg', poppler_path=POPPLER_PATH)
            
            text = ""
            for i, image in enumerate(images):
                logger.debug(f"Running OCR on page {i+1}/{len(images)}")
                # Use Tesseract to extract text from image
                page_text = pytesseract.image_to_string(image, lang='eng')
                text += page_text + "\n\n"
            
            logger.info(f"OCR extracted {len(text)} characters from {len(images)} pages")
            return text.strip()
            
        except Exception as e:
            logger.error(f"OCR extraction failed for {pdf_path}: {str(e)}")
            return ""
    
    def extract_text_from_docx(self, docx_path: str) -> str:
        """
        Extract text from DOCX file.
        
        Args:
            docx_path: Path to DOCX file
            
        Returns:
            Extracted text
        """
        try:
            from docx import Document
            
            doc = Document(docx_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            logger.info(f"Extracted {len(text)} characters from {docx_path}")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {docx_path}: {str(e)}")
            return ""
    
    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from file (auto-detect format).
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted text
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif extension == '.docx':
            return self.extract_text_from_docx(file_path)
        elif extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            logger.warning(f"Unsupported file format: {extension}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep legal formatting
        # Keep: periods, commas, parentheses, dashes, colons, semicolons
        text = re.sub(r'[^\w\s.,():\-;]', '', text)
        
        # Normalize line breaks
        text = text.replace('\n\n\n', '\n\n')
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Full text to chunk
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Find nearest sentence boundary
            if end < len(text):
                # Look for period followed by space
                boundary = text.rfind('. ', start, end)
                if boundary == -1:
                    # No sentence boundary, use hard cutoff
                    boundary = end
                else:
                    boundary += 1  # Include the period
                
                chunk = text[start:boundary].strip()
            else:
                chunk = text[start:].strip()
            
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = boundary - self.chunk_overlap if boundary - self.chunk_overlap > start else boundary
            
            if end >= len(text):
                break
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def extract_judgment_metadata(self, text: str) -> Dict[str, Any]:
        """
        Extract metadata from judgment text using pattern matching.
        
        Args:
            text: Judgment text
            
        Returns:
            Dict with extracted metadata
        """
        metadata = {
            "case_number": None,
            "parties": None,
            "court": None,
            "date": None,
            "judges": None
        }
        
        # Extract case number (various patterns)
        case_patterns = [
            r'Civil Appeal No[.:]?\s*(\d+/\d+)',
            r'Criminal Appeal No[.:]?\s*(\d+/\d+)',
            r'Case No[.:]?\s*(\d+/\d+)',
            r'Suit No[.:]?\s*(\d+/\d+)'
        ]
        
        for pattern in case_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata["case_number"] = match.group(1)
                break
        
        # Extract parties (simplified)
        parties_match = re.search(r'(.+?)\s+(?:vs?\.?|versus)\s+(.+?)(?:\n|$)', text, re.IGNORECASE)
        if parties_match:
            metadata["parties"] = f"{parties_match.group(1).strip()} vs {parties_match.group(2).strip()}"
        
        # Extract court name
        court_patterns = [
            r'(Supreme Court of Pakistan)',
            r'(High Court of [A-Z][a-z]+)',
            r'(District Court)',
            r'([A-Z][a-z]+ High Court)'
        ]
        
        for pattern in court_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata["court"] = match.group(1)
                break
        
        # Extract date
        date_patterns = [
            r'Dated?:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})',
            r'Date of [Dd]ecision:?\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                metadata["date"] = match.group(1).strip()
                break
        
        return metadata
    
    def process_judgment_document(
        self,
        file_path: Optional[str] = None,
        text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process a judgment document for indexing.
        
        Args:
            file_path: Path to file (if extracting from file)
            text: Raw text (if already extracted)
            metadata: Additional metadata
            
        Returns:
            List of processed chunks with metadata
        """
        # Extract text if file path provided
        if file_path and not text:
            text = self.extract_text_from_file(file_path)
        
        if not text:
            logger.warning("No text to process")
            return []
        
        # Clean text
        cleaned_text = self.clean_text(text)
        
        # Extract metadata from text
        extracted_metadata = self.extract_judgment_metadata(cleaned_text)
        
        # Merge with provided metadata
        if metadata:
            extracted_metadata.update(metadata)
        
        # Chunk text
        chunks = self.chunk_text(cleaned_text)
        
        # Create documents for each chunk
        documents = []
        for i, chunk in enumerate(chunks):
            doc = {
                "content": chunk,
                "chunk_index": i,
                "total_chunks": len(chunks),
                **extracted_metadata
            }
            documents.append(doc)
        
        logger.info(f"Processed document into {len(documents)} indexed chunks")
        return documents
    
    def extract_key_sections(self, text: str) -> Dict[str, str]:
        """
        Extract key sections from judgment text.
        
        Args:
            text: Full judgment text
            
        Returns:
            Dict with section names and content
        """
        sections = {}
        
        # Common section headers in judgments
        section_patterns = {
            "facts": r"Facts?:?\s*(.*?)(?=\n[A-Z][a-z]+:|$)",
            "issues": r"Issues?:?\s*(.*?)(?=\n[A-Z][a-z]+:|$)",
            "judgment": r"Judgment:?\s*(.*?)(?=\n[A-Z][a-z]+:|$)",
            "conclusion": r"Conclusion:?\s*(.*?)(?=\n[A-Z][a-z]+:|$)",
            "order": r"Order:?\s*(.*?)(?=\n[A-Z][a-z]+:|$)"
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section_name] = match.group(1).strip()
        
        return sections


# Singleton instance
_document_processor = None

def get_document_processor() -> DocumentProcessor:
    """
    Get or create singleton document processor instance.
    
    Returns:
        DocumentProcessor instance
    """
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor()
    return _document_processor
