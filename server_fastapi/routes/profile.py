from fastapi import APIRouter, Depends, HTTPException, status
from config.database import get_db
from models.user import UserResponse, UserUpdate, UserPreferences
from middlewares.auth import get_current_user
from models.user import TokenData
from bson import ObjectId
from datetime import datetime
import hashlib
import secrets
from utils.mailer import send_verification_email
from config.settings import settings
import urllib.parse
import re

router = APIRouter(prefix="/api/profile", tags=["Profile"])

def escape_regex(text: str) -> str:
    """Escape special regex characters"""
    return re.escape(text)

@router.get("/", response_model=UserResponse)
async def get_profile(
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get current user profile"""
    try:
        user = await db.users.find_one(
            {"_id": ObjectId(current_user.id)},
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
        return user
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error fetching profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch profile"
        )

@router.put("/", response_model=UserResponse)
async def update_profile(
    profile_update: UserUpdate,
    current_user: TokenData = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update user profile"""
    try:
        user = await db.users.find_one({"_id": ObjectId(current_user.id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        update_data = {"updatedAt": datetime.utcnow()}
        email_changed = False
        
        update_dict = profile_update.model_dump(exclude_unset=True)
        
        # Validate name
        if "name" in update_dict and update_dict["name"]:
            if len(update_dict["name"]) < 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Name must be at least 2 characters long"
                )
            update_data["name"] = update_dict["name"]
        
        # Handle email change
        if "email" in update_dict and update_dict["email"]:
            new_email = update_dict["email"].lower()
            if new_email != user["email"].lower():
                # Check if email already exists
                escaped_email = escape_regex(new_email)
                existing = await db.users.find_one({
                    "email": {"$regex": f"^{escaped_email}$", "$options": "i"},
                    "_id": {"$ne": user["_id"]}
                })
                
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already in use"
                    )
                
                # Generate new verification token
                raw_token = secrets.token_hex(32)
                token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
                from datetime import timedelta
                expires_at = datetime.utcnow() + timedelta(hours=24)
                
                update_data["email"] = new_email
                update_data["isEmailVerified"] = False
                update_data["emailVerificationTokenHash"] = token_hash
                update_data["emailVerificationExpiresAt"] = expires_at
                email_changed = True
        
        # Handle preferences
        if "preferences" in update_dict and update_dict["preferences"]:
            prefs = update_dict["preferences"]
            if isinstance(prefs, dict):
                # Validate tone
                if prefs.get("tone") and prefs["tone"] not in ["formal", "casual"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Tone must be either 'formal' or 'casual'"
                    )
                update_data["preferences"] = {
                    "tone": prefs.get("tone", user.get("preferences", {}).get("tone", "formal")),
                    "language": "English"  # Always English as per original
                }
        
        # Handle profile picture
        if "profilePicture" in update_dict:
            update_data["profilePicture"] = update_dict["profilePicture"]
        
        # Update user
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": update_data}
        )
        
        # Send verification email if email changed
        verification_sent = False
        if email_changed:
            verification_url = f"{settings.WEB_BASE_URL}/verify-email?token={raw_token}&email={urllib.parse.quote(update_data['email'])}"
            try:
                await send_verification_email(update_data["email"], verification_url)
                verification_sent = True
            except Exception as email_err:
                print(f"Failed to send verification email: {email_err}")
        
        # Fetch updated user
        updated_user = await db.users.find_one(
            {"_id": user["_id"]},
            {
                "password": 0,
                "resetPasswordTokenHash": 0,
                "resetPasswordExpiresAt": 0,
                "emailVerificationTokenHash": 0,
                "emailVerificationExpiresAt": 0
            }
        )
        
        updated_user["_id"] = str(updated_user["_id"])
        
        response_data = dict(updated_user)
        if email_changed:
            response_data["message"] = (
                "Profile updated successfully. Verification email sent to new address."
                if verification_sent
                else "Profile updated successfully. However, verification email couldn't be sent."
            )
        
        return response_data
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
