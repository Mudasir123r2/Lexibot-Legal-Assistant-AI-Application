import re

text = """Journal 2004 YLR 482 Court LAHORE HIGH COUR T Date 2003-07-09 Appeal No. CRIMINAL REVISION NO. 698-D OF 2003 Judge FARRUKH LA TIF Parties MUHAMMAD MASOOD ABBASI (APPELLANT) VVVERSUS MST MAMONA ABBASI RESPONDENT Lawyers SYED MUHAMMAD ALI GILLANI FOR APPELLANT . Statutes MUSLIM F AMIL Y LAWS ORDINANCE (VIII OF 1961) - FORM II, COLUMNS 18 AND 19 MUSLIM F AMIL Y LAWS ORDINANCE (VIII OF 1961) - S. 7 AND FORM II, COLUMN 19 ISLAMIC LA W MUSLIM F AMIL Y LAWS ORDINANCE (VIII OF 1961) - S. 7 AND FORM II,
COPYRIGHT 2021 easylaw.ai. ALL RIGHTS RESERVED. DISCLAIMER (https://www.easylaw.ai) CASE NO. 1208380DOWNLOAD CASE"""

def clean_easylaw_excerpt(text):
    if not text: return text
    
    # 1. Strip useless footers completely
    text = re.sub(r'COPYRIGHT 20\d{2}\s*easylaw.*?All Rights Reserved\.?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'DISCLAIMER\s*\(?https?://.*?easylaw\.ai.*?\)?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'CASE\s*NO\.\s*\d+[\s\n]*DOWNLOAD\s*CASE', '', text, flags=re.IGNORECASE)
    text = re.sub(r'CASE\s*NO\.\s*\d+(?:\s*|$)', '', text, flags=re.IGNORECASE) # Sometimes just Case No
    
    # 2. Fix specific capitalized spaced words
    text = text.replace('F AMIL Y', 'FAMILY')
    text = text.replace('COUR T', 'COURT')
    text = text.replace('LA W', 'LAW')
    text = text.replace('LA TIF', 'LATIF')
    text = text.replace('VVVERSUS', 'VERSUS')
    text = text.replace('VVERSUS', 'VERSUS')
    text = text.replace('v. VERSUS', 'VERSUS')
    # "VERSUSMST" to "VERSUS MST"
    text = re.sub(r'(VERSUS)([A-Z]{2,})', r'\1 \2', text)
    
    # 3. Add clean structural newlines to the merged header block
    text = re.sub(r'\b(Court|Date|Appeal No\.|Judge|Parties|Lawyers|Statutes|Judgment|Issue|Fact|Facts|Held|Decision|Arguments)\s*\b', r'\n\1: ', text)
    
    # Clean up double newlines and spaces
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

print(clean_easylaw_excerpt(text))