"""
Prompt Builder Service for AI-Enhanced Document Generator.
Constructs task-specific prompts for document generation, rewriting,
summarization, and expansion with strict grounding and formatting rules.
"""

from typing import Dict, List, Optional
from app.models.schemas import (
    GenerateDocumentRequest,
    RewriteRequest,
    SummarizeRequest,
    ExpandRequest,
    ToneOption,
    LengthOption
)

CATEGORY_SECTIONS: Dict[str, List[str]] = {
    "Project documentation": [
        "1. Executive Summary & Problem Framing",
        "2. Architecture Overview & High-Level System Design",
        "3. Component Breakdown & Module Interfaces (APIs & Data Models)",
        "4. Non-Functional Requirements (Security, Scalability, High Availability)",
        "5. Deployment Strategy & Observability",
        "6. Implementation Milestones & Verification Checklist"
    ],
    "Technical reports": [
        "1. Executive Summary & Abstract",
        "2. Problem Statement & Scope of Investigation",
        "3. Methodology & Technical Evaluation Framework",
        "4. Benchmark Analysis & Comparative Findings",
        "5. Architectural Trade-offs, Failure Modes & Edge Cases",
        "6. Strategic Recommendations & Action Plan"
    ],
    "Research reports": [
        "1. Abstract & Executive Summary",
        "2. Research Objectives, Hypotheses & Background",
        "3. Literature Review & Conceptual Framework",
        "4. Methodology, Data Gathering & Analysis",
        "5. Findings, Empirical Discussion & Implications",
        "6. Limitations, Future Directions & Conclusion"
    ],
    "Business proposals": [
        "1. Executive Summary & Opportunity Overview",
        "2. Client Pain Points & Market Context",
        "3. Proposed Solution Architecture & Deliverables",
        "4. Value Proposition, ROI Projections & Measurable Impact",
        "5. Implementation Schedule, Phases & Key Milestones",
        "6. Investment Budget Breakdown & Governance",
        "7. Call to Action & Mutual Next Steps"
    ],
    "Resumes": [
        "1. Candidate Header & Professional Title",
        "2. Executive Summary / Value Proposition",
        "3. Core Competencies & Technical Skills Matrix",
        "4. Professional Experience (Chronological, with quantifiable achievements)",
        "5. Key Projects, Architecture Accomplishments & Patents",
        "6. Education, Certifications & Continuous Learning"
    ],
    "Cover letters": [
        "1. Professional Header & Formal Salutation",
        "2. Compelling Hook & Target Role Declaration",
        "3. High-Impact Career Accomplishments aligned with Role Requirements",
        "4. Company Mission Alignment & Cultural Value Add",
        "5. Reiteration of Value & Professional Call to Action",
        "6. Formal Sign-off"
    ],
    "Meeting summaries": [
        "1. Meeting Header (Topic, Date, Purpose, Attendees & Key Roles)",
        "2. Executive Brief & High-Level Outcomes",
        "3. Key Discussion Points & Debate Highlights",
        "4. Decisions Made & Formal Consensus",
        "5. Action Items & Accountability Matrix (Task, Owner, Deadline, Priority)",
        "6. Next Steps & Follow-up Schedule"
    ],
    "Academic assignments": [
        "1. Title, Academic Context & Thesis Statement",
        "2. Background, Contextual Setting & Key Concepts",
        "3. Core Thematic Arguments & Evidence Evaluation",
        "4. Critical Analysis, Counterarguments & Rebuttal",
        "5. Synthesis, Implications & Scholarly Conclusion",
        "6. Academic References (Grounding sources only)"
    ],
    "General Document": [
        "1. Executive Summary & Objectives",
        "2. Context, Scope & Key Challenges",
        "3. Detailed Strategic Framework & Core Findings",
        "4. Operational Guidelines & Best Practices",
        "5. Summary, Recommendations & Next Steps"
    ]
}

LENGTH_GUIDANCE: Dict[str, str] = {
    "Concise (~300-500 words)": "Strictly concise: target approximately 350-500 words. High-density, laser-focused, zero redundant filler.",
    "Standard (~800-1,200 words)": "Standard professional length: target approximately 800-1,200 words. Comprehensive and well-structured with actionable depth.",
    "In-depth (~1,500-2,500 words)": "In-depth comprehensive dossier: target approximately 1,500-2,500 words. Deep technical exposition, exhaustive scenarios, and detailed breakdowns."
}

