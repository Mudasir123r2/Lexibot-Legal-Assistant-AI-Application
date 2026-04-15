import pathlib
import re

formatter_code = '''
def format_judgment_title(citation: str, court: str, original_title: str = "", excerpt: str = "") -> str:
    \"\"\"Format judgment title by extracting from excerpt if exact metadata is missing\"\"\"
    import re
    
    citation = str(citation or "").strip()
    court = str(court or "").strip()
    original_title = str(original_title or "").strip()
    excerpt = str(excerpt or "").strip()
    
    # Extract from excerpt if citation is missing
    extracted_case_no = ""
    extracted_parties = ""
    
    if excerpt:
        # Try to find parties (e.g. Appellant Versus Respondent)
        parties_match = re.search(r'([A-Za-z\s\.\(\)]+?)\s+(?:Appellant|Petitioner).*?(?:Versus|VERSUS|Vs\.?|vs\.?)\s+([A-Za-z\s\.\(\)]+?)\s+(?:Respondent|Defendant)', excerpt, re.IGNORECASE)
        if parties_match:
            p1 = re.sub(r'\s+', ' ', parties_match.group(1)).strip()
            p2 = re.sub(r'\s+', ' ', parties_match.group(2)).strip()
            # Clean up common noise
            p1 = p1.replace("decd through LRs", "").replace("deceased through LRs", "").strip()
            p2 = p2.replace("decd through LRs", "").replace("deceased through LRs", "").strip()
            extracted_parties = f"{p1} v. {p2}"
            
        # Try to find case number
        case_match = re.search(r'(?:Appeal|C\.P\.L\.A\.|W\.P\.|Suit|Revision|C\.R\.|No\.)[\sA-Za-z]*No\.?\s*[\d\-\/A-Za-z\s]+?(?:of|dated)?\s*\d{4}', excerpt, re.IGNORECASE)
        if case_match:
            extracted_case_no = re.sub(r'\s+', ' ', case_match.group(0)).strip()
            
    final_citation = citation if citation else extracted_case_no
    
    # Construction logic
    if final_citation and extracted_parties and court:
        return f"{final_citation} — {extracted_parties} — {court}"
    elif final_citation and court:
        return f"{final_citation} — {court}"
    elif extracted_parties and court:
        return f"{extracted_parties} — {court}"
    elif final_citation:
        return f"{final_citation} — {court if court else 'Unknown Court'}"
        
    valid_original = original_title and not original_title.startswith("Document from") and "EasyLaw" not in original_title
    if valid_original:
        return original_title
        
    if court:
        return f"Judgment — {court}"
        
    return "Untitled Judgment"
'''

file_paths = [
    pathlib.Path(r'D:\Lexibot-Legal-Assistant-AI-Application\server_fastapi\routes\judgments.py'),
    pathlib.Path(r'D:\Lexibot-Legal-Assistant-AI-Application\server_fastapi\services\rag_pipeline.py')
]

for file_path in file_paths:
    if not file_path.exists(): continue
    content = file_path.read_text(encoding='utf-8')
    
    # Replace function definition
    if 'def format_judgment_title_rag' in content: # rag_pipeline.py
        content = re.sub(r'def format_judgment_title_rag.*?return \"Untitled Judgment\"\n', formatter_code.replace('format_judgment_title', 'format_judgment_title_rag').strip() + '\n', content, flags=re.DOTALL)
        
        # update calls in rag_pipeline to pass excerpt
        content = re.sub(r'format_judgment_title\(doc\.get\(\"case_number\", \"\"\), doc\.get\(\"court\", \"\"\), doc\.get\(\"title\", \"\"\)\)', 
                         'format_judgment_title_rag(doc.get("case_number", ""), doc.get("court", ""), doc.get("title", ""), doc.get("excerpt", doc.get("content", "")))', content)
                         
    elif 'def format_judgment_title' in content: # judgments.py
        content = re.sub(r'def format_judgment_title.*?return \"Untitled Judgment\"\n', formatter_code.strip() + '\n', content, flags=re.DOTALL)
        
        # Semantic search block
        content = re.sub(r'format_judgment_title\(doc\.get\(\"case_number\"\), doc\.get\(\"court\"\), doc\.get\(\"title\"\)\)',
                         'format_judgment_title(doc.get("case_number"), doc.get("court"), doc.get("title"), doc.get("excerpt"))', content)
                         
        # SQLite metadata chunk loop block
        content = re.sub(r'format_judgment_title\(chunk\.get\(\"case_number\"\), chunk\.get\(\"court\"\), title\)',
                         'format_judgment_title(chunk.get("case_number"), chunk.get("court"), title, chunk.get("excerpt"))', content)
                         
        # SQLite search query loop block
        content = re.sub(r'format_judgment_title\(case_num, row\[\"court\"\], title\)',
                         'format_judgment_title(case_num, row["court"], title, row["excerpt"])', content)
                         
        # Judgment by ID read block (MongoDB) -> we don't have excerpt easily here unless its summary, so pass summary
        content = re.sub(r'format_judgment_title\(judgment\.get\(\"caseNumber\"\).*?judgment\.get\(\"name\"\)\)',
                         'format_judgment_title(judgment.get("caseNumber") or judgment.get("case_number"), judgment.get("court"), judgment.get("title") or judgment.get("name"), judgment.get("summary") or judgment.get("fullText", ""))', content)
                         
        # Judgment by ID read block (SQLite) 
        content = re.sub(r'format_judgment_title\(ref_row\[\"case_number\"\], ref_row\[\"court\"\], ref_row\[\"title\"\]\)',
                         'format_judgment_title(ref_row["case_number"], ref_row["court"], ref_row["title"], ref_row["excerpt"])', content)
                         
    file_path.write_text(content, encoding='utf-8')

print("Excerpts regex extractor injected!")
