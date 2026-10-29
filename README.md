# AICTE SmartVerify — SIH26261 MVP

> **AI-Powered Application Validation, Document Authentication, and Regulatory Compliance Verification**  
> *Developed for the Smart India Hackathon (SIH 2026) Problem Statement SIH26261*  
> **Notice**: Independent academic and technical prototype for demonstration and audit evaluation. Not an official AICTE production system.

---

## 1. Overview & Vision

**AICTE SmartVerify** is an enterprise-grade regulatory decision-support system designed to assist scrutiny committees in verifying technical-institution approval applications (Extension of Approval - EoA, Intake increases, and new course approvals).

### Key Architectural Pillars
- **Strict Human-in-the-Loop Guarantee**: Zero automatic approvals or adverse decisions. Automated subsystems only flag discrepancies, link evidence, and score compliance; all regulatory determinations remain with authorized officials.
- **Deterministic, Transparent Validation**: Scrutiny rules, date validations, and institutional record comparisons are deterministic and fully auditable.
- **Evidence-Linked Explainability**: Every validation finding links directly to a source document, page number, and highlighted excerpt.
- **Multi-Tier OCR & Classification**: Combines fast PyMuPDF stream extraction with fallback OCR (Tesseract / PaddleOCR) and heuristic keyword classification.
- **Simulated Authority Verification Adapter**: Modular adapter interface querying simulated State Technical Board and University registries for certificate validity.
- **Immutable, Tamper-Evident Audit Trail**: Every submission, OCR correction, validation run, and committee override is immutably logged with before-and-after states.

---

## 2. Monorepo Structure

```
smartverify/
├── backend/                  # Python FastAPI Backend
│   ├── app/
│   │   ├── api/v1/           # REST API Route Endpoints (Auth, Apps, Docs, Validation, etc.)
│   │   ├── models/           # SQLAlchemy Database Entities (PostgreSQL / SQLite)
│   │   ├── schemas/          # Pydantic Request & Response Models
│   │   ├── services/         # Core Logic (OCR, Classifier, Validation, Compliance, Adapters)
│   │   ├── database.py       # Session management & DB Engine
│   │   └── main.py           # FastAPI application root & middleware
│   ├── tests/                # Automated pytest suite (17 comprehensive tests)
│   ├── requirements.txt      # Python dependencies
│   ├── seed_demo_data.py     # Deterministic demo dataset seeder (8 scenarios)
│   └── smartverify.db        # SQLite development database fallback
├── frontend/                 # Next.js 16 Web Application
│   ├── src/
│   │   ├── app/              # Next.js App Router Pages
│   │   │   ├── applications/ # Dossier List, New Form, [id] 8-Tab Detail View
│   │   │   ├── review-queue/ # Scrutiny Committee Triage Queue
│   │   │   ├── verification/ # Authority Verification Portal & Sandbox
│   │   │   ├── rules/        # Compliance & Checklist Rules Configuration
│   │   │   ├── audit/        # Immutable Audit Trail Browser
│   │   │   ├── settings/     # Demo Reset, Role Switcher, Engine Status
│   │   │   ├── layout.tsx    # Root layout with AuthProvider, Navbar, Sidebar
│   │   │   └── page.tsx      # Executive Overview Dashboard with Live Stats
│   │   ├── components/       # Reusable UI & Modals (EvidenceViewer, FindingDetail)
│   │   └── lib/              # Typed API Client, Auth Context, TypeScript Interfaces
│   ├── package.json          # Next.js, React, Tailwind CSS dependencies
│   └── tsconfig.json         # TypeScript configuration
├── data/
│   ├── synthetic/            # Dynamically generated sample regulatory PDFs
│   └── uploads/              # Isolated, secure uploaded document directory
├── docs/
│   ├── architecture.md       # Full System Architecture & Data Flow Specification
│   ├── api_spec.md           # REST API Reference & Swagger Documentation
│   └── user_guide.md         # Step-by-Step Persona Walkthrough Guide
├── .env.example              # Environment variables template
└── README.md                 # Project documentation & setup instructions
```

