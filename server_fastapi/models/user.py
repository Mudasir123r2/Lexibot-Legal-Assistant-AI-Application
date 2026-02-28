from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    client = "client"
    advocate = "advocate"
    admin = "admin"

class UserPreferences(BaseModel):
    tone: str = "formal"
    language: str = "English"

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole = UserRole.client

class UserCreate(UserBase):
    password: str
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        if len(v) > 100:
            raise ValueError('Name cannot exceed 100 characters')
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v) > 72:
            raise ValueError('Password cannot exceed 72 characters (bcrypt limit)')
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = None
    profilePicture: Optional[str] = None
    preferences: Optional[UserPreferences] = None

class UserInDB(UserBase):
    id: str = Field(alias="_id")
    hashed_password: str
    isActive: bool = True
    profilePicture: Optional[str] = None
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    resetPasswordTokenHash: Optional[str] = None
    resetPasswordExpiresAt: Optional[datetime] = None
    isEmailVerified: bool = False
    emailVerificationTokenHash: Optional[str] = None
    emailVerificationExpiresAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}

class UserResponse(UserBase):
    id: str = Field(alias="_id")
    isActive: bool
    profilePicture: Optional[str] = None
    preferences: UserPreferences
    isEmailVerified: bool
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True
        from_attributes = True

class Token(BaseModel):
    token: str
    user: Dict

class TokenData(BaseModel):
    id: str
    role: UserRole

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    password: str
    
    @field_validator('password')
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class VerifyEmailRequest(BaseModel):
    token: str
    email: EmailStr
