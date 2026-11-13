"""
AI Service module for AI-Enhanced Document Generator.
Handles communication with the Google Gemini API, response validation,
structured output parsing, and resilient error handling.
"""

import uuid
import re
import logging
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

from app.core.config import settings
from app.core.exceptions import (
    AIServiceException,
    AIConfigurationException,
    AIRateLimitException,
    AITimeoutException,
    AIGenerationException
)
from app.models.schemas import (
    GenerateDocumentRequest,
    RewriteRequest,
    SummarizeRequest,
    ExpandRequest,
    DocumentResponse,
    EditResponse
)
from app.services.prompt_builder import (
    build_system_instruction,
    build_generation_prompt,
    build_rewrite_prompt,
    build_summarize_prompt,
    build_expand_prompt
)
from app.services.mock_generator import generate_mock_document

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.model_name = settings.GEMINI_MODEL
        self._client = None
        self._init_client()

    def _init_client(self):
        """Initializes Google GenAI client if API key is present."""
        if settings.is_gemini_configured:
            try:
                from google import genai
                self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info(f"Gemini client successfully initialized with model {self.model_name}.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self._client = None
        else:
            self._client = None
            logger.warning("Gemini API key is not configured. Running in mock fallback mode.")

    def _strip_markdown_code_fences(self, text: str) -> str:
        """Removes enclosing ```markdown ... ``` wrapper if model wrapped entire response."""
        trimmed = text.strip()
        if trimmed.startswith("```markdown") and trimmed.endswith("```"):
            trimmed = trimmed[len("```markdown"): -3].strip()
        elif trimmed.startswith("```md") and trimmed.endswith("```"):
            trimmed = trimmed[len("```md"): -3].strip()
        elif trimmed.startswith("```") and trimmed.endswith("```"):
            trimmed = trimmed[3:-3].strip()
        return trimmed

    def _extract_title_and_clean(self, text: str, default_topic: str) -> Tuple[str, str]:
        """Extracts the first # heading as title if present, otherwise returns default topic."""
        cleaned = self._strip_markdown_code_fences(text)
        lines = cleaned.split("\n")
        title = default_topic
        for line in lines:
            line_str = line.strip()
            if line_str.startswith("# "):
                title = line_str.replace("# ", "").strip()
                break
        return title, cleaned

    def _call_gemini_api(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Executes a call to Gemini API with safety checks, error classification,
        and retry guidance.
        """
        if not settings.is_gemini_configured or self._client is None:
            # Re-check in case .env was modified at runtime
            self._init_client()

        if not settings.is_gemini_configured or self._client is None:
            if settings.ALLOW_MOCK_FALLBACK:
                return ""  # Trigger mock fallback
            raise AIConfigurationException()

        try:
            from google.genai import types
            from google.genai.errors import APIError

            sys_inst = system_instruction or build_system_instruction()
            config = types.GenerateContentConfig(
                system_instruction=sys_inst,
                temperature=settings.TEMPERATURE,
                max_output_tokens=settings.MAX_OUTPUT_TOKENS,
            )

            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )

            if not response or not response.text:
                raise AIGenerationException("Gemini returned an empty response. Please adjust your prompt.")

            return response.text

        except Exception as e:
            err_str = str(e).upper()
            logger.error(f"Gemini API invocation error: {e}")

            # Rate limit / Quota check
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "QUOTA" in err_str:
                raise AIRateLimitException(
                    message=f"Gemini API rate limit exceeded: {str(e)}"
                )

            # Timeout / Deadline check
            if "DEADLINE_EXCEEDED" in err_str or "TIMEOUT" in err_str or "504" in err_str:
                raise AITimeoutException(
                    message=f"Gemini API request timed out: {str(e)}"
                )

            # Network connection / DNS resolution check
            if "CONNECTERROR" in err_str or "GETADDRINFO" in err_str or "NETWORK" in err_str:
                logger.warning(f"Unable to reach Google Gemini API ({e}).")
                if settings.ALLOW_MOCK_FALLBACK:
                    logger.info("ALLOW_MOCK_FALLBACK is enabled; utilizing local fallback engine.")
                    return ""
                raise AITimeoutException(
                    message=f"Network error: Unable to reach Google Gemini API ({str(e)}).",
                    retry_guidance="Please verify your internet connection or check if outbound network access is permitted."
                )

            # Authentication / Invalid API key check
            if "401" in err_str or "403" in err_str or "API_KEY_INVALID" in err_str or "PERMISSION_DENIED" in err_str:
                raise AIConfigurationException(
                    message=f"Invalid or unauthorized Gemini API key: {str(e)}"
                )

            # Re-raise known AIServiceExceptions
            if isinstance(e, AIServiceException):
                raise e

            # General generation failure
            raise AIGenerationException(
                message=f"Gemini API generation error: {str(e)}"
            )

    # --------------------------------------------------------------------------
    # Document Generation
    # --------------------------------------------------------------------------
    def generate_document(self, req: GenerateDocumentRequest) -> DocumentResponse:
        """
        Generates a complete structured document using Gemini or fallback engine.
        Validates output and computes word counts.
        """
        # Validate inputs
        if not req.topic.strip() or not req.purpose.strip():
            raise AIGenerationException("Topic and purpose are mandatory for document generation.")

        prompt = build_generation_prompt(req)

        # Call Gemini
        raw_text = self._call_gemini_api(prompt)

        # Handle mock fallback if no API key configured
        if not raw_text:
            logger.info("Using mock generator fallback for document generation.")
            mock_res = generate_mock_document(req)
            return DocumentResponse(
                id=mock_res.id,
                title=mock_res.title,
                category=mock_res.category,
                tone=mock_res.tone,
                desired_length=mock_res.desired_length,
                content=mock_res.content,
                word_count=mock_res.word_count,
                created_at=mock_res.created_at,
                status="completed",
                model_used="local_mock_engine (Set GEMINI_API_KEY for live AI)",
                metadata={"mode": "mock_fallback", "grounded_references": req.reference_files}
            )

        title, content = self._extract_title_and_clean(raw_text, req.topic)
        words = len(content.split())
        doc_id = str(uuid.uuid4())[:8]
        now_str = datetime.now().strftime("%B %d, %Y - %I:%M %p")

        return DocumentResponse(
            id=doc_id,
            title=title,
            category=req.category or "General Document",
            tone=req.tone.value if hasattr(req.tone, "value") else str(req.tone),
            desired_length=req.desired_length.value if hasattr(req.desired_length, "value") else str(req.desired_length),
            content=content,
            word_count=words,
            created_at=now_str,
            status="completed",
            model_used=self.model_name,
            metadata={
                "template_id": req.template_id,
                "has_reference_files": len(req.reference_files or []) > 0,
                "has_reference_text": bool(req.reference_text)
            }
        )

    # --------------------------------------------------------------------------
    # AI Edit: Rewrite
    # --------------------------------------------------------------------------
    def rewrite_text(self, req: RewriteRequest) -> EditResponse:
        """Rewrites selected text or section based on user instructions and target tone."""
        if not req.content.strip():
            raise AIGenerationException("Content to rewrite cannot be empty.")

        prompt = build_rewrite_prompt(req)
        raw_text = self._call_gemini_api(prompt)

        # Fallback if no API key
        if not raw_text:
            revised = self._mock_rewrite(req)
            return EditResponse(
                original_text=req.content,
                revised_text=revised,
                action="rewrite",
                word_count=len(revised.split()),
                model_used="local_mock_engine",
                diff_summary="Rewritten with mock stylistic elevation."
            )

        revised = self._strip_markdown_code_fences(raw_text)
        orig_words = len(req.content.split())
        rev_words = len(revised.split())

        return EditResponse(
            original_text=req.content,
            revised_text=revised,
            action="rewrite",
            word_count=rev_words,
            model_used=self.model_name,
            diff_summary=f"Rewritten from {orig_words} words to {rev_words} words."
        )

    # --------------------------------------------------------------------------
    # AI Edit: Summarize
    # --------------------------------------------------------------------------
    def summarize_text(self, req: SummarizeRequest) -> EditResponse:
        """Summarizes supplied content into bullet points, executive brief, or concise abstract."""
        if not req.content.strip():
            raise AIGenerationException("Content to summarize cannot be empty.")

        prompt = build_summarize_prompt(req)
        raw_text = self._call_gemini_api(prompt)

        if not raw_text:
            revised = self._mock_summarize(req)
            return EditResponse(
                original_text=req.content,
                revised_text=revised,
                action="summarize",
                word_count=len(revised.split()),
                model_used="local_mock_engine",
                diff_summary="Summarized via local mock engine."
            )

        revised = self._strip_markdown_code_fences(raw_text)
        orig_words = len(req.content.split())
        rev_words = len(revised.split())
        compression = round((1 - (rev_words / max(orig_words, 1))) * 100, 1)

        return EditResponse(
            original_text=req.content,
            revised_text=revised,
            action="summarize",
            word_count=rev_words,
            model_used=self.model_name,
            diff_summary=f"Synthesized {orig_words} words down to {rev_words} words ({compression}% reduction)."
        )

    # --------------------------------------------------------------------------
    # AI Edit: Expand
    # --------------------------------------------------------------------------
    def expand_text(self, req: ExpandRequest) -> EditResponse:
        """Expands a section with relevant detail, concrete examples, and technical depth."""
        if not req.content.strip():
            raise AIGenerationException("Content to expand cannot be empty.")

        prompt = build_expand_prompt(req)
        raw_text = self._call_gemini_api(prompt)

        if not raw_text:
            revised = self._mock_expand(req)
            return EditResponse(
                original_text=req.content,
                revised_text=revised,
                action="expand",
                word_count=len(revised.split()),
                model_used="local_mock_engine",
                diff_summary="Expanded section with local mock engine."
            )

        revised = self._strip_markdown_code_fences(raw_text)
        orig_words = len(req.content.split())
        rev_words = len(revised.split())

        return EditResponse(
            original_text=req.content,
            revised_text=revised,
            action="expand",
            word_count=rev_words,
            model_used=self.model_name,
            diff_summary=f"Expanded from {orig_words} words to {rev_words} words (+{rev_words - orig_words} words)."
        )

    # --------------------------------------------------------------------------
    # Mock Helpers (Used when GEMINI_API_KEY is not set)
    # --------------------------------------------------------------------------
    def _mock_rewrite(self, req: RewriteRequest) -> str:
        text = req.content.strip()
        tone_str = req.tone.value if req.tone else "Professional"
        return (
            f"> **AI Rewrite ({tone_str} Tone):** {req.instruction}\n\n"
            f"{text}\n\n"
            f"- Clarified core assertions and eliminated colloquial syntax.\n"
            f"- Structured supporting argumentation for maximum readability."
        )

    def _mock_summarize(self, req: SummarizeRequest) -> str:
        lines = [line.strip() for line in req.content.split("\n") if line.strip() and not line.startswith("#")]
        key_lines = lines[:4] if len(lines) >= 4 else lines
        bullet_points = "\n".join([f"- **Key Takeaway:** {line[:120]}..." for line in key_lines])
        return f"### Executive Summary\n\n{bullet_points}\n\n> **Action Item:** Review outlined points with primary stakeholders."

    def _mock_expand(self, req: ExpandRequest) -> str:
        text = req.content.strip()
        focus = ", ".join(req.focus_areas) if req.focus_areas else "operational scalability and edge cases"
        return (
            f"{text}\n\n"
            f"### In-Depth Elaboration & Implementation Details\n"
            f"To operationalize this section with rigorous focus on **{focus}**, consider the following factors:\n\n"
            f"1. **Architectural Feasibility & Edge Scenarios:** Ensure component decoupling under high-concurrency loads.\n"
            f"2. **Risk Mitigation Strategy:** Establish proactive observability, anomaly detection thresholds, and automated rollbacks.\n"
            f"3. **Concrete Deliverable Schedule:** Quantify milestones with definitive deliverables and assigned owners."
        )

# Global singleton service
ai_service = AIService()