def build_system_instruction() -> str:
    """Returns the core system persona and formatting rules for Gemini."""
    return (
        "You are an expert full-stack AI document architect and enterprise technical writer. "
        "Your mission is to generate publication-grade, professionally structured documents "
        "that strictly adhere to user-specified document types, audience, tone, and length.\n\n"
        "STRICT GROUNDING & INTEGRITY CONSTRAINTS:\n"
        "1. Distinguish between grounded facts from reference materials and plausible assumptions. "
        "Explicitly flag assumptions with '[Assumption]' when necessary.\n"
        "2. DO NOT hallucinate fake citations, non-existent URLs, fake studies, or fabricated statistics.\n"
        "3. If reference materials or text are provided, you MUST ground your output in those materials.\n"
        "4. Format the output in rich, clean GitHub Flavored Markdown (H1 '# ', H2 '## ', H3 '### ', "
        "bullet lists, structured markdown tables, bolding, blockquotes '> ', and checklists '- [ ]').\n"
        "5. Maintain absolute professional consistency with the requested tone and target length."
    )

def build_generation_prompt(req: GenerateDocumentRequest) -> str:
    """
    Constructs a detailed, task-specific prompt for document generation.
    Incorporates document type, objectives, audience, tone, length,
    required sections, and reference text constraints.
    """
    category = req.category or "General Document"
    sections = CATEGORY_SECTIONS.get(category, CATEGORY_SECTIONS["General Document"])
    length_note = LENGTH_GUIDANCE.get(
        req.desired_length.value if hasattr(req.desired_length, "value") else str(req.desired_length),
        "Target approximately 800-1,200 words."
    )
    tone_val = req.tone.value if hasattr(req.tone, "value") else str(req.tone)

    prompt_parts: List[str] = []

    prompt_parts.append(f"# TASK: Generate a Complete, Structured '{category}' Document\n")
    prompt_parts.append("## DOCUMENT SPECIFICATIONS")
    prompt_parts.append(f"- **Document Type / Category:** {category}")
    prompt_parts.append(f"- **Document Topic / Title:** {req.topic}")
    prompt_parts.append(f"- **Primary Purpose / Objective:** {req.purpose}")
    prompt_parts.append(f"- **Intended Audience:** {req.intended_audience}")
    prompt_parts.append(f"- **Communication Tone:** {tone_val}")
    prompt_parts.append(f"- **Length & Scope Guideline:** {length_note}")

    if req.additional_instructions and req.additional_instructions.strip():
        prompt_parts.append(f"- **Additional User Instructions:** {req.additional_instructions.strip()}")

    # Reference material injection
    has_ref_files = bool(req.reference_files and len(req.reference_files) > 0)
    has_ref_text = bool(req.reference_text and req.reference_text.strip())

    if has_ref_files or has_ref_text:
        prompt_parts.append("\n## REFERENCE CONTEXT & GROUNDING")
        if has_ref_files:
            prompt_parts.append(f"- **Referenced Source Files:** {', '.join(req.reference_files)}")
        if has_ref_text:
            prompt_parts.append("The user has provided the following reference source text:")
            prompt_parts.append("```text")
            prompt_parts.append(req.reference_text.strip())
            prompt_parts.append("```")
        prompt_parts.append(
            "> **Grounding Directive:** Extract and synthesize key facts, terminology, metrics, and parameters "
            "from the above reference material. Do not contradict or invent details that conflict with it."
        )

    # Required sections
    prompt_parts.append("\n## REQUIRED STRUCTURAL BLUEPRINT")
    prompt_parts.append("Your document MUST include the following structured sections (use appropriate Markdown headings):")
    for sec in sections:
        prompt_parts.append(f"- {sec}")

    # Formatting guidelines
    prompt_parts.append("\n## OUTPUT INSTRUCTIONS")
    prompt_parts.append(
        "1. Begin immediately with the top-level document title using `# <Title>`.\n"
        "2. Include a concise metadata header block (Audience, Tone, Status, Date).\n"
        "3. Write out every section in full with detailed, substantive content matching the requested length.\n"
        "4. Use tables where comparisons or metrics are relevant.\n"
        "5. Output clean, valid Markdown only. Do not wrap the entire output in triple backtick code fences."
    )

    return "\n".join(prompt_parts)

