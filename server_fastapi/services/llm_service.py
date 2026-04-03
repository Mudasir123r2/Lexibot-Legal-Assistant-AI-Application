"""
LLM Service using Cerebras API
Provides fast inference for legal question answering and text generation.
"""

from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import List, Dict, Optional
import logging
import time
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMService:
    """
    Service for LLM-powered text generation using Cerebras API.
    
    Cerebras provides extremely fast inference for Llama models:
    - Llama 3.1 8B - Excellent for rapid generation
    
    Benefits of Cerebras:
    - Fast inference on specialized hardware
    - Large context window capabilities
    - Great for legal/technical text understanding
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize LLM service.
        
        Args:
            api_key: Cerebras API key (from env if not provided)
            model: Model name to use
        """
        self.api_key = api_key or settings.CEREBRAS_API_KEY
        self.model = model or settings.LLM_MODEL
        self.base_url = settings.CEREBRAS_BASE_URL
        self.max_tokens = settings.MAX_TOKENS
        self.client = None
        
        if not self.api_key or self.api_key == "your_cerebras_api_key_here":
            logger.warning("⚠️  Cerebras API key not configured. LLM features will use fallback responses.")
        else:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Cerebras client using LangChain API."""
        try:
            # Initialize minimal LangChain ChatOpenAI object just to test config
            self.lc_llm = ChatOpenAI(
                openai_api_key=self.api_key,
                openai_api_base=self.base_url,
                model_name=self.model,
                max_tokens=2048
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
        """
        Generate a response from the LLM.
        
        Args:
            prompt: User prompt/question
            system_prompt: System instructions for the model
            max_tokens: Maximum tokens in response (max: 65536)
            temperature: Sampling temperature (0-1, lower = more focused)
            
        Returns:
            Generated text response
        """
        if not hasattr(self, 'lc_llm') or not self.lc_llm:
            return self._fallback_response(prompt)
        
        try:
            # Ensure max_tokens doesn't exceed context window
            safe_max_tokens = min(max_tokens, 2048)
            
            # Orchestrate Generation via LangChain PromptTemplates
            if system_prompt:
                chat_template = ChatPromptTemplate.from_messages([
                    ("system", "{system_prompt}"),
                    ("user", "{user_prompt}")
                ])
                messages = chat_template.format_messages(
                    system_prompt=system_prompt,
                    user_prompt=prompt
                )
            else:
                chat_template = ChatPromptTemplate.from_messages([
                    ("user", "{user_prompt}")
                ])
                messages = chat_template.format_messages(
                    user_prompt=prompt
                )
                
            # Create a dynamic sequence chain for this targeted run
            chain_llm = ChatOpenAI(
                openai_api_key=self.api_key,
                openai_api_base=self.base_url,
                model_name=self.model,
                max_tokens=safe_max_tokens,
                temperature=temperature,
                max_retries=0 # We will handle retries via the application logger
            )
            
            max_retries = 3
            retry_delay = 2  # seconds
            
            for attempt in range(max_retries):
                try:
                    # Execute LangChain Runnable Sequence
                    response = chain_llm.invoke(messages)
                    return response.content
                    
                except Exception as api_error:
                    error_str = str(api_error)
                    
                    # Check for rate limit errors
                    if "429" in error_str or "rate_limit" in error_str.lower() or "quota" in error_str.lower():
                        if attempt < max_retries - 1:
                            wait_time = retry_delay * (2 ** attempt)  # exponential backoff
                            logger.warning(f"⏳ Rate limit hit, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                            time.sleep(wait_time)
                            continue
                        else:
                            logger.error(f"❌ Rate limit exceeded after {max_retries} retries")
                            return "I apologize, but I'm currently experiencing high demand and have reached my usage limit. Please try again in a few moments. If this persists, the system administrator may need to upgrade the API quota."
                    else:
                        # Other errors, raise immediately
                        raise api_error
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            
            # Provide user-friendly error messages
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                return "I apologize, but I've reached my token usage limit for now. Please wait a few moments and try again. Consider asking shorter questions or the administrator may need to upgrade the API quota."
            elif "timeout" in error_str.lower():
                return "Request timed out."
            else:
                return self._fallback_response(prompt)
    
    def generate_with_context(
        self,
        query: str,
        context_documents: List[Dict],
        max_tokens: int = 1024,
        temperature: float = 0.3,
        user_role: str = "client"
    ) -> str:
        """
        Generate response using retrieved context documents (RAG).
        
        Args:
            query: User question
            context_documents: List of retrieved documents with 'content' field
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            user_role: User's role (client/advocate/admin) for tailored responses
            
        Returns:
            Generated answer based on context
        """
        # Build context from retrieved documents with proper titles and citations
        context_parts = []
        for i, doc in enumerate(context_documents[:5]):
            category = str(doc.get('category', 'judgment'))[:50]
            title = str(doc.get('title', 'Untitled'))[:200]
            citation = str(doc.get('citation', ''))[:100]
            court = str(doc.get('court', ''))[:100]
            date = str(doc.get('date', ''))[:50]
            parties = str(doc.get('parties', ''))[:200]
            
            # Determine document type
            is_law = category.lower() in ['laws', 'legal provisions', 'statute', 'legislation']
            doc_type = "Legal Provision" if is_law else "Case Judgment"
            
            # Build a more descriptive case name
            # If title is just a number or case number, and we have parties, use parties
            case_name = title
            if parties and (title.isdigit() or len(title) < 10 or 'WP-No' in title or 'W.P.No' in title):
                case_name = f"{parties} [{title}]" if title != 'Untitled' else parties
            
            # Build header with actual case name/title
            header = f"[{doc_type}] {case_name}"
            if citation and citation not in case_name:
                header += f" (Citation: {citation})"
            if court:
                header += f" | Court: {court}"
            if date:
                header += f" | Date: {date}"
            
            content = doc.get('content', '')
            if len(content) > 1500:
                content = content[:1500] + "... [Content truncated for length]"
                
            context_parts.append(f"{header}\n\nContent:\n{content}")
        
        separator = "\n\n" + "=" * 80 + "\n\n"
        context_text = separator.join(context_parts)
        
        # Role-specific system prompts
        if user_role == "advocate":
            system_prompt = """You are LexiBot, an AI legal assistant specializing in Pakistani law for legal professionals.

