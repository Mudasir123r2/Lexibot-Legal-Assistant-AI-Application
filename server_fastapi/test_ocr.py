"""
Test OCR functionality on a sample scanned PDF
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from utils.document_processor import DocumentProcessor
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

def test_ocr_availability():
    """Test if OCR libraries are available."""
    print("\n" + "="*60)
    print("Step 1: Testing OCR Availability")
    print("="*60)
    
    dp = DocumentProcessor(use_ocr=True)
    
    if dp.use_ocr:
        print("✅ OCR is AVAILABLE")
        print("   - pytesseract: Installed")
        print("   - pdf2image: Installed")
        print("   - Pillow: Installed")
        return True
    else:
        print("❌ OCR is NOT AVAILABLE")
        print("\n   Missing Python packages. Install with:")
        print("   pip install pytesseract pdf2image Pillow")
        return False

def test_system_tools():
    """Test if Tesseract and Poppler are installed."""
    print("\n" + "="*60)
    print("Step 2: Testing System Tools")
    print("="*60)
    
    import subprocess
    
    # Test Tesseract
    try:
        result = subprocess.run(
            ['tesseract', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        version_line = result.stdout.split('\n')[0]
        print(f"✅ Tesseract OCR: {version_line}")
        tesseract_ok = True
    except FileNotFoundError:
        print("❌ Tesseract NOT FOUND")
        print("   Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Add to PATH: C:\\Program Files\\Tesseract-OCR")
        tesseract_ok = False
    except Exception as e:
        print(f"❌ Tesseract Error: {e}")
        tesseract_ok = False
    
    # Test Poppler
    try:
        result = subprocess.run(
            ['pdfinfo', '-v'],
            capture_output=True,
            text=True,
            timeout=5
        )
        version_line = result.stderr.split('\n')[0]  # pdfinfo outputs to stderr
        print(f"✅ Poppler (pdfinfo): {version_line}")
        poppler_ok = True
    except FileNotFoundError:
        print("❌ Poppler NOT FOUND")
        print("   Download from: https://github.com/oschwartz10612/poppler-windows/releases/")
        print("   Extract to: C:\\poppler")
        print("   Add to PATH: C:\\poppler\\Library\\bin")
        poppler_ok = False
    except Exception as e:
        print(f"❌ Poppler Error: {e}")
        poppler_ok = False
    
    return tesseract_ok and poppler_ok

def test_sample_pdf():
    """Test OCR on a sample PDF from Datacollection."""
    print("\n" + "="*60)
    print("Step 3: Testing OCR on Sample PDF")
    print("="*60)
    
    # Find a sample PDF
    datacollection = Path("D:/fyp/lexibot-judgment/Datacollectiom")
    
    if not datacollection.exists():
        print("❌ Datacollection folder not found")
        return False
    
    # Try to find a PDF in any subfolder
    sample_pdf = None
    for folder in ["divorce", "bail", "Criminal Appeal", "custody", "Family", "Laws"]:
        folder_path = datacollection / folder
        if folder_path.exists():
            pdfs = list(folder_path.glob("*.pdf"))
            if pdfs:
                sample_pdf = pdfs[0]
                break
    
    if not sample_pdf:
        print("❌ No PDF found in Datacollection")
        return False
    
    print(f"\nTesting on: {sample_pdf.name}")
    print(f"Location: {sample_pdf.parent.name}/")
    
    dp = DocumentProcessor(use_ocr=True)
    
    print("\nExtracting text (this may take 10-30 seconds for scanned PDFs)...")
    text = dp.extract_text_from_pdf(str(sample_pdf))
    
    print("\n" + "-"*60)
    print("Extraction Results:")
    print("-"*60)
    print(f"Characters extracted: {len(text)}")
    print(f"First 500 characters:\n")
    print(text[:500])
    print("\n...")
    
    if len(text) > 100:
        print("\n✅ OCR WORKING! Successfully extracted text from PDF")
        return True
    else:
        print("\n⚠️ Very little text extracted. PDF might be:")
        print("   - Completely blank")
        print("   - Corrupted")
        print("   - OCR not working properly")
        return False

def main():
    """Run all OCR tests."""
    print("\n" + "="*60)
    print("OCR System Test for Lexibot Judgment RAG")
    print("="*60)
    
    # Test 1: Python packages
    if not test_ocr_availability():
        print("\n⚠️ Install Python packages first, then re-run this test")
        return
    
    # Test 2: System tools
    if not test_system_tools():
        print("\n⚠️ Install Tesseract and Poppler, then re-run this test")
        print("   See INSTALL_OCR.md for detailed instructions")
        return
    
    # Test 3: Sample PDF
    test_sample_pdf()
    
    print("\n" + "="*60)
    print("OCR Test Complete!")
    print("="*60)
    print("\nIf all tests passed, you're ready to ingest documents with OCR:")
    print("python scripts\\ingest_judgments.py --source files --directory \"D:\\fyp\\lexibot-judgment\\Datacollectiom\" --recursive --clear")
    print("\n")

if __name__ == "__main__":
    main()
