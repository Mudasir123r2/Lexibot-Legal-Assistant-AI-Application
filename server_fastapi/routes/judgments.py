from fastapi import APIRouter, Depends, HTTPException, status, Query
from config.database import get_db
from models.judgment import JudgmentCreate, JudgmentUpdate, JudgmentResponse, JudgmentSearchRequest
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
import re

router = APIRouter(prefix="/api/judgments", tags=["Judgments"])

@router.get("/search")
async def search_judgments(
    query: Optional[str] = Query(None, description="Search in title, case number, keywords, summary"),
    caseType: Optional[str] = Query(None, description="Filter by case type"),
    court: Optional[str] = Query(None, description="Filter by court name"),
    limit: int = Query(20, le=100),
    page: int = Query(1, ge=1)
):
    try:
        from services.rag_pipeline import get_rag_pipeline
        rag = get_rag_pipeline()
        vector_store = rag.vector_store
        
        # Deduplicate FAISS chunks into unified file boundaries
        unique_judgments = {}
        for chunk in vector_store.metadata:
            title = chunk.get("title", "")
            if not title or title == "Untitled":
                continue
            if title not in unique_judgments:
                # Mock a MongoDB-style _id using the title hex for unique fetching later if needed
                import hashlib
                mock_id = hashlib.md5(title.encode()).hexdigest()[:24]
                unique_judgments[title] = {
                    "_id": chunk.get("_id", chunk.get("id", mock_id)),
                    "title": title,
                    "caseNumber": chunk.get("case_number", "N/A"),
                    "caseType": chunk.get("case_type", chunk.get("category", "")),
                    "court": chunk.get("court", ""),
                    "dateOfJudgment": chunk.get("date", datetime.utcnow().isoformat()),
                    "judge": chunk.get("judge", ""),
                    "summary": chunk.get("excerpt", chunk.get("content", "")[:300]) + "..."
                }
                
        all_judgments = list(unique_judgments.values())
        
        # Use simple string matching for category/court filters
        if caseType:
            c_lower = caseType.lower()
            all_judgments = [j for j in all_judgments if c_lower in j.get("caseType", "").lower()]
            
        if court:
            court_lower = court.lower()
            all_judgments = [j for j in all_judgments if court_lower in j.get("court", "").lower()]
            
        # If the user performed a deep string search, prioritize FAISS semantic ranking!
        if query and len(query.strip()) > 2:
            semantic_docs = rag.search_judgments(query, top_k=limit)
            if semantic_docs:
                all_judgments = []
                for doc in semantic_docs:
                    import hashlib
                    doc_title = doc.get("title", "Untitled")
                    mock_id = hashlib.md5(doc_title.encode()).hexdigest()[:24]
                    all_judgments.append({
                        "_id": doc.get("id", mock_id),
                        "title": doc_title,
                        "caseNumber": doc.get("case_type", "N/A"),
                        "caseType": doc.get("case_type", ""),
                        "court": doc.get("court", ""),
                        "dateOfJudgment": doc.get("date", datetime.utcnow().isoformat()),
                        "summary": doc.get("excerpt", "")
                    })
        elif query:
            # Fallback string filter if query is too short for semantic
            q_lower = query.lower()
            all_judgments = [j for j in all_judgments if q_lower in str(j).lower()]
        
        # Calculate pagination
        total = len(all_judgments)
        skip = (page - 1) * limit
        paginated_judgments = all_judgments[skip:skip+limit]
        
        return {
            "judgments": paginated_judgments,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        print(f"Error searching FAISS metadata judgments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search judgments via FAISS pipeline"
        )

@router.get("/{judgment_id}", response_model=JudgmentResponse)
async def get_judgment(judgment_id: str, db = Depends(get_db)):
    """Get a specific judgment by ID"""
    try:
        from bson.errors import InvalidId
        try:
            judgment = await db.judgments.find_one({"_id": ObjectId(judgment_id)})
        except InvalidId:
            judgment = None
            
        if not judgment:
            from services.rag_pipeline import get_rag_pipeline
            vector_store = get_rag_pipeline().vector_store
            chunks = []
            doc_title = None
            first_chunk = None
            
            for chunk in vector_store.metadata:
                chunk_title = chunk.get("title", "Untitled")
                import hashlib
                mock_id = chunk.get("id", hashlib.md5(chunk_title.encode()).hexdigest()[:24])
                if mock_id == judgment_id:
                    chunks.append(chunk)
                    if not first_chunk:
                        first_chunk = chunk
                        doc_title = chunk_title
                        
            if not chunks:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Judgment not found"
                )
                
            full_text = "\n\n".join([c.get("content", "") for c in chunks])
            return {
                "_id": judgment_id,
                "title": doc_title or "Untitled",
                "caseNumber": first_chunk.get("case_number") or "N/A",
                "court": first_chunk.get("court") or "Not Specified",
                "judge": first_chunk.get("judge") or "Not Specified",
                "dateOfJudgment": first_chunk.get("date") or datetime.utcnow().isoformat(),
                "fullText": full_text or "No content available.",
                "summary": first_chunk.get("summary") or "No summary available.",
                "caseType": first_chunk.get("case_type") or "Not Specified",
                "keyInformation": {
                    "parties": [{"name": str(first_chunk.get("parties")), "role": "Unknown"}] if first_chunk.get("parties") else [],
                    "issues": [],
                    "decisions": [],
                    "deadlines": [],
                    "obligations": []
                },
                "keywords": [],
                "citations": [],
                "referencedCases": [],
                "jurisdiction": "",
                "year": None,
                "tags": [],
                "createdAt": datetime.utcnow().isoformat(),
                "updatedAt": datetime.utcnow().isoformat()
            }
        
        judgment["_id"] = str(judgment["_id"])
        
        # Populate referenced cases
        if judgment.get("referencedCases"):
            ref_ids = [ObjectId(ref) for ref in judgment["referencedCases"] if ObjectId.is_valid(str(ref))]
            ref_cases_cursor = db.judgments.find(
                {"_id": {"$in": ref_ids}},
                {"title": 1, "caseNumber": 1, "dateOfJudgment": 1}
            )
            ref_cases = await ref_cases_cursor.to_list(length=None)
            judgment["referencedCasesData"] = ref_cases
        
        return judgment
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error fetching judgment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch judgment"
        )

