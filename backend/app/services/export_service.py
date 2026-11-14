"""
Document Export Service for PDF and DOCX.
Generates publication-quality, selectable PDFs via ReportLab
and structured, editable Microsoft Word documents via python-docx.
"""

import os
import re
import logging
from typing import List, Dict, Any, Union, Optional
from datetime import datetime

# ReportLab imports for PDF rendering
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from reportlab.pdfgen import canvas

# python-docx imports for DOCX rendering
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from app.utils.file_utils import get_temp_export_path

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Numbered Canvas for PDF (Page X of Y)
# ------------------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Footer divider line
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 42, 612 - 54, 42)

        # Footer text: Left is generator info, Right is Page X of Y
        self.drawString(54, 30, "AI-Enhanced Document Generator")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 30, page_str)

        self.restoreState()

# ------------------------------------------------------------------------------
# Markdown Pre-processing Helper
# ------------------------------------------------------------------------------
def _extract_markdown_text(content: Union[str, Dict[str, Any]]) -> str:
    """Extracts raw markdown string from either string or JSONB content."""
    if isinstance(content, dict):
        if "markdown" in content:
            return str(content["markdown"])
        elif "content" in content:
            return str(content["content"])
        elif "text" in content:
            return str(content["text"])
        # Format dictionary nicely if no explicit markdown field
        return "\n\n".join([f"**{k}:** {v}" for k, v in content.items()])
    return str(content)

def _sanitize_inline_xml(text: str) -> str:
    """Escapes XML entities for ReportLab Paragraphs while preserving bold/italic tags."""
    # Convert bold **text** to <b>text</b>
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Convert italic *text* or _text_ to <i>text</i>
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", t)
    # Convert code `code` to <font face="Courier">code</font>
    t = re.sub(r"`(.+?)`", r'<font face="Courier" color="#334155">\1</font>', t)
    # Escape standalone ampersands not part of HTML tags
    t = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;|b>|/b>|i>|/i>|font|/font)", "&amp;", t)
    return t

