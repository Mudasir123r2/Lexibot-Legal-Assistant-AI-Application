import sys
import logging
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from utils.document_processor import get_document_processor

logging.basicConfig(level=logging.INFO)

mock_ocr = """
SC SMC No. 11/2011 Supreme Court Pakistan
C.R.P. Nos. 309 to 312, 320, 321
Page 1

This is the start of the judgment. The court noted several factual anomalies in the allocations.

SC SMC No. 11/2011 Supreme Court Pakistan
C.R.P. Nos. 309 to 312, 320, 321
Page 2

Here is a list of allottees:
Name    Plot No.    Size    Date    Price
Ahmed   12          500     2011    1500000
Fatima  18          250     2011    750000
Ali     21          500     2012    1600000

SC SMC No. 11/2011 Supreme Court Pakistan
C.R.P. Nos. 309 to 312, 320, 321
Page 3

The findings are as follows. 
1. The allotments were done without proper authorization and in violation of the rules.
2. The prices were artificially low.

SC SMC No. 11/2011 Supreme Court Pakistan
C.R.P. Nos. 309 to 312, 320, 321
Page 4

This demonstrates a clear abuse of public office. The appeal is dismissed.
"""

doc_processor = get_document_processor()
doc_processor.chunk_size = 300 # deliberately small to test cascading
doc_processor.chunk_overlap = 50

print("--- ORIGINAL TEXT LENGTH ---", len(mock_ocr))
cleaned = doc_processor.clean_text(mock_ocr)

print("\n--- CLEANED TEXT ---")
print(cleaned)

print("\n--- CHUNKING ---")
chunks = doc_processor.chunk_text(cleaned)
for i, c in enumerate(chunks):
    print(f"\n[CHUNK {i+1} | Length: {len(c)}]")
    print(c)
