from services.llm_service import get_llm_service

def main():
    llm = get_llm_service()
    text = "Journal 1984 PLD 329 Court SUPREME COUR TDate 1984-06-02 Appeal No. CONSTIUTIONAL PETITION NO. 566 OF 1984 Judge ASLAM RIAZ HUSSAIN, NASIM HASAN SHAH AND M. S. H. QURAISHI Parties ABDUL RAHIM (PETITIONER) VESUSMST SHAHIDA KHAN RESPONDENT Lawyers SHAUKA TALI..."
    print(llm.clean_ocr_text(text, metadata={}))

if __name__ == "__main__":
    main()
