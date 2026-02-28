from fastapi import APIRouter, Depends, HTTPException, status
from config.database import get_db
from models.reminder import ReminderCreate, ReminderUpdate, ReminderResponse
from middlewares.auth import get_current_user
from models.user import TokenData
from bson import ObjectId
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/api/reminders", tags=["Reminders"])

@router.get("/", response_model=List[ReminderResponse])
async def get_reminders(
    upcoming: Optional[bool] = None,
    completed: Optional[bool] = None,
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get reminders for authenticated user"""
    try:
        filter_query = {"userId": current_user.id}
        
        if upcoming:
            filter_query["dueDate"] = {"$gte": datetime.utcnow()}
            filter_query["isCompleted"] = False
        elif completed:
            filter_query["isCompleted"] = True
        
        reminders_cursor = db.reminders.find(filter_query).sort("dueDate", 1)
        reminders = await reminders_cursor.to_list(length=None)
        
        # Convert ObjectIds to strings
        for reminder in reminders:
            reminder["_id"] = str(reminder["_id"])
            reminder["userId"] = str(reminder["userId"])
            if reminder.get("caseId"):
                case_id = reminder["caseId"]
                # Populate case details
                case = await db.cases.find_one(
                    {"_id": ObjectId(case_id)},
                    {"title": 1, "caseType": 1}
                )
                if case:
                    reminder["case"] = {
                        "title": case.get("title"),
                        "caseType": case.get("caseType")
                    }
                reminder["caseId"] = str(case_id)
        
        return reminders
        
    except Exception as e:
        print(f"Error fetching reminders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reminders"
        )

@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_data: ReminderCreate,
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new reminder"""
    try:
        reminder_doc = {
            "userId": ObjectId(current_user.id),
            "caseId": ObjectId(reminder_data.caseId) if reminder_data.caseId else None,
            "title": reminder_data.title,
            "description": reminder_data.description,
            "dueDate": reminder_data.dueDate,
            "priority": reminder_data.priority.value,
            "isCompleted": False,
            "completedAt": None,
            "notifyBeforeDays": reminder_data.notifyBeforeDays,
            "notificationSent": False,
            "notificationSentAt": None,
            "isRecurring": reminder_data.isRecurring,
            "recurrencePattern": reminder_data.recurrencePattern,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = await db.reminders.insert_one(reminder_doc)
        reminder_doc["_id"] = str(result.inserted_id)
        reminder_doc["userId"] = str(reminder_doc["userId"])
        if reminder_doc.get("caseId"):
            reminder_doc["caseId"] = str(reminder_doc["caseId"])
        
        return reminder_doc
        
    except Exception as e:
        print(f"Error creating reminder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create reminder"
        )

@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: str,
    reminder_update: ReminderUpdate,
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update a reminder"""
    try:
        update_data = {"updatedAt": datetime.utcnow()}
        
        update_dict = reminder_update.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                if key == "caseId":
                    update_data[key] = ObjectId(value) if value else None
                elif hasattr(value, "value"):  # Enum
                    update_data[key] = value.value
                else:
                    update_data[key] = value
        
        if reminder_update.isCompleted and not update_data.get("completedAt"):
            update_data["completedAt"] = datetime.utcnow()
        
        result = await db.reminders.find_one_and_update(
            {"_id": ObjectId(reminder_id), "userId": current_user.id},
            {"$set": update_data},
            return_document=True
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )
        
        result["_id"] = str(result["_id"])
        result["userId"] = str(result["userId"])
        if result.get("caseId"):
            result["caseId"] = str(result["caseId"])
        
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error updating reminder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update reminder"
        )

@router.patch("/{reminder_id}/complete", response_model=ReminderResponse)
async def complete_reminder(
    reminder_id: str,
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """Mark a reminder as completed"""
    try:
        result = await db.reminders.find_one_and_update(
            {"_id": ObjectId(reminder_id), "userId": current_user.id},
            {
                "$set": {
                    "isCompleted": True,
                    "completedAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
            },
            return_document=True
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )
        
        result["_id"] = str(result["_id"])
        result["userId"] = str(result["userId"])
        if result.get("caseId"):
            result["caseId"] = str(result["caseId"])
        
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error completing reminder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete reminder"
        )

@router.delete("/{reminder_id}")
async def delete_reminder(
    reminder_id: str,
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete a reminder"""
    try:
        result = await db.reminders.delete_one({
            "_id": ObjectId(reminder_id),
            "userId": current_user.id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )
        
        return {"message": "Reminder deleted successfully"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error deleting reminder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete reminder"
        )
