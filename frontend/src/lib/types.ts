export type UserRole = "INSTITUTION" | "REVIEWER" | "ADMIN";

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  institution_id?: string | null;
  is_active: boolean;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  role: UserRole;
  username: string;
  institution_id?: string | null;
  full_name: string;
}

export type ApplicationCategory =
  | "EXTENSION_OF_APPROVAL"
  | "INCREASE_IN_INTAKE"
  | "NEW_INSTITUTION"
  | "NEW_PROGRAMME";

export type ApplicationStatus =
  | "DRAFT"
  | "SUBMITTED"
  | "UNDER_SCRUTINY"
  | "DEFICIENCIES_COMMUNICATED"
  | "PENDING_REVIEW"
  | "SCRUTINY_COMPLETED";

export type ValidationOverallStatus =
  | "NOT_EVALUATED"
  | "CLEAN"
  | "DEFICIENCIES_DETECTED"
  | "HIGH_RISK";

export interface Application {
  id: string;
  institution_id: string;
  institution_name: string;
  category: ApplicationCategory;
  academic_year: string;
  programme: string;
  course_name: string;
  existing_intake: number;
  requested_intake: number;
  contact_person: string;
  contact_email: string;
  contact_phone: string;
  status: ApplicationStatus;
  validation_status: ValidationOverallStatus;
  assigned_reviewer_id?: number | null;
  submission_date?: string | null;
  created_at: string;
  updated_at: string;
  document_count?: number;
  open_findings_count?: number;
  high_findings_count?: number;
  // Aliases for UI display
  application_category?: string;
  institution_code?: string;
}

export interface ApplicationDetail extends Application {
  documents: DocumentItem[];
  extracted_fields: ExtractedField[];
  checklist: ApplicationChecklistItem[];
  validation_findings: ValidationFinding[];
  compliance_evaluations: ComplianceEvaluation[];
  verification_results: VerificationResult[];
}

export type DocumentType =
  | "PREVIOUS_APPROVAL"
  | "AFFIDAVIT"
  | "FACULTY_LIST"
  | "NOC"
  | "ACCREDITATION_CERT"
  | "INFRASTRUCTURE_EVIDENCE"
  | "PAYMENT_RECEIPT"
  | "OTHER";

export type OCRStatus = "PENDING" | "COMPLETED" | "FAILED";

export interface DocumentItem {
  id: string;
  application_id: string;
  original_filename: string;
  stored_filename: string;
  file_size_bytes: number;
  mime_type: string;
  sha256_hash: string;
  doc_type: DocumentType;
  classification_confidence: number;
  classification_method: string;
  ocr_status: OCRStatus;
  ocr_engine_used: string;
  page_count: number;
  uploaded_at: string;
  extracted_text_preview?: string | null;
}

export interface ExtractedField {
  id: number;
  document_id: string;
  application_id: string;
  field_name: string;
  extracted_value: string;
  normalized_value: string;
  page_number: number;
  confidence: number;
  extraction_method: string;
  snippet?: string | null;
  is_corrected: boolean;
  corrected_value?: string | null;
  corrected_by?: string | null;
  corrected_at?: string | null;
  created_at: string;
}

export interface ApplicationChecklistItem {
  id: number;
  application_id: string;
  rule_code: string;
  requirement_name: string;
  document_type: string;
  is_required: boolean;
  is_submitted: boolean;
  document_id?: string | null;
  validation_status: string;
  explanation?: string | null;
  evidence_summary?: string | null;
  updated_at: string;
}

export interface ChecklistRule {
  id: number;
  rule_code: string;
  category: string;
  document_type: string;
  requirement_name: string;
  description: string;
  is_required: boolean;
  is_active: boolean;
  version: string;
  created_at: string;
  updated_at: string;
}

