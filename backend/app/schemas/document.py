from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="Document title")
    document_type: str = Field(..., min_length=1, max_length=100, description="Document category/type")
    content: Union[str, Dict[str, Any]] = Field(..., description="Document content as Markdown or structured JSON")
    status: Optional[str] = Field("draft", pattern="^(draft|completed|archived)$")

    @field_validator("title", "document_type")
    @classmethod
    def strip_and_validate(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Field cannot be empty or blank")
        return clean

class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    document_type: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[Union[str, Dict[str, Any]]] = None
    status: Optional[str] = Field(None, pattern="^(draft|completed|archived)$")

    @field_validator("title", "document_type")
    @classmethod
    def strip_if_present(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.strip()
            if not clean:
                raise ValueError("Field cannot be empty or blank")
            return clean
        return v

class DocumentInDB(BaseModel):
    id: str
    user_id: str
    title: str
    document_type: str
    content: Union[str, Dict[str, Any]]
    created_at: str
    updated_at: str
    status: str = "draft"

class DocumentListResponse(BaseModel):
    documents: List[DocumentInDB]
    total: int
    page: int
    limit: int
