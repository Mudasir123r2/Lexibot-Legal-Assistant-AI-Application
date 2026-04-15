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
        Clean and normalize text. Preserves tabular/vertical structure and removes duplicate OCR headers.
        """
        # 1. Deduplicate repetitive OCR headers/footers (e.g., repeating case numbers across PDF pages)
        lines = text.split('\n')
        line_counts = {}
        for line in lines:
            line_str = line.strip()
            if len(line_str) > 5:
                line_counts[line_str] = line_counts.get(line_str, 0) + 1
                
        cleaned_lines = []
        for line in lines:
            line_str = line.strip()
            # If a line repeats >3 times across the document, it's almost certainly OCR pagination noise
            if len(line_str) > 5 and line_counts.get(line_str, 0) > 3:
                continue
            cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)

        # 2. Prevent flattening: Consolidate horizontal spaces only, safely preserving line breaks
        text = re.sub(r'[ \t\f\v]+', ' ', text)
        
        # 3. Clean extreme vertical whitespace (compress >2 newlines into 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 4. Remove special characters but keep legal formatting and critically preserve newlines (\n)
        text = re.sub(r'[^\w\s.,():\-;\n]', '', text)
        
        return text.strip()
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks semantically.
        Cascades from Paragraph -> Line -> Sentence.
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end >= len(text):
                chunk = text[start:].strip()
                if chunk:
                    chunks.append(chunk)
                break
                
            # Semantic search window (look back from 'end' to find a clean break)
            window_text = text[start:end]
            
            # Cascade 1: Double newline (Paragraphs)
            boundary_offset = window_text.rfind('\n\n')
            
            # Cascade 2: Single newline (Tables / Lists)
            if boundary_offset == -1 or boundary_offset < self.chunk_size // 2:
                boundary_offset = window_text.rfind('\n')
                
            # Cascade 3: Sentence ending
            if boundary_offset == -1 or boundary_offset < self.chunk_size // 2:
                boundary_offset = window_text.rfind('. ')
            
            # If a boundary was found, include it in the chunk
            if boundary_offset != -1:
                if window_text[boundary_offset:].startswith('\n\n'):
                    boundary_offset += 2
                elif window_text[boundary_offset:].startswith('\n'):
                    boundary_offset += 1
                elif window_text[boundary_offset:].startswith('. '):
                    boundary_offset += 2
            else:
                # No clean boundary, force cutoff
                boundary_offset = len(window_text)
                
            chunk = text[start:start+boundary_offset].strip()
            if chunk:
                chunks.append(chunk)
            
            # Advance start pointer, applying overlap
            next_start = start + boundary_offset - self.chunk_overlap
            
            # Prevent infinite loops if overlap is bigger than the identified boundary chunk
            if next_start <= start:
                next_start = start + boundary_offset
                
            start = next_start
            
        logger.info(f"Semantically split text into {len(chunks)} chunks")
        return chunks
    
    def extract_judgment_metadata(self, text: str, filename: str = "") -> Dict[str, Any]:
        """
        Extract metadata from judgment text using pattern matching.
        
        Args:
            text: Judgment text
            filename: Source filename for additional pattern matching
            
        Returns:
            Dict with extracted metadata
        """
        metadata = {
            "case_number": None,
            "parties": None,
            "court": None,
            "date": None,
            "judges": None,
            "lawyers": None,
            "journal": None,
            "year": None
        }
        
        # Parse filename if it looks like EasyLaw_1955_PLD_1_ID.pdf
        if filename:
            file_match = re.search(r'(?:EasyLaw_)?(\d{4})_([A-Za-z_]+)_(\d+)', filename, re.IGNORECASE)
            if file_match:
                metadata["year"] = file_match.group(1)
                metadata["journal"] = file_match.group(2).replace('_', ' ')
                metadata["case_number"] = file_match.group(3)
        
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
                
        # Extract Judge(s)
        judge_patterns = [
            r'Before\s+[:]?\s*([^,\n]+)',
            r'PRESENT:\s+([^,\n]+)',
            r'Coram[:]?\s*([^,\n]+)'
        ]
        for pattern in judge_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                # Exclude if it looks like a date or unrelated
                if len(val) < 50 and "court" not in val.lower():
                    metadata["judges"] = val
                    break

        # Extract Lawyers
        lawyer_patterns = [
            r'For the Appellants?[:]?\s*([^,\n]+)',
            r'For the Respondents?[:]?\s*([^,\n]+)',
            r'Counsel for.+?[:]\s*([^,\n]+)'
        ]
        lawyers = []
        for pattern in lawyer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                if len(val) < 50:
                    lawyers.append(val)
        if lawyers:
            metadata["lawyers"] = " | ".join(lawyers)
            
        # Construct standard title: [Parties], [Year] [Journal] [Case/Page] ([Court])
        parties = metadata["parties"] or "Unknown v. Unknown"
        year = metadata["year"] or metadata["date"] or "Unknown Year"
        # Only use year if it exists as 4 digits
        if year and len(str(year)) > 4:
            year_match = re.search(r'\d{4}', str(year))
            year = year_match.group(0) if year_match else "Unknown Year"
        
        journal = metadata["journal"] or ""
        case_no = metadata["case_number"] or ""
        court = metadata["court"] or "Unknown Court"
        
        citation = f"{year} {journal} {case_no}".replace("  ", " ").strip()
        if citation:
            metadata["title"] = f"{parties}, {citation} ({court})"
        else:
            metadata["title"] = f"{parties} ({court})"
            
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
        filename = metadata.get("source_file", "") if metadata else ""
        extracted_metadata = self.extract_judgment_metadata(cleaned_text, filename=filename)
        
        # Merge with provided metadata
        # Prioritize the dynamically formatted title if parties were found.
        has_extracted_parties = "parties" in extracted_metadata and "Unknown v. Unknown" not in extracted_metadata["title"]
        
        if metadata:
            original_title = metadata.pop("title", None)
            extracted_metadata.update(metadata)
            if not has_extracted_parties and original_title:
                extracted_metadata["title"] = original_title
        
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
