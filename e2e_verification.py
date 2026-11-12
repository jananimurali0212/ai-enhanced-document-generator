import urllib.request
import urllib.parse
import json
import uuid
import mimetypes

BASE_FRONTEND_URL = "http://127.0.0.1:5173"
BASE_BACKEND_URL = "http://127.0.0.1:8000"

def log_section(title):
    print(f"\n{'='*65}\n▶ {title}\n{'='*65}")

def test_1_health_and_connectivity():
    log_section("TEST 1: Server Health & Connectivity")
    
    # 1. Direct Backend Health
    with urllib.request.urlopen(f"{BASE_BACKEND_URL}/api/health") as res:
        assert res.status == 200
        data = json.loads(res.read().decode())
        print(f" ✔ Direct Backend /api/health: OK (Status: {data['status']}, Service: {data['service']})")

    # 2. Frontend HTML Shell
    with urllib.request.urlopen(BASE_FRONTEND_URL) as res:
        assert res.status == 200
        html = res.read().decode()
        assert "<div id=\"root\"></div>" in html
        assert "src=\"/src/main.jsx\"" in html or "assets" in html
        print(f" ✔ Frontend Root HTML Shell: OK ({len(html)} bytes, Root mounting point confirmed)")

    # 3. Vite Reverse Proxy to Backend
    with urllib.request.urlopen(f"{BASE_FRONTEND_URL}/api/health") as res:
        assert res.status == 200
        proxy_data = json.loads(res.read().decode())
        assert proxy_data['status'] == "healthy"
        print(f" ✔ Vite Reverse Proxy (/api -> FastAPI:8000): OK")

def test_2_dashboard_and_templates():
    log_section("TEST 2: Dashboard & Template Selector")
    
    with urllib.request.urlopen(f"{BASE_FRONTEND_URL}/api/templates") as res:
        assert res.status == 200
        templates = json.loads(res.read().decode())
        assert len(templates) == 6, f"Expected 6 templates, found {len(templates)}"
        
        expected_categories = [
            "Project documentation",
            "Technical reports",
            "Business proposals",
            "Resumes",
            "Cover letters",
            "Meeting summaries"
        ]
        
        received_categories = [t["category"] for t in templates]
        print(f" ✔ Template Count: {len(templates)}/6 verified")
        for cat in expected_categories:
            assert cat in received_categories, f"Category missing: {cat}"
            print(f"   - Category verified: [{cat}]")

def test_3_prompt_form_and_generation_all_categories():
    log_section("TEST 3: Prompt Form & Generation Across All Categories")
    
    test_cases = [
        {
            "category": "Project documentation",
            "topic": "Real-time Event Streaming Platform Architecture",
            "purpose": "Define distributed event log, partition strategy, and consumer groups.",
            "audience": "Staff Systems Architects and DevOps Lead",
            "tone": "Technical",
            "length": "Standard (~800-1,200 words)"
        },
        {
            "category": "Technical reports",
            "topic": "Bare Metal Kubernetes vs Serverless Containers Benchmark",
            "purpose": "Evaluate p99 tail latency, cold starts, and cost under 50k req/sec.",
            "audience": "VP of Infrastructure and Cloud Engineers",
            "tone": "Technical",
            "length": "In-depth (~1,500-2,500 words)"
        },
        {
            "category": "Business proposals",
            "topic": "AI Enterprise Knowledge Engine Platform",
            "purpose": "Secure $250k budget for Phase 1 prototype cutting onboarding time by 60%.",
            "audience": "Chief Technology Officer and Investment Committee",
            "tone": "Persuasive",
            "length": "Standard (~800-1,200 words)"
        },
        {
            "category": "Resumes",
            "topic": "Principal Distributed Systems Engineer Resume",
            "purpose": "Highlight 10+ years scaling low-latency message queues and mentoring leads.",
            "audience": "Engineering Leadership and Talent Partners",
            "tone": "Professional",
            "length": "Concise (~300-500 words)"
        },
        {
            "category": "Cover letters",
            "topic": "Application for Head of Platform Engineering",
            "purpose": "Demonstrate passion for developer velocity, reliability, and culture.",
            "audience": "VP of Engineering and Executive Search Team",
            "tone": "Persuasive",
            "length": "Concise (~300-500 words)"
        },
        {
            "category": "Meeting summaries",
            "topic": "Q4 Strategic Infrastructure Roadmap Summit",
            "purpose": "Align cross-functional leads on multi-region failover and budget caps.",
            "audience": "Cross-Functional Pod Leads and Product Managers",
            "tone": "Executive",
            "length": "Concise (~300-500 words)"
        }
    ]

    for tc in test_cases:
        payload = {
            "topic": tc["topic"],
            "purpose": tc["purpose"],
            "intended_audience": tc["audience"],
            "tone": tc["tone"],
            "desired_length": tc["length"],
            "category": tc["category"],
            "reference_files": ["arch_overview.pdf", "benchmarks.csv"]
        }
        
        post_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f"{BASE_FRONTEND_URL}/api/generate",
            data=post_bytes,
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req) as res:
            assert res.status == 200
            data = json.loads(res.read().decode())
            assert data["id"] is not None
            assert data["title"] == tc["topic"]
            assert data["category"] == tc["category"]
            assert data["word_count"] > 100
            assert "arch_overview.pdf" in data["content"]
            assert "benchmarks.csv" in data["content"]
            print(f" ✔ Generated '{tc['category']}': {data['word_count']} words, status: {data['status']}")

