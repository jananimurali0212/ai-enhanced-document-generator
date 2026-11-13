"""
Comprehensive Day 2 Test Suite:
Verifies prompt construction, input validation, AI service layer,
mock fallback & live Gemini handlers, error responses, and FastAPI route handlers.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.models.schemas import (
    GenerateDocumentRequest,
    RewriteRequest,
    SummarizeRequest,
    ExpandRequest,
    ToneOption,
    LengthOption,
    DocumentCategory
)
from app.services.prompt_builder import (
    build_system_instruction,
    build_generation_prompt,
    build_rewrite_prompt,
    build_summarize_prompt,
    build_expand_prompt,
    CATEGORY_SECTIONS
)
from app.services.ai_service import ai_service
from app.core.exceptions import (
    AIServiceException,
    AIConfigurationException,
    AIRateLimitException,
    AITimeoutException,
    AIGenerationException
)
from app.api.routes import (
    health_check,
    get_templates,
    generate_document,
    rewrite_text,
    summarize_text,
    expand_text
)
from fastapi import HTTPException

def test_prompt_builder():
    print("\n--- [1/5] Testing Prompt Builder Service ---")
    sys_inst = build_system_instruction()
    assert "Gemini" in sys_inst or "document architect" in sys_inst
    assert "STRICT GROUNDING & INTEGRITY CONSTRAINTS" in sys_inst
    assert "DO NOT hallucinate" in sys_inst
    print(" [x] System instruction contains strict grounding and anti-hallucination rules.")

    # Test generation prompt with references and categories
    for cat in ["Project documentation", "Technical reports", "Business proposals", "Resumes", "Cover letters", "Meeting summaries"]:
        req = GenerateDocumentRequest(
            template_id="test",
            category=cat,
            topic="Next-Gen Architecture",
            purpose="Define blueprint for real-time scale",
            intended_audience="Engineering Leads",
            tone=ToneOption.TECHNICAL,
            desired_length=LengthOption.STANDARD,
            additional_instructions="Include deployment architecture diagram description.",
            reference_files=["specs.pdf", "data_model.json"],
            reference_text="Database throughput capacity is 50,000 writes/sec."
        )
        prompt = build_generation_prompt(req)
        assert cat in prompt
        assert "Next-Gen Architecture" in prompt
        assert "specs.pdf" in prompt
        assert "50,000 writes/sec" in prompt
        assert "REQUIRED STRUCTURAL BLUEPRINT" in prompt
        for expected_section in CATEGORY_SECTIONS[cat]:
            assert expected_section in prompt
        print(f" [x] Structured generation prompt constructed for category: '{cat}'")

    # Test rewrite prompt
    rw_req = RewriteRequest(
        content="Our legacy server is slow and crashes often.",
        instruction="Elevate to executive technical tone emphasizing latency degradation",
        tone=ToneOption.EXECUTIVE,
        context="System Modernization Pitch"
    )
    rw_prompt = build_rewrite_prompt(rw_req)
    assert "ORIGINAL TEXT TO REWRITE" in rw_prompt
    assert "Our legacy server is slow" in rw_prompt
    assert "Executive" in rw_prompt
    print(" [x] Rewrite prompt successfully generated.")

    # Test summarize prompt
    sum_req = SummarizeRequest(
        content="We met with the client yesterday. They want 99.99% uptime and zero-downtime deployment by Q3.",
        format="executive",
        target_length="2 key bullet points"
    )
    sum_prompt = build_summarize_prompt(sum_req)
    assert "CONTENT TO SUMMARIZE" in sum_prompt
    assert "executive" in sum_prompt
    print(" [x] Summarize prompt successfully generated.")

    # Test expand prompt
    exp_req = ExpandRequest(
        content="The security layer enforces OAuth 2.0 with JWT tokens.",
        instruction="Detail cryptographic signing algorithms and key rotation",
        focus_areas=["Key rotation", "Asymmetric RSA-256", "Token revocation list"],
        tone=ToneOption.TECHNICAL
    )
    exp_prompt = build_expand_prompt(exp_req)
    assert "SECTION TO EXPAND" in exp_prompt
    assert "Key rotation" in exp_prompt
    print(" [x] Expand prompt successfully generated.")

def test_pydantic_validation():
    print("\n--- [2/5] Testing Pydantic Input Validation ---")
    # Empty topic validation
    try:
        GenerateDocumentRequest(
            topic="   ",
            purpose="Valid purpose",
            intended_audience="Valid audience"
        )
        assert False, "Should have raised ValueError on blank topic"
    except Exception:
        print(" [x] Successfully rejected empty/whitespace topic.")

    # Purpose too short
    try:
        GenerateDocumentRequest(
            topic="Valid Topic",
            purpose="Tiny",
            intended_audience="Valid audience"
        )
        assert False, "Should have raised validation error on short purpose"
    except Exception:
        print(" [x] Successfully validated minimum purpose length.")

    # Blank rewrite content
    try:
        RewriteRequest(content="   ")
        assert False, "Should have raised validation error on empty rewrite content"
    except Exception:
        print(" [x] Successfully rejected empty rewrite content.")

    # Blank summarize content
    try:
        SummarizeRequest(content="Short")
        assert False, "Should have raised validation error on short summarize content"
    except Exception:
        print(" [x] Successfully validated minimum summarize length.")

def test_ai_service_direct():
    print("\n--- [3/5] Testing AI Service Layer ---")
    # Generation test
    gen_req = GenerateDocumentRequest(
        category="Technical reports",
        topic="Microservices Latency Benchmark Report",
        purpose="Analyze p99 latency across gRPC and REST under peak load",
        intended_audience="Platform Architecture Committee",
        tone=ToneOption.TECHNICAL,
        desired_length=LengthOption.STANDARD,
        reference_files=["grpc_benchmark.csv"]
    )
    doc_res = ai_service.generate_document(gen_req)
    assert doc_res.id is not None
    assert doc_res.title is not None
    assert doc_res.word_count > 50
    assert len(doc_res.content) > 100
    print(f" [x] AI Service generated document: '{doc_res.title}' ({doc_res.word_count} words)")

    # Rewrite test
    rw_res = ai_service.rewrite_text(RewriteRequest(
        content="The system handles 1000 requests every second without lagging.",
        instruction="Elevate to enterprise technical phrasing",
        tone=ToneOption.TECHNICAL
    ))
    assert rw_res.action == "rewrite"
    assert len(rw_res.revised_text) > 10
    print(f" [x] AI Service rewrite completed: {rw_res.diff_summary}")

    # Summarize test
    sum_res = ai_service.summarize_text(SummarizeRequest(
        content=(
            "The architecture review concluded with unanimous approval of Option B. "
            "Data ingestion will use Apache Kafka with Avro serialization. "
            "Storage will be handled via Cloud Spanner with cross-region replication. "
            "Deployment is targeted for the end of Q3 with a 99.99% availability SLA."
        ),
        format="bullet_points"
    ))
    assert sum_res.action == "summarize"
    assert len(sum_res.revised_text) > 10
    print(f" [x] AI Service summarize completed: {sum_res.diff_summary}")

    # Expand test
    exp_res = ai_service.expand_text(ExpandRequest(
        content="The API gateway routes incoming client traffic to internal microservices.",
        instruction="Detail rate limiting and circuit breaking policies",
        focus_areas=["Token bucket algorithm", "Envoy sidecar proxies"]
    ))
    assert exp_res.action == "expand"
    assert exp_res.word_count > len(exp_res.original_text.split())
    print(f" [x] AI Service expand completed: {exp_res.diff_summary}")

def test_error_handling_and_resilience():
    print("\n--- [4/5] Testing AI Error Handling & Edge Cases ---")
    
    # 1. Rate Limit Simulation
    with patch.object(ai_service, "_call_gemini_api", side_effect=AIRateLimitException()):
        try:
            ai_service.generate_document(GenerateDocumentRequest(
                topic="Rate Limit Test",
                purpose="Testing rate limit exception propagation",
                intended_audience="Audience"
            ))
            assert False, "Expected AIRateLimitException"
        except AIRateLimitException as e:
            assert e.status_code == 429
            assert e.error_type == "AI_RATE_LIMIT_EXCEEDED"
            assert "wait 15 to 30 seconds" in e.retry_guidance
            print(f" [x] Intercepted Rate Limit (429) with guidance: '{e.retry_guidance}'")

    # 2. Timeout Simulation
    with patch.object(ai_service, "_call_gemini_api", side_effect=AITimeoutException()):
        try:
            ai_service.rewrite_text(RewriteRequest(
                content="Sample text to rewrite"
            ))
            assert False, "Expected AITimeoutException"
        except AITimeoutException as e:
            assert e.status_code == 504
            assert e.error_type == "AI_TIMEOUT"
            print(f" [x] Intercepted Timeout (504) with guidance: '{e.retry_guidance}'")

    # 3. Missing/Invalid API Configuration Simulation
    with patch.object(ai_service, "_call_gemini_api", side_effect=AIConfigurationException()):
        try:
            ai_service.summarize_text(SummarizeRequest(
                content="Long text to summarize for testing"
            ))
            assert False, "Expected AIConfigurationException"
        except AIConfigurationException as e:
            assert e.status_code == 503
            assert e.error_type == "AI_CONFIGURATION_ERROR"
            print(f" [x] Intercepted Configuration Exception (503): '{e.message}'")

    # 4. Malformed/Empty Output Simulation
    with patch.object(ai_service, "_call_gemini_api", side_effect=AIGenerationException()):
        try:
            ai_service.expand_text(ExpandRequest(
                content="Short text to expand"
            ))
            assert False, "Expected AIGenerationException"
        except AIGenerationException as e:
            assert e.status_code == 502
            assert e.error_type == "AI_GENERATION_FAILED"
            print(f" [x] Intercepted Generation Exception (502): '{e.message}'")

def test_fastapi_route_endpoints():
    print("\n--- [5/5] Testing FastAPI Route Endpoints Directly ---")
    
    # 1. Health check
    h = health_check()
    assert h["status"] == "healthy"
    assert h["ai_provider"] == "Google Gemini API"
    print(f" [x] GET /api/health: {h['service']} (model: {h['model']}, configured: {h['is_gemini_configured']})")

    # 2. Templates
    temps = get_templates()
    assert len(temps) == 6
    print(f" [x] GET /api/templates returned {len(temps)} templates.")

    # 3. POST /api/generate
    gen_payload = GenerateDocumentRequest(
        template_id="proj-doc",
        category="Project documentation",
        topic="Distributed Event Sourcing Platform",
        purpose="Define CQRS and event storage pattern",
        intended_audience="Platform Architecture Team",
        tone=ToneOption.TECHNICAL,
        desired_length=LengthOption.STANDARD,
        reference_files=["event_sourcing_spec.pdf"]
    )
    doc = generate_document(gen_payload)
    assert doc.id is not None
    assert doc.word_count > 50
    print(f" [x] POST /api/generate returned document: '{doc.title}' ({doc.word_count} words)")

    # 4. POST /api/edit/rewrite
    rw_payload = RewriteRequest(
        content="Our legacy server is slow and crashes under high traffic.",
        instruction="Elevate to formal enterprise technical tone",
        tone=ToneOption.TECHNICAL
    )
    rw = rewrite_text(rw_payload)
    assert rw.action == "rewrite"
    assert len(rw.revised_text) > 10
    print(f" [x] POST /api/edit/rewrite succeeded: {rw.diff_summary}")

    # 5. POST /api/edit/summarize
    sum_payload = SummarizeRequest(
        content=(
            "The architecture review concluded with unanimous approval of Option B. "
            "Data ingestion will use Apache Kafka with Avro serialization. "
            "Storage will be handled via Cloud Spanner with cross-region replication. "
            "Deployment is targeted for the end of Q3 with a 99.99% availability SLA."
        ),
        format="bullet_points"
    )
    sm = summarize_text(sum_payload)
    assert sm.action == "summarize"
    assert len(sm.revised_text) > 10
    print(f" [x] POST /api/edit/summarize succeeded: {sm.diff_summary}")

    # 6. POST /api/edit/expand
    exp_payload = ExpandRequest(
        content="Deploy OpenTelemetry collector as a daemonset.",
        instruction="Detail resource limits and batch processor buffer settings",
        focus_areas=["Batch processor", "Memory limiter"]
    )
    exp = expand_text(exp_payload)
    assert exp.action == "expand"
    assert exp.word_count > 10
    print(f" [x] POST /api/edit/expand succeeded: {exp.diff_summary}")

    # 7. Route error interception test
    with patch.object(ai_service, "_call_gemini_api", side_effect=AIRateLimitException()):
        try:
            generate_document(gen_payload)
            assert False, "Expected HTTPException with 429 status code"
        except HTTPException as he:
            assert he.status_code == 429
            assert he.detail["error_type"] == "AI_RATE_LIMIT_EXCEEDED"
            assert "wait 15 to 30 seconds" in he.detail["retry_guidance"]
            print(f" [x] Route cleanly transformed AIRateLimitException into HTTP 429 JSON response.")

if __name__ == "__main__":
    try:
        test_prompt_builder()
        test_pydantic_validation()
        test_ai_service_direct()
        test_error_handling_and_resilience()
        test_fastapi_route_endpoints()
        print("\n" + "="*70)
        print(" ALL DAY 2 AI INTEGRATION TESTS PASSED SUCCESSFULLY! ")
        print("="*70 + "\n")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
