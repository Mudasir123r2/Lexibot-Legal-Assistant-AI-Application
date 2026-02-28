from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from config.database import get_db
from models.user import (
    UserCreate, UserResponse, LoginRequest, Token, 
    ForgotPasswordRequest, ResetPasswordRequest, VerifyEmailRequest
)
from utils.auth import get_password_hash, verify_password, create_access_token
from utils.mailer import send_reset_email, send_verification_email
from config.settings import settings
import hashlib
import secrets
from datetime import datetime, timedelta
from bson import ObjectId
import re
import urllib.parse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

def escape_regex(text: str) -> str:
    """Escape special regex characters"""
    return re.escape(text)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db = Depends(get_db)):
    """Register a new user"""
    try:
        print(f"Registration attempt - Name: {user_data.name}, Email: {user_data.email}, Role: {user_data.role}")
        # Check if email already exists (case-insensitive)
        escaped_email = escape_regex(user_data.email.lower())
        print(f"Checking for existing user with email: {escaped_email}")
        existing_user = await db.users.find_one({
            "email": {"$regex": f"^{escaped_email}$", "$options": "i"}
        })
        
        if existing_user:
            print(f"Email already exists: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email is already registered. Please use a different email or try logging in."
            )
        
        print("Email is available, generating verification token...")
        # Generate email verification token
        raw_token = secrets.token_hex(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        print("Hashing password...")
        # Hash password (truncate to 72 bytes for bcrypt compatibility)
        password_to_hash = user_data.password[:72] if len(user_data.password) > 72 else user_data.password
        hashed_password = get_password_hash(password_to_hash)
        
        print("Creating user document...")
        # Create user document
        user_doc = {
            "name": user_data.name,
            "email": user_data.email.lower(),
            "password": hashed_password,
            "role": user_data.role.value,
            "isActive": True,
            "profilePicture": None,
            "preferences": {
                "tone": "formal",
                "language": "English"
            },
            "resetPasswordTokenHash": None,
            "resetPasswordExpiresAt": None,
            "isEmailVerified": False,
            "emailVerificationTokenHash": token_hash,
            "emailVerificationExpiresAt": expires_at,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        print("Inserting user into database...")
        result = await db.users.insert_one(user_doc)
        print(f"User created with ID: {result.inserted_id}")
        
        # Send verification email
        verification_url = f"{settings.WEB_BASE_URL}/verify-email?token={raw_token}&email={urllib.parse.quote(user_data.email)}"
        
        print(f"Sending verification email to {user_data.email}...")
        try:
            await send_verification_email(user_data.email, verification_url)
            return {
                "message": "Registration successful! Please check your email to verify your account."
            }
        except Exception as email_err:
            print(f"Failed to send verification email: {email_err}")
            return {
                "message": "Registration successful! However, we couldn't send the verification email. Please contact support."
            }
            
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        print(f"Registration error: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, db = Depends(get_db)):
    """Login user and return JWT token"""
    try:
        # Find user case-insensitively
        escaped_email = escape_regex(credentials.email.lower())
        user = await db.users.find_one({
            "email": {"$regex": f"^{escaped_email}$", "$options": "i"}
        })
        
        print(f"🔐 Login attempt for: {credentials.email}")
        
        if not user:
            print(f"❌ User not found: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        print(f"✅ User found: {user['email']}")
        
        # Verify password
        try:
            # Truncate password to 72 bytes for bcrypt compatibility
            password_to_verify = credentials.password[:72] if len(credentials.password) > 72 else credentials.password
            print(f"🔑 Verifying password (hash starts with): {user['password'][:20]}...")
            is_valid = verify_password(password_to_verify, user["password"])
            print(f"🔑 Password valid: {is_valid}")
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )
        except ValueError as ve:
            print(f"Password verification error: {ve}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if email is verified
        if not user.get("isEmailVerified", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email before signing in. Check your inbox for the verification link."
            )
        
        # Check if account is active
        if user.get("isActive", True) == False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account disabled, contact admin"
            )
        
        # Create access token
        token_data = {
            "id": str(user["_id"]),
            "role": user["role"]
        }
        token = create_access_token(token_data)
        
        return {
            "token": token,
            "user": {
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again later."
        )

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db = Depends(get_db)):
    """Send password reset email"""
    try:
        print(f"📧 Forgot password request for: {request.email}")
        # Find user case-insensitively
        escaped_email = escape_regex(request.email.lower())
        user = await db.users.find_one({
            "email": {"$regex": f"^{escaped_email}$", "$options": "i"}
        })
        
        # Always return success to avoid user enumeration
        if not user:
            print(f"⚠️ User not found: {request.email}")
            return {"message": "If that email exists, a reset link has been sent."}
        
        print(f"✅ User found: {user.get('email')}")
        # Generate reset token
        raw_token = secrets.token_hex(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        
        print("💾 Updating user with reset token...")
        # Update user with reset token
        await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "resetPasswordTokenHash": token_hash,
                    "resetPasswordExpiresAt": expires_at,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        # Send reset email
        reset_url = f"{settings.WEB_BASE_URL}/reset-password?token={raw_token}&email={urllib.parse.quote(user['email'])}"
        
        print(f"📨 Sending reset email to: {user['email']}")
        print(f"🔗 Reset URL: {reset_url}")
        try:
            await send_reset_email(user["email"], reset_url)
            print("✅ Reset email sent successfully")
            return {"message": "If that email exists, a reset link has been sent."}
        except Exception as email_err:
            print(f"❌ Failed to send reset email: {email_err}")
            import traceback
            print(traceback.format_exc())
            # Cleanup on failure
            await db.users.update_one(
                {"_id": user["_id"]},
                {
                    "$unset": {
                        "resetPasswordTokenHash": "",
                        "resetPasswordExpiresAt": ""
                    },
                    "$set": {"updatedAt": datetime.utcnow()}
                }
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send reset email. Please try again later."
            )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Forgot password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred. Please try again later."
        )

class ResetRequestBody(BaseModel):
    email: str
    token: str
    newPassword: str

@router.post("/reset")
async def reset_password_v2(
    request: ResetRequestBody,
    db = Depends(get_db)
):
    """Reset user password with token (frontend format)"""
    try:
        # Find user case-insensitively
        escaped_email = escape_regex(request.email.lower())
        user = await db.users.find_one({
            "email": {"$regex": f"^{escaped_email}$", "$options": "i"}
        })
        
        if not user or not user.get("resetPasswordTokenHash") or not user.get("resetPasswordExpiresAt"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset link"
            )
        
        # Check if token expired
        if user["resetPasswordExpiresAt"] < datetime.utcnow():
            await db.users.update_one(
                {"_id": user["_id"]},
                {
                    "$unset": {
                        "resetPasswordTokenHash": "",
                        "resetPasswordExpiresAt": ""
                    },
                    "$set": {"updatedAt": datetime.utcnow()}
                }
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset link has expired. Please request a new one."
            )
        
        # Verify token
        token_hash = hashlib.sha256(request.token.encode()).hexdigest()
        if token_hash != user["resetPasswordTokenHash"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        # Update password and clear reset token
        hashed_password = get_password_hash(request.newPassword)
        print(f"🔄 Resetting password for: {user['email']}")
        print(f"🔑 New hash: {hashed_password[:30]}...")
        
        result = await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "password": hashed_password,
                    "updatedAt": datetime.utcnow()
                },
                "$unset": {
                    "resetPasswordTokenHash": "",
                    "resetPasswordExpiresAt": ""
                }
            }
        )
        print(f"✅ Update result: matched={result.matched_count}, modified={result.modified_count}")
        
        return {"message": "Password reset successful. You can now sign in."}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reset password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred. Please try again later."
        )

