import {
  AuthToken,
  User,
  Application,
  ApplicationDetail,
  DocumentItem,
  ExtractedField,
  ApplicationChecklistItem,
  ChecklistRule,
  ValidationFinding,
  ComplianceEvaluation,
  ComplianceRule,
  VerificationResult,
  MockAuthorityRecord,
  EvidenceRequest,
  AuditEvent,
  DashboardStats,
  UserRole,
} from "./types";

function getApiBaseUrl(): string {
  let raw = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  raw = raw.trim();
  if (!raw.startsWith("http://") && !raw.startsWith("https://")) {
    raw = `https://${raw}`;
  }
  raw = raw.replace(/\/+$/, "");
  if (!raw.endsWith("/api/v1")) {
    raw = `${raw}/api/v1`;
  }
  return raw;
}

const API_BASE = getApiBaseUrl();

function getAuthHeaders(): HeadersInit {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("smartverify_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }
  return headers;
}

export const api = {
  // Auth
  async login(usernameOrEmail: string, password: string): Promise<AuthToken> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: usernameOrEmail, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Authentication failed. Please check your credentials.");
    }
    const data = await res.json();
    if (typeof window !== "undefined") {
      localStorage.setItem("smartverify_token", data.access_token);
      localStorage.setItem("smartverify_user", JSON.stringify(data));
    }
    return data;
  },

  async logout(): Promise<void> {
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: "POST",
        headers: getAuthHeaders(),
      });
    } catch {
      // Ignore network/server errors during local logout cleanup
    } finally {
      if (typeof window !== "undefined") {
        localStorage.removeItem("smartverify_token");
        localStorage.removeItem("smartverify_user");
      }
    }
  },

  async getCurrentUser(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch user profile");
    return res.json();
  },

  // Dashboard
  async getDashboardStats(): Promise<DashboardStats> {
    const res = await fetch(`${API_BASE}/dashboard/stats`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch dashboard metrics");
    return res.json();
  },

  // Applications
  async listApplications(params?: {
    category?: string;
    status?: string;
    validation_status?: string;
    search?: string;
  }): Promise<{ total: number; items: Application[] }> {
    const query = new URLSearchParams();
    if (params?.category) query.set("category", params.category);
    if (params?.status) query.set("status", params.status);
    if (params?.validation_status) query.set("validation_status", params.validation_status);
    if (params?.search) query.set("search", params.search);

    const res = await fetch(`${API_BASE}/applications?${query.toString()}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to list applications");
    return res.json();
  },

  async getApplication(id: string): Promise<Application> {
    const res = await fetch(`${API_BASE}/applications/${id}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to get application");
    return res.json();
  },

  async getApplications(): Promise<Application[]> {
    const res = await this.listApplications();
    return res.items;
  },

  async getApplicationDetail(id: string): Promise<ApplicationDetail> {
    const [app, documents, extracted_fields, checklist, validation_findings, compliance_evaluations, verification_results] = await Promise.all([
      this.getApplication(id),
      this.listDocuments(id).catch(() => []),
      this.listApplicationFields(id).catch(() => []),
      this.getApplicationChecklist(id).catch(() => []),
      this.getFindings(id).catch(() => []),
      this.getCompliance(id).catch(() => []),
      this.getVerificationResults(id).catch(() => []),
    ]);
    return {
      ...app,
      documents,
      extracted_fields,
      checklist,
      validation_findings,
      compliance_evaluations,
      verification_results,
    };
  },

  async createApplication(data: Partial<Application>): Promise<Application> {
    const res = await fetch(`${API_BASE}/applications`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to create application");
    return res.json();
  },

  async updateApplication(id: string, data: Partial<Application>): Promise<Application> {
    const res = await fetch(`${API_BASE}/applications/${id}`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update application");
    return res.json();
  },

  async submitApplication(id: string): Promise<Application> {
    const res = await fetch(`${API_BASE}/applications/${id}/submit`, {
      method: "POST",
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to submit application");
    return res.json();
  },

  async reopenApplication(id: string): Promise<Application> {
    const res = await fetch(`${API_BASE}/applications/${id}/reopen`, {
      method: "POST",
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to reopen application");
    return res.json();
  },

  // Documents
  async listDocuments(applicationId: string): Promise<DocumentItem[]> {
    const res = await fetch(`${API_BASE}/applications/${applicationId}/documents`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to list documents");
    return res.json();
  },

  getDocumentViewUrl(docId: string): string {
    return `${API_BASE}/documents/${docId}/view`;
  },

  async uploadDocuments(
    applicationId: string,
    files: File[],
    docTypes?: (string | null | undefined)[]
  ): Promise<any> {
    const formData = new FormData();
    files.forEach((f) => formData.append("files", f));
    if (docTypes && docTypes.length > 0) {
      docTypes.forEach((dt) => {
        formData.append("doc_types", dt || "");
      });
    }

    const token = typeof window !== "undefined" ? localStorage.getItem("smartverify_token") : null;
    const headers: HeadersInit = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE}/applications/${applicationId}/documents`, {
      method: "POST",
      headers,
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Document upload failed");
    }
    return res.json();
  },

  async deleteDocument(docId: string): Promise<{ message: string; deleted_id: string }> {
    const res = await fetch(`${API_BASE}/documents/${docId}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to delete document");
    }
    return res.json();
  },

  async updateDocumentType(docId: string, docType: string): Promise<DocumentItem> {
    const res = await fetch(`${API_BASE}/documents/${docId}/type`, {
      method: "PATCH",
      headers: getAuthHeaders(),
      body: JSON.stringify({ doc_type: docType }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to update document type");
    }
    return res.json();
  },


  // Fields
  async listApplicationFields(applicationId: string): Promise<ExtractedField[]> {
    const res = await fetch(`${API_BASE}/applications/${applicationId}/fields`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch extracted fields");
    return res.json();
  },

  async correctField(fieldId: number, correctedValue: string, justification: string): Promise<ExtractedField> {
    const res = await fetch(`${API_BASE}/fields/${fieldId}/correct`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        corrected_value: correctedValue,
        justification,
      }),
    });
    if (!res.ok) throw new Error("Failed to correct field");
    return res.json();
  },

  // Checklist
  async getApplicationChecklist(applicationId: string): Promise<ApplicationChecklistItem[]> {
    const res = await fetch(`${API_BASE}/applications/${applicationId}/checklist`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch checklist");
    return res.json();
  },

  async listChecklistRules(): Promise<ChecklistRule[]> {
    const res = await fetch(`${API_BASE}/checklist/rules`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch checklist rules");
    return res.json();
  },

  async updateChecklistRule(ruleCode: string, data: Partial<ChecklistRule>): Promise<ChecklistRule> {
    const res = await fetch(`${API_BASE}/checklist/rules/${ruleCode}`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update checklist rule");
    return res.json();
  },

  // Validation & Findings
  async triggerValidation(applicationId: string): Promise<ValidationFinding[]> {
    const res = await fetch(`${API_BASE}/applications/${applicationId}/validate`, {
      method: "POST",
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Validation trigger failed");
    return res.json();
  },

  async getFindings(applicationId: string): Promise<ValidationFinding[]> {
    const res = await fetch(`${API_BASE}/applications/${applicationId}/findings`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch findings");
    return res.json();
  },

  async resolveFinding(findingId: string, action: string, notes: string): Promise<ValidationFinding> {
    const res = await fetch(`${API_BASE}/findings/${findingId}/resolve`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify({ action, resolution_notes: notes }),
    });
    if (!res.ok) throw new Error("Failed to resolve finding");
    return res.json();
  },

  async overrideFinding(findingId: string, newStatus: string, reason: string): Promise<ValidationFinding> {
    const res = await fetch(`${API_BASE}/findings/${findingId}/override`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify({ new_status: newStatus, override_reason: reason }),
    });
    if (!res.ok) throw new Error("Failed to override finding");
    return res.json();
  },

  // Compliance
  async evaluateCompliance(applicationId: string): Promise<ComplianceEvaluation[]> {
    const res = await fetch(`${API_BASE}/applications/${applicationId}/evaluate`, {
      method: "POST",
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Compliance evaluation failed");
    return res.json();
  },

  async getCompliance(applicationId: string): Promise<ComplianceEvaluation[]> {
    const res = await fetch(`${API_BASE}/applications/${applicationId}/compliance`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch compliance evaluations");
    return res.json();
  },

  async listComplianceRules(): Promise<ComplianceRule[]> {
    const res = await fetch(`${API_BASE}/compliance/rules`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch compliance rules");
    return res.json();
  },

  async updateComplianceRule(ruleId: string, data: Partial<ComplianceRule>): Promise<ComplianceRule> {
    const res = await fetch(`${API_BASE}/compliance/rules/${ruleId}`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update compliance rule");
    return res.json();
  },

  // Verification Adapter
  async triggerVerification(
    applicationId: string,
    certificateNumber: string,
    authorityName: string,
    documentId?: string
  ): Promise<VerificationResult> {
    const res = await fetch(`${API_BASE}/applications/${applicationId}/verify`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        certificate_number: certificateNumber,
        authority_name: authorityName,
        document_id: documentId,
      }),
    });
    if (!res.ok) throw new Error("Verification trigger failed");
    return res.json();
  },

  async getVerificationResults(applicationId: string): Promise<VerificationResult[]> {
    const res = await fetch(`${API_BASE}/applications/${applicationId}/verification`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch verification results");
    return res.json();
  },

  async listMockAuthorityRecords(): Promise<MockAuthorityRecord[]> {
    const res = await fetch(`${API_BASE}/verification/mock-records`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch simulated authority registry");
    return res.json();
  },

  // Evidence Requests
  async listEvidenceRequests(applicationId: string): Promise<EvidenceRequest[]> {
    const res = await fetch(`${API_BASE}/applications/${applicationId}/evidence-requests`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch evidence requests");
    return res.json();
  },

  async createEvidenceRequest(applicationId: string, findingId: string | null, text: string): Promise<EvidenceRequest> {
    const res = await fetch(`${API_BASE}/applications/${applicationId}/evidence-requests`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        finding_id: findingId,
        request_text: text,
      }),
    });
    if (!res.ok) throw new Error("Failed to create evidence request");
    return res.json();
  },

  async respondToEvidenceRequest(requestId: string, responseText: string, docId?: string): Promise<EvidenceRequest> {
    const res = await fetch(`${API_BASE}/evidence-requests/${requestId}/respond`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        response_text: responseText,
        response_document_id: docId,
      }),
    });
    if (!res.ok) throw new Error("Failed to submit response");
    return res.json();
  },

  // Audit
  async searchAuditTrail(params?: {
    application_id?: string;
    action?: string;
    actor_id?: string;
    entity_type?: string;
    search?: string;
  }): Promise<AuditEvent[]> {
    const query = new URLSearchParams();
    if (params?.application_id) query.set("application_id", params.application_id);
    if (params?.action) query.set("action", params.action);
    if (params?.actor_id) query.set("actor_id", params.actor_id);
    if (params?.entity_type) query.set("entity_type", params.entity_type);
    if (params?.search) query.set("search", params.search);

    const res = await fetch(`${API_BASE}/audit?${query.toString()}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch audit trail");
    return res.json();
  },

  // Demo Reseed
  async resetDemoSeed(): Promise<{ status: string; message: string }> {
    const res = await fetch(`${API_BASE}/demo/reset-seed`, {
      method: "POST",
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to reset demo dataset");
    return res.json();
  },
};
