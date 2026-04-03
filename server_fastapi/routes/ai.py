"""
AI Routes - RAG-Powered Legal Assistant
Handles chat, search, summarization, prediction, and guidance using RAG pipeline.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from config.database import get_db
from models.chatlog import ChatRequest, ChatResponse
from middlewares.auth import get_current_user
from models.user import TokenData
from services.rag_pipeline import get_rag_pipeline
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI"])

# Initialize RAG pipeline
rag = get_rag_pipeline()


# Request/Response Models
class JudgmentSearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10
    court: Optional[str] = None
    caseType: Optional[str] = None
    yearFrom: Optional[int] = None
    yearTo: Optional[int] = None
    searchMode: str = "hybrid"  # semantic, keyword, or hybrid
    court: Optional[str] = None
    caseType: Optional[str] = None
    yearFrom: Optional[int] = None
    yearTo: Optional[int] = None
    searchMode: str = "hybrid"  # semantic, keyword, or hybrid


class JudgmentSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int


class SummarizeRequest(BaseModel):
    judgmentId: Optional[str] = None
    judgmentText: Optional[str] = None


class SummarizeResponse(BaseModel):
    summary: str
    judgmentId: Optional[str] = None


class OutcomePredictionRequest(BaseModel):
    caseDescription: str
    caseType: Optional[str] = None
    legalContext: Optional[str] = None


class OutcomePredictionResponse(BaseModel):
    prediction: str
    confidence: float
    explanation: str
    full_analysis: Optional[str] = None
    risk_factors: List[str] = []
    recommendations: List[str] = []
    legal_basis: Optional[str] = None
    confidence_analysis: Optional[str] = None
    similarCases: List[Dict[str, Any]]


class GuidanceRequest(BaseModel):
    caseType: str
    situationDescription: str


class GuidanceResponse(BaseModel):
    guidance: str
    caseType: str
    similarCases: List[Dict[str, Any]]


# Routes
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    AI-powered chat using RAG pipeline.
    
    Features:
    - Retrieves relevant legal judgments
    - Generates contextual responses
    - Maintains conversation history per session
    """
    try:
        logger.info(f"Chat request from user {current_user.id}: {request.message[:100]}")
        
        # Generate or use existing session ID
        session_id = request.sessionId or str(uuid.uuid4())
        
        # Check if this session already exists
        existing_session = await db.chatlogs.find_one({
            "userId": current_user.id,
            "sessionId": session_id
        })
        
        # Section 3.1: Check Database of Common Queries (FAQ) BEFORE hitting AI
        faq_match = None
        faqs = await db.faq_knowledge.find({}).to_list(length=100)
        user_query_clean = request.message.lower().strip().replace("?", "")
        
        for faq in faqs:
            q_clean = faq.get("question", "").lower().strip().replace("?", "")
            if q_clean == user_query_clean or (len(q_clean) > 5 and q_clean in user_query_clean):
                faq_match = faq.get("answer")
                break
                
        if faq_match:
            response_text = faq_match
            confidence = 100.0  # Perfect confidence for pre-approved answers
            sources = [{"title": "LexiBot Verified Knowledge Base", "type": "FAQ"}]
            logger.info("Chat query intercepted by Pre-set FAQ Knowledge Base.")
        else:
            # Use RAG pipeline for response generation with user role
            rag_result = rag.query(
                question=request.message,
                top_k=5,
                include_sources=True,
                user_role=current_user.role
            )
            
            response_text = rag_result["answer"]
            confidence = rag_result.get("confidence", 0.0)
            sources = rag_result.get("sources", [])
        
        # Prepare new messages
        user_message = {
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow()
        }
        
        assistant_message = {
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.utcnow(),
            "sources": sources
        }
        
        # Prepare context
        context = {
            "queryType": "rag_chat",
            "confidence": confidence,
            "sourcesCount": len(sources),
            "relatedCaseId": request.caseId
        }
        
        if request.context is not None:
            try:
                context.update(request.context.model_dump())
            except Exception:
                pass
        
        if existing_session:
            # Append messages to existing session
            await db.chatlogs.update_one(
                {"_id": existing_session["_id"]},
                {
                    "$push": {
                        "messages": {
                            "$each": [user_message, assistant_message]
                        }
                    },
                    "$set": {
                        "updatedAt": datetime.utcnow(),
                        "context": context
                    }
                }
            )
            chat_log_id = str(existing_session["_id"])
            logger.info(f"✅ Updated existing chat session: {session_id}")
        else:
            # Create new chat session
            chat_log = {
                "userId": current_user.id,
                "caseId": request.caseId,
                "messages": [user_message, assistant_message],
                "context": context,
                "sessionId": session_id,
                "status": "active",
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            
            result = await db.chatlogs.insert_one(chat_log)
            chat_log_id = str(result.inserted_id)
            logger.info(f"✅ Created new chat session: {session_id}")
        
        logger.info(f"✅ Chat response generated with {len(sources)} sources, confidence: {confidence}")
        
        return {
            "response": response_text,
            "sessionId": session_id,
            "chatLogId": chat_log_id
        }
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}"
        )


