from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class FeedbackType(str, Enum):
    general = "general"
    bug = "bug"
    feature = "feature"
    improvement = "improvement"
    chat = "chat"
    search = "search"
    prediction = "prediction"
    other = "other"


class FeedbackStatus(str, Enum):
    pending = "pending"
    reviewed = "reviewed"
    resolved = "resolved"
    dismissed = "dismissed"


class FeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    feedbackType: FeedbackType = FeedbackType.general
    message: str = Field(..., min_length=10, max_length=2000)
    contactEmail: Optional[str] = None
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Feedback message must be at least 10 characters')
        return v.strip()


class FeedbackResponse(BaseModel):
    id: str = Field(alias="_id")
    userId: str
    userName: str
    userEmail: str
    rating: int
    feedbackType: str
    message: str
    contactEmail: Optional[str] = None
    status: str = "pending"
    adminResponse: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True
        from_attributes = True


class FeedbackUpdate(BaseModel):
    status: Optional[FeedbackStatus] = None
    adminResponse: Optional[str] = None
