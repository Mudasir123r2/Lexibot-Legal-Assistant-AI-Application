"""
PDF Diagnostic Tool
Checks what's actually in your PDF files to identify the issue.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from PyPDF2 import PdfReader
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def analyze_pdf(pdf_path: str):
    """Analyze a PDF file in detail."""
    try:
        reader = PdfReader(pdf_path)
        
        logger.info("=" * 70)
        logger.info(f"📄 FILE: {Path(pdf_path).name}")
        logger.info("=" * 70)
        logger.info(f"Total Pages: {len(reader.pages)}")
        logger.info("")
        
        total_text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            total_text += page_text + "\n"
            
            logger.info(f"Page {i+1}:")
            logger.info(f"  - Characters: {len(page_text)}")
            logger.info(f"  - Lines: {len(page_text.splitlines())}")
            
            if len(page_text.strip()) > 0:
                # Show first 200 chars of page
                preview = page_text.strip()[:200].replace("\n", " ")
                logger.info(f"  - Preview: {preview}...")
            else:
                logger.info(f"  - ⚠️ EMPTY PAGE (likely image-based)")
            logger.info("")
        
        logger.info(f"Total Extracted: {len(total_text)} characters")
        
        if len(total_text.strip()) < 100:
            logger.warning("⚠️ LOW CONTENT - Likely scanned/image PDF needing OCR")
        else:
            logger.info("✅ Good text content extracted")
        
        logger.info("=" * 70)
        logger.info("")
        
        return total_text
        
    except Exception as e:
        logger.error(f"Error analyzing {pdf_path}: {str(e)}")
        return ""

def main():
    """Analyze sample PDFs from different folders."""
    
    base_path = Path("D:/fyp/lexibot-judgment/Datacollectiom")
    
    # Test files from different categories
    test_files = [
        base_path / "divorce" / "2012_LHC_1234.pdf",  # First divorce case
        base_path / "Criminal Appeal" / "1.pdf",  # The one user showed
        base_path / "bail" / "crl.p._52_k_2023.pdf",  # A bail case
    ]
    
    # If specific files don't exist, find any PDF in each folder
    folders = ["divorce", "Criminal Appeal", "bail", "custody", "Family"]
    
    for folder in folders:
        folder_path = base_path / folder
        if not folder_path.exists():
            continue
            
        pdf_files = list(folder_path.glob("*.pdf"))
        if pdf_files:
            logger.info(f"\n{'='*70}")
            logger.info(f"ANALYZING SAMPLE FROM: {folder}")
            logger.info('='*70)
            
            # Analyze first PDF in folder
            analyze_pdf(str(pdf_files[0]))
            
            # Also check 2nd and 3rd if available
            if len(pdf_files) > 1:
                logger.info(f"\nSecond file check: {pdf_files[1].name}")
                text = analyze_pdf(str(pdf_files[1]))
                
            if len(pdf_files) > 5:
                logger.info(f"\nRandom file check: {pdf_files[5].name}")
                text = analyze_pdf(str(pdf_files[5]))

if __name__ == "__main__":
    main()