@router.post("/search", response_model=JudgmentSearchResponse)
async def search_judgments(
    request: JudgmentSearchRequest,
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Advanced AI-powered judgment search.
    
    Features:
    - Semantic search using RAG pipeline (understands meaning)
    - Keyword-based MongoDB search (exact matching)
    - Hybrid mode (combines both for best results)
    - Advanced filters: court, case type, date range
    - Relevance scoring and ranking
    """
    try:
        logger.info(f"Search request: {request.query} (mode: {request.searchMode})")
        
        results = []
        
        # Prepare filters for semantic search
        filters = request.filters or {}
        if request.caseType:
            filters["case_type"] = request.caseType
        
        # 1. Semantic search using RAG (vector similarity)
        if request.searchMode in ["semantic", "hybrid"]:
            semantic_results = rag.search_judgments(
                query=request.query,
                top_k=request.limit * 2 if request.searchMode == "hybrid" else request.limit,
                filters=filters
            )
            
            # Apply additional filters
            for result in semantic_results:
                if request.court and request.court.lower() not in result.get("court", "").lower():
                    continue
                
                # Year filtering
                year = result.get("year")
                if not year:
                    date_str = result.get("date", "")
                    if date_str:
                        try:
                            year = int(str(date_str).split("-")[0])
                        except:
                            year = None
                
                if request.yearFrom and year and year < request.yearFrom:
                    continue
                if request.yearTo and year and year > request.yearTo:
                    continue
                
                result["search_method"] = "semantic"
                result["relevance_score"] = round(result.get("similarity", 0.5) * 100, 1)
                results.append(result)
        
        # 2. Keyword search using MongoDB (exact matching)
        if request.searchMode in ["keyword", "hybrid"]:
            mongo_filter = {}
            
            # Text search
            if request.query:
                mongo_filter["$or"] = [
                    {"title": {"$regex": request.query, "$options": "i"}},
                    {"caseNumber": {"$regex": request.query, "$options": "i"}},
                    {"keywords": {"$regex": request.query, "$options": "i"}},
                    {"parties": {"$regex": request.query, "$options": "i"}},
                    {"citation": {"$regex": request.query, "$options": "i"}}
                ]
            
            # Apply filters
            if request.caseType:
                mongo_filter["caseType"] = request.caseType
            if request.court:
                mongo_filter["court"] = {"$regex": request.court, "$options": "i"}
            
            # Year range filtering
            if request.yearFrom or request.yearTo:
                mongo_filter["year"] = {}
                if request.yearFrom:
                    mongo_filter["year"]["$gte"] = request.yearFrom
                if request.yearTo:
                    mongo_filter["year"]["$lte"] = request.yearTo
            
            # Execute MongoDB search
            keyword_cursor = db.judgments.find(
                mongo_filter,
                {"fullText": 0}
            ).sort("dateOfJudgment", -1).limit(request.limit)
            
            keyword_docs = await keyword_cursor.to_list(length=request.limit)
            
            # Format keyword results
            for doc in keyword_docs:
                formatted = {
                    "id": str(doc.get("_id")),
                    "title": doc.get("title", "Untitled"),
                    "case_type": doc.get("caseType", "Unknown"),
                    "court": doc.get("court", "Unknown"),
                    "date": str(doc.get("dateOfJudgment", "Unknown")),
                    "year": doc.get("year"),
                    "parties": doc.get("parties", ""),
                    "citation": doc.get("caseNumber", ""),
                    "excerpt": (doc.get("summary", "") or "")[:300] + "...",
                    "search_method": "keyword",
                    "relevance_score": 75.0
                }
                
                # Boost score based on match location
                query_lower = request.query.lower() if request.query else ""
                title_lower = formatted["title"].lower()
                parties_lower = formatted.get("parties", "").lower()
                
                if query_lower in title_lower:
                    formatted["relevance_score"] = 95.0
                elif query_lower in parties_lower:
                    formatted["relevance_score"] = 90.0
                elif query_lower in formatted.get("citation", "").lower():
                    formatted["relevance_score"] = 92.0
                
                results.append(formatted)
        
        # 3. Merge and deduplicate in hybrid mode
        if request.searchMode == "hybrid":
            seen_ids = {}
            merged = []
            
            for result in results:
                result_id = result.get("id") or result.get("_id")
                if result_id in seen_ids:
                    # Boost score if found by both methods
                    existing = seen_ids[result_id]
                    existing["relevance_score"] = (
                        existing["relevance_score"] + result["relevance_score"]
                    ) / 2 + 10  # Average + bonus
                    existing["search_method"] = "hybrid"
                else:
                    seen_ids[result_id] = result
                    merged.append(result)
            
            results = merged
        
        # 4. Sort by relevance
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # 5. Limit results
        results = results[:request.limit]
        
        logger.info(f"✅ Found {len(results)} judgments (mode: {request.searchMode})")
        
        return {
            "results": results,
            "total": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error in search: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_judgment(
    request: SummarizeRequest,
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Generate AI summary of a legal judgment.
    
    Features:
    - Extracts key points
    - Identifies parties and issues
    - Summarizes decision and reasoning
    """
    try:
        judgment_text = request.judgmentText
        judgment_id = request.judgmentId
        
        # If judgment ID provided, fetch from database
        if judgment_id and not judgment_text:
            from bson import ObjectId
            judgment = await db.judgments.find_one({"_id": ObjectId(judgment_id)})
            
            if not judgment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Judgment not found"
                )
            
            judgment_text = judgment.get("content") or judgment.get("summary", "")
        
        if not judgment_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No judgment text provided"
            )
        
        # Generate summary using RAG pipeline
        summary = rag.summarize_judgment(
            judgment_id=judgment_id or "unknown",
            judgment_text=judgment_text
        )
        
        logger.info(f"✅ Generated summary for judgment {judgment_id}")
        
        return {
            "summary": summary,
            "judgmentId": judgment_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error summarizing judgment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summarization failed: {str(e)}"
        )


