import pathlib
import re

formatter_code = '''
def format_judgment_title(citation: str, court: str, original_title: str = "", excerpt: str = "") -> str:
    \"\"\"Format judgment title gracefully and extract from text if needed.\"\"\"
    import re
    
    citation = str(citation or "").strip()
    court = str(court or "").strip()
    original_title = str(original_title or "").strip()
    excerpt = str(excerpt or "").strip()
    
    extracted_case_no = ""
    extracted_parties = ""
    
    if excerpt:
        # Match parties
        parties_match = re.search(r'([A-Za-z\s\.\(\)\&]+?)\s+(?:Appellant(?:s)?|Petitioner(?:s)?|Plaintiff(?:s)?).*?(?:Versus|VERSUS|Vs\.?|vs\.?)\s+([A-Za-z\s\.\(\)\&]+?)\s+(?:Respondent(?:s)?|Defendant(?:s)?)', excerpt, re.IGNORECASE)
        if parties_match:
            p1 = re.sub(r'\s+', ' ', parties_match.group(1)).replace("decd through LRs", "").replace("deceased through LRs", "").strip()
            p2 = re.sub(r'\s+', ' ', parties_match.group(2)).replace("decd through LRs", "").replace("deceased through LRs", "").strip()
            if len(p1) > 2 and len(p2) > 2:
                extracted_parties = f"{p1} v. {p2}"
                
        # Match case numbers
        case_match = re.search(r'(?:Appeal|C\.P\.L\.A\.|W\.P\.|Suit|Revision|C\.R\.|No\.?)[\sA-Za-z]*No\.?\s*[\d\-\/A-Za-z\s]+?(?:of|dated)?\s*\d{4}', excerpt, re.IGNORECASE)
        if case_match:
            extracted_case_no = re.sub(r'\s+', ' ', case_match.group(0)).strip()
            
    final_citation = citation if citation else extracted_case_no
    
    if final_citation and extracted_parties and court:
        return f"{final_citation} — {extracted_parties} — {court}"
    elif final_citation and extracted_parties:
        return f"{final_citation} — {extracted_parties}"
    elif extracted_parties and court:
        return f"{extracted_parties} — {court}"
    elif final_citation and court:
        return f"{final_citation} — {court}"
    elif final_citation:
        return f"{final_citation} — {court if court else 'Unknown Court'}"
        
    valid_original = original_title and "Document from" not in original_title and "EasyLaw" not in original_title
    if valid_original:
        return original_title
        
    if court:
        return f"Judgment — {court}"
        
    return "Untitled Judgment"
'''

file_path = pathlib.Path(r'D:\Lexibot-Legal-Assistant-AI-Application\server_fastapi\routes\judgments.py')
if file_path.exists():
    content = file_path.read_text(encoding='utf-8')
    
    # Simple replace
    old_func = re.search(r'def format_judgment_title\(.*?return \"Untitled Judgment\"\n', content, flags=re.DOTALL)
    if old_func:
        content = content.replace(old_func.group(0), formatter_code.strip() + '\n')
    
    # Update calls
    content = content.replace('format_judgment_title(doc.get("case_number"), doc.get("court"), doc.get("title"))',
                              'format_judgment_title(doc.get("case_number"), doc.get("court"), doc.get("title"), doc.get("excerpt"))')
    content = content.replace('format_judgment_title(chunk.get("case_number"), chunk.get("court"), title)',
                              'format_judgment_title(chunk.get("case_number"), chunk.get("court"), title, chunk.get("excerpt"))')
    content = content.replace('format_judgment_title(case_num, row["court"], title)',
                              'format_judgment_title(case_num, row["court"], title, row["excerpt"])')
    content = content.replace('format_judgment_title(judgment.get("caseNumber") or judgment.get("case_number"), judgment.get("court"), judgment.get("title") or judgment.get("name"))',
                              'format_judgment_title(judgment.get("caseNumber") or judgment.get("case_number"), judgment.get("court"), judgment.get("title") or judgment.get("name"), judgment.get("summary") or judgment.get("fullText", "")[:1000])')
    content = content.replace('format_judgment_title(ref_row["case_number"], ref_row["court"], ref_row["title"])',
                              'format_judgment_title(ref_row["case_number"], ref_row["court"], ref_row["title"], ref_row["excerpt"])')
                              
    file_path.write_text(content, encoding='utf-8')

# Same for RAG Pipeline
file_path_rag = pathlib.Path(r'D:\Lexibot-Legal-Assistant-AI-Application\server_fastapi\services\rag_pipeline.py')
if file_path_rag.exists():
    content_rag = file_path_rag.read_text(encoding='utf-8')
    
    old_func_rag = re.search(r'def format_judgment_title\(.*?return \"Untitled Judgment\"\n', content_rag, flags=re.DOTALL)
    if old_func_rag:
        content_rag = content_rag.replace(old_func_rag.group(0), formatter_code.strip() + '\n')
        
    content_rag = content_rag.replace('format_judgment_title(doc.get("case_number", ""), doc.get("court", ""), doc.get("title", ""))',
                                      'format_judgment_title(doc.get("case_number", ""), doc.get("court", ""), doc.get("title", ""), doc.get("excerpt", doc.get("content", "")))')
    file_path_rag.write_text(content_rag, encoding='utf-8')

print("Perfect Extraction Injected!")
