from fastapi import APIRouter, Depends, HTTPException, status
from config.database import get_db
from middlewares.auth import get_current_user, require_admin
from models.user import TokenData, UserRole
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import logging

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
