"""
Document Comparison Engine for AI-Enhanced Document Generator.
Computes mathematical text similarity, generates structured diffs
(added, removed, modified, unchanged blocks), and provides an AI-synthesized
summary of semantic improvements.
"""

import difflib
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class ComparisonService:
    """Calculates algorithmic diffs and AI change explanations between document versions."""

    def __init__(self):
        self.model_name = settings.GEMINI_MODEL

    def _generate_algorithmic_diff(self, original: str, revised: str) -> Dict[str, Any]:
        """Calculates exact line-by-line diff and similarity using difflib."""
        orig_lines = original.splitlines()
        rev_lines = revised.splitlines()

        matcher = difflib.SequenceMatcher(None, orig_lines, rev_lines)
        similarity = round(matcher.ratio() * 100, 1)

        added: List[str] = []
        removed: List[str] = []
        modified: List[Dict[str, str]] = []
        unchanged: List[str] = []
        diff_blocks: List[Dict[str, Any]] = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            orig_slice = orig_lines[i1:i2]
            rev_slice = rev_lines[j1:j2]

            if tag == "equal":
                unchanged.extend(orig_slice)
                for line in orig_slice:
                    diff_blocks.append({"type": "unchanged", "text": line})
            elif tag == "replace":
                for old_line, new_line in zip(orig_slice, rev_slice):
                    modified.append({"original": old_line, "revised": new_line})
                    diff_blocks.append({"type": "removed", "text": old_line})
                    diff_blocks.append({"type": "added", "text": new_line})
                # Handle leftover lines if one slice is longer
                if len(orig_slice) > len(rev_slice):
                    for extra_old in orig_slice[len(rev_slice):]:
                        removed.append(extra_old)
                        diff_blocks.append({"type": "removed", "text": extra_old})
                elif len(rev_slice) > len(orig_slice):
                    for extra_new in rev_slice[len(orig_slice):]:
                        added.append(extra_new)
                        diff_blocks.append({"type": "added", "text": extra_new})
            elif tag == "delete":
                removed.extend(orig_slice)
                for line in orig_slice:
                    diff_blocks.append({"type": "removed", "text": line})
            elif tag == "insert":
                added.extend(rev_slice)
                for line in rev_slice:
                    diff_blocks.append({"type": "added", "text": line})

        total_changes = len(added) + len(removed) + len(modified)

        return {
            "similarity_percentage": similarity,
            "total_changes": total_changes,
            "added": added,
            "removed": removed,
            "modified": modified,
            "unchanged_line_count": len(unchanged),
            "diff_blocks": diff_blocks
        }

    def _generate_ai_summary(self, original: str, revised: str, diff_data: Dict[str, Any]) -> str:
        """Uses Gemini to explain the key improvements and changes succinctly."""
        if settings.is_gemini_configured:
            try:
                from app.services.ai_service import ai_service
                prompt = f"""You are an executive editor reviewing two versions of a document.
Provide a concise 2-3 sentence summary explaining the key improvements, stylistic shifts, or content updates made between the original and revised text.

Similarity: {diff_data['similarity_percentage']}%
Lines Added: {len(diff_data['added'])}
Lines Removed: {len(diff_data['removed'])}
Lines Modified: {len(diff_data['modified'])}

ORIGINAL SAMPLE (first 1,500 chars):
{original[:1500]}

REVISED SAMPLE (first 1,500 chars):
{revised[:1500]}

Write a concise, professional summary highlighting what was improved. Do NOT use bullet points or markdown headings. Return 2-3 clear sentences only.
"""
                response = ai_service._call_gemini_api(
                    prompt=prompt,
                    system_instruction="You are a concise, objective document editor."
                )
                if response and response.strip():
                    return response.strip()
            except Exception as e:
                logger.warning(f"Gemini comparison summary failed ({e}). Using heuristic summary.")

        # Heuristic fallback summary
        sim = diff_data["similarity_percentage"]
        added_count = len(diff_data["added"])
        removed_count = len(diff_data["removed"])
        modified_count = len(diff_data["modified"])

        if sim == 100.0:
            return "Both document versions are identical with no textual or formatting discrepancies."
        elif sim > 85.0:
            return f"The revised document preserves {sim}% of the original text while introducing targeted refinements ({modified_count} modified lines, {added_count} additions) to polish phrasing and clarity."
        elif sim > 60.0:
            return f"The revised version incorporates substantive restructuring ({sim}% similarity), expanding key sections with {added_count} new lines and refining {modified_count} passages for improved impact."
        else:
            return f"The document underwent extensive revision ({sim}% similarity), replacing {removed_count} lines with {added_count} newly authored sections to elevate depth and structure."

    def compare_documents(
        self,
        original: str,
        revised: str,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates exact diff and similarity between two documents
        and generates an AI-powered summary of changes.
        """
        orig_clean = (original or "").strip()
        rev_clean = (revised or "").strip()

        if not orig_clean and not rev_clean:
            raise ValueError("Both original and revised text are empty.")

        diff_data = self._generate_algorithmic_diff(orig_clean, rev_clean)
        summary = self._generate_ai_summary(orig_clean, rev_clean, diff_data)

        diff_data["summary"] = summary
        diff_data["title"] = title or "Document Comparison"
        diff_data["original_word_count"] = len(orig_clean.split())
        diff_data["revised_word_count"] = len(rev_clean.split())

        return diff_data

comparison_service = ComparisonService()