---

## 3. Technology Stack

- **Frontend**: Next.js 16.4.3 (App Router), TypeScript 5.9, Tailwind CSS v4, Lucide React icons.
- **Backend**: Python 3.11+ / 3.13, FastAPI 0.115, Pydantic v2, SQLAlchemy 2.0.
- **Database**: PostgreSQL (target production) with automatic SQLite local development fallback.
- **Document Processing**: PyMuPDF (fitz), Pillow, ReportLab (synthetic PDF generator), Tesseract/PaddleOCR fallback.
- **Security**: JWT Bearer token authentication, bcrypt password hashing, UUID-based isolated file storage outside web roots.

---

## 4. Quick Start & Setup Instructions

### Prerequisites
- Node.js (v18.17+ or v20+) and npm
- Python (v3.10, v3.11, or v3.12/v3.13)
- Git

---

### macOS & Linux

#### Step 1: Clone and Configure Environment
```bash
cd smartverify
cp .env.example .env
```

#### Step 2: Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Seed the 8 demonstration scenarios and generate test PDFs
python seed_demo_data.py

# Run automated tests to verify setup
pytest ./tests -v

# Start the FastAPI server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend API and Swagger UI will be available at:* `http://127.0.0.1:8000/docs`

#### Step 3: Frontend Setup (In a New Terminal)
```bash
cd smartverify/frontend
npm install
npm run dev
```
*Frontend application will be accessible at:* `http://localhost:3000`

---

### Windows (PowerShell)

#### Step 1: Configure Environment
```powershell
cd smartverify
Copy-Item .env.example .env
```

#### Step 2: Backend Setup
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Seed demonstration data
python seed_demo_data.py

# Run tests
pytest .\tests -v

# Start backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Step 3: Frontend Setup
```powershell
cd ..\frontend
npm install
npm run dev
```

---

## 5. Demonstration Roles & Authentication

SmartVerify implements genuine account-based authentication and server-enforced role authorization. Unrestricted frontend persona switching has been removed. Role permissions are verified server-side via cryptographically signed JWT tokens and multi-tenant access control dependencies.

To switch accounts, users explicitly log out and sign in using the `/login` portal with separate stored credentials:

| Role | Email / Username | Password | Institution ID | Purpose & Capabilities |
|---|---|---|---|---|
| **Institution User** | `principal@ditm.edu.in`<br>`institution_demo` | `password123` | `1-1092837482` | Create applications, upload regulatory documents, respond to evidence clarification requests. **Tenant isolated**: Cannot view or download documents from other institutions. |
| **Scrutiny Reviewer** | `scrutiny.officer@aicte.gov.in`<br>`reviewer_demo` | `password123` | N/A | Access triage queue, inspect dossiers, review OCR extractions, resolve/override findings, request statutory evidence. |
| **System Administrator** | `admin@aicte.gov.in`<br>`admin_demo` | `password123` | N/A | Configure compliance handbook rules, manage user provisioning, review system-wide audit trails, reset/reseed demonstration databases. |

> **Quick-Fill Shortcuts**: The `/login` page includes convenient 1-click evaluation shortcuts for judges that pre-fill the form fields and authenticate through standard backend credential verification (`POST /api/v1/auth/login`). Unauthenticated role elevation backdoors are strictly prohibited.

---

## 6. Pre-Seeded Demonstration Scenarios

SmartVerify ships pre-loaded with 8 canonical scenarios:

1. **`SIH26-APP-001` (Clean Application)**: Complete EoA submission with all 6 required documents satisfied.
2. **`SIH26-APP-002` (Missing Document)**: State Board NOC omitted; checklist deficiency and high-severity finding flagged.
3. **`SIH26-APP-003` (Expired Document)**: Uploaded NOC validity expired prior to academic year.
4. **`SIH26-APP-004` (Field Mismatch)**: Requested intake (180) exceeds approved intake in approval letter (120).
5. **`SIH26-APP-005` (Institutional Record Mismatch)**: Claimed built-up area contradicts registered portal records.
6. **`SIH26-APP-006` (Duplicate Document Anomaly)**: Identical binary PDF uploaded for two different requirements (detected via SHA-256).
7. **`SIH26-APP-007` (Authority Verification Mismatch)**: Simulated state board query reveals conflicting PID.
8. **`SIH26-APP-008` (Multi-Finding Dossier)**: Compound deficiencies across faculty ratio, intake, and dates.

