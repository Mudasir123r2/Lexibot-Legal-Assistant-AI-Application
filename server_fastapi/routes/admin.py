from fastapi import APIRouter, Depends, HTTPException, status
from config.database import get_db
from middlewares.auth import get_current_user, require_admin
from models.user import TokenData, UserRole
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import logging
import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
import subprocess

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# Helper function to log admin actions
async def log_admin_action(db, admin_id: str, action: str, target_user_id: str, details: str = None):
    """Record admin action in audit log"""
    try:
        log_entry = {
            "adminId": admin_id,
            "action": action,
            "targetUserId": target_user_id,
            "details": details,
            "timestamp": datetime.utcnow()
        }
        await db.admin_logs.insert_one(log_entry)
        logger.info(f"Admin action logged: {action} by {admin_id} on {target_user_id}")
    except Exception as e:
        logger.warning(f"Failed to log admin action: {e}")

@router.get("/users")
async def get_all_users(
    current_user: TokenData = Depends(require_admin),
    db = Depends(get_db)
):
    """Get all users (admin only)"""
    try:
        users_cursor = db.users.find(
            {},
            {
                "password": 0,
                "resetPasswordTokenHash": 0,
                "resetPasswordExpiresAt": 0,
                "emailVerificationTokenHash": 0,
                "emailVerificationExpiresAt": 0
            }
        ).sort("createdAt", -1)
        
        users = await users_cursor.to_list(length=None)
        
        # Convert ObjectIds to strings
        for user in users:
            user["_id"] = str(user["_id"])
        
        # Calculate stats
        total = len(users)
        active = sum(1 for u in users if u.get("isActive", True))
        inactive = total - active
        verified = sum(1 for u in users if u.get("isEmailVerified", False))
        unverified = total - verified
        
        return {
            "users": users,
            "stats": {
                "total": total,
                "active": active,
                "inactive": inactive,
                "verified": verified,
                "unverified": unverified
            }
        }
        
    except Exception as e:
        print(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )


@router.get("/users/{user_id}")
async def get_user_details(
    user_id: str,
    current_user: TokenData = Depends(require_admin),
    db = Depends(get_db)
):
    """Get single user details (admin only)"""
    try:
        user = await db.users.find_one(
            {"_id": ObjectId(user_id)},
            {
                "password": 0,
                "resetPasswordTokenHash": 0,
                "resetPasswordExpiresAt": 0,
                "emailVerificationTokenHash": 0,
                "emailVerificationExpiresAt": 0
            }
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user["_id"] = str(user["_id"])
        return {"user": user}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error fetching user: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.patch("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    current_user: TokenData = Depends(require_admin),
    db = Depends(get_db)
):
    """Activate a user account"""
    try:
        # Prevent self-modification
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify your own account status"
            )
        
        result = await db.users.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "isActive": True,
                    "updatedAt": datetime.utcnow()
                }
            },
            return_document=True,
            projection={
                "password": 0,
                "resetPasswordTokenHash": 0,
                "resetPasswordExpiresAt": 0,
                "emailVerificationTokenHash": 0,
                "emailVerificationExpiresAt": 0
            }
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Record admin action
        await log_admin_action(
            db, 
            current_user.id, 
            "ACTIVATE_USER", 
            user_id, 
            f"Activated user account"
        )
        
        result["_id"] = str(result["_id"])
        return {
            "message": "Changes saved successfully",
            "user": result
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error activating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update user profile"
        )

@router.patch("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user: TokenData = Depends(require_admin),
    db = Depends(get_db)
):
    """Deactivate a user account"""
    try:
        # Prevent self-modification
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify your own account status"
            )
        
        result = await db.users.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "isActive": False,
                    "updatedAt": datetime.utcnow()
                }
            },
            return_document=True,
            projection={
                "password": 0,
                "resetPasswordTokenHash": 0,
                "resetPasswordExpiresAt": 0,
                "emailVerificationTokenHash": 0,
                "emailVerificationExpiresAt": 0
            }
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Record admin action
        await log_admin_action(
            db, 
            current_user.id, 
            "DEACTIVATE_USER", 
            user_id, 
            f"Deactivated user account"
        )
        
        result["_id"] = str(result["_id"])
        return {
            "message": "Changes saved successfully",
            "user": result
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error deactivating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update user profile"
        )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: TokenData = Depends(require_admin),
    db = Depends(get_db)
):
    """Delete a user (admin only)"""
    try:
        # Prevent self-deletion
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Check if target user is admin
        target_user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if target_user.get("role") == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete admin accounts"
            )
        
        # Perform hard delete
        await db.users.delete_one({"_id": ObjectId(user_id)})
        
        # Record admin action
        await log_admin_action(
            db, 
            current_user.id, 
            "DELETE_USER", 
            user_id, 
            f"Deleted user: {target_user.get('email')}"
        )
        
        return {"message": "Changes saved successfully"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update user profile"
        )


