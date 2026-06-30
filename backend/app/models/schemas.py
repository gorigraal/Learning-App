from pydantic import BaseModel, Field
from typing import Literal, Optional


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Intrebarea elevului")
    subject: str = Field(..., description="Materia / aria de invatare (ex: Matematica)")
    history: list[ChatMessage] = Field(default_factory=list)
    user_id: Optional[str] = Field(None, description="ID-ul userului (optional, pentru a include materialele personale)")


class ChatResponse(BaseModel):
    response: str
    sources_used: int


class MaterialUploadResponse(BaseModel):
    material_id: str
    filename: str
    chunks_created: int
    subject: str
    user_id: Optional[str] = None
