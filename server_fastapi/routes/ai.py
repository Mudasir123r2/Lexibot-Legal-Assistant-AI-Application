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
    searchMode: str = "hybrid"  # semantic only
    court: Optional[str] = None
    caseType: Optional[str] = None
    yearFrom: Optional[int] = None
    yearTo: Optional[int] = None
    searchMode: str = "hybrid"  # semantic only


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
            sources = []  # Keep FAQ origin invisible per user request
            logger.info("Chat query intercepted by Pre-set FAQ Knowledge Base.")
        else:
            explicit_text = None
            if request.context:
                try:
                    ctx_dict = request.context.model_dump() if hasattr(request.context, 'model_dump') else request.context
                    explicit_text = ctx_dict.get("explicitTextContext")
                except Exception:
                    pass

            query_type = "rag_chat"
            if request.context:
                try:
                    ctx_dict = request.context.model_dump() if hasattr(request.context, 'model_dump') else request.context
                    query_type = ctx_dict.get("queryType", "rag_chat")
                except Exception:
                    pass

            # Ensure we pull the user's preferred tone from DB settings
            user_doc = await db.users.find_one({"_id": current_user.id})
            tone_pref = user_doc.get("preferences", {}).get("tone", "formal") if user_doc else "formal"

            # Use RAG pipeline for response generation with user role
            rag_result = rag.query(
                question=request.message,
                top_k=5,
                include_sources=True,
                user_role=current_user.role,
                explicit_context=explicit_text,
                query_type=query_type,
                tone=tone_pref,
                chat_history=existing_session.get("messages", []) if existing_session else []
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
    
    - Hybrid mode (combines both for best results)
    - Advanced filters: court, case type, date range
    - Relevance scoring and ranking
    """
    try:
        logger.info(f"Search request: {request.query} (mode: {request.searchMode})")
        
        results = []
        
        # Prepare filters for semantic search
        filters = request.filters or {}
        
        # Inject Semantic Expansion for complex case types
        if request.caseType:
            ct = request.caseType.lower()
            types_map = {
                "civil appeal": "Civil Appeal Judgments: Property dispute appeals, Family law appeals (divorce, maintenance, custody), Contract dispute appeals, Rent and tenancy appeals, Succession / inheritance appeals, Banking & recovery suits (loan recovery appeals)",
                "criminal appeal": "Criminal Appeal Judgments: Murder / homicide appeals, Theft / robbery appeals, Fraud / cheating cases, Narcotics cases, Bail cancellation or grant appeals, Sentence reduction appeals",
                "constitution petition": "Constitutional Petition Judgments: Fundamental rights violations, Government action challenges, Illegal detentions, Service matters (jobs, promotions, dismissals), Tax / administrative authority disputes, Public interest litigation"
            }
            if ct in types_map:
                add_str = types_map[ct]
                request.query = f"{request.query} {add_str}" if request.query else add_str
                request.caseType = None  # Remove precise filter so semantic match can shine
            else:
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
                title = str(result.get("title") or "")
                cat = str(result.get("category") or result.get("case_type") or result.get("caseType") or "")
                src = str(result.get("source_file") or "")
                title_l = title.lower()

                if "easylaw" not in src.lower():
                    continue
                
                # Hard filter to remove Acts and Ordinances
                if (
                    cat.lower() in ("statute", "law", "act") 
                    or "laws/" in src.lower() 
                    or ("ordinance" in title_l)
                    or (("act," in title_l or "act 19" in title_l or "act 20" in title_l) and " vs " not in title_l and " v " not in title_l and " v. " not in title_l)
                ):
                    continue

                if request.court and request.court.lower() not in result.get("court", "").lower():
                    continue

                # Strict Court/Location Enforcer (Fixes Semantic Bleed across High Courts)
                query_l = (request.query or "").lower()
                doc_court_l = str(result.get("court") or "").lower()
                doc_content_l = str(result.get("excerpt") or result.get("content") or "").lower()
                loc_keys = ["sindh", "karachi", "lahore", "peshawar", "balochistan", "islamabad", "supreme", "federal shariat"]
                
                should_skip_due_to_location = False
                
                if "supreme court" in query_l and "supreme" not in doc_court_l and doc_court_l != "":
                    should_skip_due_to_location = True
                elif "high court" in query_l and "high court" not in doc_court_l and doc_court_l != "":
                    should_skip_due_to_location = True
                    
                for loc in loc_keys:
                    if loc in query_l:
                        if loc not in title_l and loc not in doc_court_l and loc not in doc_content_l:
                            should_skip_due_to_location = True
                            break
                            
                if should_skip_due_to_location:
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
                
                # Format fixes
                import re
                from utils.formatters import _auto_heal_ocr_spaces
                title_c = re.sub(r'(?<![a-zA-Z])(?:[a-zA-Z]\s+){3,}[a-zA-Z](?![a-zA-Z])', lambda m: m.group(0).replace(' ', ''), result.get("title", ""))
                title_c = _auto_heal_ocr_spaces(title_c)
                title_c = re.sub(r'^(?i).*?(?:bench|nch|\bcourt)\s*,\s*(?:[a-zA-Z\s\.]+\s+)?in\s+', '', title_c).strip()
                title_c = re.sub(r'^(?i).*?(?:bench|nch)\s*,\s*', '', title_c).strip()
                result["title"] = title_c

                excerpt_c = re.sub(r'(?<![a-zA-Z])(?:[a-zA-Z]\s+){3,}[a-zA-Z](?![a-zA-Z])', lambda m: m.group(0).replace(' ', ''), result.get("excerpt", ""))
                excerpt_c = _auto_heal_ocr_spaces(excerpt_c)
                result["excerpt"] = excerpt_c
                
                # Double check year
                if not year:
                    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', title_c)
                    if year_match:
                        year = int(year_match.group(1))
                
                result["year"] = year

                date_val = str(result.get("date") or result.get("dateOfJudgment") or "")
                if date_val == "None" or date_val.strip() == "":
                    date_val = str(year or "Unknown")
                result["date"] = date_val
                
                result["search_method"] = "semantic"
                result["relevance_score"] = round(result.get("similarity", 0.5) * 100, 1)
                results.append(result)
        
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

