# OCR Installation Guide for Windows

Your PDFs are mostly scanned images, so OCR is essential for text extraction.

## Step 1: Install Tesseract OCR Engine

### Download:
1. Visit: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest installer: `tesseract-ocr-w64-setup-5.3.x.exe`
3. Run the installer

### Installation Settings:
- **Installation Path**: Use default `C:\Program Files\Tesseract-OCR\`
- **Additional Languages**: English is pre-selected (sufficient for your legal docs)
- Click "Install"

### Add to System PATH:
1. Open System Properties → Environment Variables
2. Under "System variables", find `Path` → Edit
3. Add new entry: `C:\Program Files\Tesseract-OCR`
4. Click OK on all dialogs

### Verify Installation:
```powershell
tesseract --version
```
Expected output: `tesseract v5.3.x`

---

## Step 2: Install Poppler (PDF to Image Converter)

### Download:
1. Visit: https://github.com/oschwartz10612/poppler-windows/releases/
2. Download latest: `Release-XX.XX.X-0.zip`
3. Extract to: `C:\poppler\`

### Folder Structure After Extraction:
```
C:\poppler\
    Library\
        bin\          <- Contains pdfinfo.exe, pdftoppm.exe
        include\
        lib\
        share\
```

### Add to System PATH:
1. Open System Properties → Environment Variables
2. Under "System variables", find `Path` → Edit
3. Add new entry: `C:\poppler\Library\bin`
4. Click OK on all dialogs

### Verify Installation:
```powershell
pdfinfo -v
```
Expected output: `pdfinfo version X.XX.X`

---

## Step 3: Restart Terminal

**IMPORTANT**: Close ALL terminal windows and reopen to load new PATH variables.

---

## Step 4: Test OCR in Python

Run this test in your FastAPI directory:

```powershell
cd D:\fyp\lexibot-judgment\server_fastapi
.\venv\Scripts\activate
python -c "from utils.document_processor import DocumentProcessor; dp = DocumentProcessor(); print('OCR Available:', dp.use_ocr)"
```

Expected output: `OCR Available: True`

---

## Step 5: Test OCR on Sample PDF

```powershell
python test_ocr.py
```

This will test OCR on a sample scanned PDF from your collection.

---

## Troubleshooting

### Tesseract not found:
- Verify PATH includes `C:\Program Files\Tesseract-OCR`
- Restart terminal
- Check installation: `where tesseract`

### Poppler not found:
- Verify PATH includes `C:\poppler\Library\bin`
- Restart terminal
- Check installation: `where pdfinfo`

### Python can't find libraries:
```powershell
pip install pytesseract pdf2image Pillow
```

---

## Next Steps After Installation

1. **Verify OCR works**: Run test script
2. **Re-ingest documents with OCR**:
   ```powershell
   python scripts\ingest_judgments.py --source files --directory "D:\fyp\lexibot-judgment\Datacollectiom" --recursive --clear
   ```
3. **Monitor OCR in action**: Look for log messages like:
   - `"Low text density... trying OCR..."`
   - `"✅ OCR extracted X characters"`

---

## Expected Processing Time

With OCR enabled for scanned PDFs:
- **Text-based PDF**: ~1 second/document
- **Scanned image PDF**: ~5-10 seconds/document (depends on page count)
- **Total time for 462 PDFs**: 30-60 minutes (if most are scanned)

---

## Performance Tips

- OCR runs at 300 DPI (good quality/speed balance)
- Only triggered when `avg_chars_per_page < 40`
- Text-based PDFs bypass OCR (fast processing)
- Multi-page PDFs processed page-by-page

---

## System Requirements

- **Disk Space**: ~200 MB (Tesseract + Poppler)
- **RAM**: 2-4 GB recommended for OCR
- **CPU**: Multi-core recommended (OCR is CPU-intensive)
