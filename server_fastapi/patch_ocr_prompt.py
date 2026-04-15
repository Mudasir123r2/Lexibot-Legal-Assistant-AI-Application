import re

with open(r"D:\Lexibot-Legal-Assistant-AI-Application\server_fastapi\services\llm_service.py", 'r', encoding='utf-8') as f:
    code = f.read()

old_prompt = """        system_prompt = \"\"\"You are a Senior Legal Data Engineer for Lexibot. 
Transform this dirty OCR text into clean structured data. Follow ALL rules 
strictly:
  1. OCR Repair: Merge split words.
  2. Contextual Completion: Restore truncated words based on context.
  3. Legal Entity Tagging: Bold Party Names and Statutory References. 
Italicize Latin Maxims.
  4. Structure & Cleaning: Fix punctuation, remove trailing hyphens, 
standardize whitespace.
  5. Metadata: Add 'Lexibot Metadata' section at the end with 'Keywords:' and 
'Statutes Cited:'
  
  Do NOT summarize or omit content. Preserve the full text, just clean it and 
tag it.\"\"\""""

new_prompt = """        system_prompt = \"\"\"You are an Expert Legal Data Engineer and Restorer for Lexibot. 
Transform this raw, noisy, or poorly structured legal text (from OCR/scraping) into a clean, highly structured, and accurate legal document. 
Follow ALL rules strictly:

1. CLEAN TEXT & OCR REPAIR: Remove random asterisks (**), merge split words, fix punctuation, remove trailing hyphens, standardize whitespace, and correct poor sentence structure.
2. METADATA VALIDATION: Identify the true Court, Date, and Citation. If the provided metadata conflicts with the text (e.g. "Supreme Court" vs "Lahore High Court"), resolve it logically based on the judge/context and explicitly state the correct metadata at the top.
3. ADD LEGAL STRUCTURE: Reorganize the content logically into clear sections (use Markdown headers `###`):
   - Facts
   - Issues
   - Arguments
   - Analysis / Reasoning (Separate legal from religious/social commentary)
   - Decision
   *(Note: If the source text completely lacks facts/issues/arguments, state "Not explicitly detailed in the retrieved text." Do NOT hallucinate content).*
4. POST-PROCESSING & NOISE REDUCTION: Deduplicate redundant listings (like repeated Quranic verses or case names).
5. AMBIGUOUS REFERENCES: When cases are referenced (e.g., Zubaida Khatoon), try to format them cleanly as proper citations.
6. LEGAL ENTITY TAGGING: Cleanly bold Party Names and Statutory References. Italicize Latin Maxims. Avoid overwhelming formatting.
7. METADATA SECTION: Add 'Lexibot Metadata' section at the very end with 'Keywords:' and 'Statutes Cited:'.
\"\"\""""

code = code.replace(old_prompt, new_prompt)

with open(r"D:\Lexibot-Legal-Assistant-AI-Application\server_fastapi\services\llm_service.py", 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated LLM Service Prompt.")
