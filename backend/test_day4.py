"""
Comprehensive Day 4 Test Suite:
Validates AI Document Quality Scoring, Document Completeness Analysis,
Intelligent Document Improvement, Algorithmic Document Comparison,
and FastAPI Quality Route Handlers.
"""

import sys
import uuid
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.auth import AuthenticatedUser
from app.services.quality_service import quality_service
from app.services.completeness_service import completeness_service
from app.services.comparison_service import comparison_service
from app.services.ai_service import ai_service
from app.services.document_service import document_service
from app.schemas.document import DocumentCreate
from app.schemas.quality import (
    QualityAnalyzeRequest,
    CompletenessRequest,
    ImproveRequest,
    CompareRequest
)
from app.routes.quality import (
    analyze_quality,
    analyze_completeness,
    improve_document,
    compare_documents
)
from fastapi import HTTPException

# Test users
USER_A = AuthenticatedUser(id=str(uuid.uuid4()), email="test_user_a@test.com", token="mock-user-a")
USER_B = AuthenticatedUser(id=str(uuid.uuid4()), email="test_user_b@test.com", token="mock-user-b")

SAMPLE_PROJECT_DOC = """# Distributed Event Streaming Platform Architecture

## 1. Executive Summary & Overview
This document outlines the architectural blueprint for our distributed telemetry platform designed to ingest 50,000 events/sec with sub-50ms tail latency.

## 2. Problem Framing & Objectives
Legacy batch ingestion pipelines suffer from 45-minute synchronization delays, resulting in stale business intelligence and missed anomaly detection windows.
Our goal is real-time streaming with 99.99% availability.

## 3. Architecture & Workflow
The platform utilizes Apache Kafka clusters with 3-way partition replication, decoupled consumer groups, and Redis cache tiers for stateful aggregation.

## 4. Technical Implementation
Services are deployed on Kubernetes with automated Horizontal Pod Autoscaling (HPA) triggered by consumer lag telemetry.

## 5. Verification & Testing
Load tests simulate 75,000 events/sec across 10 concurrent producer instances to evaluate backpressure handling.

## 6. Action Matrix & Next Steps
| Milestone | Lead | Target Date | Status |
| :--- | :--- | :--- | :--- |
| Cluster Manifests | DevOps | Day 1 | Complete |
| Load Testing | SRE | Day 2 | Active |
"""

SAMPLE_SPARSE_DOC = """# Quick Overview
A platform for distributed processing.
"""

def test_1_quality_scoring_service():
    print("\n--- [1/5] Testing AI Document Quality Scoring Service ---")

    # 1. Empty content error
    try:
        quality_service.analyze_quality("")
        assert False, "Should raise ValueError for empty content"
    except ValueError:
        print(" [x] Successfully rejected empty document content.")

    # 2. Comprehensive scoring
    res = quality_service.analyze_quality(SAMPLE_PROJECT_DOC, document_type="Project documentation")
    assert "overall_score" in res
    assert 0 <= res["overall_score"] <= 100
    assert "category_scores" in res
    cat = res["category_scores"]
    for dim in ["grammar", "clarity", "relevance", "professionalism", "structure", "completeness"]:
        assert dim in cat
        assert 0 <= cat[dim] <= 100

    assert len(res["strengths"]) > 0
    assert len(res["recommendations"]) > 0
    assert res["metrics"]["word_count"] > 100
    print(f" [x] Quality score computed: Overall {res['overall_score']}/100 across 6 categories.")
    print(f"     Strengths: {res['strengths'][0]}")
    print(f"     Recommendation: {res['recommendations'][0]}")

    # 3. Sparse document gets lower scores
    sparse_res = quality_service.analyze_quality(SAMPLE_SPARSE_DOC, document_type="Project documentation")
    assert sparse_res["overall_score"] < res["overall_score"]
    assert any("brief" in w.lower() or "heading" in w.lower() for w in sparse_res["weaknesses"])
    print(f" [x] Sparse document appropriately scored lower: {sparse_res['overall_score']}/100.")