@router.post("/predict", response_model=OutcomePredictionResponse)
async def predict_case_outcome(
    request: OutcomePredictionRequest,
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Predict case outcome based on similar cases.
    
    Features:
    - Finds similar historical cases
    - Analyzes outcomes
    - Provides confidence score and explanation
    - Saves prediction to user history
    """
    try:
        case_desc = request.caseDescription
        if request.legalContext:
            case_desc += f"\n\nLegal Context:\n{request.legalContext}"
        
        logger.info(f"Outcome prediction request for: {request.caseDescription[:100]}")
        
        prediction_result = rag.predict_outcome(
            case_description=case_desc,
            case_type=request.caseType
        )
        
        logger.info(f"✅ Prediction: {prediction_result['prediction']} (confidence: {prediction_result['confidence']}%)")
        
        # Save prediction result to user history
        try:
            prediction_record = {
                "userId": current_user.id,
                "caseType": request.caseType,
                "caseDescription": request.caseDescription[:500],  # Truncate for storage
                "prediction": prediction_result["prediction"],
                "confidence": prediction_result["confidence"],
                "similarCasesCount": len(prediction_result.get("similar_cases", [])),
                "createdAt": datetime.utcnow()
            }
            await db.prediction_history.insert_one(prediction_record)
            logger.info(f"✅ Saved prediction to history for user {current_user.id}")
        except Exception as save_err:
            logger.warning(f"Failed to save prediction history: {save_err}")
        
        return {
            "prediction": prediction_result["prediction"],
            "confidence": prediction_result["confidence"],
            "explanation": prediction_result.get("explanation", ""),
            "full_analysis": prediction_result.get("full_analysis", ""),
            "risk_factors": prediction_result.get("risk_factors", []),
            "recommendations": prediction_result.get("recommendations", []),
            "legal_basis": prediction_result.get("legal_basis", ""),
            "confidence_analysis": prediction_result.get("confidence_analysis", ""),
            "similarCases": prediction_result.get("similar_cases", [])
        }
        
    except Exception as e:
        logger.error(f"Error predicting outcome: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction unavailable"
        )


@router.post("/guidance", response_model=GuidanceResponse)
async def get_client_guidance(
    request: GuidanceRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Provide step-by-step guidance for clients.
    
    Features:
    - Document checklist
    - Process timeline
    - Next steps
    - Related cases
    """
    try:
        logger.info(f"Guidance request for {request.caseType}")
        
        guidance_result = rag.get_client_guidance(
            case_type=request.caseType,
            situation_description=request.situationDescription
        )
        
        logger.info(f"✅ Generated guidance for {request.caseType}")
        
        return {
            "guidance": guidance_result["guidance"],
            "caseType": guidance_result["case_type"],
            "similarCases": guidance_result.get("similar_cases", [])
        }
        
    except Exception as e:
        logger.error(f"Error generating guidance: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Guidance generation failed: {str(e)}"
        )


@router.get("/chat/history")
async def get_chat_history(
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db),
    limit: int = 50,
    skip: int = 0
):
    """
    Get user's chat history (all sessions).
    
    Returns list of chat sessions ordered by most recent.
    """
    try:
        # Get all chat sessions for the user
        cursor = db.chatlogs.find(
            {"userId": current_user.id}
        ).sort("updatedAt", -1).skip(skip).limit(limit)
        
        sessions = []
        async for session in cursor:
            session["_id"] = str(session["_id"])
            # Get last message preview
            if session.get("messages"):
                last_msg = session["messages"][-1]
                session["lastMessage"] = last_msg.get("content", "")[:100]
                session["messageCount"] = len(session["messages"])
            sessions.append(session)
        
        # Get total count
        total = await db.chatlogs.count_documents({"userId": current_user.id})
        
        logger.info(f"✅ Retrieved {len(sessions)} chat sessions for user {current_user.id}")
        
        return {
            "sessions": sessions,
            "total": total,
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat history: {str(e)}"
        )


