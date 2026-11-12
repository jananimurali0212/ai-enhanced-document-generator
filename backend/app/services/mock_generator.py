import uuid
from datetime import datetime
from typing import Dict, Any
from app.models.schemas import GenerateDocumentRequest, DocumentResponse

TEMPLATES_DATA = [
    {
        "id": "proj-doc",
        "name": "Software Architecture Document",
        "category": "Project documentation",
        "description": "Comprehensive system architectural blueprint, module breakdown, APIs, and data models.",
        "icon": "Layers",
        "default_tone": "Technical",
        "default_length": "Standard (~800-1,200 words)",
        "placeholder_topic": "Real-time Event Streaming Platform Architecture",
        "placeholder_purpose": "Define the microservices architecture, event bus, and database choices for high throughput.",
        "placeholder_audience": "Senior Engineering Team, Solutions Architects, and DevOps"
    },
    {
        "id": "tech-report",
        "name": "Cloud Infrastructure Feasibility",
        "category": "Technical reports",
        "description": "In-depth technical analysis, benchmark evaluations, tradeoffs, and system recommendations.",
        "icon": "FileText",
        "default_tone": "Technical",
        "default_length": "In-depth (~1,500-2,500 words)",
        "placeholder_topic": "Evaluating Multi-Region Kubernetes vs Serverless Container Deployments",
        "placeholder_purpose": "Assess latency, cost, failover mechanics, and operational overhead across 3 tier-1 regions.",
        "placeholder_audience": "VP of Infrastructure, Cloud Engineers, Security Compliance Officers"
    },
    {
        "id": "biz-prop",
        "name": "Enterprise AI Transformation Proposal",
        "category": "Business proposals",
        "description": "Persuasive project pitch outlining value proposition, ROI projections, timeline, and deliverables.",
        "icon": "Briefcase",
        "default_tone": "Persuasive",
        "default_length": "Standard (~800-1,200 words)",
        "placeholder_topic": "AI-Powered Customer Onboarding Automation Suite",
        "placeholder_purpose": "Convince executive leadership to sponsor a 6-month pilot to cut manual KYC time by 75%.",
        "placeholder_audience": "Chief Operating Officer, Head of Product, Procurement Committee"
    },
    {
        "id": "resume",
        "name": "Executive & Tech Resume",
        "category": "Resumes",
        "description": "Structured, impact-driven resume highlighting career milestones, competencies, and quantifiable achievements.",
        "icon": "UserCheck",
        "default_tone": "Professional",
        "default_length": "Concise (~300-500 words)",
        "placeholder_topic": "Staff Full-Stack Engineer & Technical Lead Resume",
        "placeholder_purpose": "Showcase 8+ years of scalable SaaS architecture, team mentorship, and cloud migration impact.",
        "placeholder_audience": "Technical Recruiters, Engineering Directors, CTOs"
    },
    {
        "id": "cover-letter",
        "name": "Targeted Role Cover Letter",
        "category": "Cover letters",
        "description": "Compelling narrative linking past performance to prospective company mission and role requirements.",
        "icon": "Mail",
        "default_tone": "Persuasive",
        "default_length": "Concise (~300-500 words)",
        "placeholder_topic": "Application for Principal Solutions Architect at CloudScale AI",
        "placeholder_purpose": "Demonstrate alignment with company culture, highlight key distributed systems achievements.",
        "placeholder_audience": "Hiring Manager and Head of Engineering Talent"
    },
    {
        "id": "meeting-sum",
        "name": "Executive Brief & Action Matrix",
        "category": "Meeting summaries",
        "description": "Crisp synthesis of discussions, key decisions, owner allocations, deadlines, and next steps.",
        "icon": "CheckSquare",
        "default_tone": "Executive",
        "default_length": "Concise (~300-500 words)",
        "placeholder_topic": "Q4 Enterprise Product Roadmap Alignment & Resource Allocation",
        "placeholder_purpose": "Document unanimous consensus on prioritizing API v2 over legacy portal maintenance.",
        "placeholder_audience": "Cross-functional Product, Design, Engineering, and Marketing Leads"
    }
]