Your role for ADVOCATES:
- Provide detailed legal analysis with technical precision
- Cite cases by their actual names/titles, NOT as "Case Judgment 1" or "Legal Provision 1"
- Include specific citations, court names, and dates when available
- Reference both statutory law and case law comprehensively
- Use formal legal terminology appropriately
- Highlight procedural requirements and legal strategies
- Provide comparative analysis of similar cases

Citation Format:
- Good: "In Mst. Ayesha v. Muhammad Ali (2020, Lahore High Court)..."
- Bad: "According to Case Judgment 1..."

Response Style:
- Write in a professional, conversational tone
- Use clear paragraphs, not bullet points unless listing items
- Integrate citations naturally into your analysis
- Provide context before citing cases
- End with a "Sources:" section listing actual case identifiers (never use "Case Judgment 1", etc.)

Example Sources Format:
Sources:
- Mst. Ayesha v. Muhammad Rashid [WP-No.123-2020], Lahore High Court
- 2023 PLD 456, Supreme Court of Pakistan

Important:
- Only answer based on the provided context
- Clearly distinguish between case law (judgments) and statutory law (legal provisions)
- Never fabricate case references or legal provisions
- If context is insufficient, say so clearly"""
        else:  # client or default
            system_prompt = """You are LexiBot, an AI legal assistant specializing in Pakistani law for clients.

Your role for CLIENTS:
- Explain legal concepts in simple, clear language
- Cite cases by their actual names, NOT as "Case Judgment 1" or "Legal Provision 1"
- Avoid excessive legal jargon; explain technical terms when used
- Focus on practical implications and actionable steps
- Provide context about rights and obligations
- Use examples to clarify complex concepts

Citation Format:
- Good: "In a similar case, Mst. Ayesha v. Muhammad Ali (2020), the Lahore High Court ruled that..."
- Bad: "According to Case Judgment 1..."

Response Style:
- Write in a friendly, conversational tone
- Use clear paragraphs to explain concepts
- Integrate case examples naturally into your explanation
- Avoid repetitive phrasing
- End with a "Sources:" section listing actual case identifiers (never use "Case Judgment 1", etc.)

Example Sources Format:
Sources:
- Mst. Ayesha v. Muhammad Rashid [WP-No.123-2020], Lahore High Court
- 2023 PLD 456, Supreme Court of Pakistan