@router.get("/chat/session/{session_id}")
async def get_chat_session(
    session_id: str,
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get a specific chat session by session ID.
    
    Returns complete conversation history for the session.
    """
    try:
        session = await db.chatlogs.find_one({
            "userId": current_user.id,
            "sessionId": session_id
        })
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        session["_id"] = str(session["_id"])
        
        logger.info(f"✅ Retrieved chat session {session_id} for user {current_user.id}")
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat session: {str(e)}"
        )


@router.delete("/chat/session/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Delete a specific chat session.
    """
    try:
        result = await db.chatlogs.delete_one({
            "userId": current_user.id,
            "sessionId": session_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        logger.info(f"✅ Deleted chat session {session_id} for user {current_user.id}")
        
        return {"message": "Chat session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chat session: {str(e)}"
        )


@router.delete("/chat/history")
async def clear_chat_history(
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Clear all chat history for the current user.
    """
    try:
        result = await db.chatlogs.delete_many({
            "userId": current_user.id
        })
        
        logger.info(f"✅ Cleared {result.deleted_count} chat sessions for user {current_user.id}")
        
        return {
            "message": "Chat history cleared successfully",
            "deletedCount": result.deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear chat history: {str(e)}"
        )


@router.get("/stats")
async def get_rag_stats(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get RAG pipeline statistics.
    
    Returns:
    - Number of indexed documents
    - Embedding dimension
    - LLM model info
    """
    try:
        stats = rag.get_stats()
        
        return {
            "status": "operational",
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stats: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Check if AI services are operational."""
    try:
        stats = rag.get_stats()
        
        return {
            "status": "healthy",
            "services": {
                "vector_store": {
                    "status": "operational",
                    "documents": stats["vector_store"]["total_documents"]
                },
                "embedding_service": {
                    "status": "operational",
                    "dimension": stats["embedding_dimension"]
                },
                "llm_service": {
                    "status": "operational",
                    "model": stats["llm_model"]
                }
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return {
            "status": "degraded",
            "error": str(e)
        }

