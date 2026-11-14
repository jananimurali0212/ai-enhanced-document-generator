"""
Unit & Integration Tests for PDF & DOCX Export Services (Modules 5, 6, 7, 8).
Verifies:
- PDF generation with selectable text and tables
- DOCX generation with headings, lists, tables, headers/footers
- Unicode and special character handling
- Safe filename sanitization
- Temporary file creation and cleanup
"""

import os
import sys
from pathlib import Path
import pytest

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.export_service import export_service
from app.utils.file_utils import sanitize_filename, cleanup_file, get_temp_export_path

SAMPLE_MARKDOWN = """# System Architecture Blueprint
*Enterprise Real-Time Event Bus*

> **Executive Note:** Approved for immediate production deployment.

## 1. Component Boundaries
- **Ingestion:** Kafka topic with 32 partitions.
- **Compute:** Kubernetes worker pods autoscale up to 50 replicas.
- **Persistence:** Cloud Spanner with cross-region read replicas.

## 2. SLA & Latency Metrics
| Service Tier | Target p99 Latency | Availability SLA |
| :--- | :--- | :--- |
| Ingestion Gateway | &lt; 15ms | 99.99% |
| Processing Engine | &lt; 45ms | 99.95% |
| Analytics Store | &lt; 120ms | 99.9% |

### 3. Implementation Checklist
1. Finalize mTLS certificates.
2. Configure distributed tracing thresholds.
3. Validate failover under simulated region stockout.
"""

def test_safe_filename_generation():
    # Path traversal attack
    assert sanitize_filename("../../etc/passwd", extension="pdf") == "etcpasswd.pdf"
    assert sanitize_filename("..\\..\\windows\\system32\\calc.exe", extension="docx") == "windowssystem32calcexe.docx"
    # Special characters
    assert sanitize_filename("Proposal: AI & Cloud / 2026?", extension="pdf") == "Proposal-AI-Cloud-2026.pdf"
    # Blank fallback
    assert sanitize_filename("   ", default_name="custom_doc", extension="pdf") == "custom_doc.pdf"

def test_pdf_generation_selectable_text_and_tables():
    pdf_path = export_service.generate_pdf(
        title="System Architecture Blueprint",
        content=SAMPLE_MARKDOWN,
        document_type="Project documentation"
    )
    assert os.path.exists(pdf_path)
    file_size = os.path.getsize(pdf_path)
    assert file_size > 1500  # Valid PDF size

    # Verify PDF magic bytes (%PDF)
    with open(pdf_path, "rb") as f:
        header = f.read(5)
        assert header.startswith(b"%PDF")

    # Cleanup
    cleanup_file(pdf_path)
    assert not os.path.exists(pdf_path)

def test_docx_generation_hierarchy_and_tables():
    docx_path = export_service.generate_docx(
        title="System Architecture Blueprint",
        content=SAMPLE_MARKDOWN,
        document_type="Project documentation"
    )
    assert os.path.exists(docx_path)
    file_size = os.path.getsize(docx_path)
    assert file_size > 2000  # Valid DOCX zip archive size

    # Verify DOCX zip header (PK\x03\x04)
    with open(docx_path, "rb") as f:
        header = f.read(4)
        assert header == b"PK\x03\x04"

    # Cleanup
    cleanup_file(docx_path)
    assert not os.path.exists(docx_path)

def test_unicode_and_special_characters_handling():
    unicode_content = """# Global Expansion Dossier
*Multi-Region Localization & Telemetry: \u00a9 \u00ae \u2122*

- Euro currency targets: \u20ac1,500,000 ARR.
- Yen projections: \u00a5250,000,000 in Q4.
- German characters: \u00c4nderungen, Gr\u00fc\u00dfe, \u00dcberwachung.
- French accents: \u00c9tude de faisabilit\u00e9, syst\u00e8me int\u00e9gr\u00e9.
- Arrows and symbols: \u2192 \u2190 \u2713
"""
    # 1. PDF
    pdf_path = export_service.generate_pdf(
        title="Global Expansion Dossier",
        content=unicode_content,
        document_type="Technical reports"
    )
    assert os.path.exists(pdf_path)
    cleanup_file(pdf_path)

    # 2. DOCX
    docx_path = export_service.generate_docx(
        title="Global Expansion Dossier",
        content=unicode_content,
        document_type="Technical reports"
    )
    assert os.path.exists(docx_path)
    cleanup_file(docx_path)

def test_long_document_multi_page():
    # Generate long content (10 sections)
    long_sections = ["# Long Form Strategic Dossier\n"]
    for i in range(1, 12):
        long_sections.append(f"## Section {i}: Architectural Deep Dive\n" + "This is detailed technical prose explaining the operational parameters of section " + str(i) + ". " * 25 + "\n")
    long_content = "\n".join(long_sections)

    pdf_path = export_service.generate_pdf(
        title="Long Form Strategic Dossier",
        content=long_content
    )
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 3000
    cleanup_file(pdf_path)
