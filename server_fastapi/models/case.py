from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class CaseType(str, Enum):
    Civil = "Civil"
    Criminal = "Criminal"
    Family = "Family"
    Corporate = "Corporate"
    Property = "Property"
    Contract = "Contract"
    Employment = "Employment"
    IntellectualProperty = "Intellectual Property"
    Other = "Other"

class CaseStatus(str, Enum):
    Active = "Active"
    Pending = "Pending"
    Closed = "Closed"
    Archived = "Archived"

class PredictedOutcome(BaseModel):
    confidence: Optional[float] = Field(None, ge=0, le=100)
    predictedStatus: Optional[str] = None
    reasoning: Optional[str] = None

class KeyDetails(BaseModel):
    obligations: List[str] = []
    deadlines: List[str] = []
    involvedParties: List[str] = []

class CaseBase(BaseModel):
    title: str
    caseType: CaseType = CaseType.Civil
    description: Optional[str] = None
    status: CaseStatus = CaseStatus.Active
    filingDate: Optional[datetime] = None
    hearingDate: Optional[datetime] = None
    deadline: Optional[datetime] = None
    plaintiff: Optional[str] = None
    defendant: Optional[str] = None
    tags: List[str] = []
    notes: Optional[str] = None

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    caseType: Optional[CaseType] = None
    description: Optional[str] = None
    status: Optional[CaseStatus] = None
    filingDate: Optional[datetime] = None
    hearingDate: Optional[datetime] = None
    deadline: Optional[datetime] = None
    plaintiff: Optional[str] = None
    defendant: Optional[str] = None
    predictedOutcome: Optional[PredictedOutcome] = None
    keyDetails: Optional[KeyDetails] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class CaseInDB(CaseBase):
    id: str = Field(alias="_id")
    userId: str
    predictedOutcome: Optional[PredictedOutcome] = None
    keyDetails: KeyDetails = Field(default_factory=KeyDetails)
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}

class CaseResponse(CaseBase):
    id: str = Field(alias="_id")
    userId: str
    predictedOutcome: Optional[PredictedOutcome] = None
    keyDetails: KeyDetails
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True
        from_attributes = True
