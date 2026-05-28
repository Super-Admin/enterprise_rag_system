from datetime import datetime
from pydantic import BaseModel


class KBCreate(BaseModel):
    name: str
    description: str = ""
    embedding_model: str = "bge-small"


class KBResponse(BaseModel):
    id: int
    name: str
    description: str
    embedding_model: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: int
    kb_id: int
    filename: str
    file_size: int
    status: str
    error_message: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