@router.post("/", response_model=JudgmentResponse, status_code=status.HTTP_201_CREATED)
async def create_judgment(judgment_data: JudgmentCreate, db = Depends(get_db)):
    """Create a new judgment"""
    try:
        # Auto-extract year if not provided
        year = judgment_data.year
        if not year and judgment_data.dateOfJudgment:
            year = judgment_data.dateOfJudgment.year
        
        judgment_doc = {
            "caseNumber": judgment_data.caseNumber,
            "title": judgment_data.title,
            "court": judgment_data.court,
            "judge": judgment_data.judge,
            "dateOfJudgment": judgment_data.dateOfJudgment,
            "fullText": judgment_data.fullText,
            "summary": judgment_data.summary,
            "keyInformation": judgment_data.keyInformation.model_dump() if judgment_data.keyInformation else {
                "parties": [],
                "issues": [],
                "decisions": [],
                "deadlines": [],
                "obligations": []
            },
            "caseType": judgment_data.caseType,
            "keywords": judgment_data.keywords,
            "citations": judgment_data.citations,
            "referencedCases": [],
            "jurisdiction": judgment_data.jurisdiction,
            "year": year,
            "tags": judgment_data.tags,
            "embedding": None,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = await db.judgments.insert_one(judgment_doc)
        judgment_doc["_id"] = str(result.inserted_id)
        
        return judgment_doc
        
    except Exception as e:
        print(f"Error creating judgment: {e}")
        if "duplicate key error" in str(e).lower() or "caseNumber" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Case number already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create judgment"
        )
