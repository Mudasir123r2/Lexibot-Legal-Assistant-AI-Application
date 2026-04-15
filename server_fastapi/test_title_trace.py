import re

def format_judgment_title_debug(citation, court, original_title, excerpt, source_file):
    # Same logic as formatters.py, just simplified to trace
    best_reporter = "1984 PLD 329"
    best_court = court
    parties_str = ""
    case_type_str = ""

    # priority 4 reproduction
    excerpt_head = excerpt[:600]
    for pat in [
        r'([A-Za-z][\w\s\.\(\)&]{2,60}?)(?:\s+|\s*\()(?:Appellant|Petitioner|Plaintiff|Respondent|Defendant)(?:\s*\(s\)|s)?\)?\s*(?:Versus|VERSUS|Vs?\.?|v\.?)\s*([A-Za-z][\w\s\.\(\)&]{2,60}?)(?:\s+|\s*\()(?:Appellant|Petitioner|Plaintiff|Respondent|Defendant)(?:\s*\(s\)|s)?\)?',
    ]:
        m = re.search(pat, excerpt_head, re.IGNORECASE)
        print("Priority 4 matched?:", bool(m))

    print("best_reporter:", best_reporter)
    print("best_court:", best_court)
    print("parties_str:", parties_str)
    
    if best_reporter or best_court:
        citation_str = f"{best_reporter} — {best_court}" if (best_reporter and best_court) else (best_reporter or best_court)
        if parties_str and case_type_str:
            return f"{parties_str} [{case_type_str}] — {citation_str}"
        elif parties_str:
            return f"{parties_str} — {citation_str}"
        else:
            return citation_str
            
    is_placeholder = False
    if not is_placeholder:
        return original_title
    return "Fallback"

text = "Journal 1984 PLD 329 Court SUPREME COUR TDate 1984-06-02 Appeal No. CONSTIUTIONAL PETITION NO. 566 OF 1984 Judge ASLAM RIAZ HUSSAIN, NASIM HASAN SHAH AND M. S. H. QURAISHI Parties ABDUL RAHIM (PETITIONER) VESUSMST SHAHIDA KHAN RESPONDENT Lawyers SHAUKAT ALI..."

raw_original = "NASIM HASAN SHAH M. S. H. QURAISHI Parties ABDUL RAHIM v. ESUSMST SHAHIDA KHAN"

res = format_judgment_title_debug(
    "CONSTITUTIONAL PETITION NO. 566 OF 1984", 
    "Lahore High Court", 
    raw_original, 
    text, 
    "EasyLaw_1984_PLD_329_JDM.pdf"
)
print("FINAL RETURN:", res)
