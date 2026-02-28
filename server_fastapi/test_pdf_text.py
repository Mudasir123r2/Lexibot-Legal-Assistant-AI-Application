"""Test if PDFs have extractable text"""
from PyPDF2 import PdfReader
import os

divorce_dir = r'D:\fyp\lexibot-judgment\Datacollectiom\divorce'
pdf_files = [f for f in os.listdir(divorce_dir) if f.endswith('.pdf')][:10]

print("Testing first 10 divorce PDFs:\n")
for pdf in pdf_files:
    path = os.path.join(divorce_dir, pdf)
    try:
        reader = PdfReader(path)
        text = reader.pages[0].extract_text()
        print(f"{pdf}: {len(text)} chars on page 1")
    except Exception as e:
        print(f"{pdf}: ERROR - {e}")