def build_rewrite_prompt(req: RewriteRequest) -> str:
    """Constructs prompt for rewriting selected text or sections."""
    prompt_parts: List[str] = [
        "# TASK: Rewrite and Refine Document Content\n",
        "Please rewrite the provided document text according to the specific user instructions while maintaining factual accuracy.",
        f"\n**User Rewrite Instruction:** {req.instruction or 'Improve clarity, flow, and quality'}"
    ]

    if req.tone:
        tone_val = req.tone.value if hasattr(req.tone, "value") else str(req.tone)
        prompt_parts.append(f"**Target Tone:** {tone_val}")
    if req.target_length:
        prompt_parts.append(f"**Target Length Guidance:** {req.target_length}")
    if req.context and req.context.strip():
        prompt_parts.append(f"**Surrounding Document Context:** {req.context.strip()}")

    prompt_parts.append("\n## ORIGINAL TEXT TO REWRITE:")
    prompt_parts.append("```text")
    prompt_parts.append(req.content.strip())
    prompt_parts.append("```")

    prompt_parts.append(
        "\n## OUTPUT INSTRUCTIONS:\n"
        "Provide ONLY the revised rewritten text in Markdown format. "
        "Do not include conversational filler (e.g. 'Here is your rewritten text:'). "
        "Preserve core technical and factual details."
    )

    return "\n".join(prompt_parts)

def build_summarize_prompt(req: SummarizeRequest) -> str:
    """Constructs prompt for summarizing supplied document content."""
    prompt_parts: List[str] = [
        "# TASK: Summarize Document Content\n",
        "Please analyze and summarize the following content accurately.",
        f"**Requested Format:** {req.format or 'bullet_points'} (options: 'bullet_points', 'executive', 'concise')"
    ]

    if req.target_length:
        prompt_parts.append(f"**Target Length:** {req.target_length}")
    if req.context and req.context.strip():
        prompt_parts.append(f"**Document Context:** {req.context.strip()}")

    prompt_parts.append("\n## CONTENT TO SUMMARIZE:")
    prompt_parts.append("```text")
    prompt_parts.append(req.content.strip())
    prompt_parts.append("```")

    prompt_parts.append(
        "\n## OUTPUT INSTRUCTIONS:\n"
        "Provide a high-signal, accurate summary capturing key takeaways, decisions, and outcomes. "
        "Strictly adhere to the facts in the text. Output Markdown only without introductory pleasantries."
    )

    return "\n".join(prompt_parts)

def build_expand_prompt(req: ExpandRequest) -> str:
    """Constructs prompt for expanding a section with relevant detail."""
    prompt_parts: List[str] = [
        "# TASK: Expand Document Section with In-Depth Detail\n",
        "Please expand the provided section by introducing substantive detail, technical explanations, "
        "concrete examples, edge cases, and rationale.",
        f"**User Instruction:** {req.instruction or 'Provide more detail and depth'}"
    ]

    if req.focus_areas and len(req.focus_areas) > 0:
        prompt_parts.append(f"**Key Focus Areas to Elaborate:** {', '.join(req.focus_areas)}")
    if req.tone:
        tone_val = req.tone.value if hasattr(req.tone, "value") else str(req.tone)
        prompt_parts.append(f"**Tone:** {tone_val}")
    if req.context and req.context.strip():
        prompt_parts.append(f"**Surrounding Document Context:** {req.context.strip()}")

    prompt_parts.append("\n## SECTION TO EXPAND:")
    prompt_parts.append("```text")
    prompt_parts.append(req.content.strip())
    prompt_parts.append("```")

    prompt_parts.append(
        "\n## OUTPUT INSTRUCTIONS:\n"
        "Return the expanded section in full Markdown. Ensure the addition is organically integrated, "
        "technically sound, and devoid of empty fluff. Output only the revised section."
    )

    return "\n".join(prompt_parts)

