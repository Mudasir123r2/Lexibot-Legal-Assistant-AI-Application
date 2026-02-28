from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"

class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class QueryType(str, Enum):
    general = "general"
    case_analysis = "case_analysis"
    judgment_search = "judgment_search"
    summarization = "summarization"
    guidance = "guidance"

class ChatContext(BaseModel):
    queryType: QueryType = QueryType.general
    relatedJudgmentId: Optional[str] = None
    relatedCaseId: Optional[str] = None

class ChatStatus(str, Enum):
    active = "active"
    completed = "completed"

class ChatLogBase(BaseModel):
    caseId: Optional[str] = None
    sessionId: Optional[str] = None

class ChatLogCreate(ChatLogBase):
    messages: List[Message] = []
    context: Optional[ChatContext] = None

class ChatLogUpdate(BaseModel):
    messages: Optional[List[Message]] = None
    context: Optional[ChatContext] = None
    status: Optional[ChatStatus] = None

class ChatLogInDB(ChatLogBase):
    id: str = Field(alias="_id")
    userId: str
    messages: List[Message] = []
    context: ChatContext = Field(default_factory=ChatContext)
    status: ChatStatus = ChatStatus.active
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}

class ChatLogResponse(ChatLogBase):
    id: str = Field(alias="_id")
    userId: str
    messages: List[Message]
    context: ChatContext
    status: ChatStatus
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    caseId: Optional[str] = None
    sessionId: Optional[str] = None
    context: Optional[ChatContext] = None

class ChatResponse(BaseModel):
    response: str
    sessionId: str
    chatLogId: str