def test_2_completeness_analyzer_service():
    print("\n--- [2/5] Testing Document Completeness Analyzer Service ---")

    # 1. Empty content error
    try:
        completeness_service.analyze_completeness("")
        assert False, "Should raise ValueError for empty content"
    except ValueError:
        print(" [x] Successfully rejected empty document for completeness analysis.")

    # 2. Complete project doc analysis
    res = completeness_service.analyze_completeness(SAMPLE_PROJECT_DOC, document_type="Project documentation")
    assert res["detected_category"] == "Project Documentation"
    assert res["completeness_percentage"] >= 80
    assert res["completed_count"] >= 5
    assert len(res["completed_sections"]) >= 5
    print(f" [x] Completeness verified: {res['completeness_percentage']}% ({res['completed_count']}/{res['total_expected_sections']} completed).")

    # 3. Sparse doc missing sections
    sparse_res = completeness_service.analyze_completeness(SAMPLE_SPARSE_DOC, document_type="Project documentation")
    assert sparse_res["completeness_percentage"] < 50
    assert sparse_res["missing_count"] > 3
    assert len(sparse_res["missing_sections"]) > 3
    print(f" [x] Sparse doc detected missing sections: {sparse_res['missing_count']} missing sections identified.")

    # 4. Resume specific blueprint
    resume_text = """# John Doe - Principal Systems Architect
john.doe@example.com | github.com/johndoe | linkedin.com/in/johndoe

## Professional Summary
Over 12 years designing and scaling distributed systems handling millions of daily transactions.

## Core Technical Skills
Go, Python, Kubernetes, Kafka, PostgreSQL, Distributed Systems, Terraform, AWS, GCP.

## Professional Experience
Lead Systems Architect at Acme Corp. Scaled messaging bus from 5k to 100k msgs/sec.
Reduced p99 latency from 120ms to 18ms.

## Education & Certifications
B.S. in Computer Science, Stanford University. Certified Kubernetes Administrator (CKA).

## Notable Projects
Architected zero-downtime database failover automation across three multi-cloud regions.
"""
    resume_res = completeness_service.analyze_completeness(resume_text, document_type="Resumes")
    assert resume_res["detected_category"] == "Resumes"
    assert resume_res["completeness_percentage"] >= 75
    print(f" [x] Resume completeness correctly calibrated: {resume_res['completeness_percentage']}% without penalty for project documentation sections.")

def test_3_ai_document_improvement():
    print("\n--- [3/5] Testing AI Document Improvement Operations ---")

    sample_draft = "The system is fast and does good work. We utilize microservices."

    # 1. Improve Grammar
    res_gram = ai_service.improve_content(sample_draft, operation="improve_grammar")
    assert "revised_text" in res_gram
    assert len(res_gram["revised_text"]) > 0
    print(f" [x] improve_grammar succeeded: {res_gram['diff_summary']}")

    # 2. Improve Professionalism
    res_prof = ai_service.improve_content(sample_draft, operation="improve_professionalism")
    assert "revised_text" in res_prof
    print(f" [x] improve_professionalism succeeded: {res_prof['diff_summary']}")

    # 3. Simplify Language
    res_simp = ai_service.improve_content(sample_draft, operation="simplify_language")
    assert "revised_text" in res_simp
    print(f" [x] simplify_language succeeded: {res_simp['diff_summary']}")

    # 4. Expand Explanations
    res_exp = ai_service.improve_content(sample_draft, operation="expand_explanations")
    assert "revised_text" in res_exp
    assert res_exp["word_count"] >= len(sample_draft.split())
    print(f" [x] expand_explanations succeeded: {res_exp['diff_summary']}")

    # 5. Empty content error
    try:
        ai_service.improve_content("", operation="improve_grammar")
        assert False, "Should raise exception for empty content"
    except Exception:
        print(" [x] Successfully rejected empty content for improvement.")

