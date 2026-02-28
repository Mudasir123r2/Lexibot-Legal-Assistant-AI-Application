"""
Count Scanned vs Text-based PDFs
Quick analysis of your Datacollection folder.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from PyPDF2 import PdfReader
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def check_pdf_type(pdf_path: str) -> tuple:
    """
    Check if PDF is text-based or scanned image.
    Works for variable page counts (7-10+ pages).
    
    Returns:
        (total_chars, page_count, is_image_pdf)
    """
    try:
        reader = PdfReader(pdf_path)
        total_text = ""
        page_count = len(reader.pages)
        
        # Check all pages (variable page count: 7-10+ pages)
        for i in range(page_count):
            try:
                text = reader.pages[i].extract_text()
                total_text += text
            except:
                # Skip problematic pages
                continue
        
        char_count = len(total_text.strip())
        
        # Use chars-per-page average to detect scanned images
        # Scanned images: < 40 chars/page average
        avg_chars_per_page = char_count / page_count if page_count > 0 else 0
        is_image = avg_chars_per_page < 40
        
        return (char_count, page_count, is_image)
        
    except Exception as e:
        # Assume image if can't read
        return (0, 1, True)

def analyze_folder(folder_path: Path):
    """Analyze all PDFs in a folder."""
    
    pdf_files = list(folder_path.glob("*.pdf"))
    
    if not pdf_files:
        return {
            "total": 0,
            "text_based": 0,
            "image_based": 0,
            "text_chars": 0,
            "image_chars": 0
        }
    
    text_based = []
    image_based = []
    
    for pdf_file in pdf_files:
        chars, pages, is_image = check_pdf_type(str(pdf_file))
        
        if is_image:
            image_based.append((pdf_file.name, chars, pages))
        else:
            text_based.append((pdf_file.name, chars, pages))
    
    return {
        "total": len(pdf_files),
        "text_based": len(text_based),
        "image_based": len(image_based),
        "text_files": text_based,
        "image_files": image_based
    }

def main():
    """Analyze entire Datacollection folder."""
    
    base_path = Path("D:/fyp/lexibot-judgment/Datacollectiom")
    
    if not base_path.exists():
        logger.error(f"Folder not found: {base_path}")
        return
    
    # Find all subdirectories
    folders = [f for f in base_path.iterdir() if f.is_dir()]
    
    total_pdfs = 0
    total_text_based = 0
    total_image_based = 0
    
    logger.info("=" * 80)
    logger.info("PDF TYPE ANALYSIS - Datacollection Folder")
    logger.info("=" * 80)
    logger.info("")
    
    results = {}
    
    for folder in sorted(folders):
        logger.info(f"📁 Analyzing: {folder.name}")
        result = analyze_folder(folder)
        results[folder.name] = result
        
        total_pdfs += result["total"]
        total_text_based += result["text_based"]
        total_image_based += result["image_based"]
        
        logger.info(f"   Total PDFs: {result['total']}")
        logger.info(f"   ✅ Text-based: {result['text_based']} ({result['text_based']/result['total']*100:.1f}%)")
        logger.info(f"   ⚠️  Image-based: {result['image_based']} ({result['image_based']/result['total']*100:.1f}%)")
        logger.info("")
    
    logger.info("=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total PDFs: {total_pdfs}")
    logger.info(f"✅ Text-based (good): {total_text_based} ({total_text_based/total_pdfs*100:.1f}%)")
    logger.info(f"⚠️  Scanned images (need OCR): {total_image_based} ({total_image_based/total_pdfs*100:.1f}%)")
    logger.info("")
    
    logger.info("=" * 80)
    logger.info("BREAKDOWN BY FOLDER")
    logger.info("=" * 80)
    
    for folder_name in sorted(results.keys()):
        result = results[folder_name]
        if result["total"] > 0:
            image_pct = result["image_based"] / result["total"] * 100
            logger.info(f"{folder_name:20s}: {result['image_based']:3d}/{result['total']:3d} are images ({image_pct:.0f}%)")
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("RECOMMENDATION")
    logger.info("=" * 80)
    
    if total_image_based > total_pdfs * 0.3:
        logger.info("⚠️  HIGH: Over 30% of PDFs are scanned images")
        logger.info("📋 ACTION: Install Tesseract + Poppler for OCR")
        logger.info("📖 GUIDE: See OCR_SETUP.md for installation instructions")
    else:
        logger.info("✅ LOW: Most PDFs are text-based, OCR optional")
    
    logger.info("")

if __name__ == "__main__":
    main()
