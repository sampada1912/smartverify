# AICTE SmartVerify — Operational User Guide & Demonstration Walkthrough

> **Problem Statement**: SIH26261 — AI-Powered Application Validation, Document Authentication, and Regulatory Compliance Verification.  
> **Notice**: Independent academic prototype for demonstration purposes only.

---

## 1. Introduction & Authentication Roles

SmartVerify provides three distinct operational personas accessible via the one-click role switcher in the top navigation bar or the **Settings** page:

1. **Institution User (`inst_user1`)**: Technical institute administrative staff creating approval dossiers, uploading regulatory files, and addressing deficiencies.
2. **Scrutiny Committee Reviewer (`reviewer1`)**: Regulatory scrutiny officials examining dossiers, evaluating OCR extractions, requesting evidence, and recording findings.
3. **System Administrator (`admin1`)**: System regulators managing scrutiny rules, category document checklists, and auditing system actions.

---

## 2. Walkthrough: The 8 Canonical Demonstration Scenarios

SmartVerify ships pre-loaded with 8 canonical test scenarios representing the real-world regulatory challenges faced in technical education approvals:

| Application ID | Institution Name & PID | Regulatory Test Scenario | Key Observation in Dossier |
|---|---|---|---|
| **SIH26-APP-001** | Maharashtra Institute of Advanced Technology (`1-3324567891`) | **Clean Compliant Application** | All 6 mandatory documents uploaded; 0 open findings; all compliance rules `PASS`. |
| **SIH26-APP-002** | Gujarat Engineering Research Academy (`1-4412389012`) | **Missing Required Document** | State Technical Board NOC omitted; Checklist item `MISSING`; High-severity deficiency flagged. |
| **SIH26-APP-003** | Karnataka Institute of Technology (`1-5519283746`) | **Expired Document** | NOC certificate validity expired prior to AY 2026-27; Flagged with extracted date snippet. |
| **SIH26-APP-004** | Delhi Polytechnic & Technical Institute (`1-6628192034`) | **Application vs Document Mismatch** | Application requests 180 intake, but uploaded Approval Letter explicitly authorizes only 120. |
| **SIH26-APP-005** | Tamil Nadu College of Architecture (`1-7739201928`) | **Institutional Record Mismatch** | Land & built-up area claimed contradicts registered institutional baseline records. |
| **SIH26-APP-006** | Rajasthan Institute of Engineering (`1-8840192837`) | **Duplicate Document Anomaly** | Same identical PDF uploaded for both Land Revenue and Infrastructure; exact SHA-256 match flagged. |
| **SIH26-APP-007** | Punjab Technical University Campus (`1-9951203948`) | **Authority Verification Mismatch** | State Board simulated registry check returns conflicting institution PID for certificate number. |
| **SIH26-APP-008** | Bengal College of Technology & Science (`1-1029384756`) | **Multi-Finding Complex Dossier** | Multiple compound issues: faculty ratio deficiency, unverified certificate, and date anomalies. |

---

## 3. Institution User Workflow

### Step 1: Create a Technical Institution Application
1. Switch role to **Institution User** via the top-right header selector.
2. In the sidebar, navigate to **Applications** and click **+ New Application**.
3. Enter institution details:
   - Institution Name: *e.g., Pune Apex Institute of Technology*
   - Permanent Institution ID (PID): *e.g., 1-4567890123*
   - Academic Year: *2026-27*
   - Category: *Extension of Approval (EoA)*
   - Course: *Computer Science and Engineering*
   - Existing Intake: *120* | Requested Intake: *120*
4. Click **Create Application**. The system provisions the draft with an auto-generated ID (e.g., `SIH26-APP-009`) and creates the applicable checklist items.

### Step 2: Upload Regulatory Supporting Documents
1. Navigate to the **Documents** tab inside the created dossier.
2. Click **Upload Regulatory Files** and select PDF or image files.
3. The multi-tier pipeline automatically:
   - Generates SHA-256 fingerprint.
   - Classifies document type.
   - Extracts text and normalizes structured fields (PID, dates, intakes).
   - Updates the checklist status from `MISSING` to `SUBMITTED`.

### Step 3: Formal Submission
1. In the **Overview** tab, click **Formally Submit Application**.
2. The dossier moves to `SUBMITTED` status and automated validation checks run immediately.

### Step 4: Respond to Scrutiny Deficiencies
1. If the scrutiny committee requests additional evidence, open the finding or evidence request banner.
2. Submit your written clarification and attach a corrected regulatory document.
3. The validation engine re-evaluates the condition while preserving historical audit logs.

---

## 4. Scrutiny Reviewer Workflow

### Step 1: Triage via Review Queue
1. Switch role to **Reviewer** via the header selector.
2. Click **Review Queue** in the sidebar.
3. Use the filter tabs:
   - **All Queue Items**: All dossiers pending committee review.
   - **High Priority Mismatches**: Fast triage of dossiers with critical intake, PID, or duplicate issues.
   - **Deficiency Pending**: Applications awaiting applicant clarification.
4. Click **Review Dossier** on any application to open its comprehensive scrutiny record.

### Step 2: Examine Evidence-Linked Findings
1. Navigate to the **Validation Findings** tab.
2. Click **Inspect Evidence** on a finding (e.g. `FIELD_MISMATCH` on `SIH26-APP-004`).
3. The system opens the **Evidence Viewer Modal**, displaying the source document, page number, and highlighted excerpt alongside the discrepancy details.

### Step 3: Correct OCR Extraction (If Needed)
1. If a printed document is poorly scanned and an OCR value needs human committee adjustment, open the **Extracted Data** tab.
2. Click **Correct Value** on the relevant field.
3. Enter the verified value and a mandatory justification (e.g. *"Verified against physical seal on page 2"*).
4. Saving automatically re-evaluates validation checks and logs the change to the audit trail.

### Step 4: Finding Resolution & Committee Overrides
1. Open finding actions:
   - **Resolve Finding**: If the institution has addressed the issue satisfactorily.
   - **Request Additional Evidence**: Send an official clarification inquiry to the institution.
   - **Escalate Finding**: Refer to the Regional Standing Committee.
   - **Manual Status Override**: Override an automated finding with a mandatory regulatory justification.

### Step 5: Execute Simulated Authority Verification
1. Navigate to the **Authority Verification** tab.
2. Enter or select an issuing authority (State Technical Board, Affiliating University Portal) and reference number.
3. Click **Execute Authority Query**. The adapter returns deterministic status (`VERIFIED`, `MISMATCH_DETECTED`, `EXPIRED`) clearly tagged with `SIMULATED`.

---

## 5. Administrator Workflow

### Step 1: Manage Scrutiny Rules & Checklists
1. Switch role to **Administrator** via the header selector.
2. Navigate to **Compliance Rules** in the sidebar.
3. Toggle compliance evaluation rules active or disabled with real-time database persistence.
4. Edit requirement descriptions and regulatory citations.
5. In the **Category Document Checklists** tab, toggle mandatory vs. optional enforcement levels.

### Step 2: System-Wide Audit Investigation
1. Navigate to **Audit Trail** in the sidebar.
2. Query events using free-text search, action category filters, or actor filters.
3. Inspect before-and-after states to investigate any reviewer override or document modification.

### Step 3: Reseed Demo Data
1. Navigate to **Settings** in the sidebar.
2. Click **Reset & Reseed Demo Data**.
3. Confirms and executes `POST /api/v1/demo/reset-seed`, restoring all 8 test applications and generating fresh synthetic PDFs.
