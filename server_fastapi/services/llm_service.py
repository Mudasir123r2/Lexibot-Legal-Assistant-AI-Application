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
SAFE_MAX_TOKENS = 8000

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

SYSTEM_PROMPT_CLIENT = """You are Lexibot, an elite Legal Assistant AI designed to act as a highly intelligent conversational co-counsel for lawyers, advocates, and legal researchers.

CORE CAPABILITIES & CONVERSATIONAL RULES:
- BE CONVERSATIONAL: If the user says "Hi", "Hello", or asks how you are, respond naturally, professionally, and politely. DO NOT forcibly mention the document context in your greeting.
- DIRECT INQUIRIES OR CASES: If the user pastes an entire case summary, judgment, or fact pattern WITHOUT a specific question, DO NOT just say "Hello, how can I help?". You MUST acknowledge the legal text and offer specific analytical services. Say something like: "I have received the case details regarding [Briefly name the parties or issue]. How would you like me to assist you with this? I can:
  - Summarize the core legal issues
  - Extract the key arguments and statutory grounds
  - Find relevant legal precedents to support the claims
  - Explain the complex terms in plain language"
- ANSWER LEGAL QUESTIONS: When the user asks about the case, explain it clearly, extract key points, or summarize complex legal reasoning in plain English.
- DO NOT MENTION YOUR BACKEND OR CONTEXT MECHANICS: Never say phrases like "Based on the provided context", "According to the chat history provided", "As seen in the document context", "According to my active context", or "Based on previous messages". Act like a highly capable human legal assistant. Just give the answer seamlessly and directly as if you inherently know it. Do not let the user know you are reading from a "context" block or "chat history".
- ONLY mention that information is missing if you CANNOT answer the query: "I apologize, but that information is not available in the case record."

COMMUNICATION STYLE & FORMATTING (CRITICAL):
- DO NOT USE ASTERISKS OR STARS. Never use `*` or `**` anywhere in your response for any reason (no bolding, no italics, no list items).
- Use pure plain text. If you must emphasize something, use ALL CAPS.
- USE PROPER FORMATTING: Use simple dashes (-) or real bullets (•) if necessary for unordered lists.
- USE NUMBERS: Use numbered lists (1., 2., 3.) where appropriate for sequential steps or ranked items.
- Maintain a formal, academic, and highly professional tone suited for legal professionals.
- Be direct, concise, and highly analytical.

STRICT GROUNDING RULE:
- ONLY rely on the provided legal case material IF it is actually relevant to the user's specific question.
- IF THE PROVIDED DOCUMENTS ARE ENTIRELY IRRELEVANT (e.g. they are about "Privatisation Commission" but the user is asking "Hello" or "What is divorce?" or "What is the punishment for murder?"), YOU MUST COMPLETELY IGNORE THE DOCUMENTS. Do not mention them at all.
- If a user asks a general legal question outside of any relevant case, you MUST answer it brilliantly using your elite general legal knowledge, without ever shoehorning in summaries of random provided documents.

Take pride in being a top-tier conversational legal assistant.
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
10. NO COMMENTARY: Output ONLY the corrected judgment in the strict format below. NEVER START YOUR RESPONSE WITH "Here is the validated..." OR "Here is the..." OR "Sure!" OR ANY OTHER CHAT PREAMBLE. Begin the very first character of your response with "CASE TITLE:".

CASE TITLE:
[Exact as found]

CITATION:
[Exact]

COURT:
[Exact]

DATE OF DECISION:
[Exact]

JUDGES:
[List all judges]

LAWYERS:
[List all lawyers]

STATUTES:
[List all statutes with sections]

FACTS:
[DETAILED facts — include full background, events, procedural history. Minimum 2–5 paragraphs. No summarization. The longer the better.]

ISSUES:
[List all legal issues clearly]

ARGUMENTS (MANDATORY - DO NOT SKIP):
- Applicant/Petitioner Arguments:
  [Detailed arguments must be provided. If not explicitly labeled, infer them from the court's discussion of the claims.]
- Respondent Arguments:
  [Detailed arguments must be provided. If not explicitly labeled, infer them from the court's discussion of the defense/rebuttals.]

REASONING:
[VERY DETAILED — step-by-step legal reasoning, interpretation of statutes, judicial logic, references to principles or precedents. This should be the longest section. Minimum 4-8 paragraphs.]

HOLDING / DECISION:
[Full final order with explanation]
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
        user_role: str = "client",
        tone: str = "formal",
        chat_history: List[Dict[str, Any]] = None
    ) -> str:
        chat_history_str = "None"
        if chat_history:
            lines = []
            for msg in chat_history:  # Full chat history dynamically parsed
                role = msg.get("role", "unknown").upper()
                content = msg.get("content", "")
                
                # Truncate overly massive individual historical messages to protect context limits
                if len(content) > 10000:
                    content = content[:10000] + "... [Historical Content Truncated]"
                    
                lines.append(f"{role}: {content}")
            chat_history_str = "\n".join(lines)
            
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
            
        if context_parts:
            context_text = "\n\n" + "=" * 80 + "\n\n".join(context_parts)
        else:
            context_text = "No context documents provided. Rely on general legal knowledge and assist the user."

        # Get tone from kwargs or fall back to formal
        base_system = SYSTEM_PROMPT_ADVOCATE if user_role == "advocate" else SYSTEM_PROMPT_CLIENT

        tone_instruction = ""
        if tone == "casual":
            tone_instruction = "\n\nTONE INSTRUCTION: Speak in a friendly, conversational, and casual tone. Avoid overly strict or rigid academic jargon when responding, but remain accurate."
        else:
            tone_instruction = "\n\nTONE INSTRUCTION: Maintain a highly formal, academic, and professional legal tone."
            
        system_prompt = base_system + tone_instruction
        
        prompt = f"CHAT HISTORY:\n{chat_history_str}\n\nRELEVANT DOCUMENTS:\n{context_text}\n\nUSER QUESTION: {query}\n\nCRITICAL DIRECTIVE: Answer the user's question seamlessly without telling them you are looking at 'Chat History' or 'Relevant Documents'. Do NOT use phrases like 'Based on the chat history' or 'According to the provided context'. Answer as an expert AI legal assistant possessing this information inherently."
        
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
        from utils.formatters import _auto_heal_ocr_spaces
        dirty_text = _auto_heal_ocr_spaces(dirty_text)
        
        dirty_text = re.sub(r'(?i)\bp\s*esha\s*war\b', 'Peshawar', dirty_text)
        dirty_text = re.sub(r'(?i)\bp\s*akist\s*an\b', 'Pakistan', dirty_text)
        dirty_text = re.sub(r'(?i)\bmur\s*taza\b', 'Murtaza', dirty_text)
        dirty_text = re.sub(r'(?i)\bbish\s*art\b', 'Bisharat', dirty_text)
        
        metadata = metadata or {}
        known_meta_str = "\n".join([f"{k}: {v}" for k, v in metadata.items() if v])
        
        prompt = f"KNOWN METADATA:\n{known_meta_str}\n\nRAW OCR TEXT:\n```text\n{dirty_text}\n```"
        
        response = self.generate_response(prompt, SYSTEM_PROMPT_OCR_CLEAN, max_tokens=8000, temperature=0.1)
        if response.startswith("I apologize") or response.startswith("Request timed out"):
            return dirty_text
            
        # Strip preamble from LLM Output (Delete conversational lines like "Here is the validated...")
        response = re.sub(r'(?i)(sure|here is|here are|certainly|below is)[^\n]*\n+', '', response).strip()
        
        if "CASE TITLE:" in response:
            response = "CASE TITLE:" + response.split("CASE TITLE:", 1)[1]
            
        # Post-process heuristic to catch any LLM bleed-through
        response = _auto_heal_ocr_spaces(response)
        
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