class ExportService:

    # --------------------------------------------------------------------------
    # 1. PDF Generation via ReportLab
    # --------------------------------------------------------------------------
    def generate_pdf(
        self,
        title: str,
        content: Union[str, Dict[str, Any]],
        document_type: str = "General Document",
        output_path: Optional[str] = None
    ) -> str:
        """
        Renders structured document content into a selectable, professional PDF.
        Returns the absolute filepath of the generated PDF.
        """
        raw_md = _extract_markdown_text(content)
        if not output_path:
            output_path = get_temp_export_path(prefix="document", extension="pdf")

        # Document setup with 54pt (0.75 in) margins
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        styles = getSampleStyleSheet()

        # Custom Typography
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=6
        )

        meta_style = ParagraphStyle(
            "DocMeta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=14
        )

        h1_style = ParagraphStyle(
            "DocH1",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=colors.HexColor("#1E293B"),
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=True
        )

        h2_style = ParagraphStyle(
            "DocH2",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#334155"),
            spaceBefore=10,
            spaceAfter=4,
            keepWithNext=True
        )

        h3_style = ParagraphStyle(
            "DocH3",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#475569"),
            spaceBefore=8,
            spaceAfter=3,
            keepWithNext=True
        )

        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#1E293B"),
            spaceAfter=6
        )

        quote_style = ParagraphStyle(
            "DocQuote",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
            leftIndent=14,
            spaceBefore=4,
            spaceAfter=6
        )

        bullet_style = ParagraphStyle(
            "DocBullet",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            leftIndent=16,
            spaceAfter=3,
            textColor=colors.HexColor("#1E293B")
        )

        table_cell_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#1E293B")
        )

        table_header_style = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#0F172A")
        )

        story = []

        # Document Header
        story.append(Paragraph(title, title_style))
        now_str = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(f"Category: <b>{document_type}</b> &nbsp;|&nbsp; Generated on: {now_str}", meta_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=12))

        # Parse Markdown lines
        lines = raw_md.split("\n")
        in_table = False
        table_rows: List[List[str]] = []

        def flush_table():
            nonlocal in_table, table_rows
            if table_rows:
                # Build ReportLab Table
                flowable_data = []
                for row_idx, row in enumerate(table_rows):
                    row_cells = []
                    for cell in row:
                        s = table_header_style if row_idx == 0 else table_cell_style
                        row_cells.append(Paragraph(_sanitize_inline_xml(cell), s))
                    flowable_data.append(row_cells)

                # Available width = 612 - 108 = 504 pt
                col_count = max(len(r) for r in flowable_data)
                col_width = 504 / max(1, col_count)
                t = Table(flowable_data, colWidths=[col_width] * col_count)
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                story.append(Spacer(1, 4))
                story.append(t)
                story.append(Spacer(1, 8))
                table_rows = []
            in_table = False

        for raw_line in lines:
            line = raw_line.strip()

            # Handle Markdown Tables
            if line.startswith("|") and line.endswith("|"):
                # Check for divider row |---|---|
                if re.match(r"^\|[\s\-:|]+\|$", line):
                    continue
                cells = [c.strip() for c in line[1:-1].split("|")]
                table_rows.append(cells)
                in_table = True
                continue
            elif in_table:
                flush_table()

            if not line:
                continue

            # Headings
            if line.startswith("# "):
                # Skip first H1 if it repeats the title
                h_text = line[2:].strip()
                if h_text.lower() != title.lower():
                    story.append(Paragraph(_sanitize_inline_xml(h_text), h1_style))
            elif line.startswith("## "):
                story.append(Paragraph(_sanitize_inline_xml(line[3:].strip()), h2_style))
            elif line.startswith("### "):
                story.append(Paragraph(_sanitize_inline_xml(line[4:].strip()), h3_style))
            elif line.startswith("> "):
                story.append(Paragraph(_sanitize_inline_xml(line[2:].strip()), quote_style))
            elif line.startswith("- ") or line.startswith("* "):
                bullet_text = f"&bull;&nbsp; {_sanitize_inline_xml(line[2:].strip())}"
                story.append(Paragraph(bullet_text, bullet_style))
            elif re.match(r"^\d+\.\s", line):
                num_text = line.split(".", 1)[1].strip()
                match = re.match(r"^(\d+)\.", line)
                num = match.group(1) if match else "1"
                story.append(Paragraph(f"{num}.&nbsp; {_sanitize_inline_xml(num_text)}", bullet_style))
            elif line == "---":
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceAfter=8, spaceBefore=8))
            else:
                story.append(Paragraph(_sanitize_inline_xml(line), body_style))

        if in_table:
            flush_table()

        # Build PDF using NumberedCanvas
        doc.build(story, canvasmaker=NumberedCanvas)
        logger.info(f"PDF successfully rendered at {output_path}")
        return output_path

    # --------------------------------------------------------------------------
    # 2. DOCX Generation via python-docx
    # --------------------------------------------------------------------------
    def generate_docx(
        self,
        title: str,
        content: Union[str, Dict[str, Any]],
        document_type: str = "General Document",
        output_path: Optional[str] = None
    ) -> str:
        """
        Renders structured document content into a fully editable, clean Microsoft Word (.docx) document.
        Returns the absolute filepath of the generated DOCX.
        """
        raw_md = _extract_markdown_text(content)
        if not output_path:
            output_path = get_temp_export_path(prefix="document", extension="docx")

        doc = Document()

        # Configure 1-inch margins
        for section in doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

            # Header
            header = section.header
            header_p = header.paragraphs[0]
            header_p.text = f"{title} | {document_type}"
            header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            if header_p.runs:
                header_p.runs[0].font.size = Pt(8.5)
                header_p.runs[0].font.color.rgb = RGBColor(148, 163, 184)

            # Footer
            footer = section.footer
            footer_p = footer.paragraphs[0]
            footer_p.text = "AI-Enhanced Document Generator"
            footer_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            if footer_p.runs:
                footer_p.runs[0].font.size = Pt(8.5)
                footer_p.runs[0].font.color.rgb = RGBColor(148, 163, 184)

        # Base Normal Style Typography
        style_normal = doc.styles['Normal']
        style_normal.font.name = 'Calibri'
        style_normal.font.size = Pt(10.5)
        style_normal.font.color.rgb = RGBColor(30, 41, 59)

        # Title
        title_p = doc.add_paragraph()
        title_run = title_p.add_run(title)
        title_run.font.name = 'Calibri'
        title_run.font.size = Pt(22)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(15, 23, 42)
        title_p.paragraph_format.space_after = Pt(4)

        # Subtitle / Metadata
        meta_p = doc.add_paragraph()
        now_str = datetime.now().strftime("%B %d, %Y")
        meta_run = meta_p.add_run(f"Category: {document_type}  |  Generated on: {now_str}")
        meta_run.font.name = 'Calibri'
        meta_run.font.size = Pt(9.5)
        meta_run.font.color.rgb = RGBColor(100, 116, 139)
        meta_p.paragraph_format.space_after = Pt(16)

        # Parse Markdown
        lines = raw_md.split("\n")
        in_table = False
        table_rows: List[List[str]] = []

        def clean_xml_text(s: str) -> str:
            """Strips XML 1.0 illegal control characters."""
            if not s:
                return ""
            return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]", "", str(s))

        def flush_docx_table():
            nonlocal in_table, table_rows
            if table_rows:
                col_count = max(len(r) for r in table_rows)
                row_count = len(table_rows)
                table = doc.add_table(rows=row_count, cols=col_count)
                table.alignment = WD_TABLE_ALIGNMENT.CENTER

                # Apply basic borders and shading to header
                for r_idx, row_data in enumerate(table_rows):
                    row = table.rows[r_idx]
                    for c_idx, cell_value in enumerate(row_data):
                        if c_idx < len(row.cells):
                            cell = row.cells[c_idx]
                            cell.text = clean_xml_text(cell_value.strip())
                            p = cell.paragraphs[0]
                            p.paragraph_format.space_after = Pt(2)
                            p.paragraph_format.space_before = Pt(2)
                            if r_idx == 0:
                                # Header styling
                                for run in p.runs:
                                    run.font.bold = True
                                    run.font.size = Pt(9.5)
                                # Shade header cell with light gray
                                shading = parse_xml(r'<w:shd {} w:fill="F1F5F9"/>'.format(nsdecls('w')))
                                cell._tc.get_or_add_tcPr().append(shading)
                            else:
                                for run in p.runs:
                                    run.font.size = Pt(9)

                doc.add_paragraph().paragraph_format.space_after = Pt(6)
                table_rows = []
            in_table = False

        def add_formatted_runs(paragraph, text: str):
            """Parses inline bold (**text**) and italic (*text*) into formatted runs."""
            clean_text = clean_xml_text(text)
            parts = re.split(r"(\*\*.+?\*\*|\*.+?\*|`.+?`)", clean_text)
            for part in parts:
                if not part:
                    continue
                if part.startswith("**") and part.endswith("**"):
                    run = paragraph.add_run(clean_xml_text(part[2:-2]))
                    run.bold = True
                elif part.startswith("*") and part.endswith("*"):
                    run = paragraph.add_run(clean_xml_text(part[1:-1]))
                    run.italic = True
                elif part.startswith("`") and part.endswith("`"):
                    run = paragraph.add_run(clean_xml_text(part[1:-1]))
                    run.font.name = "Consolas"
                    run.font.color.rgb = RGBColor(51, 65, 85)
                else:
                    paragraph.add_run(clean_xml_text(part))

        for raw_line in lines:
            line = raw_line.strip()

            # Table handling
            if line.startswith("|") and line.endswith("|"):
                if re.match(r"^\|[\s\-:|]+\|$", line):
                    continue
                cells = [c.strip() for c in line[1:-1].split("|")]
                table_rows.append(cells)
                in_table = True
                continue
            elif in_table:
                flush_docx_table()

            if not line:
                continue

            if line.startswith("# "):
                h_text = line[2:].strip()
                if h_text.lower() != title.lower():
                    h = doc.add_heading(level=1)
                    add_formatted_runs(h, h_text)
                    h.paragraph_format.space_before = Pt(14)
                    h.paragraph_format.space_after = Pt(4)
            elif line.startswith("## "):
                h = doc.add_heading(level=2)
                add_formatted_runs(h, line[3:].strip())
                h.paragraph_format.space_before = Pt(10)
                h.paragraph_format.space_after = Pt(3)
            elif line.startswith("### "):
                h = doc.add_heading(level=3)
                add_formatted_runs(h, line[4:].strip())
                h.paragraph_format.space_before = Pt(8)
                h.paragraph_format.space_after = Pt(2)
            elif line.startswith("> "):
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.4)
                p.paragraph_format.space_after = Pt(4)
                add_formatted_runs(p, line[2:].strip())
                for run in p.runs:
                    run.italic = True
            elif line.startswith("- ") or line.startswith("* "):
                p = doc.add_paragraph(style='List Bullet')
                p.paragraph_format.space_after = Pt(2)
                add_formatted_runs(p, line[2:].strip())
            elif re.match(r"^\d+\.\s", line):
                num_text = line.split(".", 1)[1].strip()
                p = doc.add_paragraph(style='List Number')
                p.paragraph_format.space_after = Pt(2)
                add_formatted_runs(p, num_text)
            elif line == "---":
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(6)
            else:
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(5)
                add_formatted_runs(p, line)

        if in_table:
            flush_docx_table()

        doc.save(output_path)
        logger.info(f"DOCX successfully rendered at {output_path}")
        return output_path

# Global singleton
export_service = ExportService()
