from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

class ReminderBase(BaseModel):
    title: str
    description: Optional[str] = None
    dueDate: datetime
    priority: Priority = Priority.medium
    caseId: Optional[str] = None
    notifyBeforeDays: int = 1
    isRecurring: bool = False
    recurrencePattern: Optional[str] = None

class ReminderCreate(ReminderBase):
    pass

class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    dueDate: Optional[datetime] = None
    priority: Optional[Priority] = None
    caseId: Optional[str] = None
    notifyBeforeDays: Optional[int] = None
    isCompleted: Optional[bool] = None
    isRecurring: Optional[bool] = None
    recurrencePattern: Optional[str] = None

class ReminderInDB(ReminderBase):
    id: str = Field(alias="_id")
    userId: str
    isCompleted: bool = False
    completedAt: Optional[datetime] = None
    notificationSent: bool = False
    notificationSentAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}

class ReminderResponse(ReminderBase):
    id: str = Field(alias="_id")
    userId: str
    isCompleted: bool
    completedAt: Optional[datetime] = None
    notificationSent: bool
    notificationSentAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True
        from_attributes = True
