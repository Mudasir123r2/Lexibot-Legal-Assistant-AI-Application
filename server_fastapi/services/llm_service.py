"""
LLM Service using Cerebras API
Provides fast inference for legal question answering and text generation.
"""

import json
import logging
import re
import time
from typing import List, Dict, Optional, Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ==============================================================================
# PROMPTS & CONFIGURATION
# ==============================================================================

MAX_RETRIES = 3
RETRY_DELAY_SEC = 2
SAFE_MAX_TOKENS = 2048

SYSTEM_PROMPT_ADVOCATE = """You are a Legal Document Formatter for a RAG-based legal research system.
Your task is to standardize and clean legal judgment names and metadata strictly referencing Easy Law judgments.

--------------------------------------
🚨 STRICT RULES
--------------------------------------
1. NEVER use internal system names.
2. Judgment names MUST be constructed ONLY from: Citation / Reporter and Court Name.
3. IF CITATION/COURT IS MISSING: Extract it from the raw OCR text.
4. ONLY write "Not available in provided text" if the info is COMPLETELY MISSING.

Return ONLY the structured format:
### Case Title
### Court
### Date
### Citation / Appeal No.
### Parties
### Facts
### Issues
### Decision / Holding
### Statutes & Relevant Law
### Inconsistencies
"""

SYSTEM_PROMPT_CLIENT = """You are a highly professional, distinguished legal assistant AI designed to analyze, summarize, and answer questions about legal judgments, case law, and statutes.

Your primary role is to help users understand legal documents in a clear, structured, and highly reliable way.

CRITICAL FORMATTING RULE: 
- DO NOT use any markdown formatting, asterisks, bolding, italics, or special characters (like ** or * or #) in your response. 
- Use plain text formatting only. 
- Use standard spacing, capitalization, and simple text bullets (like a dash -) for structure.
- Maintain a formal, academic, and highly professional tone suited for lawyers and judges.

Core Capabilities:
- Summarize legal cases (Facts, Issues, Reasoning, Holding)
- Explain legal principles and doctrines
- Identify key legal issues and arguments
- Interpret statutes and case law references
- Simplify complex legal language into plain English
- Compare legal concepts when asked
- Answer questions strictly based on provided case material

Strict Grounding Rule (VERY IMPORTANT):
- You MUST only use the information provided in the input context (case text, judgment, statutes, notes).
- Ensure facts come strictly from the same chunk. Avoid mixing multiple cases into a single factual narrative.
- Summarize and present facts case-by-case (grouping findings by their specific citation match).
- Do NOT use external knowledge or assumptions.
- If information is not present in the provided context, respond with: "This information is not available in the provided case material."

Reasoning Style:
- Be structured, analytical, and professional.
- Prefer clean, plain-text spacing to separate sections (e.g., Facts:, Issue:, Reasoning:, Holding:).
- When explaining concepts, simplify without losing legal meaning.
- Define legal terms (e.g., "judgment in rem", "precedent") when needed.

Restrictions:
- Do not fabricate case laws, citations, or statutes.
- Do not answer questions outside the provided context.
- Do not give personal legal advice.
- Do not speculate beyond the document.

Output Style:
- Professional plain text
- Simple dashes for bullet points when helpful
- Concise but complete explanations
- Formal court assistant tone
"""

SYSTEM_PROMPT_SUMMARY = """You are a Legal Document Summarizer specializing in Pakistani judgments.
Process via 5 steps: Analysis, Pre-summarization, Abstractive Summarization, Plain Language Conversion, Length Control.

Target Format:
- Case Title & Citation
- Key Parties Involved
- Main Legal Issues
- Court's Decision/Ruling
- Important Legal Principles Established
- Key Precedents Cited
"""

