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
    parties: Optional[str] = Query(None, description="Search by party names"),
    citation: Optional[str] = Query(None, description="Search by citation/case number"),
    yearFrom: Optional[int] = Query(None, description="Year range start"),
    yearTo: Optional[int] = Query(None, description="Year range end"),
    limit: int = Query(20, le=100),
    page: int = Query(1, ge=1),
    db = Depends(get_db)
):
    """
    Advanced judgment search with multiple filters.
    
    Search capabilities:
    - query: Search in title, case number, keywords, summary
    - parties: Search by petitioner/respondent names
    - citation: Search by specific citation or case number
    - Filters: caseType, court, year range
    - Pagination with configurable limit
    """
    try:
        filter_query = {}
        search_conditions = []
        
        # General text search
        if query:
            search_conditions.extend([
                {"title": {"$regex": query, "$options": "i"}},
                {"caseNumber": {"$regex": query, "$options": "i"}},
                {"keywords": {"$regex": query, "$options": "i"}},
                {"summary": {"$regex": query, "$options": "i"}}
            ])
        
        # Party name search
        if parties:
            search_conditions.append({"parties": {"$regex": parties, "$options": "i"}})
        
        # Citation search
        if citation:
            search_conditions.extend([
                {"caseNumber": {"$regex": citation, "$options": "i"}},
                {"citation": {"$regex": citation, "$options": "i"}}
            ])
        
        # Apply OR conditions if any
        if search_conditions:
            filter_query["$or"] = search_conditions
        
        # Exact/partial match filters
        if caseType:
            filter_query["caseType"] = caseType
        
        if court:
            filter_query["court"] = {"$regex": court, "$options": "i"}
        
        # Year range
        if yearFrom or yearTo:
            filter_query["year"] = {}
            if yearFrom:
                filter_query["year"]["$gte"] = yearFrom
            if yearTo:
                filter_query["year"]["$lte"] = yearTo
        
        # Calculate skip for pagination
        skip = (page - 1) * limit
        
        # Get total count
        total = await db.judgments.count_documents(filter_query)
        
        # Get paginated results (excluding fullText for list view)
        judgments_cursor = db.judgments.find(
            filter_query,
            {"fullText": 0}
        ).sort("dateOfJudgment", -1).skip(skip).limit(limit)
        
        judgments = await judgments_cursor.to_list(length=limit)
        
        # Convert ObjectIds to strings
        for judgment in judgments:
            judgment["_id"] = str(judgment["_id"])
            if "referencedCases" in judgment:
                judgment["referencedCases"] = [str(ref) for ref in judgment.get("referencedCases", [])]
        
        return {
            "judgments": judgments,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        print(f"Error searching judgments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search judgments"
        )

@router.get("/{judgment_id}", response_model=JudgmentResponse)
async def get_judgment(judgment_id: str, db = Depends(get_db)):
    """Get a specific judgment by ID"""
    try:
        judgment = await db.judgments.find_one({"_id": ObjectId(judgment_id)})
        
        if not judgment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Judgment not found"
            )
        
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
