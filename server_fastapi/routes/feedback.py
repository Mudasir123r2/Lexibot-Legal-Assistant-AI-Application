from fastapi import APIRouter, Depends, HTTPException, status, Query
from config.database import get_db
from models.feedback import FeedbackCreate, FeedbackResponse, FeedbackUpdate, FeedbackStatus
from middlewares.auth import get_current_user, require_admin
from models.user import TokenData
from bson import ObjectId
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback_data: FeedbackCreate,
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Submit user feedback.
    
    Features:
    - Rating (1-5 stars)
    - Feedback type categorization
    - Optional contact email for follow-up
    """
    try:
        # Get user details
        user = await db.users.find_one({"_id": ObjectId(current_user.id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create feedback document
        feedback_doc = {
            "userId": current_user.id,
            "userName": user.get("name", "Unknown"),
            "userEmail": user.get("email", ""),
            "userRole": current_user.role,
            "rating": feedback_data.rating,
            "feedbackType": feedback_data.feedbackType.value,
            "message": feedback_data.message,
            "contactEmail": feedback_data.contactEmail,
            "status": FeedbackStatus.pending.value,
            "adminResponse": None,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = await db.feedbacks.insert_one(feedback_doc)
        
        return {
            "message": "Thank you! Your feedback has been submitted successfully.",
            "feedbackId": str(result.inserted_id)
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error submitting feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback. Please try again."
        )


@router.get("/my-feedback")
async def get_my_feedback(
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db),
    limit: int = Query(20, le=100),
    page: int = Query(1, ge=1)
):
    """Get current user's submitted feedback"""
    try:
        skip = (page - 1) * limit
        
        cursor = db.feedbacks.find(
            {"userId": current_user.id}
        ).sort("createdAt", -1).skip(skip).limit(limit)
        
        feedbacks = await cursor.to_list(length=limit)
        
        for feedback in feedbacks:
            feedback["_id"] = str(feedback["_id"])
        
        total = await db.feedbacks.count_documents({"userId": current_user.id})
        
        return {
            "feedbacks": feedbacks,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        print(f"Error fetching feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch feedback"
        )


# Admin routes for managing feedback
@router.get("/all")
async def get_all_feedback(
    current_user: TokenData = Depends(require_admin),
    db = Depends(get_db),
    limit: int = Query(50, le=200),
    page: int = Query(1, ge=1),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    feedback_type: Optional[str] = Query(None, description="Filter by type")
):
    """Get all feedback (admin only)"""
    try:
        skip = (page - 1) * limit
        
        filter_query = {}
        if status_filter:
            filter_query["status"] = status_filter
        if feedback_type:
            filter_query["feedbackType"] = feedback_type
        
        cursor = db.feedbacks.find(filter_query).sort("createdAt", -1).skip(skip).limit(limit)
        
        feedbacks = await cursor.to_list(length=limit)
        
        for feedback in feedbacks:
            feedback["_id"] = str(feedback["_id"])
        
        total = await db.feedbacks.count_documents(filter_query)
        
        # Calculate stats
        stats = {
            "total": total,
            "pending": await db.feedbacks.count_documents({"status": "pending"}),
            "reviewed": await db.feedbacks.count_documents({"status": "reviewed"}),
            "resolved": await db.feedbacks.count_documents({"status": "resolved"}),
            "avgRating": 0
        }
        
        # Calculate average rating
        pipeline = [
            {"$group": {"_id": None, "avgRating": {"$avg": "$rating"}}}
        ]
        avg_result = await db.feedbacks.aggregate(pipeline).to_list(length=1)
        if avg_result:
            stats["avgRating"] = round(avg_result[0]["avgRating"], 2)
        
        return {
            "feedbacks": feedbacks,
            "stats": stats,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        print(f"Error fetching all feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch feedback"
        )


@router.patch("/{feedback_id}")
async def update_feedback_status(
    feedback_id: str,
    update_data: FeedbackUpdate,
    current_user: TokenData = Depends(require_admin),
    db = Depends(get_db)
):
    """Update feedback status and add admin response (admin only)"""
    try:
        update_fields = {"updatedAt": datetime.utcnow()}
        
        if update_data.status:
            update_fields["status"] = update_data.status.value
        if update_data.adminResponse is not None:
            update_fields["adminResponse"] = update_data.adminResponse
        
        result = await db.feedbacks.find_one_and_update(
            {"_id": ObjectId(feedback_id)},
            {"$set": update_fields},
            return_document=True
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        result["_id"] = str(result["_id"])
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error updating feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update feedback"
        )


@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: str,
    current_user: TokenData = Depends(require_admin),
    db = Depends(get_db)
):
    """Delete feedback (admin only)"""
    try:
        result = await db.feedbacks.delete_one({"_id": ObjectId(feedback_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        return {"message": "Feedback deleted successfully"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error deleting feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete feedback"
        )
