from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
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
    RESEARCH_REPORT = "Research reports"
    BUSINESS_PROPOSAL = "Business proposals"
    RESUME = "Resumes"
    COVER_LETTER = "Cover letters"
    MEETING_SUMMARY = "Meeting summaries"
    ACADEMIC_ASSIGNMENT = "Academic assignments"
    GENERAL = "General Document"

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
    template_id: Optional[str] = Field("custom", description="Template identifier or 'custom'")
    category: Optional[str] = Field("Project documentation", description="Document category")
    topic: str = Field(..., min_length=2, max_length=500, description="The subject or title of the document")
    purpose: str = Field(..., min_length=5, max_length=2500, description="Primary goal or objective of this document")
    intended_audience: str = Field(..., min_length=3, max_length=500, description="Who will be reading this document")
    tone: ToneOption = Field(default=ToneOption.PROFESSIONAL, description="Desired communication tone")
    desired_length: LengthOption = Field(default=LengthOption.STANDARD, description="Target document word count")
    additional_instructions: Optional[str] = Field("", max_length=3000, description="Additional custom instructions")
    reference_files: Optional[List[str]] = Field(default_factory=list, description="Names of uploaded reference files")
    reference_text: Optional[str] = Field(None, max_length=50000, description="Extracted or provided reference text for grounding")

    @field_validator("topic", "purpose", "intended_audience")
    @classmethod
    def strip_and_validate_non_empty(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Field cannot be empty or solely whitespace")
        return clean

class RewriteRequest(BaseModel):
    content: str = Field(..., min_length=3, max_length=25000, description="The text or section to rewrite")
    instruction: Optional[str] = Field(
        "Improve clarity, tone, and professional flow while preserving core meaning",
        max_length=1500,
        description="Specific instructions for rewriting"
    )
    tone: Optional[ToneOption] = Field(None, description="Target tone for the rewritten text")
    target_length: Optional[str] = Field(None, description="Optional length guidance (e.g., 'concise', 'detailed')")
    context: Optional[str] = Field(None, max_length=5000, description="Surrounding document context or topic")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Content to rewrite cannot be empty")
        return clean

class SummarizeRequest(BaseModel):
    content: str = Field(..., min_length=10, max_length=50000, description="Content to summarize")
    format: Optional[str] = Field(
        "bullet_points",
        description="Summary format: 'bullet_points', 'executive', or 'concise'"
    )
    target_length: Optional[str] = Field(None, description="Desired summary length guidance")
    context: Optional[str] = Field(None, max_length=5000, description="Optional document context")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Content to summarize cannot be empty")
        return clean

class ExpandRequest(BaseModel):
    content: str = Field(..., min_length=3, max_length=25000, description="Content or section to expand")
    instruction: Optional[str] = Field(
        "Expand this section with relevant technical detail, concrete examples, and thorough explanation",
        max_length=1500,
        description="Specific expansion instructions"
    )
    focus_areas: Optional[List[str]] = Field(default_factory=list, description="Specific topics or points to elaborate on")
    tone: Optional[ToneOption] = Field(None, description="Target tone for the expanded content")
    context: Optional[str] = Field(None, max_length=5000, description="Surrounding document context")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Content to expand cannot be empty")
        return clean

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
    model_used: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class EditResponse(BaseModel):
    original_text: str
    revised_text: str
    action: str
    word_count: int
    model_used: Optional[str] = None
    diff_summary: Optional[str] = None

class UploadResponse(BaseModel):
    filename: str
    size_bytes: int
    content_type: str
    status: str
    uploaded_at: str

class ErrorResponse(BaseModel):
    detail: str
    error_type: str
    retry_guidance: Optional[str] = None

# Day 3 Persistence & Export Schemas (re-exported for convenience)
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentInDB, DocumentListResponse
from app.schemas.export import ExportRequest

# Day 4 Quality, Completeness & Comparison Schemas
from app.schemas.quality import (
    QualityAnalyzeRequest,
    QualityAnalyzeResponse,
    QualityCategoryScores,
    CompletenessRequest,
    CompletenessResponse,
    ImproveRequest,
    ImproveResponse,
    CompareRequest,
    CompareResponse
)