def generate_mock_document(req: GenerateDocumentRequest) -> DocumentResponse:
    now_str = datetime.now().strftime("%B %d, %Y - %I:%M %p")
    doc_id = str(uuid.uuid4())[:8]
    
    file_mention = ""
    if req.reference_files and len(req.reference_files) > 0:
        file_mention = f"\n> **Reference Materials Grounding:** Synced and extracted insights from {len(req.reference_files)} uploaded source(s): `{', '.join(req.reference_files)}`.\n"

    # Dynamic Markdown based on category
    category = req.category or "General Document"
    
    if "Project documentation" in category:
        content = f"""# {req.topic}
*System Architecture & Technical Specification*

**Document Version:** 1.0  
**Status:** Approved for Implementation  
**Audience:** {req.intended_audience}  
**Tone:** {req.tone.value} | **Target Scope:** {req.desired_length.value}  
**Generated Date:** {now_str}
{file_mention}
---

## 1. Executive Summary & Objective
The primary purpose of this specification is to **{req.purpose.strip()}**. As digital systems evolve, maintaining high availability, modularity, and rapid delivery cycles is paramount. This document serves as the authoritative blueprint for engineering teams tasked with deploying and validating these solutions.

## 2. Target Audience & System Stakeholders
Designed directly for **{req.intended_audience}**, this specification balances high-level conceptual boundaries with rigorous architectural requirements:
- **Core Engineering:** Interface contracts, schema definitions, and protocol standards.
- **Operations & SRE:** Telemetry hooks, health check endpoints, and failover topologies.
- **Security & Compliance:** Token lifecycle policies, encryption in-transit (TLS 1.3), and zero-trust perimeter access.

## 3. High-Level Architectural Diagram
```
+-------------------------------------------------------+
|                 Client Application Layer              |
+-------------------------------------------------------+
                           |
                     (HTTPS / gRPC)
                           v
+-------------------------------------------------------+
|           API Gateway & Auth Verification             |
+-------------------------------------------------------+
         |                                  |
         v                                  v
+------------------------+      +------------------------+
| Core Domain Service    | <--> | Async Pipeline Worker  |
+------------------------+      +------------------------+
         |                                  |
         +-----------------+----------------+
                           |
                           v
+-------------------------------------------------------+
|           Resilient Storage / Cache Layer             |
+-------------------------------------------------------+
```

## 4. Key Functional Requirements
1. **Deterministic Latency:** 99th percentile response time must not exceed 150ms under peak load.
2. **Horizontal Scalability:** Stateless compute workers capable of autoscaling based on memory saturation.
3. **Auditability & Observability:** Structured JSON logs published to centralized tracing hubs.

## 5. Security & Data Protection Measures
- Enforce mutual TLS between internal container namespaces.
- Secret rotation managed via automated vault managers with strict IAM boundary checks.

## 6. Implementation Milestones
| Milestone | Focus Deliverables | Target Timeline | Status |
| :--- | :--- | :--- | :--- |
| Phase 1 | Foundation, Schema Contracts & Mock Harness | Weeks 1-2 | Completed |
| Phase 2 | Core Engine Implementation & Async Queues | Weeks 3-5 | In Progress |
| Phase 3 | Load Profiling, Pentesting & Pilot Rollout | Weeks 6-8 | Planned |

---
*Created by AI-Enhanced Document Generator — Ready for review and export.*
"""

    elif "Business proposals" in category:
        content = f"""# Strategic Business Proposal: {req.topic}

**Target Client / Organization:** {req.intended_audience}  
**Prepared On:** {now_str}  
**Proposal Stance:** {req.tone.value}  
**Executive Champion:** Enterprise AI Solutions Group  
{file_mention}
---

## 1. Executive Briefing & Opportunity
Every forward-thinking enterprise faces the imperative to innovate while accelerating operational efficiency. This proposal presents a turnkey approach to **{req.purpose.strip()}**.

By pairing best-in-class generative intelligence with human-in-the-loop governance, we eliminate frictional bottlenecks and deliver rapid time-to-value.

## 2. Identified Pain Points vs. Proposed Value
| Operational Challenge | Today's Baseline | Proposed Solution Impact |
| :--- | :--- | :--- |
| Manual Document Drafting | 4.5 hours per technical dossier | Under 8 minutes with smart grounding |
| Inconsistent Branding & Tone | Disjointed cross-team output | Unified enterprise styleguide adherence |
| Knowledge Silos | Static PDFs lost in cloud storage | Context-aware ingestion and citation |

## 3. Scope of Work & Deliverables
Our engagement is structured into three iterative deliverables:
1. **Discovery & Asset Integration:** Ingest existing reference collateral and benchmark compliance rules.
2. **Custom Template & Workflow Deployment:** Tailored prompt pipelines suited to `{req.intended_audience}`.
3. **Pilot Evaluation & Enterprise Scaling:** Continuous metric tracking, user enablement workshops, and full team onboarding.

## 4. Projected Return on Investment (ROI)
- **Time Savings:** Estimated 70% decrease in preliminary draft turnaround.
- **Cost Efficiency:** Amortized return within 90 days of general deployment.
- **Quality Assurance:** Reduced revision cycles from an average of 4 iterations down to 1.5.

## 5. Next Steps & Approval
To commence Phase 1 integration, please review and endorse the attached service charter. We look forward to partnering with your leadership to achieve these transformative objectives.
"""

    elif "Technical reports" in category:
        content = f"""# Technical Investigation & Analysis Report
## Subject: {req.topic}

**Author:** Technical Research & Architecture Group  
**Review Board:** {req.intended_audience}  
**Report Tone:** {req.tone.value}  
**Timestamp:** {now_str}  
{file_mention}
---

### 1. Abstract & Problem Formulation
This technical report documents our empirical findings and analytical evaluation regarding **{req.purpose.strip()}**. As workloads grow in complexity, choosing the right paradigm requires benchmarking real-world throughput, operational complexity, and fault tolerance.

### 2. Experimental Methodology
We performed rigorous baseline testing simulating production-grade traffic:
- **Test Scenarios:** 10,000 synthetic requests/second across multiple availability zones.
- **Telemetry Collected:** CPU saturation, memory allocation leaks, p99 latency distributions, and cold-start overhead.
- **Controlled Variables:** Consistent network bandwidth and standardized container compute sizes.

### 3. Empirical Findings & Benchmarks
```
Throughput (Requests/sec)
---------------------------------------------
Standard Monolith     : [████████░░░░░░░░░░]  3,200 req/s
Optimized Microservice: [███████████████░░░]  7,800 req/s
Target Modern Stack   : [██████████████████]  11,400 req/s
```

### 4. Tradeoff Matrix
- **Advantages:** Immediate 3x scalability boost, fine-grained fault isolation, modular deployment pipelines.
- **Considerations:** Requires disciplined distributed tracing and centralized log correlation.

### 5. Final Recommendations
Based on empirical metrics, we strongly advocate transitioning to the modernized architecture outlined in Section 3 to fulfill the requirements of {req.intended_audience}.
"""

    elif "Meeting summaries" in category:
        content = f"""# Executive Meeting Brief & Action Matrix
## Topic: {req.topic}

**Convened On:** {now_str}  
**Attendees & Stakeholders:** {req.intended_audience}  
**Synthesis Tone:** {req.tone.value}  
{file_mention}
---

### 1. Meeting Objectives & Context
The session was convened to establish strategic alignment and **{req.purpose.strip()}**.

### 2. Key Decisions Reached
- **Decision A:** Unanimous sign-off on the foundational Day 1 UI shell and technical layout.
- **Decision B:** Standardized on React + Tailwind CSS frontend coupled with a modular Python FastAPI backend.
- **Decision C:** Multi-file drag-and-drop reference support prioritized for subsequent model grounding.

### 3. Discussion Points & Open Questions
1. **API Integration Strategy:** Confirmed initial mock-first methodology to allow UI verification prior to live LLM binding.
2. **Performance Constraints:** Agreed on optimistic client-side feedback for all generation actions.

### 4. Action Items & Accountability Matrix
| Action Item | Responsible Owner | Target Due Date | Status |
| :--- | :--- | :--- | :--- |
| Complete Frontend Shell & Tailwind Layout | Lead UI Engineer | End of Day 1 | Completed |
| Finalize FastAPI Endpoints & Pydantic Validation | Backend Lead | End of Day 1 | Completed |
| Wire Reference File Ingestion Parser | Data Pipeline Dev | Day 2 | Next Up |
"""

    elif "Resumes" in category:
        content = f"""# {req.topic}
**Contact:** engineering-lead@example.com | LinkedIn: /in/lead-engineer | GitHub: @techarchitect  
**Target Focus:** {req.purpose.strip()}  
**Intended For:** {req.intended_audience}  
{file_mention}
---

## PROFESSIONAL SUMMARY
Results-driven engineering professional with extensive experience leading multidisciplinary teams to build reliable, high-throughput cloud applications. Adept at bridging strategic business vision with pragmatic software execution, consistently delivering products that elevate customer satisfaction and engineering velocity.

## CORE COMPETENCIES
- **Languages & Frameworks:** Python (FastAPI, Flask), JavaScript/TypeScript (React, Node.js), Go, SQL
- **Cloud & DevOps:** AWS, Google Cloud, Docker, Kubernetes, CI/CD Pipelines, Terraform
- **Architecture:** Microservices, Event-Driven Architecture, REST/gRPC, Secure API Design

## SELECTED PROFESSIONAL EXPERIENCE

### **Staff Software Architect** | *NextGen Systems Inc.* (2022 – Present)
- Spearheaded the modernization of enterprise document pipelines, decreasing processing times by 62%.
- Mentored 14 engineers across frontend and backend disciplines, implementing code health standards.
- Designed resilient microservices serving over 2M monthly active requests at 99.99% uptime.

### **Senior Full-Stack Developer** | *CloudScale Solutions* (2019 – 2022)
- Built interactive analytics dashboards using React, Tailwind CSS, and asynchronous backend services.
- Reduced p95 latency from 450ms to 95ms via intelligent caching and database indexing.

## EDUCATION & CERTIFICATIONS
- **B.S. in Computer Science** — State University
- **Certified Cloud Solutions Architect** — 2024
"""

    else: # Cover letters & fallback
        content = f"""# {req.topic}

{now_str}

**To:** {req.intended_audience}  
**Regarding:** Application & Opportunity Overview  
{file_mention}
Dear Hiring Team,

I am writing to express my enthusiastic interest in joining your organization to contribute toward **{req.purpose.strip()}**. With a proven track record of engineering scalable platforms, intuitive user interfaces, and robust backend architectures, I am eager to apply my background to your high-impact initiatives.

Throughout my career, I have prioritized user-centric engineering—ensuring that every line of code translates directly into reliable performance and delightful user experiences. Whether developing high-velocity FastAPI microservices or crafting polished React frontends with Tailwind CSS, I thrive in collaborative environments where continuous improvement is the standard.

What excites me most about your team is your dedication to technological excellence and practical innovation. I welcome the opportunity to discuss how my skill set and passion can accelerate your product roadmap.

Thank you for your time and thoughtful consideration.

Sincerely,  
**Candidate Name**  
*Full-Stack Engineer & System Architect*
"""

    word_count = len(content.split())
    
    return DocumentResponse(
        id=doc_id,
        title=req.topic,
        category=category,
        tone=req.tone.value,
        desired_length=req.desired_length.value,
        content=content,
        word_count=word_count,
        created_at=now_str,
        status="completed"
    )