@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    email: str = Query(...),
    db = Depends(get_db)
):
    """Reset user password with token"""
    try:
        # Find user case-insensitively
        escaped_email = escape_regex(email.lower())
        user = await db.users.find_one({
            "email": {"$regex": f"^{escaped_email}$", "$options": "i"}
        })
        
        if not user or not user.get("resetPasswordTokenHash") or not user.get("resetPasswordExpiresAt"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset link"
            )
        
        # Check if token expired
        if user["resetPasswordExpiresAt"] < datetime.utcnow():
            await db.users.update_one(
                {"_id": user["_id"]},
                {
                    "$unset": {
                        "resetPasswordTokenHash": "",
                        "resetPasswordExpiresAt": ""
                    },
                    "$set": {"updatedAt": datetime.utcnow()}
                }
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset link has expired. Please request a new one."
            )
        
        # Verify token
        token_hash = hashlib.sha256(request.token.encode()).hexdigest()
        if token_hash != user["resetPasswordTokenHash"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        # Update password and clear reset token
        hashed_password = get_password_hash(request.password)
        print(f"🔄 Resetting password for: {user['email']}")
        print(f"🔑 New hash: {hashed_password[:30]}...")
        
        result = await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "password": hashed_password,
                    "updatedAt": datetime.utcnow()
                },
                "$unset": {
                    "resetPasswordTokenHash": "",
                    "resetPasswordExpiresAt": ""
                }
            }
        )
        print(f"✅ Update result: matched={result.matched_count}, modified={result.modified_count}")
        
        return {"message": "Password reset successful. You can now sign in."}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during password reset. Please try again."
        )

@router.get("/verify-email")
async def verify_email(
    token: str = Query(...),
    email: str = Query(...),
    db = Depends(get_db)
):
    """Verify user email address"""
    try:
        # Find user case-insensitively
        escaped_email = escape_regex(email.lower())
        user = await db.users.find_one({
            "email": {"$regex": f"^{escaped_email}$", "$options": "i"}
        })
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification link"
            )
        
        # Check if already verified
        if user.get("isEmailVerified", False):
            return {"message": "Email already verified. You can now sign in."}
        
        # Check if token exists and not expired
        if not user.get("emailVerificationTokenHash") or not user.get("emailVerificationExpiresAt"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification link"
            )
        
        if user["emailVerificationExpiresAt"] < datetime.utcnow():
            await db.users.update_one(
                {"_id": user["_id"]},
                {
                    "$unset": {
                        "emailVerificationTokenHash": "",
                        "emailVerificationExpiresAt": ""
                    },
                    "$set": {"updatedAt": datetime.utcnow()}
                }
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification link has expired. Please register again."
            )
        
        # Verify token
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        if token_hash != user["emailVerificationTokenHash"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification link"
            )
        
        # Mark email as verified and clear token
        await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "isEmailVerified": True,
                    "updatedAt": datetime.utcnow()
                },
                "$unset": {
                    "emailVerificationTokenHash": "",
                    "emailVerificationExpiresAt": ""
                }
            }
        )
        
        return {"message": "Email verified successfully! You can now sign in."}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Email verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during email verification. Please try again."
        )
