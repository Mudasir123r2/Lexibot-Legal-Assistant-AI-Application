import re

def clean_text(text):
    if not text: return text
    
    # Pre-clean
    text = str(text)

    # 1. Extreme Versus Anomalies
    text = re.sub(r'(?i)v\.\s*v+ersus\b', 'VERSUS', text)
    text = re.sub(r'(?i)\bv+ersus\b', 'VERSUS', text)
    text = re.sub(r'(?i)v+ersus([A-Za-z])', r'VERSUS \1', text) 
    
    # Fix VVVERSUSF -> VERSUS F
    text = re.sub(r'VV+ERSUS([A-Za-z])', r'VERSUS \1', text)
    
    # 2. Merged Roles (SHERRIFFPETITIONER -> SHERRIFF PETITIONER)
    # Match any word that ends in PETITIONER, RESPONDENT, etc.
    text = re.sub(r'(?i)([a-z])(PETITIONER|RESPONDENT|APPELLANT|DEFENDANT|PLAINTIFF)S?\b', r'\1 \2', text)
    text = re.sub(r'([A-Z])(PETITIONERS|RESPONDENTS|APPELLANTS|DEFENDANTS|PLAINTIFFS)\b', r'\1 \2', text)
    text = re.sub(r'([A-Z])(PETITIONER|RESPONDENT|APPELLANT|DEFENDANT|PLAINTIFF)\b', r'\1 \2', text)
    
    # 3. specific known OCR typos like THROUGH1 LEGD
    text = re.sub(r'(?i)\bTHROUGH1?\s*LEGD\b', 'THROUGH LEGAL', text)
    
    # 4. Cleaning up dots
    text = re.sub(r'\.\s*\.\s*\.*', ' ', text)
    
    # 5. Fix common scattered letters like F ATIMA -> FATIMA, RIT A -> RITA
    # Single letter followed by space and capitalized word (like F ATIMA)
    text = re.sub(r'\b([A-Z])\s([A-Z][a-z]+)\b', r'\1\2', text)
    text = re.sub(r'\b([A-Z]{2,})\s([A-Z])\b', r'\1\2', text) # RIT A
    
    # Double spaces collapse
    text = re.sub(r'\s{2,}', ' ', text)
    
    return text.strip()

print("ORIGINAL 1: SUBA THROUGH1 LEGD HEIRS PETITIONERS v. VVERSUS . .. . F ATIMA BIBI LEGAL HEIRS")
print("CLEANED  1: " + clean_text("SUBA THROUGH1 LEGD HEIRS PETITIONERS v. VVERSUS . .. . F ATIMA BIBI LEGAL HEIRS"))

print("ORIGINAL 2: PETITIONERSVVVERSUSF ATIMA BIBI")
print("CLEANED  2: " + clean_text("PETITIONERSVVVERSUSF ATIMA BIBI"))

print("ORIGINAL 3: SAMUEL SHERRIFFPETITIONER v. VVERSUS RIT A MOODY")
print("CLEANED  3: " + clean_text("SAMUEL SHERRIFFPETITIONER v. VVERSUS RIT A MOODY"))