export type FindingCategory =
  | "MISSING_DOCUMENT"
  | "MISSING_FIELD"
  | "INVALID_DATE"
  | "EXPIRED_DOCUMENT"
  | "ID_MISMATCH"
  | "REFERENCE_CONFLICT"
  | "FIELD_MISMATCH"
  | "INSTITUTIONAL_RECORD_MISMATCH"
  | "INTAKE_INCONSISTENCY"
  | "DUPLICATE_DOCUMENT"
  | "ANOMALY";

export type FindingSeverity = "INFO" | "LOW" | "MEDIUM" | "HIGH";

export type FindingStatus =
  | "OPEN"
  | "UNDER_REVIEW"
  | "REQUESTED_INFORMATION"
  | "RESOLVED"
  | "ESCALATED";

export interface ValidationFinding {
  id: string;
  application_id: string;
  document_id?: string | null;
  category: FindingCategory;
  severity: FindingSeverity;
  status: FindingStatus;
  title: string;
  explanation: string;
  expected_value?: string | null;
  observed_value?: string | null;
  source_record?: string | null;
  page_number?: number | null;
  evidence_snippet?: string | null;
  recommended_action: string;
  resolution_notes?: string | null;
  override_reason?: string | null;
  resolved_by?: string | null;
  resolved_at?: string | null;
  detection_timestamp: string;
}

export type VerificationStatus =
  | "VERIFIED"
  | "MISMATCH_DETECTED"
  | "EXPIRED"
  | "SOURCE_UNAVAILABLE"
  | "VERIFICATION_PENDING"
  | "MANUAL_REVIEW_REQUIRED";

export interface VerificationResult {
  id: number;
  application_id: string;
  document_id?: string | null;
  authority_name: string;
  certificate_number: string;
  status: VerificationStatus;
  is_simulated: boolean;
  check_timestamp: string;
  mismatch_details?: string | null;
}

export interface MockAuthorityRecord {
  id: number;
  authority_name: string;
  certificate_number: string;
  institution_id: string;
  institution_name: string;
  doc_type: string;
  issue_date?: string | null;
  expiry_date?: string | null;
  status: string;
  is_simulated: boolean;
}

export type ComplianceStatus =
  | "PASS"
  | "FAIL"
  | "WARNING"
  | "NOT_APPLICABLE"
  | "NEEDS_REVIEW";

export type ComplianceRuleSeverity = "INFO" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface ComplianceRule {
  id: number;
  rule_id: string;
  rule_name: string;
  description: string;
  category_condition: string;
  required_evidence_type: string;
  evaluation_logic: string;
  severity: ComplianceRuleSeverity;
  is_enabled: boolean;
  version: string;
  effective_date: string;
}

export interface ComplianceEvaluation {
  id: number;
  application_id: string;
  rule_id: string;
  rule_name: string;
  status: ComplianceStatus;
  explanation: string;
  evidence_summary?: string | null;
  evaluated_at: string;
}

export type EvidenceRequestStatus = "PENDING" | "RESPONDED" | "CLOSED";

export interface EvidenceRequest {
  id: string;
  application_id: string;
  finding_id?: string | null;
  requested_by: string;
  request_text: string;
  status: EvidenceRequestStatus;
  response_text?: string | null;
  response_document_id?: string | null;
  requested_at: string;
  responded_at?: string | null;
}

export interface AuditEvent {
  id: number;
  timestamp: string;
  actor_id: string;
  actor_role: string;
  action: string;
  entity_type: string;
  entity_id: string;
  application_id?: string | null;
  before_state?: string | null;
  after_state?: string | null;
  details?: string | null;
  ip_address?: string | null;
}

export interface DashboardStats {
  total_applications: number;
  draft_applications: number;
  submitted_applications: number;
  applications_needing_review: number;
  open_findings_count: number;
  missing_documents_count: number;
  expired_documents_count: number;
  verification_status_distribution: Record<string, number>;
  category_distribution: Record<string, number>;
  recent_activity: AuditEvent[];
  recent_applications: Application[];
}
