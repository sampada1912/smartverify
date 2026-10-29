# AICTE SmartVerify — System Architecture & Design Specification

> **SIH Problem Statement SIH26261**: AI-Powered Application Validation, Document Authentication, and Regulatory Compliance Verification.  
> **Classification**: Independent Academic & Technical Prototype (Not an official AICTE production system).

---

## 1. Executive Summary & Design Philosophy

**AICTE SmartVerify** is an enterprise-grade regulatory decision-support system engineered to streamline scrutiny of technical education institutions applying for approvals, extensions of approval (EoA), and intake modifications.

### Core Architectural Principles
1. **Zero Automated Regulatory Actions (Human-in-the-Loop)**: The system never automatically issues approvals or adverse decisions. Automated subsystems only detect deficiencies, extract evidence snippets, and flag anomalies. All regulatory outcomes remain with authorized human scrutiny committees.
2. **Deterministic, Transparent Validation**: Scrutiny rules, date validations, and institutional record comparisons are evaluated by deterministic, auditable rule functions—not opaque, hallucination-prone generative models.
3. **Evidence-Linked Explainability**: Every validation finding is linked to a concrete source document, page number, observed text snippet, and explicit regulatory rationale.
4. **Pluggable Verification Adapters**: Central and state authority lookups (e.g., State Board NOCs, University Affiliations) adhere to a clean adapter interface (`BaseVerificationAdapter`). In this prototype, deterministic simulated adapters verify certificates against known test registers.
5. **Immutable, Tamper-Evident Audit Logging**: Every upload, OCR extraction, field correction, scrutiny check, reviewer override, and evidence exchange is permanently recorded with actor identity, before-and-after states, and UTC timestamps.

---

## 2. High-Level Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                              CLIENT INTERFACE TIER                                |
|   Next.js 16 (App Router) + TypeScript + Tailwind CSS + Lucide Icons + Responsive UI  |
+------------------------------------------+----------------------------------------+
                                           | HTTPS / REST / JWT
                                           v
+-----------------------------------------------------------------------------------+
|                               API GATEWAY & SECURITY                              |
|          FastAPI v0.115 + CORS Middleware + OAuth2 Password Bearer / JWT          |
|                 Role-Based Access Control (INSTITUTION, REVIEWER, ADMIN)          |
+-----+-------------------+-------------------+-------------------+-----------------+
      |                   |                   |                   |
      v                   v                   v                   v
+-------------+   +---------------+   +---------------+   +-----------------------+
| APPLICATION |   |   DOCUMENT    |   |  VALIDATION   |   | COMPLIANCE & CHECKLIST|
|   SERVICE   |   |   PIPELINE    |   |    ENGINE     |   |         ENGINE        |
+-------------+   +-------+-------+   +-------+-------+   +-----------+-----------+
                          |                   |                       |
            +-------------+-------------+     |                       |
            | Multi-Tier Extraction     |     |                       |
            | 1. PyMuPDF Native Stream  |     |                       |
            | 2. OCR Fallback Adapter   |     |                       |
            | 3. Keyword Classifier     |     |                       |
            | 4. Regex Entity Extractor |     |                       |
            +-------------+-------------+     |                       |
                          |                   v                       v
                          |           +---------------+   +-----------------------+
                          |           | ANOMALY &     |   | VERIFICATION ADAPTER  |
                          |           | DUPLICATE     |   | Simulated Registry    |
                          |           | DETECTION     |   | State Board / Uni     |
                          |           | (SHA-256)     |   | Deterministic Checks  |
                          |           +-------+-------+   +-----------+-----------+
                          |                   |                       |
                          +-------------------+-----------------------+
                                              |
                                              v
+-----------------------------------------------------------------------------------+
|                             DATA & PERSISTENCE TIER                               |
|   SQLAlchemy 2.0 ORM  -->  SQLite (Dev Fallback) / PostgreSQL (Target Production)  |
|   Secure File Storage -->  Outside web root, UUID keys, SHA-256 verification      |
|   Audit Trail Service -->  Immutable chronological event store                    |
+-----------------------------------------------------------------------------------+
```

---

## 3. Subsystem Breakdown

### 3.1 Frontend Tier (`smartverify/frontend`)
- **Framework**: Next.js 16.4.3 with React 19, TypeScript, and Tailwind CSS.
- **Visual Design**: Strict enterprise regulatory theme. Deep navy typography (`#0f172a`), clean slate background (`#f8fafc`), green for passed requirements, amber for pending evidence, red for critical discrepancies. Zero flashy animations or glassmorphic gradients.
- **State & Authentication**: `AuthContext` provides one-click persona switching between `INSTITUTION`, `REVIEWER`, and `ADMIN` with JWT management.
- **Component Architecture**:
  - `Navbar` with regulatory banner, prototype notice, user role badge.
  - `Sidebar` with collapsible navigation covering Overview, Applications, Review Queue, Document Verification, Compliance Rules, Audit Trail, and Settings.
  - 8-Tab Application Dossier (`OverviewTab`, `ChecklistTab`, `DocumentsTab`, `ExtractedDataTab`, `ValidationFindingsTab`, `ComplianceTab`, `VerificationTab`, `AuditTab`).
  - Interactive Modals (`EvidenceViewerModal` for side-by-side snippet inspection, `FindingDetailModal` for overrides with mandatory justification).

### 3.2 Document Processing & OCR Subsystem (`app/services/`)
- **Ingestion & Validation**:
  - Files validated against MIME types (`application/pdf`, `image/png`, `image/jpeg`) and size limits (max 25MB).
  - Stored outside web directories using non-guessable UUID filenames (`app_storage/uploads/`).
  - SHA-256 cryptographic hash calculated immediately upon write.
