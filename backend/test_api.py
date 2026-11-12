import sys
from datetime import datetime
from app.models.schemas import GenerateDocumentRequest, ToneOption, LengthOption
from app.services.mock_generator import TEMPLATES_DATA, generate_mock_document

def run_tests():
    print("[1/3] Verifying Templates...")
    assert len(TEMPLATES_DATA) == 6, f"Expected 6 templates, got {len(TEMPLATES_DATA)}"
    categories = [t["category"] for t in TEMPLATES_DATA]
    expected_categories = [
        "Project documentation",
        "Technical reports",
        "Business proposals",
        "Resumes",
        "Cover letters",
        "Meeting summaries"
    ]
    for exp in expected_categories:
        assert exp in categories, f"Missing category: {exp}"
    print(f" -> Found all 6 categories: {categories}")

    print("\n[2/3] Verifying Document Generation per Category...")
    for template in TEMPLATES_DATA:
        req = GenerateDocumentRequest(
            template_id=template["id"],
            category=template["category"],
            topic=template["placeholder_topic"],
            purpose=template["placeholder_purpose"],
            intended_audience=template["placeholder_audience"],
            tone=template["default_tone"],
            desired_length=template["default_length"],
            reference_files=["sample_spec.pdf", "architecture.docx"]
        )
        doc = generate_mock_document(req)
        assert doc.id is not None
        assert doc.title == template["placeholder_topic"]
        assert len(doc.content) > 200
        assert "sample_spec.pdf" in doc.content
        print(f" -> Generated: '{doc.title[:45]}...' ({doc.word_count} words)")

    print("\n[3/3] Testing Custom Unstructured Document Generation...")
    custom_req = GenerateDocumentRequest(
        template_id="custom",
        category="General Document",
        topic="Enterprise Cloud Migration Strategy",
        purpose="Outline migration roadmap from legacy VM to managed containers",
        intended_audience="Cloud Steering Committee",
        tone=ToneOption.EXECUTIVE,
        desired_length=LengthOption.STANDARD,
        reference_files=[]
    )
    custom_doc = generate_mock_document(custom_req)
    assert custom_doc.word_count > 100
    print(f" -> Custom Document Generated: {custom_doc.title} ({custom_doc.word_count} words)")

    print("\nALL BACKEND TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()

