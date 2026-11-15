"""
Document Completeness Analyzer module for AI-Enhanced Document Generator.
Compares document structure against type-specific blueprints to identify:
- Completed sections
- Incomplete sections (scaffolded or sparse)
- Missing required sections
- Actionable content recommendations
- Completeness percentage
"""

import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Canonical blueprints of expected sections per document type
EXPECTED_SECTIONS_REGISTRY: Dict[str, List[Dict[str, Any]]] = {
    "project documentation": [
        {"name": "Executive Summary & Overview", "keywords": ["summary", "overview", "introduction", "background"], "min_words": 15},
        {"name": "Problem Framing & Objectives", "keywords": ["problem", "objectives", "goals", "scope", "requirements"], "min_words": 15},
        {"name": "Architecture & Workflow", "keywords": ["architecture", "workflow", "design", "system", "infrastructure"], "min_words": 15},
        {"name": "Technical Implementation", "keywords": ["implementation", "specs", "components", "stack", "data flow"], "min_words": 15},
        {"name": "Verification & Testing", "keywords": ["testing", "verification", "validation", "benchmark", "quality"], "min_words": 15},
        {"name": "Action Matrix & Next Steps", "keywords": ["next steps", "action", "timeline", "matrix", "milestones"], "min_words": 12},
    ],
    "technical reports": [
        {"name": "Executive Summary", "keywords": ["executive summary", "abstract", "overview"], "min_words": 15},
        {"name": "Methodology & Framework", "keywords": ["methodology", "framework", "setup", "evaluation", "testbed"], "min_words": 15},
        {"name": "Empirical Findings & Data", "keywords": ["findings", "results", "data", "metrics", "benchmark", "latency"], "min_words": 15},
        {"name": "Technical Discussion", "keywords": ["discussion", "trade-offs", "analysis", "observations"], "min_words": 15},
        {"name": "Conclusion & Recommendations", "keywords": ["conclusion", "recommendations", "summary", "takeaways"], "min_words": 15},
    ],
    "business proposals": [
        {"name": "Executive Summary", "keywords": ["executive summary", "overview", "pitch"], "min_words": 15},
        {"name": "Problem Statement & Opportunity", "keywords": ["problem", "opportunity", "market", "need", "challenge"], "min_words": 15},
        {"name": "Proposed Solution & Scope", "keywords": ["solution", "proposed", "scope", "deliverables", "features"], "min_words": 15},
        {"name": "Budget, Pricing & ROI", "keywords": ["budget", "pricing", "cost", "roi", "investment", "commercials"], "min_words": 12},
        {"name": "Timeline & Roadmap", "keywords": ["timeline", "roadmap", "milestones", "schedule", "phases"], "min_words": 12},
        {"name": "Team & Credentials", "keywords": ["team", "credentials", "qualification", "experience", "governance"], "min_words": 12},
    ],
    "resumes": [
        {"name": "Contact Information", "keywords": ["contact", "email", "phone", "linkedin", "github", "portfolio"], "min_words": 8},
        {"name": "Professional Summary", "keywords": ["summary", "profile", "about", "objective"], "min_words": 15},
        {"name": "Core Technical Skills", "keywords": ["skills", "technologies", "competencies", "tools", "stack"], "min_words": 10},
        {"name": "Professional Experience", "keywords": ["experience", "employment", "history", "career", "work"], "min_words": 20},
        {"name": "Education & Certifications", "keywords": ["education", "degree", "university", "certifications", "licenses"], "min_words": 10},
        {"name": "Projects & Impact", "keywords": ["projects", "initiatives", "open source", "achievements"], "min_words": 15},
    ],
    "cover letters": [
        {"name": "Salutation & Opening Hook", "keywords": ["dear", "hiring", "team", "applying", "role", "position"], "min_words": 15},
        {"name": "Value Proposition & Experience", "keywords": ["experience", "background", "skills", "impact", "delivered"], "min_words": 20},
        {"name": "Company Alignment & Culture", "keywords": ["excited", "mission", "values", "culture", "why", "interest"], "min_words": 15},
        {"name": "Call to Action & Sign-off", "keywords": ["sincerely", "regards", "interview", "discuss", "thank you"], "min_words": 10},
    ],
    "meeting summaries": [
        {"name": "Context & Participants", "keywords": ["attendees", "participants", "context", "date", "purpose"], "min_words": 10},
        {"name": "Key Discussion Points", "keywords": ["discussion", "agenda", "topics", "review", "notes"], "min_words": 15},
        {"name": "Decisions Made", "keywords": ["decisions", "agreed", "consensus", "resolutions"], "min_words": 12},
        {"name": "Action Items & Owners", "keywords": ["action items", "owners", "tasks", "next steps", "deliverables"], "min_words": 12},
    ],
    "general": [
        {"name": "Introduction & Context", "keywords": ["introduction", "overview", "context", "background", "summary"], "min_words": 15},
        {"name": "Main Content & Analysis", "keywords": ["analysis", "body", "details", "findings", "discussion", "scope"], "min_words": 20},
        {"name": "Conclusion & Next Steps", "keywords": ["conclusion", "summary", "next steps", "recommendations", "outlook"], "min_words": 15},
    ]
}

