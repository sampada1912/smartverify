"use client";

import React, { useEffect, useState, use } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Application, ApplicationDetail, DocumentItem, ValidationFinding } from "@/lib/types";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { OverviewTab } from "@/components/applications/OverviewTab";
import { ChecklistTab } from "@/components/applications/ChecklistTab";
import { DocumentsTab } from "@/components/applications/DocumentsTab";
import { ExtractedDataTab } from "@/components/applications/ExtractedDataTab";
import { ValidationFindingsTab } from "@/components/applications/ValidationFindingsTab";
import { ComplianceTab } from "@/components/applications/ComplianceTab";
import { VerificationTab } from "@/components/applications/VerificationTab";
import { AuditTab } from "@/components/applications/AuditTab";
import { EvidenceViewerModal } from "@/components/evidence/EvidenceViewerModal";
import {
  ArrowLeft,
  Building2,
  Calendar,
  Layers,
  FileText,
  AlertTriangle,
  Scale,
  ShieldCheck,
  History,
  PlayCircle,
  RefreshCw,
  Clock,
  Sparkles,
} from "lucide-react";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function ApplicationDetailPage({ params }: PageProps) {
  const resolvedParams = use(params);
  const applicationId = resolvedParams.id;
  const router = useRouter();

  const [application, setApplication] = useState<ApplicationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<
    "overview" | "checklist" | "documents" | "extracted" | "findings" | "compliance" | "verification" | "audit"
  >("overview");

  const [runningAll, setRunningAll] = useState(false);
  const [actionMsg, setActionMsg] = useState<string | null>(null);

  // Evidence inspection modal state
  const [inspectDoc, setInspectDoc] = useState<DocumentItem | null>(null);
  const [inspectFinding, setInspectFinding] = useState<ValidationFinding | null>(null);
  const [isEvidenceOpen, setIsEvidenceOpen] = useState(false);

  const fetchData = async () => {
    try {
      setError(null);
      const data = await api.getApplicationDetail(applicationId);
      setApplication(data);
    } catch (err: any) {
      setError(err.message || "Failed to load application details");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [applicationId]);

  const handleRunFullValidation = async () => {
    if (!application) return;
    setRunningAll(true);
    setActionMsg(null);
    try {
      await api.triggerValidation(application.id);
      await api.evaluateCompliance(application.id);
      setActionMsg("Automated document validation and compliance checks completed.");
      await fetchData();
    } catch (err: any) {
      setActionMsg(err.message || "Scrutiny checks failed");
    } finally {
      setRunningAll(false);
    }
  };

  const handleInspectEvidence = (docId: string, finding: ValidationFinding) => {
    if (!application) return;
    const doc = application.documents.find((d) => d.id === docId) || null;
    setInspectDoc(doc);
    setInspectFinding(finding);
    setIsEvidenceOpen(true);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="w-9 h-9 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-sm font-medium text-slate-600">Retrieving application dossier and scrutiny records...</p>
      </div>
    );
  }

  if (error || !application) {
    return (
      <div className="max-w-xl mx-auto mt-12 bg-white p-8 rounded-xl border border-red-200 text-center shadow-xs">
        <AlertTriangle className="w-10 h-10 text-red-500 mx-auto mb-3" />
        <h2 className="text-lg font-bold text-slate-900">Application Not Found</h2>
        <p className="text-sm text-slate-500 mt-1 mb-6">
          {error || `No regulatory record found for application ID ${applicationId}.`}
        </p>
        <Link
          href="/applications"
          className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Applications List</span>
        </Link>
      </div>
    );
  }

  const openFindingsCount = application.validation_findings.filter(
    (f) => f.status === "OPEN" || f.status === "REQUESTED_INFORMATION"
  ).length;

  const highSeverityCount = application.validation_findings.filter(
    (f) => f.severity === "HIGH" && f.status !== "RESOLVED"
  ).length;

  return (
    <div className="space-y-6">
      {/* Breadcrumb & Navigation */}
      <div className="flex items-center justify-between">
        <Link
          href="/applications"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to All Applications</span>
        </Link>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchData}
            title="Refresh dossier data"
            className="p-2 border border-slate-200 bg-white rounded-lg text-slate-600 hover:bg-slate-50 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={handleRunFullValidation}
            disabled={runningAll}
            className="inline-flex items-center gap-2 px-3.5 py-2 bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold rounded-lg shadow-xs transition-colors disabled:opacity-50"
          >
            {runningAll ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <PlayCircle className="w-4 h-4" />
            )}
            <span>Run Complete Scrutiny Checks</span>
          </button>
        </div>
      </div>

      {actionMsg && (
        <div className="p-3 bg-blue-50 border border-blue-200 text-blue-800 rounded-lg text-xs font-medium flex items-center justify-between">
          <span>{actionMsg}</span>
          <button onClick={() => setActionMsg(null)} className="text-blue-500 hover:text-blue-800">
            Dismiss
          </button>
        </div>
      )}

      {/* Header Dossier Banner */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="font-mono text-xs font-bold px-2 py-0.5 bg-slate-100 text-slate-800 rounded border border-slate-300">
                {application.id}
              </span>
              <StatusBadge status={application.status} />
              <span className="text-xs font-medium px-2 py-0.5 bg-blue-50 text-blue-700 rounded border border-blue-200">
                {application.category}
              </span>
              <span className="text-xs font-medium px-2 py-0.5 bg-slate-50 text-slate-600 rounded border border-slate-200">
                AY {application.academic_year}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <Building2 className="w-5 h-5 text-slate-400 shrink-0" />
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">
                {application.institution_name}
              </h1>
              <span className="text-xs font-mono font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                PID: {application.institution_id}
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500">
              <span className="flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-slate-400" />
                <span>{application.programme}</span>
              </span>
              <span>•</span>
              <span>Approved Intake: <strong>{application.existing_intake}</strong></span>
              <span>•</span>
              <span>Requested Intake: <strong>{application.requested_intake}</strong></span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                <span>Submitted: {application.submission_date ? new Date(application.submission_date).toLocaleDateString() : "Draft"}</span>
              </span>
            </div>
          </div>

          {/* Quick Metrics Badge */}
          <div className="flex items-center gap-3 bg-slate-50 p-3 rounded-lg border border-slate-200 shrink-0">
            <div className="text-center px-3 border-r border-slate-200">
              <div className="text-lg font-bold text-slate-900">{application.documents.length}</div>
              <div className="text-[11px] font-medium text-slate-500">Documents</div>
            </div>
            <div className="text-center px-3 border-r border-slate-200">
              <div className={`text-lg font-bold ${openFindingsCount > 0 ? "text-amber-600" : "text-emerald-600"}`}>
                {openFindingsCount}
              </div>
              <div className="text-[11px] font-medium text-slate-500">Open Findings</div>
            </div>
            <div className="text-center px-3">
              <div className={`text-lg font-bold ${highSeverityCount > 0 ? "text-red-600" : "text-slate-600"}`}>
                {highSeverityCount}
              </div>
              <div className="text-[11px] font-medium text-slate-500">High Deficiencies</div>
            </div>
          </div>
        </div>

        {/* Tab Navigation Navigation Bar */}
        <div className="flex items-center gap-1 overflow-x-auto border-t border-slate-200 mt-6 pt-3 -mb-2">
          <button
            onClick={() => setActiveTab("overview")}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors flex items-center gap-2 ${
              activeTab === "overview"
                ? "bg-slate-900 text-white"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <span>Overview</span>
          </button>

          <button
            onClick={() => setActiveTab("checklist")}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors flex items-center gap-2 ${
              activeTab === "checklist"
                ? "bg-slate-900 text-white"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <span>Checklist</span>
            <span
              className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                activeTab === "checklist" ? "bg-slate-700 text-white" : "bg-slate-200 text-slate-700"
              }`}
            >
              {application.checklist.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab("documents")}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors flex items-center gap-2 ${
              activeTab === "documents"
                ? "bg-slate-900 text-white"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Documents</span>
            <span
              className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                activeTab === "documents" ? "bg-slate-700 text-white" : "bg-slate-200 text-slate-700"
              }`}
            >
              {application.documents.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab("extracted")}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors flex items-center gap-2 ${
              activeTab === "extracted"
                ? "bg-slate-900 text-white"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Extracted Data</span>
            <span
              className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                activeTab === "extracted" ? "bg-slate-700 text-white" : "bg-slate-200 text-slate-700"
              }`}
            >
              {application.extracted_fields.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab("findings")}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors flex items-center gap-2 ${
              activeTab === "findings"
                ? "bg-slate-900 text-white"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Validation Findings</span>
            {openFindingsCount > 0 && (
              <span
                className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                  activeTab === "findings" ? "bg-amber-500 text-slate-950 font-bold" : "bg-amber-100 text-amber-800 font-bold"
                }`}
              >
                {openFindingsCount}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab("compliance")}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors flex items-center gap-2 ${
              activeTab === "compliance"
                ? "bg-slate-900 text-white"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <Scale className="w-3.5 h-3.5" />
            <span>Compliance Rules</span>
            <span
              className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                activeTab === "compliance" ? "bg-slate-700 text-white" : "bg-slate-200 text-slate-700"
              }`}
            >
              {application.compliance_evaluations.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab("verification")}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors flex items-center gap-2 ${
              activeTab === "verification"
                ? "bg-slate-900 text-white"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Authority Verification</span>
            <span
              className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                activeTab === "verification" ? "bg-slate-700 text-white" : "bg-slate-200 text-slate-700"
              }`}
            >
              {application.verification_results.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab("audit")}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors flex items-center gap-2 ${
              activeTab === "audit"
                ? "bg-slate-900 text-white"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <History className="w-3.5 h-3.5" />
            <span>Audit History</span>
          </button>
        </div>
      </div>

      {/* Tab Panels */}
      <div className="mt-4">
        {activeTab === "overview" && (
          <OverviewTab application={application} onRefresh={fetchData} />
        )}

        {activeTab === "checklist" && (
          <ChecklistTab checklist={application.checklist} onRefresh={fetchData} />
        )}

        {activeTab === "documents" && (
          <DocumentsTab
            applicationId={application.id}
            documents={application.documents}
            onRefresh={fetchData}
          />
        )}

        {activeTab === "extracted" && (
          <ExtractedDataTab
            fields={application.extracted_fields}
            onRefresh={fetchData}
          />
        )}

        {activeTab === "findings" && (
          <ValidationFindingsTab
            findings={application.validation_findings}
            onRefresh={fetchData}
            onInspectEvidence={handleInspectEvidence}
          />
        )}

        {activeTab === "compliance" && (
          <ComplianceTab
            applicationId={application.id}
            evaluations={application.compliance_evaluations}
            onRefresh={fetchData}
          />
        )}

        {activeTab === "verification" && (
          <VerificationTab
            applicationId={application.id}
            results={application.verification_results}
            onRefresh={fetchData}
          />
        )}

        {activeTab === "audit" && (
          <AuditTab applicationId={application.id} />
        )}
      </div>

      {/* Standalone Evidence Viewer Modal */}
      {inspectDoc && (
        <EvidenceViewerModal
          isOpen={isEvidenceOpen}
          onClose={() => {
            setIsEvidenceOpen(false);
            setInspectDoc(null);
            setInspectFinding(null);
          }}
          document={inspectDoc}
          finding={inspectFinding}
        />
      )}
    </div>
  );
}