- **Classification**:
  - Modular heuristic classifier scans document tokens for regulatory keywords (`NOC`, `AFFIDAVIT`, `APPROVAL LETTER`, `FACULTY LIST`, `LAND REVENUE`, `ACCREDITATION`, `FEE RECEIPT`).
  - Returns document category and confidence score. Designed to swap directly with a fine-tuned LayoutLM/BERT classifier.
- **Multi-Tier Text Extraction**:
  - *Tier 1*: Native PyMuPDF text stream extraction (fast, vector-accurate).
  - *Tier 2*: Scanned PDF / Image OCR fallback using Tesseract / PaddleOCR wrapper with error resilience.
- **Entity Normalization**:
  - Regex patterns normalize Dates (`YYYY-MM-DD`), Institution IDs (`1-\d+`), Intake figures, Built-up area (sqm), Faculty counts, and Receipt references.

### 3.3 Scrutiny Validation Engine (`app/services/validation_engine.py`)
Executes deterministic checks across 11 regulatory dimensions:
1. `MISSING_DOCUMENT`: Required checklist documents not uploaded.
2. `MISSING_FIELD`: Document uploaded but critical regulatory identifiers omitted.
3. `INVALID_DATE`: Unparseable date strings or invalid formats.
4. `EXPIRED_DOCUMENT`: Document issue or expiry date predates active academic year.
5. `ID_MISMATCH`: Institution PID extracted from document contradicts application header.
6. `REFERENCE_CONFLICT`: Inconsistent certificate numbers across associated submissions.
7. `FIELD_MISMATCH`: Application values (e.g. requested intake) conflict with document text.
8. `INSTITUTIONAL_RECORD_MISMATCH`: Values contradict synthetic portal records (e.g. land/area records).
9. `INTAKE_INCONSISTENCY`: Requested intake expansion exceeds regulatory caps without necessary faculty/infrastructure evidence.
10. `DUPLICATE_DOCUMENT`: Exact binary match detected via SHA-256 hash or repeated certificate number.
11. `ANOMALY`: Suspicious metadata alterations or post-issuance PDF revisions flagged for review.

### 3.4 Configurable Compliance & Checklist Engine (`app/services/compliance_engine.py`)
- Rules are stored in database tables (`ChecklistRule`, `ComplianceRule`), completely decoupled from frontend code.
- Administrators can activate, deactivate, and adjust evaluation parameters at runtime.
- Evaluates rules into 5 explicit states: `PASS`, `FAIL`, `WARNING`, `NOT_APPLICABLE`, `NEEDS_REVIEW`.

### 3.5 Verification Adapter Interface (`app/services/verification_adapter.py`)
- Abstract interface `BaseVerificationAdapter` defining `verify(authority_name, cert_number, submitted_data)`.
- Implemented as `MockAuthorityVerificationAdapter` querying a seeded database table of mock records across:
  - State Board of Technical Education
  - State Affiliating University Portal
  - Directorate of Technical Education
  - Central Revenue & Land Registry
- Produces deterministic states: `VERIFIED`, `MISMATCH_DETECTED`, `EXPIRED`, `SOURCE_UNAVAILABLE`, `MANUAL_REVIEW_REQUIRED`. Every response is explicitly tagged with `is_simulated = True`.

### 3.6 Immutable Audit Subsystem (`app/services/audit_service.py`)
- Every mutation creates a row in `AuditEvent` with:
  - `timestamp`: UTC ISO timestamp
  - `actor_id`: Username or `system`
  - `actor_role`: `INSTITUTION`, `REVIEWER`, `ADMIN`, or `SYSTEM`
  - `action`: Canonical action enum
  - `entity_type` & `entity_id`
  - `before_state` & `after_state`
  - `details`: Human-readable summary
- Direct modification or deletion of audit events via API endpoints is strictly prohibited.

---

## 4. Database Schema Entity Relationship

```
+--------------------+        +---------------------+        +--------------------+
|       User         |        |     Application     |------->|    DocumentItem    |
| - id (PK)          |        | - id (PK, str)      |        | - id (PK, str)     |
| - username         |        | - institution_id    |        | - sha256_hash      |
| - role (enum)      |        | - category (enum)   |        | - doc_type (enum)  |
+--------------------+        | - status (enum)     |        +---------+----------+
                              | - validation_status |                  |
                              +----------+----------+                  |
                                         |                             v
      +--------------------+-------------+------------+      +--------------------+
      |                    |                          |      |   ExtractedField   |
      v                    v                          v      | - field_name       |
+--------------------+ +---------------------+ +-----------+ | - normalized_value |
|ValidationFinding   | |ComplianceEvaluation | |Checklist  | | - snippet          |
| - category (enum)  | | - rule_id           | | Item      | +--------------------+
| - severity (enum)  | | - status (enum)     | | - status  |
| - status (enum)    | | - evidence_details  | +-----------+
| - evidence_snippet | +---------------------+
+--------------------+
```

---

## 5. Security & Isolation Model

| Dimension | Implementation | Production Roadmap |
|---|---|---|
| **Storage Security** | Stored in dedicated directory outside web root under UUID paths | S3/GCS Object Store with KMS envelope encryption |
| **Authentication** | JWT Bearer tokens with bcrypt password hashing | OIDC / SAML integration with Government SSO (Parichay / Jan Parichay) |
| **Execution Sandbox** | No uploaded file is executed; PDFs read in memory via PyMuPDF | Isolated ephemeral microVM container for untrusted document parsing |
| **Integrity** | SHA-256 fingerprint computed at upload time | WORM (Write Once, Read Many) tamper-evident storage for regulatory dossiers |
| **Authorization** | FastAPI role dependencies (`require_reviewer`, `require_admin`) | Fine-grained ABAC (Attribute-Based Access Control) with regional jurisdiction |