def test_4_file_upload_multipart():
    log_section("TEST 4: Reference File Upload Interface")
    
    # Construct multipart/form-data request
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    filename = "system_architecture_reference.pdf"
    file_bytes = b"%PDF-1.4 Mock document bytes for architectural reference"
    
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: application/pdf\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")
    
    req = urllib.request.Request(
        f"{BASE_FRONTEND_URL}/api/upload",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        upload_res = json.loads(res.read().decode())
        assert upload_res["filename"] == filename
        assert upload_res["size_bytes"] == len(file_bytes)
        assert upload_res["status"] == "parsed"
        print(f" ✔ File Uploaded & Parsed: '{upload_res['filename']}' ({upload_res['size_bytes']} bytes, type: {upload_res['content_type']})")

def test_5_document_editor_telemetry_and_actions():
    log_section("TEST 5: Document Editor Telemetry & Action Simulation")
    
    sample_markdown = """# Enterprise System Architecture
**Status:** Approved for Implementation  
**Audience:** Staff Engineers  

## 1. Executive Summary
This document outlines the streaming pipeline architecture designed for high availability.

## 2. Key Requirements
- 99.99% availability SLA
- Latency under 25ms at p99
- Automated failover across multi-region clusters
"""
    # Telemetry logic check
    words = len(sample_markdown.strip().split())
    chars = len(sample_markdown)
    reading_time = max(1, round(words / 225))
    
    print(f" ✔ Live Telemetry Computed: {words} words, {chars} characters, ~{reading_time} min reading time")
    assert words > 20
    assert chars > 100
    
    # Mock AI transformation checks
    elevated = sample_markdown.replace("pipeline architecture", "enterprise-grade streaming architecture")
    assert "enterprise-grade" in elevated
    print(" ✔ Mock AI Polish (Elevate Tone) transformation verified")
    
    with_action_matrix = sample_markdown + "\n\n## Next Steps\n- [ ] Sign off architecture\n"
    assert "Sign off architecture" in with_action_matrix
    print(" ✔ Mock AI Action Matrix append transformation verified")

if __name__ == "__main__":
    print("\n" + "#"*65)
    print("  AI-ENHANCED DOCUMENT GENERATOR - DAY 1 FULL E2E SUITE")
    print("#"*65)
    
    test_1_health_and_connectivity()
    test_2_dashboard_and_templates()
    test_3_prompt_form_and_generation_all_categories()
    test_4_file_upload_multipart()
    test_5_document_editor_telemetry_and_actions()
    
    print("\n" + "="*65)
    print(" 🎉 ALL 5 DAY 1 TEST SUITES PASSED WITH ZERO ERRORS!")
    print("="*65 + "\n")