class CompletenessService:
    """Evaluates document structural completeness based on category expectations."""

    def _match_category(self, document_type: str) -> str:
        """Normalizes document type to a canonical registry key."""
        clean = (document_type or "").strip().lower()
        for key in EXPECTED_SECTIONS_REGISTRY:
            if key in clean or clean in key:
                return key
        if "project" in clean or "doc" in clean:
            return "project documentation"
        if "report" in clean or "paper" in clean:
            return "technical reports"
        if "proposal" in clean or "pitch" in clean:
            return "business proposals"
        if "resume" in clean or "cv" in clean:
            return "resumes"
        if "cover" in clean or "letter" in clean:
            return "cover letters"
        if "meeting" in clean or "notes" in clean:
            return "meeting summaries"
        return "general"

    def _extract_document_sections(self, content: str) -> List[Dict[str, Any]]:
        """Parses headings and their associated content bodies from markdown text."""
        sections = []
        lines = content.split("\n")
        current_heading = "Document Header"
        current_lines: List[str] = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                # Clean markdown heading markers
                if current_lines or current_heading != "Document Header":
                    body_text = "\n".join(current_lines).strip()
                    words = len(re.findall(r"\b\w+\b", body_text))
                    sections.append({
                        "heading": current_heading,
                        "content": body_text,
                        "word_count": words
                    })
                current_heading = re.sub(r"^#+\s*", "", stripped)
                current_lines = []
            else:
                current_lines.append(line)

        # Append last section
        body_text = "\n".join(current_lines).strip()
        words = len(re.findall(r"\b\w+\b", body_text))
        sections.append({
            "heading": current_heading,
            "content": body_text,
            "word_count": words
        })

        return sections

    def analyze_completeness(
        self,
        content: str,
        document_type: str = "General Document"
    ) -> Dict[str, Any]:
        """
        Analyzes document structure against expected blueprints.
        Returns completed, incomplete, and missing sections with percentage score.
        """
        trimmed = content.strip()
        if not trimmed:
            raise ValueError("Document content cannot be empty for completeness analysis.")

        category_key = self._match_category(document_type)
        expected_sections = EXPECTED_SECTIONS_REGISTRY.get(category_key, EXPECTED_SECTIONS_REGISTRY["general"])
        parsed_sections = self._extract_document_sections(trimmed)

        completed_sections = []
        incomplete_sections = []
        missing_sections = []
        recommendations = []

        for expected in expected_sections:
            expected_name = expected["name"]
            keywords = expected["keywords"]
            min_words = expected["min_words"]

            # Search for matching section in parsed document
            matched_section = None
            for p_sec in parsed_sections:
                p_heading = p_sec["heading"].lower()
                p_content = p_sec["content"].lower()

                # Heading keyword match
                if any(kw in p_heading for kw in keywords):
                    matched_section = p_sec
                    break
                # Alternatively check first few lines of content
                if any(kw in p_content[:150] for kw in keywords):
                    matched_section = p_sec
                    break

            if matched_section:
                wc = matched_section["word_count"]
                has_structure = bool(re.search(r"^\s*[-*|]\s*", matched_section["content"], re.MULTILINE))
                threshold = max(6, min_words // 2) if has_structure else min_words
                if wc >= threshold:
                    completed_sections.append({
                        "name": expected_name,
                        "matched_heading": matched_section["heading"],
                        "word_count": wc,
                        "status": "completed"
                    })
                else:
                    incomplete_sections.append({
                        "name": expected_name,
                        "matched_heading": matched_section["heading"],
                        "word_count": wc,
                        "expected_min_words": min_words,
                        "status": "incomplete",
                        "suggestion": f"Elaborate on '{expected_name}' (currently {wc} words, expected {min_words}+ words)"
                    })
                    recommendations.append(f"Expand '{expected_name}' with deeper explanation and concrete details")
            else:
                missing_sections.append({
                    "name": expected_name,
                    "expected_min_words": min_words,
                    "status": "missing",
                    "suggestion": f"Add a dedicated '## {expected_name}' section"
                })
                recommendations.append(f"Add missing required section: '{expected_name}'")

        # Calculate completeness score
        total_expected = len(expected_sections)
        earned_points = (len(completed_sections) * 1.0) + (len(incomplete_sections) * 0.4)
        completeness_percentage = round((earned_points / max(1, total_expected)) * 100)
        completeness_percentage = max(0, min(100, completeness_percentage))

        # Additional structural observations
        total_doc_words = len(re.findall(r"\b\w+\b", trimmed))
        if total_doc_words < 250:
            recommendations.append("Overall document length is relatively short for this document type")

        return {
            "document_type": document_type,
            "detected_category": category_key.title(),
            "completeness_percentage": completeness_percentage,
            "total_expected_sections": total_expected,
            "completed_count": len(completed_sections),
            "incomplete_count": len(incomplete_sections),
            "missing_count": len(missing_sections),
            "completed_sections": completed_sections,
            "incomplete_sections": incomplete_sections,
            "missing_sections": missing_sections,
            "recommendations": recommendations[:5]
        }

completeness_service = CompletenessService()
