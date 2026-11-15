"""
Pydantic Schemas for Day 4 Quality Assessment, Completeness Analysis,
Intelligent Improvement, and Document Comparison.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator

class QualityAnalyzeRequest(BaseModel):
    document_id: Optional[str] = Field(None, description="Optional ID of saved document to evaluate")
    content: Optional[str] = Field(None, max_length=100000, description="Raw document text if evaluating unsaved draft")
    document_type: Optional[str] = Field("General Document", description="Category or document type for rubric calibration")
    context: Optional[str] = Field(None, max_length=5000, description="Optional intent or context of the document")

class QualityCategoryScores(BaseModel):
    grammar: int = Field(..., ge=0, le=100)
    clarity: int = Field(..., ge=0, le=100)
    relevance: int = Field(..., ge=0, le=100)
    professionalism: int = Field(..., ge=0, le=100)
    structure: int = Field(..., ge=0, le=100)
    completeness: int = Field(..., ge=0, le=100)

class QualityAnalyzeResponse(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    category_scores: QualityCategoryScores
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    metrics: Optional[Dict[str, Any]] = None
    evaluation_engine: str = "heuristic_rubric"

# ----------------------------------------------------------------------
# Completeness Analysis Schemas
# ----------------------------------------------------------------------

class CompletenessRequest(BaseModel):
    document_id: Optional[str] = Field(None, description="Optional ID of saved document to analyze")
    content: Optional[str] = Field(None, max_length=100000, description="Document content to analyze")
    document_type: Optional[str] = Field("General Document", description="Document type for section expectations")

class CompletenessResponse(BaseModel):
    document_type: str
    detected_category: str
    completeness_percentage: int = Field(..., ge=0, le=100)
    total_expected_sections: int
    completed_count: int
    incomplete_count: int
    missing_count: int
    completed_sections: List[Dict[str, Any]]
    incomplete_sections: List[Dict[str, Any]]
    missing_sections: List[Dict[str, Any]]
    recommendations: List[str]

# ----------------------------------------------------------------------
# Improvement Schemas
# ----------------------------------------------------------------------

class ImproveRequest(BaseModel):
    document_id: Optional[str] = Field(None, description="Optional ID of saved document")
    content: Optional[str] = Field(None, max_length=50000, description="Text or section to improve")
    operation: str = Field(
        "improve_writing",
        description="Operation: improve_grammar, improve_professionalism, simplify_language, expand_explanations, shorten_content, improve_readability, improve_structure, rewrite_paragraph"
    )
    instruction: Optional[str] = Field(None, max_length=2000, description="Custom instruction override")
    context: Optional[str] = Field(None, max_length=5000, description="Surrounding document context or topic")

class ImproveResponse(BaseModel):
    original_text: str
    revised_text: str
    operation: str
    directive: str
    diff_summary: str
    model_used: str
    word_count: int

# ----------------------------------------------------------------------
# Comparison Schemas
# ----------------------------------------------------------------------

class CompareRequest(BaseModel):
    document_id_1: Optional[str] = Field(None, description="Optional ID of baseline document")
    document_id_2: Optional[str] = Field(None, description="Optional ID of comparison document")
    original_text: Optional[str] = Field(None, max_length=100000, description="Baseline / original text")
    revised_text: Optional[str] = Field(None, max_length=100000, description="Updated / revised text")
    title: Optional[str] = Field(None, description="Comparison label or title")

class CompareResponse(BaseModel):
    title: str
    summary: str
    similarity_percentage: float
    total_changes: int
    added: List[str]
    removed: List[str]
    modified: List[Dict[str, str]]
    unchanged_line_count: int
    diff_blocks: List[Dict[str, Any]]
    original_word_count: int
    revised_word_count: int
