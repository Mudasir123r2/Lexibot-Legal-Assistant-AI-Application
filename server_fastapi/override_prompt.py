with open(r"D:\Lexibot-Legal-Assistant-AI-Application\server_fastapi\services\llm_service.py", "r", encoding="utf-8") as f:
    text = f.read()

import re
pattern = re.compile(r'system_prompt\s*=\s*\"\"\"You are a Senior Legal Data Engineer for Lexibot\.\s+Transform this dirty OCR text into clean structured data\.\s+Follow ALL rules\s+strictly:(?:.|\n)*?tag it\.\"\"\"')
new_str = '''system_prompt = """You are an Expert Legal Data Engineer and Restorer for Lexibot. 
Transform this raw, noisy, or poorly structured legal text (from OCR/scraping) into a clean, highly structured, and accurate legal document. 
Follow ALL rules strictly:

1. CLEAN TEXT & OCR REPAIR: Remove random asterisks (**), merge split words, fix punctuation, standardize whitespace, and correct poor sentence connections. Remove redundant tokens.
2. CORRECT METADATA VALIDATION: Identify the true Court, Date, and Citation. If the text mentions a different Court than the title implies (e.g. "Supreme Court" vs "Lahore High Court"), resolve it logically based on the judge/context and explicitly state the Correct Court at the top.
3. ADD LEGAL STRUCTURE: Reorganize the content logically. Add these clear Markdown sections (use `###`):
   ### Facts
   ### Issues
   ### Arguments
   ### Analysis / Legal Reasoning (Clearly separate legal from religious/social commentary)
   ### Decision / Ratio Decidendi
   *(Note: If the source text lacks facts/issues/arguments, definitively state "Not explicitly detailed in the retrieved text" under that heading. Do NOT hallucinate).*
4. POST-PROCESSING & NOISE REDUCTION: Deduplicate redundant listings (like repeated Quranic verses or case names).
5. AMBIGUOUS REFERENCES RESOLUTION: When cases are referenced (e.g., "case of Zubaida Khatoon"), try to format them clearly or note missing reference data.
6. LEGAL ENTITY TAGGING: Cleanly Bold **Party Names** and **Statutory References**. *Italicize* Latin Maxims. Do not excessively format.
7. METADATA SECTION: Add an organized 'Lexibot Metadata' section at the end with 'Keywords:' and 'Statutes Cited:'.
"""'''

if pattern.search(text):
    text = pattern.sub(new_str, text, count=1)
    with open(r"D:\Lexibot-Legal-Assistant-AI-Application\server_fastapi\services\llm_service.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("YES replaced")
else:
    print("NO MATCH")