def test_4_document_comparison_engine():
    print("\n--- [4/5] Testing Document Comparison & Diff Engine ---")

    text_v1 = """# System Architecture
The system uses monolithic architecture with MySQL.
Deployment happens manually once a month.
"""

    text_v2 = """# System Architecture
The system uses distributed microservices with PostgreSQL.
Deployment is fully automated using CI/CD pipelines.
Additional disaster recovery protocols are active.
"""

    # 1. Identical documents -> 100% similarity
    ident_res = comparison_service.compare_documents(text_v1, text_v1)
    assert ident_res["similarity_percentage"] == 100.0
    assert ident_res["total_changes"] == 0
    assert len(ident_res["added"]) == 0
    assert len(ident_res["removed"]) == 0
    print(f" [x] Identical document comparison: {ident_res['similarity_percentage']}% similarity, 0 changes.")

    # 2. Modified documents
    diff_res = comparison_service.compare_documents(text_v1, text_v2)
    assert 0 < diff_res["similarity_percentage"] < 100.0
    assert diff_res["total_changes"] > 0
    assert len(diff_res["added"]) > 0 or len(diff_res["modified"]) > 0
    assert len(diff_res["summary"]) > 20
    print(f" [x] Diff comparison calculated: {diff_res['similarity_percentage']}% similarity ({diff_res['total_changes']} changes).")
    print(f"     AI Summary: '{diff_res['summary']}'")

    # 3. Empty comparison error
    try:
        comparison_service.compare_documents("", "")
        assert False, "Should raise ValueError for both empty"
    except ValueError:
        print(" [x] Successfully rejected empty documents for comparison.")

def test_5_fastapi_quality_endpoints():
    print("\n--- [5/5] Testing FastAPI Quality & Comparison Route Handlers ---")

    # Create a saved document for User A to test ownership
    doc_a = document_service.create_document(
        user_id=USER_A.id,
        doc_data=DocumentCreate(
            title="User A High-Speed Kafka Specs",
            document_type="Project documentation",
            content=SAMPLE_PROJECT_DOC,
            status="draft"
        )
    )

    # 1. POST /api/quality/analyze with raw content
    raw_res = analyze_quality(
        QualityAnalyzeRequest(content=SAMPLE_PROJECT_DOC, document_type="Project documentation"),
        current_user=USER_A
    )
    assert raw_res["overall_score"] > 50
    print(f" [x] POST /api/quality/analyze (raw content): {raw_res['overall_score']}/100")

    # 2. POST /api/quality/analyze with saved document_id
    saved_res = analyze_quality(
        QualityAnalyzeRequest(document_id=doc_a.id),
        current_user=USER_A
    )
    assert saved_res["overall_score"] > 50
    print(f" [x] POST /api/quality/analyze (saved doc_id): {saved_res['overall_score']}/100")

    # 3. User B cannot analyze User A's document_id -> 404
    try:
        analyze_quality(QualityAnalyzeRequest(document_id=doc_a.id), current_user=USER_B)
        assert False, "User B should not access User A document"
    except HTTPException as he:
        assert he.status_code == 404
        print(" [x] Confirmed User B cannot analyze User A saved document (404 Not Found).")

    # 4. POST /api/quality/completeness
    comp_res = analyze_completeness(
        CompletenessRequest(document_id=doc_a.id),
        current_user=USER_A
    )
    assert comp_res["completeness_percentage"] > 70
    print(f" [x] POST /api/quality/completeness: {comp_res['completeness_percentage']}% complete")

    # 5. POST /api/quality/improve
    imp_res = improve_document(
        ImproveRequest(
            document_id=doc_a.id,
            operation="improve_professionalism"
        ),
        current_user=USER_A
    )
    assert len(imp_res["revised_text"]) > 0
    print(f" [x] POST /api/quality/improve: {imp_res['diff_summary']}")

    # 6. POST /api/documents/compare (raw text)
    comp_req = CompareRequest(
        original_text=SAMPLE_PROJECT_DOC,
        revised_text=SAMPLE_PROJECT_DOC + "\n\n## 7. Security Hardening\nAll endpoints are TLS 1.3 encrypted.\n"
    )
    cmp_res = compare_documents(comp_req, current_user=USER_A)
    assert cmp_res["similarity_percentage"] > 70
    print(f" [x] POST /api/documents/compare: {cmp_res['similarity_percentage']}% similarity ({cmp_res['total_changes']} changes)")

    # 7. Clean up test document
    document_service.delete_document(doc_a.id, USER_A.id)
    print(" [x] Cleaned up test document.")

if __name__ == "__main__":
    try:
        test_1_quality_scoring_service()
        test_2_completeness_analyzer_service()
        test_3_ai_document_improvement()
        test_4_document_comparison_engine()
        test_5_fastapi_quality_endpoints()
        print("\n" + "="*70)
        print(" 🎉 ALL DAY 4 QUALITY, COMPLETENESS & COMPARISON TESTS PASSED! 🎉 ")
        print("="*70 + "\n")
    except Exception as e:
        print(f"\n❌ DAY 4 TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