*To reset the database and regenerate clean test PDFs at any time, click **Reset & Reseed Demo Data** on the Settings page (Admin only) or run `python seed_demo_data.py`.*

---

## 7. Automated Testing Suite

The backend includes a comprehensive automated test suite with **31 passing tests** covering:
- **Multi-User Security & Authorization** (`tests/test_multi_user_security.py`):
  1. Admin authentication & admin profile verification.
  2. Reviewer authentication & review triage scope.
  3. Institution authentication & institution ID binding.
  4. Invalid password and nonexistent user credential rejection (401).
  5. Prevention of role spoofing via client-side state or tampered tokens.
  6. Rejection of user-supplied role fields in API request bodies.
  7. Server-enforced tenant isolation: Rejection of cross-institution application and findings access (403).
  8. Prevention of non-admin modification of compliance rules (403).
  9. Prevention of non-admin user provisioning (403).
  10. Rejection of unauthenticated API calls across all endpoints (401).
  11. Prevention of unauthorized document viewing and streaming downloads (403).
  12. Logout session clearing and `USER_LOGOUT` immutable audit logging.
  13. Admin-only restriction on prototype database resets (403).
- **Core Scrutiny & Business Workflows**:
  - Role-based permissions & profile (`tests/test_auth.py`)
  - Application lifecycle & category checklists (`tests/test_applications.py`)
  - Deterministic 11-dimension scrutiny validation engine (`tests/test_validation.py`)
  - Compliance engine evaluation & authority verification adapter (`tests/test_compliance_and_verification.py`)
  - Immutable audit event logging and scoping (`tests/test_audit.py`)

Run tests anytime with:
```bash
cd smartverify/backend
./venv/bin/pytest tests/ -v
```

---

## 8. Implemented Features & Known Limitations

### Implemented Features
- Full Next.js 16 App Router UI with responsive enterprise compliance dashboard.
- Live overview statistics computed dynamically from database entities.
- Dynamic category-driven document checklists stored in database.
- Multi-tier document parsing with PyMuPDF and fallback OCR support.
- Heuristic keyword document classification.
- Regex entity normalizer for PIDs, dates, intakes, faculty, and receipts.
- Deterministic 11-dimension scrutiny validation engine.
- Side-by-side Evidence Viewer modal with document rendering and snippet highlighting.
- Human-in-the-loop finding management with mandatory override justification.
- Two-way evidence clarification requests between Reviewer and Institution.
- Simulated Issuing Authority Adapter with deterministic sandbox testing.
- Searchable, filterable immutable regulatory audit trail.

### Known Prototype Limitations & Production Roadmap
- **Database**: Development environment utilizes SQLite fallback. Production deployment requires high-availability PostgreSQL with replication.
- **Storage**: Files are stored in a secured local directory (`data/uploads/`). Production roadmap requires S3/GCS compliant object storage with KMS client-side encryption.
- **Asynchronous Workers**: OCR and validation execute synchronously within the request lifecycle for demonstration simplicity. Production deployment should offload processing to Celery/Redis worker queues.
- **Issuing Authorities**: Real-world production requires formal credentialed integration with national APIs (DigiLocker, e-Sanad, State DTE portals) using the extensible `BaseVerificationAdapter` pattern.

---

## 9. Documentation Directory
- [System Architecture Specification](file:///Users/sampadabathe/Desktop/sih26/smartverify/docs/architecture.md)
- [REST API Reference & OpenAPI Endpoints](file:///Users/sampadabathe/Desktop/sih26/smartverify/docs/api_spec.md)
- [Operational User Guide & Persona Walkthrough](file:///Users/sampadabathe/Desktop/sih26/smartverify/docs/user_guide.md)
