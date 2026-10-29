# AICTE SmartVerify — REST API Specification & Endpoints Reference

> **Base URL**: `http://localhost:8000/api/v1`  
> **Interactive Swagger Documentation**: `http://localhost:8000/docs`  
> **ReDoc Documentation**: `http://localhost:8000/redoc`

---

## 1. Authentication & Session

### `POST /auth/demo-login`
Instant demonstration role authentication.
- **Request Body**:
  ```json
  {
    "role": "REVIEWER" // "INSTITUTION" | "REVIEWER" | "ADMIN"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "role": "REVIEWER",
    "username": "reviewer1",
    "institution_id": null,
    "full_name": "Senior Scrutiny Reviewer"
  }
  ```

### `GET /auth/me`
Retrieve details of the active authenticated session.
- **Headers**: `Authorization: Bearer <token>`
- **Response `200 OK`**: User profile with role, institution ID, and permissions.

---

## 2. Application Scrutiny Dossiers

### `GET /applications`
Query list of applications with filtering and pagination.
- **Query Parameters**:
  - `category`: `EXTENSION_OF_APPROVAL`, `INCREASE_IN_INTAKE`, etc.
  - `status`: `DRAFT`, `SUBMITTED`, `UNDER_SCRUTINY`, `DEFICIENCIES_COMMUNICATED`, etc.
  - `validation_status`: `NOT_EVALUATED`, `CLEAN`, `DEFICIENCIES_DETECTED`, `HIGH_RISK`
  - `search`: Full text search on ID, institution name, or PID.
  - `skip`: Integer offset (default `0`)
  - `limit`: Page size (default `50`)
- **Response `200 OK`**:
  ```json
  {
    "total": 8,
    "items": [
      {
        "id": "SIH26-APP-001",
        "institution_id": "1-3324567891",
        "institution_name": "Maharashtra Institute of Advanced Technology",
        "category": "EXTENSION_OF_APPROVAL",
        "academic_year": "2026-27",
        "programme": "ENGINEERING_AND_TECHNOLOGY",
        "course_name": "Computer Science and Engineering",
        "existing_intake": 120,
        "requested_intake": 120,
        "status": "UNDER_SCRUTINY",
        "validation_status": "CLEAN",
        "document_count": 6,
        "open_findings_count": 0,
        "high_findings_count": 0,
        "submission_date": "2026-10-15T09:30:00Z",
        "created_at": "2026-10-14T11:00:00Z",
        "updated_at": "2026-10-15T09:30:00Z"
      }
    ]
  }
  ```

### `POST /applications`
Create a new technical institution application draft.
- **Request Body**: `ApplicationCreate` (institution_id, institution_name, category, course, intake, contact details).
- **Behavior**: Auto-generates unique `SIH26-APP-XXX` ID and provisions default checklist items based on category rules.

### `GET /applications/{id}`
Retrieve complete application header, metadata, and aggregate counts.

### `POST /applications/{id}/submit`
Formally submit application for regulatory scrutiny committee examination.
- **Behavior**: Moves status from `DRAFT` to `SUBMITTED`, stamps submission timestamp, and triggers an automated validation and compliance run.

---

## 3. Document Ingestion, OCR & Extraction

### `POST /applications/{id}/documents`
Upload one or multiple regulatory supporting files (PDF, PNG, JPEG).
- **Content-Type**: `multipart/form-data`
- **Form Data**: `files` (array of file binaries)
- **Pipeline Processing**:
  1. Validates MIME type and file size (< 25MB).
  2. Generates SHA-256 fingerprint.
  3. Writes to outside-web storage under UUID filename.
  4. Heuristic classification of document category.
  5. Multi-tier text extraction (PyMuPDF -> OCR fallback).
  6. Structured entity extraction (PID, dates, intakes, area, faculty, receipts).
  7. Updates checklist status and logs audit event.

### `GET /documents/{id}/view`
Stream PDF or image for secure, authenticated inline browser inspection.
- **Headers**: `Authorization: Bearer <token>`
- **Content-Disposition**: `inline; filename="<original_filename>"`