@router.get("/logs")
async def get_admin_logs(
    current_user: TokenData = Depends(require_admin),
    db = Depends(get_db),
    limit: int = 50
):
    """Get admin action logs"""
    try:
        cursor = db.admin_logs.find().sort("timestamp", -1).limit(limit)
        logs = await cursor.to_list(length=limit)
        
        for log in logs:
            log["_id"] = str(log["_id"])
        
        return {"logs": logs, "total": len(logs)}
        
    except Exception as e:
        print(f"Error fetching admin logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch admin logs"
        )

# ================= SERVER KNOWLEDGE BASE & INGESTION ROUTES =================

def run_ingestion_subprocess():
    """Runs the python embedding ingestion script in the background."""
    try:
        # Run the ingest_judgments script for 'files'
        subprocess.run(
            ["python", "scripts/ingest_judgments.py", "--source", "files", "--directory", "data/raw_documents"], 
            check=True
        )
        logger.info("Knowledge base ingestion subprocess completed successfully.")
    except Exception as e:
        logger.error(f"Knowledge base ingestion script failed: {e}")

@router.post("/knowledge/upload")
async def upload_knowledge_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    current_user: TokenData = Depends(require_admin),
    db = Depends(get_db)
):
    """Upload PDF/DOCX files and automatically trigger chunking and vector FAISS ingestion"""
    try:
        UPLOAD_DIR = "data/raw_documents"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        saved_files = []
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(file.filename)
            
        # Record admin action
        await log_admin_action(
            db, 
            current_user.id, 
            "UPLOAD_KNOWLEDGE", 
            "system", 
            f"Uploaded {len(saved_files)} files: {', '.join(saved_files)}"
        )
        
        # Trigger the NLP embedding generation in the background!
        background_tasks.add_task(run_ingestion_subprocess)
        
        return {
            "message": f"Successfully uploaded {len(saved_files)} documents. Deep-learning ingestion pipeline has started in the background."
        }
    except Exception as e:
        logger.error(f"Knowledge upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload and process documents.")


# ================= FAQ PRESET ROUTINES =================

class FAQItem(BaseModel):
    question: str
    answer: str

@router.get("/knowledge/faq")
async def get_all_faqs(current_user: TokenData = Depends(require_admin), db = Depends(get_db)):
    """Fetch all preset FAQ elements"""
    try:
        cursor = db.faq_knowledge.find().sort("createdAt", -1)
        faqs = await cursor.to_list(length=None)
        for f in faqs:
            f["_id"] = str(f["_id"])
        return {"faqs": faqs}
    except Exception as e:
        logger.error(f"Error fetching FAQs: {e}")
        raise HTTPException(status_code=500, detail="Failed to load FAQs")

@router.post("/knowledge/faq")
async def create_faq(
    faq: FAQItem,
    current_user: TokenData = Depends(require_admin), 
    db = Depends(get_db)
):
    """Create a new preset common query"""
    try:
        new_faq = {
            "question": faq.question,
            "answer": faq.answer,
            "createdBy": current_user.id,
            "createdAt": datetime.utcnow()
        }
        result = await db.faq_knowledge.insert_one(new_faq)
        
        await log_admin_action(db, current_user.id, "CREATE_FAQ", "system", f"Created FAQ: {faq.question[:30]}")
        
        return {"message": "FAQ added successfully", "id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Error creating FAQ: {e}")
        raise HTTPException(status_code=500, detail="Failed to create FAQ")

@router.delete("/knowledge/faq/{faq_id}")
async def delete_faq(
    faq_id: str,
    current_user: TokenData = Depends(require_admin),
    db = Depends(get_db)
):
    """Delete a preset FAQ"""
    try:
        await db.faq_knowledge.delete_one({"_id": ObjectId(faq_id)})
        await log_admin_action(db, current_user.id, "DELETE_FAQ", "system", f"Deleted FAQ {faq_id}")
        return {"message": "FAQ deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting FAQ: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete FAQ")
