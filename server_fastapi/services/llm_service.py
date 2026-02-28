"""
LLM Service using Cerebras API
Provides fast inference for legal question answering and text generation.
"""

from openai import OpenAI
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
    - Llama 3.3 70B - Excellent for legal reasoning
    - Max tokens: 65,536 (very large context)
    
    Benefits of Cerebras:
    - Fast inference on specialized hardware
    - Large context window (65k tokens)
    - Great for legal/technical text understanding
    - Rate limits: 30/min, 900/hour, 14,400/day
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize LLM service.
        
        Args:
            api_key: Cerebras API key (from env if not provided)
            model: Model name to use (default: llama-3.3-70b)
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
        """Initialize Cerebras client using OpenAI-compatible API."""
        try:
            # Initialize with minimal parameters for compatibility
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                max_retries=2,
                timeout=30.0
            )
            logger.info(f"✅ Cerebras LLM initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize Cerebras client: {str(e)}")
            self.client = None
    
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
        if not self.client:
            return self._fallback_response(prompt)
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Ensure max_tokens doesn't exceed Cerebras limit
            max_tokens = min(max_tokens, self.max_tokens)
            
            # Retry logic with exponential backoff for rate limits
            max_retries = 3
            retry_delay = 2  # seconds
            
            for attempt in range(max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    
                    return response.choices[0].message.content
                    
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
                return "The request timed out. Please try asking a shorter or simpler question."
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
            category = doc.get('category', 'judgment')
            title = doc.get('title', 'Untitled')
            citation = doc.get('citation', '')
            court = doc.get('court', '')
            date = doc.get('date', '')
            parties = doc.get('parties', '')
            
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
            
            context_parts.append(f"{header}\n\nContent:\n{doc.get('content', '')}")
        
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
1. Answer based ONLY on the context provided above

2. NEVER use generic references like:
   ❌ "Case Judgment 1", "Case Judgment 2", "[Case Judgment] 14"
   ❌ "Legal Provision 1", "Legal Provision 2"
   
3. ALWAYS cite by the actual case name/identifier from the headers above:
   ✅ "In WP-No.282-B-2012 (High Court)..."
   ✅ "According to W.P.No.3153_of_2022_638011056757659398 (High Court of Sindh)..."
   ✅ "The case of 2023 PLD 456 demonstrates..."

4. Write naturally - integrate case references into sentences:
   - Example: "In a divorce case decided by the Lahore High Court (WP-No.282-B-2012), the court ruled that..."
   - Avoid: "According to Case Judgment 1..."

5. In your Sources section at the end, list ONLY the actual case names/numbers with courts:
   - Format: "Case Number/Name, Court Name"
   - Example: "WP-No.282-B-2012, High Court"
   - NEVER write: "[Case Judgment] 14, Peshawar High Court"

6. If the context doesn't contain sufficient information, say so clearly

Write in a clear, conversational tone and explain how different cases relate to each other."""

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
        system_prompt = """You are a legal document summarizer. Create clear, structured summaries of legal judgments.

Include:
- Case title and citation
- Key parties involved
- Main legal issues
- Court's decision/ruling
- Important legal principles established
- Key precedents cited"""

        prompt = f"""Summarize the following legal judgment:

{judgment_text[:4000]}  

Provide a concise but comprehensive summary."""

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
        system_prompt = """Extract key information from legal judgments in JSON format.

Extract:
- parties: Names of parties involved
- court: Name of the court
- date: Date of judgment
- case_number: Case/citation number
- case_type: Type of case (Civil, Criminal, etc.)
- outcome: Final decision
- key_issues: Main legal issues"""

        prompt = f"""Extract structured information from this judgment:

{judgment_text[:3000]}

Respond with a JSON object containing the extracted information."""

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
2. Verify your API key at Cerebras dashboard
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