SYSTEM_PROMPT_OCR_CLEAN = """You are a Senior Legal Data Engineer and Pakistani Law Expert.
Your task is to VALIDATE, CLEAN, and CORRECT a structured legal judgment. Ensure legal data integrity and consistency.

🚨 CRITICAL RULES (STRICT):
1. PRESERVE ORIGINAL MEANING & HEAL OCR: Fix formatting, grammar, and typos. Aggressively fix OCR artifacts where words/names are improperly spaced or capitalized (e.g., "bish art" -> "Bisharat", "A D V O C A T E" -> "Advocate", "Pesha War" -> "Peshawar", "MUR TAZA" -> "Murtaza", "P AKIST AN" -> "Pakistan", repairing ALL judge/lawyer/place names).
2. DO NOT ADD NEW LEGAL CONCEPTS: DO NOT introduce legal doctrines not present in the case (e.g., Khula in dower cases, restitution in custody cases). If a concept is NOT explicitly supported by facts/issue/reasoning -> REMOVE IT.
3. HOLDING MUST BE 100% CONSISTENT: The HOLDING must strictly match Facts, Issue, and Reasoning. Delete unrelated legal doctrines. Include clear legal doctrine labels/tags in the holding (e.g., [Khula without consent], [No restitution unless proved]).
4. REMOVE RAG CONTAMINATION & DEDUPLICATE: If multiple legal topics appear, identify the primary legal issue and remove unrelated secondary doctrines. Deduplicate all repeated information from overlapping FAISS chunks. Remove redundant "conclusion" sections if "HOLDING" is present.
5. STANDARDIZE FORMATTING:
   - Case Title: "Party A v. Party B (Appeal/Writ No. 123 of 2000)". Do NOT use square brackets.
   - Citation: Format as YYYY PLD XXX (Court).
   - Court: Must be specific (e.g., Lahore High Court). PLD/SCMR/YLR typically belong to High Courts or Supreme Court. If text says District Court but citation is PLD, correct to High Court.
   - Dates: Decision Date and Citation Reporter Year may differ. Standardize and resolve mismatches.
   - Statutes: Consolidate and formalize statutes without duplication (e.g., "West Pakistan Family Courts Act, 1964").
6. PARTY CONFUSION: If multiple unrelated cases appear merged due to OCR, clearly label consolidated proceedings or split them.
7. ISSUE & REASONING: Frame issues legally and comprehensively, avoiding over-simplification. Ensure reasoning flows structurally without repetitive circular logic.
8. STRICT HEADERS: Use exact headers in ALL CAPS. DO NOT use markdown bolding (**), asterisks (*), or hashtags. Output plain text headers only.
9. SEPARATE LINES: Put JUDGES: and LAWYERS: entirely on separate lines. They MUST NEVER be on the same line.
10. NO COMMENTARY: Output ONLY the corrected judgment in the strict format below.

CASE TITLE:
CITATION:
COURT:
DATE OF DECISION:
JUDGES:
LAWYERS:
STATUTES:

FACTS:
ISSUE:
REASONING:
HOLDING:
"""

SYSTEM_PROMPT_EXTRACTION = """You are an advanced Legal Information Extraction model.
Output pure JSON matching this exact structure:
{
  "entities": {"parties": [], "court": ""},
  "dates": {"judgment_date": "", "deadlines": []},
  "obligations": [],
  "citations": [],
  "relationships": [],
  "case_number": "",
  "case_type": "",
  "outcome": "",
  "key_issues": []
}"""


# ==============================================================================
# CORE LLM SERVICE
# ==============================================================================