Important:
- Only answer based on the provided context
- Make it clear when you're citing a court decision vs. a law/regulation
- Never make up case references or legal requirements
- Recommend consulting a lawyer for specific legal advice"""

        prompt = f"""Context from Legal Database:
{context_text}

User Question: {query}

Critical Instructions:
1. FOCUS ON LEGAL QUESTIONS: Answer the user's question based ONLY on the context provided above. If the context doesn't contain sufficient information, say so clearly. Do not hallucinate or make up legal facts.

2. AVOID GENERIC CITATIONS: Never use generic references like "Case Judgment 1" or "Legal Provision 1".

3. CITATION FORMAT: ALWAYS cite by the actual case name/identifier from the headers above (e.g., "In WP-No.282-B-2012...", "The case of 2023 PLD 456...").

4. STYLE: Write naturally and concisely. Integrate case references seamlessly into your sentences. Do not introduce yourself in every message.

5. SOURCES SECTION: In your Sources section at the end, list ONLY the actual case names/numbers with courts."""

        return self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
    
    def summarize_judgment(
        self,
        judgment_text: str,
        max_tokens: int = 512
    ) -> str:
        """
        Generate a summary of a legal judgment.
        
        Args:
            judgment_text: Full text of the judgment
            max_tokens: Maximum tokens in summary
            
        Returns:
            Concise summary
        """
        system_prompt = """You are a highly advanced Legal Document Summarizer. 
You MUST process the judgment through the following 5-step pipeline internally before generating your final output:
1. Document Analysis: Identify the structural components and key headers.
2. Extractive Pre-summarization: Extract the most critical sentences defining the core facts.
3. Abstractive Summarization: Transform these extractions into a coherent, high-level narrative.
4. Plain Language Conversion: Convert all complex technical legalese into easily comprehensible language.
5. Length Control: Ensure the final output is bounded, concise, and structured.

Final Output Format Required:
- Case Title & Citation
- Key Parties Involved
- Main Legal Issues
- Court's Decision/Ruling
- Important Legal Principles Established
- Key Precedents Cited

Generate only the final plain-language summary."""

        prompt = f"""Summarize the following legal judgment:

{judgment_text[:5000]}  

Provide a concise, plain-language, and comprehensive summary conforming strictly to the structured pipeline."""

        return self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=0.2
        )
    
    def extract_case_info(self, judgment_text: str) -> Dict[str, str]:
        """
        Extract structured information from a judgment.
        
        Args:
            judgment_text: Full judgment text
            
        Returns:
            Dict with extracted fields
        """
        system_prompt = """You are an advanced Legal Information Extraction model. 
You must analyze the text and strictly extract structured data following this 5-stage taxonomy:
1. Entity Recognition: Names of all individuals, companies, and courts.
2. Date Extraction: Key dates, deadlines, hearing schedules, and judgments.
3. Obligation Extraction: Legal duties, penalties, directions, or mandates ordered by the court.
4. Citation Extraction: Identifiers for past case precedents or statutory laws invoked.
5. Relationship Extraction: The structural relationship between entities (e.g., Appellant vs Respondent).

Output pure JSON matching the exact keys below:
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

        prompt = f"""Extract structured information and metadata from this judgment:

{judgment_text[:4000]}

Respond ONLY with a valid JSON object following the required taxonomy scheme."""

        try:
            response = self.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=512,
                temperature=0.1
            )
            
            # Try to parse JSON from response
            import json
            # Extract JSON from potential markdown code blocks
            response_clean = response.strip()
            if response_clean.startswith("```"):
                response_clean = response_clean.split("```")[1]
                if response_clean.startswith("json"):
                    response_clean = response_clean[4:]
            
            return json.loads(response_clean.strip())
        except:
            return {"error": "Could not extract information"}
    
    def _fallback_response(self, query: str) -> str:
        """
        Provide fallback response when LLM is unavailable.
        
        Args:
            query: User query
            
        Returns:
            Fallback message
        """
        return """I apologize, but the AI service is currently unavailable. 

This could be because:
- The Cerebras API key is not configured
- There's a temporary connection issue
- Rate limits have been reached

Please:
1. Check if CEREBRAS_API_KEY is set in your .env file
2. Verify your API key at the Cerebras dashboard
3. Try again in a moment

In the meantime, you can browse judgments using the search feature."""


# Singleton instance
_llm_service = None

def get_llm_service() -> LLMService:
    """
    Get or create singleton LLM service instance.
    
    Returns:
        LLMService instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
