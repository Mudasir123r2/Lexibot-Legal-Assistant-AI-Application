"""
RAG (Retrieval-Augmented Generation) Pipeline
Orchestrates the complete flow: Query → Embedding → Vector Search → LLM Generation
"""

from typing import List, Dict, Any, Optional
import logging
from .embeddings import get_embedding_service
from .vector_store import get_vector_store
from .llm_service import get_llm_service

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Complete RAG pipeline for legal question answering.
    
    Flow:
    1. User asks a question
    2. Convert question to embedding
    3. Search FAISS for similar legal documents
    4. Retrieve top-k most relevant documents
    5. Send documents + question to LLM
    6. LLM generates grounded answer
    
    Benefits:
    - Answers are based on actual legal judgments (not hallucinated)
    - Can cite specific cases
    - More accurate than pure LLM generation
    """
    
    def __init__(self):
        """Initialize RAG pipeline with all services."""
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store()
        self.llm_service = get_llm_service()
        logger.info("✅ RAG Pipeline initialized")
    
    def query(
        self,
        question: str,
        top_k: int = 5,
        include_sources: bool = True,
        user_role: str = "client"
    ) -> Dict[str, Any]:
        """
        Main RAG query method.
        
        Args:
            question: User's legal question
            top_k: Number of documents to retrieve
            include_sources: Whether to include source documents in response
            user_role: User's role (client/advocate/admin) for tailored responses
            
        Returns:
            Dict containing:
                - answer: Generated answer
                - sources: Retrieved source documents (if include_sources=True)
                - confidence: Confidence score
        """
        try:
            logger.info(f"Processing RAG query for {user_role}: {question[:100]}...")
            
            # Step 1: Embed the query
            query_embedding = self.embedding_service.embed_query(question)
            
            # Step 2: Search vector store
            retrieved_docs = self.vector_store.search(query_embedding, k=top_k)
            
            if not retrieved_docs:
                return {
                    "answer": "I couldn't find any relevant legal judgments in my database for your question. Please try rephrasing or asking about a different topic.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Step 3: Generate answer using LLM with retrieved context and user role
            answer = self.llm_service.generate_with_context(
                query=question,
                context_documents=retrieved_docs,
                user_role=user_role
            )
            
            # Calculate average confidence from retrieval scores
            avg_similarity = sum(doc.get('similarity', 0) for doc in retrieved_docs) / len(retrieved_docs)
            
            result = {
                "answer": answer,
                "confidence": round(avg_similarity, 3)
            }
            
            if include_sources:
                result["sources"] = self._format_sources(retrieved_docs)
            
            logger.info(f"✅ RAG query completed. Retrieved {len(retrieved_docs)} docs, confidence: {result['confidence']}")
            return result
            
        except Exception as e:
            logger.error(f"Error in RAG query: {str(e)}")
            return {
                "answer": f"An error occurred while processing your question: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }
    
    def search_judgments(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant judgments without LLM generation.
        
        Args:
            query: Search query
            top_k: Number of results
            filters: Optional filters (case_type, court, etc.)
            
        Returns:
            List of matching judgments with metadata
        """
        try:
            # Embed query
            query_embedding = self.embedding_service.embed_query(query)
            
            # Search vector store
            results = self.vector_store.search(query_embedding, k=top_k * 2)  # Get extra for filtering
            
            # Apply filters if provided
            if filters:
                results = self._apply_filters(results, filters)
            
            # Limit to top_k after filtering
            results = results[:top_k]
            
            return self._format_sources(results)
            
        except Exception as e:
            logger.error(f"Error in judgment search: {str(e)}")
            return []
    
    def summarize_judgment(self, judgment_id: str, judgment_text: str) -> str:
        """
        Generate summary of a specific judgment.
        
        Args:
            judgment_id: ID of the judgment
            judgment_text: Full text of judgment
            
        Returns:
            Summary text
        """
        try:
            summary = self.llm_service.summarize_judgment(judgment_text)
            return summary
        except Exception as e:
            logger.error(f"Error summarizing judgment {judgment_id}: {str(e)}")
            return "Could not generate summary at this time."
    
    def predict_outcome(
        self,
        case_description: str,
        case_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Predict case outcome based on similar cases.
        
        Args:
            case_description: Description of the case
            case_type: Type of case (Civil, Criminal, etc.)
            
        Returns:
            Dict with prediction and similar cases
        """
        try:
            # Search for similar cases
            filters = {"case_type": case_type} if case_type else None
            similar_cases = self.search_judgments(case_description, top_k=10, filters=filters)
            
            if not similar_cases:
                return {
                    "prediction": "Insufficient data for prediction",
                    "confidence": 0.0,
                    "similar_cases": []
                }
            
            # Analyze outcomes of similar cases
            outcomes = {}
            for case in similar_cases:
                outcome = case.get('outcome', 'Unknown')
                outcomes[outcome] = outcomes.get(outcome, 0) + 1
            
            # Most common outcome
            predicted_outcome = max(outcomes, key=outcomes.get) if outcomes else "Unknown"
            confidence = (outcomes[predicted_outcome] / len(similar_cases)) * 100 if outcomes else 0
            
            # Build rich context for LLM
            context_parts = []
            for i, case in enumerate(similar_cases[:8], 1):
                case_info = f"""Case {i}: {case.get('title', 'N/A')}
- Court: {case.get('court', 'N/A')}
- Date: {case.get('date', 'N/A')}
- Outcome: {case.get('outcome', 'N/A')}
- Summary: {case.get('excerpt', 'N/A')[:200]}
- Similarity: {case.get('similarity', 0) * 100:.1f}%"""
                context_parts.append(case_info)
            
            context_text = "\n\n".join(context_parts)
            
            # Generate comprehensive analysis using LLM
            prompt = f"""You are an expert legal analyst specializing in case outcome prediction.

Based on these similar historical cases from Pakistani courts:

{context_text}

---

Current Case Description:
{case_description}

Case Type: {case_type or 'General'}

Task: Provide a comprehensive outcome prediction analysis in the following format:

1. PREDICTED OUTCOME: [State the most likely outcome based on precedents]

2. DETAILED REASONING: [Explain why this outcome is predicted, referencing specific similar cases and patterns]

3. RISK FACTORS: [List 3-5 key risks or weaknesses in the case]
- Risk 1
- Risk 2
- etc.

4. RECOMMENDATIONS: [Provide 3-5 actionable recommendations]
- Recommendation 1
- Recommendation 2
- etc.

5. LEGAL BASIS: [Cite relevant legal principles, precedents, or patterns from the similar cases]

6. CONFIDENCE ANALYSIS: [Explain the confidence level and any uncertainties]

Be specific, objective, and reference the similar cases by their case numbers where applicable."""

            full_analysis = self.llm_service.generate_response(
                prompt=prompt,
                system_prompt="You are an expert Pakistani legal analyst. Provide detailed, objective predictions based on case precedents. Be thorough but clear.",
                max_tokens=1500,
                temperature=0.2  # Lower for more consistent predictions
            )
            
            # Parse the LLM response to extract structured data
            import re
            
            # Extract sections
            reasoning_match = re.search(r'2\. DETAILED REASONING:(.+?)(?=3\. RISK FACTORS:|$)', full_analysis, re.DOTALL)
            reasoning = reasoning_match.group(1).strip() if reasoning_match else full_analysis[:500]
            
            risk_match = re.search(r'3\. RISK FACTORS:(.+?)(?=4\. RECOMMENDATIONS:|$)', full_analysis, re.DOTALL)
            risk_text = risk_match.group(1).strip() if risk_match else ""
            risk_factors = [r.strip('- ').strip() for r in risk_text.split('\n') if r.strip().startswith('-')]
            
            rec_match = re.search(r'4\. RECOMMENDATIONS:(.+?)(?=5\. LEGAL BASIS:|$)', full_analysis, re.DOTALL)
            rec_text = rec_match.group(1).strip() if rec_match else ""
            recommendations = [r.strip('- ').strip() for r in rec_text.split('\n') if r.strip().startswith('-')]
            
            legal_match = re.search(r'5\. LEGAL BASIS:(.+?)(?=6\. CONFIDENCE ANALYSIS:|$)', full_analysis, re.DOTALL)
            legal_basis = legal_match.group(1).strip() if legal_match else ""
            
            confidence_match = re.search(r'6\. CONFIDENCE ANALYSIS:(.+?)$', full_analysis, re.DOTALL)
            confidence_analysis = confidence_match.group(1).strip() if confidence_match else ""
            
            return {
                "prediction": predicted_outcome,
                "confidence": round(confidence, 1),
                "explanation": reasoning,
                "full_analysis": full_analysis,
                "risk_factors": risk_factors[:5] if risk_factors else [],
                "recommendations": recommendations[:5] if recommendations else [],
                "legal_basis": legal_basis,
                "confidence_analysis": confidence_analysis,
                "similar_cases": similar_cases[:5]
            }
            
        except Exception as e:
            logger.error(f"Error predicting outcome: {str(e)}")
            return {
                "prediction": "Error",
                "confidence": 0.0,
                "similar_cases": []
            }
    
    def get_client_guidance(
        self,
        case_type: str,
        situation_description: str
    ) -> Dict[str, Any]:
        """
        Provide step-by-step guidance for clients.
        
        Args:
            case_type: Type of legal case
            situation_description: Client's situation
            
        Returns:
            Dict with guidance, checklist, and next steps
        """
        try:
            # Search for relevant cases
            similar_cases = self.search_judgments(
                f"{case_type} {situation_description}",
                top_k=5,
                filters={"case_type": case_type}
            )
            
            prompt = f"""You are advising a client about a {case_type} case.

Situation: {situation_description}

Provide:
1. Overview of what to expect
2. Document checklist (list of required documents)
3. Step-by-step process
4. Timeline estimates
5. Important considerations

Keep language simple and clear for non-lawyers."""

            guidance = self.llm_service.generate_response(
                prompt=prompt,
                system_prompt="You are a helpful legal assistant providing client guidance. Be clear, empathetic, and practical.",
                max_tokens=1024
            )
            
            return {
                "guidance": guidance,
                "case_type": case_type,
                "similar_cases": similar_cases[:3]
            }
            
        except Exception as e:
            logger.error(f"Error generating client guidance: {str(e)}")
            return {
                "guidance": "Could not generate guidance at this time.",
                "case_type": case_type,
                "similar_cases": []
            }
    
    def _format_sources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format retrieved documents for response.
        
        Args:
            documents: Raw documents from vector store
            
        Returns:
            Formatted source documents
        """
        formatted = []
        for doc in documents:
            formatted_doc = {
                "id": doc.get("_id") or doc.get("id"),
                "title": doc.get("title", "Untitled"),
                "case_type": doc.get("case_type", "Unknown"),
                "court": doc.get("court", "Unknown"),
                "date": doc.get("date", "Unknown"),
                "similarity": doc.get("similarity", 0.0),
                "excerpt": doc.get("content", "")[:300] + "..."  # First 300 chars
            }
            formatted.append(formatted_doc)
        return formatted
    
    def _apply_filters(
        self,
        documents: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply filters to search results.
        
        Args:
            documents: List of documents
            filters: Filter criteria
            
        Returns:
            Filtered documents
        """
        filtered = []
        for doc in documents:
            match = True
            for key, value in filters.items():
                if key in doc and doc[key] != value:
                    match = False
                    break
            if match:
                filtered.append(doc)
        return filtered
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            "vector_store": self.vector_store.get_stats(),
            "embedding_dimension": self.embedding_service.get_dimension(),
            "llm_model": self.llm_service.model
        }


# Singleton instance
_rag_pipeline = None

def get_rag_pipeline() -> RAGPipeline:
    """
    Get or create singleton RAG pipeline instance.
    
    Returns:
        RAGPipeline instance
    """
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
