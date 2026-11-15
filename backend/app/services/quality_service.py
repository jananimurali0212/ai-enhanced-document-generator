"""
Quality Evaluation Service module for AI-Enhanced Document Generator.
Provides multi-dimensional semantic and objective quality scoring across:
1. Grammar and spelling
2. Clarity and readability
3. Content relevance
4. Professional tone
5. Structure and organization
6. Completeness
7. Consistency
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class QualityService:
    """Intelligent document quality scoring and evaluation service."""

    def __init__(self):
        self.model_name = settings.GEMINI_MODEL

    def _calculate_objective_metrics(self, content: str) -> Dict[str, Any]:
        """Calculates linguistic and structural statistics from document text."""
        trimmed = content.strip()
        if not trimmed:
            return {
                "word_count": 0,
                "sentence_count": 0,
                "paragraph_count": 0,
                "heading_count": 0,
                "avg_sentence_len": 0,
                "has_headings": False,
                "has_lists": False,
                "has_tables": False,
                "readability_score": 0
            }

        words = re.findall(r"\b\w+\b", trimmed)
        word_count = len(words)

        sentences = [s for s in re.split(r"[.!?]+", trimmed) if s.strip()]
        sentence_count = max(1, len(sentences))
        avg_sentence_len = round(word_count / sentence_count, 1)

        paragraphs = [p for p in trimmed.split("\n\n") if p.strip()]
        paragraph_count = max(1, len(paragraphs))

        headings = [line for line in trimmed.split("\n") if line.strip().startswith("#")]
        heading_count = len(headings)

        has_lists = bool(re.search(r"^\s*[-*]\s+", trimmed, re.MULTILINE) or re.search(r"^\s*\d+\.\s+", trimmed, re.MULTILINE))
        has_tables = bool(re.search(r"^\|.+\|$", trimmed, re.MULTILINE))

        # Basic Flesch Reading Ease approximation
        # 206.835 - 1.015 * (total words / total sentences) - 84.6 * (total syllables / total words)
        # Approximate syllables by vowel sequences
        vowel_runs = len(re.findall(r"[aeiouy]+", trimmed.lower()))
        syllables_per_word = (vowel_runs / max(1, word_count))
        flesch_score = round(206.835 - (1.015 * avg_sentence_len) - (84.6 * syllables_per_word), 1)
        normalized_readability = max(20, min(100, int(flesch_score)))

        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "heading_count": heading_count,
            "avg_sentence_len": avg_sentence_len,
            "has_headings": heading_count > 0,
            "has_lists": has_lists,
            "has_tables": has_tables,
            "readability_score": normalized_readability
        }

    def _evaluate_heuristic_fallback(
        self,
        content: str,
        document_type: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provides consistent, explainable evaluation when AI is unavailable."""
        wc = metrics["word_count"]
        headings = metrics["heading_count"]
        has_lists = metrics["has_lists"]
        has_tables = metrics["has_tables"]
        avg_len = metrics["avg_sentence_len"]

        # Grammar & spelling score estimate (penalize extreme run-ons or repeated punctuation)
        grammar_score = 88
        if avg_len > 35:
            grammar_score -= 8
        if re.search(r"[!?,]{2,}", content):
            grammar_score -= 5
        grammar_score = max(55, min(95, grammar_score))

        # Clarity score based on readability & sentence length
        clarity_score = 85
        if 12 <= avg_len <= 24:
            clarity_score += 5
        elif avg_len > 30:
            clarity_score -= 10
        clarity_score = max(50, min(95, clarity_score))

        # Structure & Organization score
        structure_score = 70
        if headings >= 3:
            structure_score += 15
        elif headings >= 1:
            structure_score += 8
        if has_lists:
            structure_score += 5
        if has_tables:
            structure_score += 5
        structure_score = max(50, min(98, structure_score))

        # Professionalism score
        prof_score = 85
        casual_markers = len(re.findall(r"\b(gonna|wanna|cool|stuff|things|awesome|kinda)\b", content, re.IGNORECASE))
        if casual_markers > 0:
            prof_score -= min(25, casual_markers * 5)
        prof_score = max(55, min(95, prof_score))

        # Relevance & Completeness score
        completeness_score = 75
        if wc >= 600:
            completeness_score += 15
        elif wc >= 300:
            completeness_score += 8
        elif wc < 150:
            completeness_score -= 20
        completeness_score = max(45, min(95, completeness_score))

        relevance_score = 86

        # Overall weighted composite score
        overall = int(
            (grammar_score * 0.15) +
            (clarity_score * 0.20) +
            (relevance_score * 0.20) +
            (prof_score * 0.15) +
            (structure_score * 0.15) +
            (completeness_score * 0.15)
        )

        strengths = []
        if headings >= 2:
            strengths.append("Logical section breakdown with prominent hierarchical headings")
        if has_lists or has_tables:
            strengths.append("Effective use of formatted lists or tables for visual data scannability")
        if 14 <= avg_len <= 26:
            strengths.append("Balanced sentence pacing maintaining readability without run-ons")
        if wc >= 400:
            strengths.append("Substantive depth with sufficient technical elaboration")
        if not strengths:
            strengths.append("Direct presentation of primary subject matter")

        weaknesses = []
        if headings < 2:
            weaknesses.append("Document lacks sufficient heading structure (H2/H3) to delineate sections")
        if wc < 300:
            weaknesses.append("Content is relatively brief; key concepts could benefit from deeper elaboration")
        if avg_len > 28:
            weaknesses.append("Certain sentences are overly complex and could be segmented for clarity")
        if not has_tables and "report" in document_type.lower():
            weaknesses.append("No structured tabular data found to support technical claims")
        if not weaknesses:
            weaknesses.append("Fine-tune conclusion with immediate next steps and verification milestones")

        recommendations = [
            f"Review sections for {document_type.lower()} standard conventions",
            "Ensure concrete milestones and measurable success criteria are explicitly defined",
            "Verify all technical abbreviations are defined upon initial occurrence"
        ]
        if headings < 2:
            recommendations.insert(0, "Add numbered section headings (## 1. Executive Summary, ## 2. Architecture)")

        return {
            "overall_score": overall,
            "category_scores": {
                "grammar": grammar_score,
                "clarity": clarity_score,
                "relevance": relevance_score,
                "professionalism": prof_score,
                "structure": structure_score,
                "completeness": completeness_score
            },
            "strengths": strengths[:4],
            "weaknesses": weaknesses[:4],
            "recommendations": recommendations[:4],
            "metrics": metrics,
            "evaluation_engine": "heuristic_rubric"
        }

    def analyze_quality(
        self,
        content: str,
        document_type: str = "General Document",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates document quality using Gemini GenAI if available,
        with fallback to verified objective rubric.
        """
        trimmed = content.strip()
        if not trimmed:
            raise ValueError("Document content cannot be empty for quality analysis.")

        metrics = self._calculate_objective_metrics(trimmed)

        # Attempt Gemini semantic evaluation if client is configured
        if settings.is_gemini_configured:
            try:
                from google.genai import types

                prompt = f"""You are an elite editorial analyst and document quality auditor.
Evaluate the following document thoroughly and objectively.

Document Type: {document_type}
Document Context / Intent: {context or 'Standard evaluation'}
Document Word Count: {metrics['word_count']} words

--- DOCUMENT CONTENT ---
{trimmed[:15000]}
--- END CONTENT ---

Evaluate across these 6 core dimensions on a scale of 0 to 100:
1. grammar (spelling, syntax, punctuation)
2. clarity (readability, conciseness, flow)
3. relevance (focus on declared topic, elimination of fluff)
4. professionalism (tone, vocabulary, objectivity)
5. structure (headings, organization, scannability)
6. completeness (coverage of expected domain sections)

You MUST respond strictly with valid, parseable JSON matching this schema:
{{
  "overall_score": <integer 0-100>,
  "category_scores": {{
    "grammar": <integer 0-100>,
    "clarity": <integer 0-100>,
    "relevance": <integer 0-100>,
    "professionalism": <integer 0-100>,
    "structure": <integer 0-100>,
    "completeness": <integer 0-100>
  }},
  "strengths": [
    "<specific strength 1>",
    "<specific strength 2>"
  ],
  "weaknesses": [
    "<specific area needing improvement 1>",
    "<specific area needing improvement 2>"
  ],
  "recommendations": [
    "<concrete, actionable suggestion 1>",
    "<concrete, actionable suggestion 2>"
  ]
}}
Do NOT wrap your JSON in markdown code blocks or backticks. Return bare JSON only.
"""
                from app.services.ai_service import ai_service
                raw_response = ai_service._call_gemini_api(
                    prompt=prompt,
                    system_instruction="You are a professional document auditor. Always return raw JSON adhering strictly to the requested schema."
                )

                if raw_response:
                    cleaned_json = raw_response.strip()
                    if cleaned_json.startswith("```json"):
                        cleaned_json = cleaned_json[7:]
                    if cleaned_json.startswith("```"):
                        cleaned_json = cleaned_json[3:]
                    if cleaned_json.endswith("```"):
                        cleaned_json = cleaned_json[:-3]
                    cleaned_json = cleaned_json.strip()

                    parsed = json.loads(cleaned_json)
                    # Validate keys
                    if "overall_score" in parsed and "category_scores" in parsed:
                        parsed["metrics"] = metrics
                        parsed["evaluation_engine"] = "gemini_semantic_rubric"
                        return parsed
            except Exception as e:
                logger.warning(f"Gemini quality evaluation failed or returned unparseable JSON ({e}). Falling back to heuristic rubric.")

        # Heuristic fallback
        return self._evaluate_heuristic_fallback(trimmed, document_type, metrics)

quality_service = QualityService()