class LLMService:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.CEREBRAS_API_KEY
        self.model = model or settings.LLM_MODEL
        self.base_url = getattr(settings, "CEREBRAS_BASE_URL", "https://api.cerebras.ai/v1")
        self.max_tokens = getattr(settings, "MAX_TOKENS", 1024)
        self.lc_llm = None
        
        if not self.api_key or self.api_key == "your_cerebras_api_key_here":
            logger.warning("⚠️ Cerebras API key not configured. Using fallback responses.")
        else:
            self._initialize_client()
            
    def _initialize_client(self):
        try:
            self.lc_llm = ChatOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                model=self.model,
                max_tokens=SAFE_MAX_TOKENS,
                temperature=0.3,
                max_retries=0
            )
            logger.info(f"✅ Cerebras LangChain initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize LangChain client: {str(e)}")
            self.lc_llm = None

    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.3
    ) -> str:
        if not self.lc_llm:
            return self._fallback_response(prompt)
            
        safe_tokens = min(max_tokens, SAFE_MAX_TOKENS)
        
        messages = []
        if system_prompt:
            messages.append(("system", system_prompt))
        messages.append(("user", prompt))
            
        chat_template = ChatPromptTemplate.from_messages(messages)
        formatted_messages = chat_template.format_messages()
        
        # We temporarily override params just for this request
        chain_llm = self.lc_llm.bind(max_tokens=safe_tokens, temperature=temperature)
        
        for attempt in range(MAX_RETRIES):
            try:
                response = chain_llm.invoke(formatted_messages)
                return response.content
            except Exception as e:
                error_str = str(e)
                logger.error(f"LLM API ERROR: {error_str}")
                
                is_rate_limit = any(k in error_str.lower() for k in ["429", "rate_limit", "quota"])
                if is_rate_limit and attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_DELAY_SEC * (2 ** attempt)
                    logger.warning(f"⏳ Rate limit hit, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                elif is_rate_limit:
                    return ("I apologize, but I'm currently experiencing high demand and have reached my usage limit. "
                            "Please try again in a few moments.")
                else:
                    if "timeout" in error_str.lower():
                        return "Request timed out."
                    return self._fallback_response(prompt)
                    
        return self._fallback_response(prompt)

    # ==============================================================================
    # DOMAIN SPECIFIC METHODS
    # ==============================================================================

    def generate_with_context(
        self,
        query: str,
        context_documents: List[Dict[str, Any]],
        max_tokens: int = 1024,
        temperature: float = 0.3,
        user_role: str = "client"
    ) -> str:
        context_parts = []
        for doc in context_documents[:5]:
            title = str(doc.get('title', 'Untitled'))[:200]
            citation = str(doc.get('citation', ''))[:100]
            court = str(doc.get('court', ''))[:100]
            date = str(doc.get('date', ''))[:50]
            parties = str(doc.get('parties', ''))[:200]
            
            case_name = title
            if parties and (title.isdigit() or len(title) < 10 or 'WP-No' in title):
                case_name = f"{parties} [{title}]" if title != 'Untitled' else parties
                
            header = f"[Easy Law Judgment] {case_name}"
            if citation and citation not in case_name:
                header += f" (Citation: {citation})"
            if court:
                header += f" | Court: {court}"
            if date:
                header += f" | Date: {date}"
                
            content = doc.get('content', '')
            if len(content) > 32000:
                content = content[:32000] + "... [Content truncated]"
                
            # Wrap context securely to prevent prompt injection
            context_parts.append(f"{header}\n\n```text\n{content}\n```")
            
        context_text = "\n\n" + "=" * 80 + "\n\n".join(context_parts)
        
        system_prompt = SYSTEM_PROMPT_ADVOCATE if user_role == "advocate" else SYSTEM_PROMPT_CLIENT
        prompt = f"CONTEXT DOCUMENTS:\n{context_text}\n\nUSER QUESTION: {query}"
        
        return self.generate_response(prompt, system_prompt, max_tokens, temperature)

    def summarize_judgment(self, judgment_text: str, max_tokens: int = 512) -> str:
        prompt = f"Summarize the following legal judgment:\n\n```text\n{judgment_text[:30000]}\n```"
        response = self.generate_response(prompt, SYSTEM_PROMPT_SUMMARY, max_tokens, temperature=0.2)
        if response.startswith("I apologize") or response.startswith("Request timed out"):
            return "Summary currently unavailable due to AI service disruption."
        return response

    def clean_ocr_text(self, dirty_text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        # Pre-process common OCR artifacts deterministically before LLM to save tokens / ensure accuracy
        import re
        dirty_text = re.sub(r'(?i)\bp\s*esha\s*war\b', 'Peshawar', dirty_text)
        dirty_text = re.sub(r'(?i)\bp\s*akist\s*an\b', 'Pakistan', dirty_text)
        dirty_text = re.sub(r'(?i)\bmur\s*taza\b', 'Murtaza', dirty_text)
        dirty_text = re.sub(r'(?i)\bbish\s*art\b', 'Bisharat', dirty_text)
        
        metadata = metadata or {}
        known_meta_str = "\n".join([f"{k}: {v}" for k, v in metadata.items() if v])
        
        prompt = f"KNOWN METADATA:\n{known_meta_str}\n\nRAW OCR TEXT:\n```text\n{dirty_text}\n```"
        
        response = self.generate_response(prompt, SYSTEM_PROMPT_OCR_CLEAN, max_tokens=4000, temperature=0.1)
        if response.startswith("I apologize") or response.startswith("Request timed out"):
            return dirty_text
        return response

    def extract_case_info(self, judgment_text: str) -> Dict[str, Any]:
        fallback_json = {
            "entities": {"parties": [], "court": ""},
            "dates": {"judgment_date": "", "deadlines": []},
            "obligations": [], "citations": [], "relationships": [],
            "case_number": "", "case_type": "", "outcome": "", "key_issues": []
        }
        
        prompt = f"Extract structured info from:\n\n```text\n{judgment_text[:20000]}\n```"
        response = self.generate_response(prompt, SYSTEM_PROMPT_EXTRACTION, max_tokens=1024, temperature=0.1)
        
        try:
            # Extract via regex to avoid markdown artifacts
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return json.loads(response)
        except Exception as e:
            logger.warning(f"Failed to parse JSON extraction: {e}")
            return fallback_json

    def _fallback_response(self, query: str) -> str:
        return ("I apologize, but the AI service is currently unavailable. "
                "Please verify the Cerebras API Key, check constraints, or try again later.")

# Singleton Instance
_llm_service = None

def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
