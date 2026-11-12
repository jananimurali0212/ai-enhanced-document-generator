from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ToneOption(str, Enum):
    PROFESSIONAL = "Professional"
    TECHNICAL = "Technical"
    PERSUASIVE = "Persuasive"
    CASUAL = "Casual"
    EXECUTIVE = "Executive"
    ACADEMIC = "Academic"

class LengthOption(str, Enum):
    CONCISE = "Concise (~300-500 words)"
    STANDARD = "Standard (~800-1,200 words)"
    IN_DEPTH = "In-depth (~1,500-2,500 words)"

class DocumentCategory(str, Enum):
    PROJECT_DOC = "Project documentation"
    TECHNICAL_REPORT = "Technical reports"
    BUSINESS_PROPOSAL = "Business proposals"
    RESUME = "Resumes"
    COVER_LETTER = "Cover letters"
    MEETING_SUMMARY = "Meeting summaries"

class Template(BaseModel):
    id: str
    name: str
    category: DocumentCategory
    description: str
    icon: str
    default_tone: ToneOption
    default_length: LengthOption
    placeholder_topic: str
    placeholder_purpose: str
    placeholder_audience: str

class GenerateDocumentRequest(BaseModel):
    template_id: Optional[str] = "custom"
    category: Optional[str] = "Project documentation"
    topic: str = Field(..., min_length=2, description="The subject or title of the document")
    purpose: str = Field(..., min_length=5, description="Primary goal or objective of this document")
    intended_audience: str = Field(..., min_length=3, description="Who will be reading this document")
    tone: ToneOption = ToneOption.PROFESSIONAL
    desired_length: LengthOption = LengthOption.STANDARD
    additional_instructions: Optional[str] = ""
    reference_files: Optional[List[str]] = Field(default_factory=list)

class DocumentResponse(BaseModel):
    id: str
    title: str
    category: str
    tone: str
    desired_length: str
    content: str
    word_count: int
    created_at: str
    status: str = "completed"

class UploadResponse(BaseModel):
    filename: str
    size_bytes: int
    content_type: str
    status: str
    uploaded_at: str
