from fastapi import APIRouter, Depends, HTTPException, status
from config.database import get_db
from models.case import CaseCreate, CaseUpdate, CaseResponse
from middlewares.auth import get_current_user
from models.user import TokenData
from bson import ObjectId
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/cases", tags=["Cases"])

@router.get("/", response_model=List[CaseResponse])
async def get_user_cases(
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all cases for the authenticated user"""
    try:
        cases_cursor = db.cases.find({"userId": current_user.id}).sort("createdAt", -1)
        cases = await cases_cursor.to_list(length=None)
        
        # Convert ObjectId to string for response
        for case in cases:
            case["_id"] = str(case["_id"])
            case["userId"] = str(case["userId"])
        
        return cases
    except Exception as e:
        print(f"Error fetching cases: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch cases"
        )

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: str,
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get a specific case by ID"""
    try:
        case = await db.cases.find_one({
            "_id": ObjectId(case_id),
            "userId": current_user.id
        })
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        case["_id"] = str(case["_id"])
        case["userId"] = str(case["userId"])
        return case
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error fetching case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch case"
        )

@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_data: CaseCreate,
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new case"""
    try:
        case_doc = {
            "userId": ObjectId(current_user.id),
            "title": case_data.title,
            "caseType": case_data.caseType.value,
            "description": case_data.description,
            "status": case_data.status.value,
            "filingDate": case_data.filingDate,
            "hearingDate": case_data.hearingDate,
            "deadline": case_data.deadline,
            "plaintiff": case_data.plaintiff,
            "defendant": case_data.defendant,
            "predictedOutcome": None,
            "keyDetails": {
                "obligations": [],
                "deadlines": [],
                "involvedParties": []
            },
            "tags": case_data.tags,
            "notes": case_data.notes,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = await db.cases.insert_one(case_doc)
        case_doc["_id"] = str(result.inserted_id)
        case_doc["userId"] = str(case_doc["userId"])
        
        return case_doc
        
    except Exception as e:
        print(f"Error creating case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create case"
        )

@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: str,
    case_update: CaseUpdate,
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update an existing case"""
    try:
        # Build update document
        update_data = {"updatedAt": datetime.utcnow()}
        
        update_dict = case_update.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                if hasattr(value, "value"):  # Enum
                    update_data[key] = value.value
                elif hasattr(value, "model_dump"):  # Pydantic model
                    update_data[key] = value.model_dump()
                else:
                    update_data[key] = value
        
        result = await db.cases.find_one_and_update(
            {"_id": ObjectId(case_id), "userId": current_user.id},
            {"$set": update_data},
            return_document=True
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        result["_id"] = str(result["_id"])
        result["userId"] = str(result["userId"])
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error updating case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update case"
        )

@router.delete("/{case_id}")
async def delete_case(
    case_id: str,
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete a case"""
    try:
        result = await db.cases.delete_one({
            "_id": ObjectId(case_id),
            "userId": current_user.id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        return {"message": "Case deleted successfully"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error deleting case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete case"
        )
