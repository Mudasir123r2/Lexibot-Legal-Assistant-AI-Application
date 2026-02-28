from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Party(BaseModel):
    name: str
    role: str

class KeyInformation(BaseModel):
    parties: List[Party] = []
    issues: List[str] = []
    decisions: List[str] = []
    deadlines: List[str] = []
    obligations: List[str] = []

class JudgmentBase(BaseModel):
    caseNumber: str
    title: str
    court: str
    judge: Optional[str] = None
    dateOfJudgment: datetime
    fullText: str
    summary: Optional[str] = None
    caseType: Optional[str] = None
    keywords: List[str] = []
    citations: List[str] = []
    jurisdiction: Optional[str] = None
    year: Optional[int] = None
    tags: List[str] = []

class JudgmentCreate(JudgmentBase):
    keyInformation: Optional[KeyInformation] = None

class JudgmentUpdate(BaseModel):
    title: Optional[str] = None
    court: Optional[str] = None
    judge: Optional[str] = None
    dateOfJudgment: Optional[datetime] = None
    fullText: Optional[str] = None
    summary: Optional[str] = None
    keyInformation: Optional[KeyInformation] = None
    caseType: Optional[str] = None
    keywords: Optional[List[str]] = None
    citations: Optional[List[str]] = None
    jurisdiction: Optional[str] = None
    year: Optional[int] = None
    tags: Optional[List[str]] = None

class JudgmentInDB(JudgmentBase):
    id: str = Field(alias="_id")
    keyInformation: KeyInformation = Field(default_factory=KeyInformation)
    referencedCases: List[str] = []
    embedding: Optional[List[float]] = None
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}

class JudgmentResponse(JudgmentBase):
    id: str = Field(alias="_id")
    keyInformation: KeyInformation
    referencedCases: List[str] = []
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True
        from_attributes = True

class JudgmentSearchRequest(BaseModel):
    query: Optional[str] = None
    caseType: Optional[str] = None
    court: Optional[str] = None
    yearFrom: Optional[int] = None
    yearTo: Optional[int] = None
    keywords: Optional[List[str]] = None
    limit: int = 20
    skip: int = 0
