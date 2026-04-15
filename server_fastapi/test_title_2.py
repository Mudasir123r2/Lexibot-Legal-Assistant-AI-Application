import re
from utils.formatters import format_judgment_title

text = "Journal 1984 PLD 329 Court SUPREME COUR TDate 1984-06-02 Appeal No. CONSTIUTIONAL PETITION NO. 566 OF 1984 Judge ASLAM RIAZ HUSSAIN, NASIM HASAN SHAH AND M. S. H. QURAISHI Parties ABDUL RAHIM (PETITIONER) VESUSMST SHAHIDA KHAN RESPONDENT Lawyers SHAUKAT ALI..."
original_title = "NASIM HASAN SHAH M. S. H. QURAISHI Parties ABDUL RAHIM v. ESUSMST SHAHIDA KHAN"

res = format_judgment_title(
    "CONSTITUTIONAL PETITION NO. 566 OF 1984", 
    "Lahore High Court", 
    original_title, 
    text, 
    "EasyLaw_1984_PLD_329_JDM.pdf"
)
print("FINAL TITLE RETURNS:", res)
