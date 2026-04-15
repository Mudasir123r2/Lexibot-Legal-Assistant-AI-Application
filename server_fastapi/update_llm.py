import re

def update():
    with open('server_fastapi/services/llm_service.py', 'r', encoding='utf-8') as f:
        text = f.read()

    new_func = '''    def clean_ocr_text(self, dirty_text: str, metadata: dict = None) -> str:
        """
        Produce a beautifully formatted Legal Case Brief from the RAW OCR text, deduplicating any FAISS repeating chunks.
        """
        if metadata is None:
            metadata = {}
        
        system_prompt = """You are an Expert Legal Analyst for a premium legal research system.

Your task is to take RAW OCR text of a Pakistani Legal Judgment and transform it into a beautifully structured, highly readable Case Brief.

--------------------------------------
🚨 STRICT RULES
--------------------------------------

1. DO NOT output a raw wall of text. DO NOT dump OCR garbage.
2. The raw text may contain duplicated sentences or paragraphs due to overlapping database chunks. DEDUPLICATE all repeated information!
3. Structure your response EXACTLY as follows. Use ALL CAPS for these headers so the UI formats them correctly:

CASE TITLE
[Extract from text or metadata]

COURT
[Extract from text or metadata]

DATE
[Extract from text or metadata]

FACTS
[A concise summary of the background facts]

ISSUE
[What is the main legal question?]

REASONING
[The court's logical analysis and application of law, combining fragmented paragraphs into a cohesive narrative. Remove duplicates.]

HOLDING
[The final decision and order of the court]

4. DO NOT add AI commentary (e.g. "Here is the brief"). Just output the headers and content.
5. If some information is not in the text, write "Not provided in the judgment."
"""

        known_meta_str = "\\n".join([f"{k}: {v}" for k, v in metadata.items() if v])
        prompt = f"KNOWN METADATA FOR CONTEXT:\\n{known_meta_str}\\n\\nRAW OCR TEXT TO PROCESS:\\n{dirty_text}"

        try:
            response = self.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4000,
                temperature=0.1
            )
            if response.startswith("I apologize"):
                return dirty_text
            return response
        except Exception as e:
            logger.error(f"OCR Cleaning/Briefing failed: {e}")
            return dirty_text'''

    pattern = r'    def clean_ocr_text\(self, dirty_text: str, metadata: dict = None\) -> str:.*?return dirty_text'
    text = re.sub(pattern, new_func, text, flags=re.DOTALL)
    
    with open('server_fastapi/services/llm_service.py', 'w', encoding='utf-8') as f:
        f.write(text)

if __name__ == '__main__':
    update()