### `GET /applications/{id}/fields`
Retrieve all normalized structured OCR fields extracted from dossier documents.

### `PUT /fields/{id}/correct`
Reviewer correction of an extracted OCR field.
- **Request Body**:
  ```json
  {
    "corrected_value": "180",
    "justification": "Verified against physical stamp on page 2 of approval letter"
  }
  ```
- **Behavior**: Records corrected value, timestamp, reviewer username, and writes immutable audit entry. Re-triggers validation checks.

---

## 4. Scrutiny Validation & Findings

### `POST /applications/{id}/validate`
Trigger deterministic regulatory validation rules across all uploaded documents and application parameters.
- **Response**: Array of `ValidationFinding` objects.

### `GET /applications/{id}/findings`
Retrieve all open, resolved, and escalated findings for an application.

### `PUT /findings/{id}/resolve`
Reviewer resolves an open finding with explanatory notes.
- **Request Body**:
  ```json
  {
    "action": "RESOLVE",
    "resolution_notes": "Institution provided valid clarification letter via evidence request."
  }
  ```

### `PUT /findings/{id}/override`
Reviewer overrides a finding status with mandatory regulatory justification.
- **Request Body**:
  ```json
  {
    "new_status": "RESOLVED",
    "override_reason": "Regional Committee authorized waiver as per AICTE Gazette Notification Sec 4(b)"
  }
  ```

---

## 5. Compliance & Checklist Rules Engine

### `GET /applications/{id}/checklist`
Retrieve dynamic category-driven checklist requirements and submission status.

### `GET /checklist/rules`
Administrator listing of all configurable checklist rules.

### `PUT /checklist/rules/{rule_code}`
Configure checklist rule (toggle mandatory status, enable/disable).

### `POST /applications/{id}/evaluate`
Execute the configurable compliance engine against the dossier.
- **Evaluates**:
  - `RULE-EOA-PREV-APPROVAL`: Previous year approval letter continuity.
  - `RULE-EOA-NOC`: Valid, unexpired State Board NOC.
  - `RULE-EOA-FACULTY-RATIO`: Cadre and faculty count sufficiency.
  - `RULE-LAND-BUILTUP`: Infrastructure adequacy.
  - `RULE-VERIF-NOC`: Authority verification match.
  - `RULE-NO-DUPLICATE-DOCS`: Binary file uniqueness.
  - `RULE-INST-RECORD-CONSISTENCY`: Concordance with registered institutional profile.
  - `RULE-INTAKE-REQUEST-LIMIT`: Intake expansion compliance.
- **Returns**: Statuses `PASS`, `FAIL`, `WARNING`, `NOT_APPLICABLE`, `NEEDS_REVIEW`.

---

## 6. Verification Adapter (Simulated Registry)

### `POST /applications/{id}/verify`
Query issuing authority registry for document authenticity.
- **Request Body**:
  ```json
  {
    "certificate_number": "NOC-2024-MH-4421",
    "authority_name": "STATE_TECHNICAL_BOARD_MOCK"
  }
  ```
- **Response**:
  ```json
  {
    "id": 1,
    "application_id": "SIH26-APP-001",
    "authority_name": "STATE_TECHNICAL_BOARD_MOCK",
    "certificate_number": "NOC-2024-MH-4421",
    "status": "VERIFIED",
    "is_simulated": true,
    "check_timestamp": "2026-10-25T14:15:00Z",
    "mismatch_details": null
  }
  ```

### `GET /verification/mock-records`
List all seeded demonstration records in the mock issuing authority registry.

---

## 7. Audit Trail

### `GET /audit`
Search and filter immutable audit events.
- **Query Parameters**: `application_id`, `action`, `actor_id`, `entity_type`, `search`, `skip`, `limit`.
- **Response**: Chronological list of events with `timestamp`, `actor_id`, `action`, `entity_type`, `before_state`, `after_state`, and `details`.

---

## 8. Demonstration Management

### `POST /demo/reset-seed`
Reset SQLite/PostgreSQL database to initial state and reseed all 8 canonical SIH test scenarios and synthetic PDFs.
- **Access**: Available to all roles for demonstration convenience.
