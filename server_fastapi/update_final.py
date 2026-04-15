# -*- coding: utf-8 -*-
import re

file_path = r"D:\Lexibot-Legal-Assistant-AI-Application\server_fastapi\services\llm_service.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Update signature
content = content.replace("def clean_ocr_text(self, dirty_text: str) -> str:", "def clean_ocr_text(self, dirty_text: str, metadata: dict = None) -> str:")

# Update prompt body
new_prompt_body = r'''        if metadata is None:
            metadata = {}
            
        system_prompt = """You are a strict, structured legal data extractor and formatter.
You will receive raw OCR text and a set of Known Metadata.

CRITICAL RULES:
1. ONLY utilize the provided KNOWN METADATA for the Court, Date, Citation, Appeal No, Parties, and Statutes. Do NOT invent, extract, or overwrite these fields using the raw OCR text. If a metadata field is missing or empty, write "Not available in the provided metadata".
2. NEVER use internal chunk IDs or file names (like "EasyLaw_2000_...").
3. Your FINAL output must be clean Markdown, but you must strictly follow this format:

### Case Title
<Citation or Year from metadata> - <Court Name from metadata>

### Court
[Exactly from metadata]

### Date
[Exactly from metadata]

### Citation / Appeal No.
[Exactly from metadata]

### Parties
[Exactly from metadata]

### Facts
[Extract concise facts from text cleanly. No OCR noise. If none, write "Not explicitly detailed in the retrieved text."]

### Issues
[Extract legal issues. If none, write "Not explicitly detailed in the retrieved text."]

### Arguments
[Extract arguments if present. If none, write "Not explicitly detailed in the retrieved text."]

### Analysis / Legal Reasoning
[Summarize reasoning. Maintain professional legal tone. Separate law from social commentary.]

### Decision / Holding
[State the exact outcome.]

### Statutes & Relevant Law
[Exactly from metadata or extracted from text]

If there are inconsistencies between the text and the Known Metadata, list them at the bottom under "### Inconsistencies".

Do NOT output raw JSON, just the structured Markdown above. Do not include random asterisks ** from OCR noise.
"""

        known_meta_str = "\n".join([f"{k}: {v}" for k, v in metadata.items() if v])
        prompt = f"KNOWN METADATA:\n{known_meta_str}\n\nRAW OCR TEXT TO CLEAN & STRUCTURE:\n{dirty_text}"
'''

pattern = re.compile(r'system_prompt\s*=\s*\"\"\".*?\"\"\"\n+        prompt = f\"Please clean and tag this legal text:\\n\\n.*?\"', re.DOTALL)
if pattern.search(content):
    content = pattern.sub(new_prompt_body, content)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated clean_ocr_text prompt and signature!")
else:
    print("Could not find the prompt block to replace.")
