import pathlib
import re

file_path = pathlib.Path(r'D:\Lexibot-Legal-Assistant-AI-Application\server_fastapi\routes\judgments.py')
content = file_path.read_text(encoding='utf-8')

helper_func = '''
def format_judgment_title(citation: str, court: str, original_title: str = "") -> str:
    \"\"\"Format judgment title strictly as <Citation> — <Court Name>\"\"\"
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

if 'def format_judgment_title' not in content:
    content = content.replace('logger = logging.getLogger(__name__)', 'logger = logging.getLogger(__name__)\n' + helper_func)

# Replace "title":         doc.get("title") or "Untitled Judgment" etc.
# in Semantic Search:
content = re.sub(r'\"title\":\s+doc\.get\(\"title\"\)\s+or\s+\"Untitled Judgment\"', 
                 '\"title\": format_judgment_title(doc.get(\"case_number\"), doc.get(\"court\"), doc.get(\"title\"))', content)

# in SQLite block search
content = re.sub(r'\"title\":\s+title,.*?\"caseNumber\":\s+case_num\s+or\s+\"N/A\"', 
                 '\"title\": format_judgment_title(case_num, row[\"court\"], title),\n                            \"caseNumber\": case_num or \"N/A\"', content, flags=re.DOTALL)

# in MongoDB read block (judgment endpoint)
content = re.sub(r'\"title\":\s+judgment\.get\(\"title\"\)\s+or\s+judgment\.get\(\"name\"\)\s+or\s+\"Untitled Judgment\"',
                 '\"title\": format_judgment_title(judgment.get(\"caseNumber\") or judgment.get(\"case_number\"), judgment.get(\"court\"), judgment.get(\"title\") or judgment.get(\"name\"))', content)

# in SQLite read block (judgment endpoint)
content = re.sub(r'\"title\":\s+ref_row\[\"title\"\]\s+or\s+\"Untitled Judgment\"',
                 '\"title\": format_judgment_title(ref_row[\"case_number\"], ref_row[\"court\"], ref_row[\"title\"])', content)

# save back
file_path.write_text(content, encoding='utf-8')
print('Updated routes!')
