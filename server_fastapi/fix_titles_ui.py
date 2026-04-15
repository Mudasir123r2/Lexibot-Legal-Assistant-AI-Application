import pathlib
import re

file_paths = [
    pathlib.Path(r'D:\Lexibot-Legal-Assistant-AI-Application\server_fastapi\routes\judgments.py'),
    pathlib.Path(r'D:\Lexibot-Legal-Assistant-AI-Application\server_fastapi\services\rag_pipeline.py')
]

for file_path in file_paths:
    if not file_path.exists(): continue
    content = file_path.read_text(encoding='utf-8')
    
    # We want to replace the format_judgment_title return rules.
    # Instead of returning "Not available in provided metadata", return original title if possible, or fallback carefully.
    new_helper = '''
def format_judgment_title(citation: str, court: str, original_title: str = "") -> str:
    \"\"\"Format judgment title gracefully avoiding 'Not available' spam if possible.\"\"\"
    citation = str(citation or "").strip()
    court = str(court or "").strip()
    original_title = str(original_title or "").strip()
    
    # If original title has a real looking citation (e.g. "1994 SCMR 200"), we could just use it.
    valid_original = original_title and not original_title.startswith("Document from") and "EasyLaw" not in original_title
    
    if citation and court:
        return f"{citation} — {court}"
    elif citation:
        return f"{citation} — {court if court else 'Unknown Court'}"
    
    if valid_original:
        return original_title
        
    if court:
        return f"Judgment — {court}"
    
    return "Untitled Judgment"
'''
    
    # Replace existing helper
    content = re.sub(r'def format_judgment_title.*?return \"Not available in provided metadata\"\n', new_helper.strip() + '\n', content, flags=re.DOTALL)
    
    content = re.sub(r'def format_judgment_title_rag.*?return \"Not available in provided metadata\"\n', new_helper.replace('format_judgment_title', 'format_judgment_title_rag').strip() + '\n', content, flags=re.DOTALL)

    file_path.write_text(content, encoding='utf-8')

print('Titles UI fixed!')
