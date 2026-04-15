import pathlib
import re

file_path = pathlib.Path(r'D:\Lexibot-Legal-Assistant-AI-Application\server_fastapi\services\rag_pipeline.py')
content = file_path.read_text(encoding='utf-8')

helper_func = '''
def format_judgment_title_rag(citation: str, court: str, original_title: str = "") -> str:
    citation = str(citation or "").strip()
    court = str(court or "").strip()
    
    if citation and court:
        return f"{citation} — {court}"
    elif citation:
        return f"{citation} — Not available in provided metadata"
    elif court:
        return f"Not available in provided metadata — {court}"
    
    original_title = str(original_title or "").strip()
    if original_title and "EasyLaw_" not in original_title and ".txt" not in original_title:
        return original_title
        
    return "Not available in provided metadata"
'''

if 'def format_judgment_title_rag' not in content:
    content = content.replace('class RAGPipeline:', helper_func + '\nclass RAGPipeline:')

content = re.sub(r'\"title\":\s*doc\.get\([\"\']title[\"\'],\s*[\"\']Untitled Judgment[\"\']\),',
                 '"title": format_judgment_title_rag(doc.get("case_number", ""), doc.get("court", ""), doc.get("title", "")),', content)

file_path.write_text(content, encoding='utf-8')
print('Updated rag_pipeline titles!')
