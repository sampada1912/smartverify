"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { ApplicationCategory, ChecklistRule } from "@/lib/types";
import {
  Building2,
  ArrowLeft,
  Save,
  FileCheck2,
  AlertCircle,
  UploadCloud,
  FileText,
  FileSpreadsheet,
  Image as ImageIcon,
  Trash2,
  CheckCircle2,
  AlertTriangle,
  Info,
  Check,
  Plus
} from "lucide-react";

interface StagedFile {
  id: string;
  file: File;
  docType: string;
  isAutoDetected: boolean;
  status: "ready" | "uploading" | "success" | "error";
  error?: string;
}

const DOCUMENT_TYPE_LABELS: Record<string, string> = {
  PREVIOUS_APPROVAL: "Previous Approval / EoA Letter",
  AFFIDAVIT: "Statutory Affidavit (Format-1)",
  FACULTY_LIST: "Faculty Details & Cadre Ratio",
  NOC: "State Govt / University NOC",
  ACCREDITATION_CERT: "NBA / NAAC Accreditation Certificate",
  INFRASTRUCTURE_EVIDENCE: "Land & Instructional Area Proof",
  PAYMENT_RECEIPT: "TER Fee Payment Receipt",
  OTHER: "Other Supporting Evidence",
};

const DEFAULT_CHECKLIST_RULES: ChecklistRule[] = [
  {
    id: 1,
    rule_code: "CHK-EOA-01",
    category: "EXTENSION_OF_APPROVAL",
    document_type: "PREVIOUS_APPROVAL",
    requirement_name: "Previous Year AICTE Approval Letter (EoA)",
    description: "Copy of the latest Extension of Approval letter issued by the Council for academic continuity.",
    is_required: true,
    is_active: true,
    version: "2026.1-PROTOTYPE",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 2,
    rule_code: "CHK-EOA-02",
    category: "EXTENSION_OF_APPROVAL",
    document_type: "AFFIDAVIT",
    requirement_name: "Statutory Affidavit (Format-1) on Non-Judicial Stamp",
    description: "Affidavit submitted by Chairman/Secretary stating compliance with all faculty, infrastructure, and anti-ragging norms.",
    is_required: true,
    is_active: true,
    version: "2026.1-PROTOTYPE",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 3,
    rule_code: "CHK-EOA-03",
    category: "EXTENSION_OF_APPROVAL",
    document_type: "FACULTY_LIST",
    requirement_name: "Faculty Details & Cadre Ratio Certification",
    description: "Consolidated list of teaching faculty including cadre ratio (1:20 or 1:15) and Ph.D qualifications.",
    is_required: true,
    is_active: true,
    version: "2026.1-PROTOTYPE",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 4,
    rule_code: "CHK-EOA-04",
    category: "EXTENSION_OF_APPROVAL",
    document_type: "NOC",
    requirement_name: "State Government & Affiliating University NOC",
    description: "Valid No Objection Certificate or continuation of affiliation for the requested academic session.",
    is_required: true,
    is_active: true,
    version: "2026.1-PROTOTYPE",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 5,
    rule_code: "CHK-EOA-05",
    category: "EXTENSION_OF_APPROVAL",
    document_type: "INFRASTRUCTURE_EVIDENCE",
    requirement_name: "Land Area & Instructional Built-Up Area Proof",
    description: "Architect certificate validating barrier-free instructional space and requisite contiguous campus land.",
    is_required: true,
    is_active: true,
    version: "2026.1-PROTOTYPE",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 6,
    rule_code: "CHK-EOA-06",
    category: "EXTENSION_OF_APPROVAL",
    document_type: "PAYMENT_RECEIPT",
    requirement_name: "Technical Education Regulatory (TER) Payment Receipt",
    description: "Official receipt confirming regulatory processing fee deposit through the AICTE national portal.",
    is_required: true,
    is_active: true,
    version: "2026.1-PROTOTYPE",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 7,
    rule_code: "CHK-EOA-07",
    category: "INCREASE_IN_INTAKE",
    document_type: "ACCREDITATION_CERT",
    requirement_name: "National Board of Accreditation (NBA) Certificate",
    description: "Mandatory valid Tier-I/II NBA accreditation certificate required for expansion in sanctioned student intake.",
    is_required: true,
    is_active: true,
    version: "2026.1-PROTOTYPE",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

function formatBytes(bytes: number, decimals = 1): string {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}

function guessDocumentType(filename: string): string {
  const name = filename.toLowerCase();
  if (name.includes("eoa") || name.includes("approval") || name.includes("previous")) return "PREVIOUS_APPROVAL";
  if (name.includes("affidavit") || name.includes("undertaking") || name.includes("format")) return "AFFIDAVIT";
  if (name.includes("faculty") || name.includes("cadre") || name.includes("staff") || name.includes("teacher")) return "FACULTY_LIST";
  if (name.includes("noc") || name.includes("permission") || name.includes("affiliat")) return "NOC";
  if (name.includes("nba") || name.includes("naac") || name.includes("accredit")) return "ACCREDITATION_CERT";
  if (name.includes("infra") || name.includes("land") || name.includes("built") || name.includes("area")) return "INFRASTRUCTURE_EVIDENCE";
  if (name.includes("fee") || name.includes("receipt") || name.includes("payment") || name.includes("ter") || name.includes("challan")) return "PAYMENT_RECEIPT";
  return "OTHER";
}

function getFileIcon(filename: string) {
  const ext = filename.split(".").pop()?.toLowerCase();
  if (ext === "csv") return <FileSpreadsheet className="w-5 h-5 text-emerald-600 shrink-0" />;
  if (["png", "jpg", "jpeg"].includes(ext || "")) return <ImageIcon className="w-5 h-5 text-purple-600 shrink-0" />;
  return <FileText className="w-5 h-5 text-blue-600 shrink-0" />;
}

export default function NewApplicationPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [progressMessage, setProgressMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [validationAlert, setValidationAlert] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    institution_id: "1-1092837482",
    institution_name: "Delhi Institute of Technology & Management",
    category: "EXTENSION_OF_APPROVAL" as ApplicationCategory,
    academic_year: "2026-27",
    programme: "ENGINEERING_AND_TECHNOLOGY",
    course_name: "Computer Science and Engineering",
    existing_intake: 120,
    requested_intake: 120,
    contact_person: "Dr. Alok Verma",
    contact_email: "principal@ditm.edu.in",
    contact_phone: "+91-9810123456",
  });

  // Checklist rules state
  const [masterRules, setMasterRules] = useState<ChecklistRule[]>(DEFAULT_CHECKLIST_RULES);
  const [rulesLoading, setRulesLoading] = useState(true);

  // Staged files state
  const [stagedFiles, setStagedFiles] = useState<StagedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [targetRequirementForUpload, setTargetRequirementForUpload] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Fetch master checklist rules on mount
  useEffect(() => {
    let isMounted = true;
    async function loadRules() {
      try {
        const fetched = await api.listChecklistRules();
        if (isMounted && fetched && fetched.length > 0) {
          setMasterRules(fetched);
        }
      } catch (e) {
        // Fallback to default rules if offline or unseeded
        console.warn("Using default checklist rules fallback:", e);
      } finally {
        if (isMounted) setRulesLoading(false);
      }
    }
    loadRules();
    return () => {
      isMounted = false;
    };
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name.includes("intake") ? parseInt(value) || 0 : value,
    }));
    setValidationAlert(null);
  };

  // Applicable checklist items for current category
  const applicableRules = masterRules.filter(
    (r) => r.is_active && (r.category === "ALL" || r.category === formData.category)
  );

  const requiredRules = applicableRules.filter((r) => r.is_required);
  const satisfiedRequired = requiredRules.filter((r) =>
    stagedFiles.some((sf) => sf.docType === r.document_type)
  );
  const progressPercent =
    requiredRules.length > 0 ? Math.round((satisfiedRequired.length / requiredRules.length) * 100) : 100;

  // File Handling
  const handleFilesSelected = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setError(null);
    setValidationAlert(null);

    const allowedExtensions = ["pdf", "png", "jpg", "jpeg", "csv"];
    const maxSizeBytes = 25 * 1024 * 1024; // 25MB

    const newFiles: StagedFile[] = [];

    Array.from(files).forEach((file) => {
      const ext = file.name.split(".").pop()?.toLowerCase() || "";
      if (!allowedExtensions.includes(ext)) {
        setError(
          `File '${file.name}' has an unsupported extension ('.${ext}'). Allowed: PDF, PNG, JPG, JPEG, CSV.`
        );
        return;
      }

      if (file.size > maxSizeBytes) {
        setError(`File '${file.name}' (${formatBytes(file.size)}) exceeds the maximum allowed limit of 25MB.`);
        return;
      }

      // Check for duplicate staged filename
      if (stagedFiles.some((sf) => sf.file.name === file.name && sf.file.size === file.size)) {
        return;
      }

      const assignedType = targetRequirementForUpload || guessDocumentType(file.name);

      newFiles.push({
        id: `file_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
        file,
        docType: assignedType,
        isAutoDetected: !targetRequirementForUpload,
        status: "ready",
      });
    });

    if (newFiles.length > 0) {
      setStagedFiles((prev) => [...prev, ...newFiles]);
    }
    setTargetRequirementForUpload(null);

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFilesSelected(e.dataTransfer.files);
  };

  const handleRemoveFile = (id: string) => {
    setStagedFiles((prev) => prev.filter((f) => f.id !== id));
    setValidationAlert(null);
  };

  const handleUpdateFileType = (id: string, newType: string) => {
    setStagedFiles((prev) =>
      prev.map((f) => (f.id === id ? { ...f, docType: newType, isAutoDetected: false } : f))
    );
    setValidationAlert(null);
  };

  const triggerUploadForRequirement = (docType: string) => {
    setTargetRequirementForUpload(docType);
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Submission Workflow
  const handleSubmit = async (submitDirectly: boolean) => {
    setError(null);
    setValidationAlert(null);

    // Basic form verification
    if (!formData.institution_id || !formData.institution_name || !formData.course_name) {
      setError("Please complete all mandatory institution and course fields.");
      return;
    }

    // If submitting directly for scrutiny, verify all required checklist documents are attached
    if (submitDirectly) {
      const missingRequired = requiredRules.filter(
        (r) => !stagedFiles.some((sf) => sf.docType === r.document_type)
      );

      if (missingRequired.length > 0) {
        const missingNames = missingRequired.map((r) => r.requirement_name).join(", ");
        setValidationAlert(
          `Mandatory Documents Missing: The following required documents have not been attached: ${missingNames}. Please attach the required evidence before submitting for regulatory scrutiny, or click "Save as Draft" to save your progress.`
        );
        return;
      }
    }

    setLoading(true);
    try {
      // 1. Create Application Record
      setProgressMessage("Initializing application dossier and regulatory checklist...");
      const created = await api.createApplication(formData);

      // 2. Upload Staged Files (if any)
      if (stagedFiles.length > 0) {
        setProgressMessage(
          `Uploading and extracting ${stagedFiles.length} supporting document(s) with OCR...`
        );
        const filesToUpload = stagedFiles.map((sf) => sf.file);
        const docTypes = stagedFiles.map((sf) => sf.docType);
        await api.uploadDocuments(created.id, filesToUpload, docTypes);
      }

      // 3. Submit for Scrutiny if chosen
      if (submitDirectly) {
        setProgressMessage("Executing automated regulatory compliance and validation rules...");
        await api.submitApplication(created.id);
      }

      setProgressMessage("Finalizing dossier... Redirecting.");
      router.push(`/applications/${created.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to process application");
      setLoading(false);
      setProgressMessage(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Top Bar */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <Link
          href="/applications"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Applications</span>
        </Link>
        <span className="text-xs text-slate-400 font-mono">
          Auto ID Generated on Creation
        </span>
      </div>

      <div className="bg-white p-6 sm:p-8 rounded-lg border border-slate-200 shadow-xs space-y-6">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Building2 className="w-5 h-5 text-blue-600" />
            <span>New Technical Institution Regulatory Application</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Initiate a new institutional approval or extension dossier for Council scrutiny. Attach supporting documents for automated OCR, classification, and regulatory compliance verification.
          </p>
        </div>

        {error && (
          <div className="p-3 bg-red-50 text-red-700 text-xs rounded border border-red-200 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
            <div className="flex-1 font-medium">{error}</div>
          </div>
        )}

        {validationAlert && (
          <div className="p-3.5 bg-amber-50 text-amber-900 text-xs rounded border border-amber-200 flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <div className="flex-1 space-y-1">
              <span className="font-semibold block text-amber-950">Submission Pre-Check Warning</span>
              <p className="text-amber-800 leading-relaxed">{validationAlert}</p>
            </div>
          </div>
        )}

        {/* Institution & Programme Details */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          {/* Institution ID */}
          <div>
            <label className="text-slate-700 font-semibold block mb-1">
              Permanent Institute ID (PID):
            </label>
            <input
              type="text"
              name="institution_id"
              value={formData.institution_id}
              onChange={handleChange}
              placeholder="e.g. 1-1092837482"
              className="w-full p-2.5 border border-slate-300 rounded focus:outline-blue-600 font-mono"
              required
            />
          </div>

          {/* Institution Name */}
          <div>
            <label className="text-slate-700 font-semibold block mb-1">
              Institution Legal Name:
            </label>
            <input
              type="text"
              name="institution_name"
              value={formData.institution_name}
              onChange={handleChange}
              placeholder="e.g. Delhi Institute of Technology & Management"
              className="w-full p-2.5 border border-slate-300 rounded focus:outline-blue-600"
              required
            />
          </div>

          {/* Category */}
          <div>
            <label className="text-slate-700 font-semibold block mb-1">
              Application Category:
            </label>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="w-full p-2.5 border border-slate-300 rounded focus:outline-blue-600 bg-white font-medium"
            >
              <option value="EXTENSION_OF_APPROVAL">Extension of Approval (EoA)</option>
              <option value="INCREASE_IN_INTAKE">Increase in Intake</option>
              <option value="NEW_INSTITUTION">New Technical Institution</option>
              <option value="NEW_PROGRAMME">Introduction of New Programme</option>
            </select>
          </div>

          {/* Academic Year */}
          <div>
            <label className="text-slate-700 font-semibold block mb-1">
              Academic Session:
            </label>
            <input
              type="text"
              name="academic_year"
              value={formData.academic_year}
              onChange={handleChange}
              className="w-full p-2.5 border border-slate-300 rounded focus:outline-blue-600"
              required
            />
          </div>

          {/* Programme */}
          <div>
            <label className="text-slate-700 font-semibold block mb-1">
              Discipline / Programme:
            </label>
            <select
              name="programme"
              value={formData.programme}
              onChange={handleChange}
              className="w-full p-2.5 border border-slate-300 rounded focus:outline-blue-600 bg-white"
            >
              <option value="ENGINEERING_AND_TECHNOLOGY">Engineering and Technology</option>
              <option value="MANAGEMENT">Management (MBA/PGDM)</option>
              <option value="PHARMACY">Pharmacy</option>
              <option value="MCA">Computer Applications (MCA)</option>
            </select>
          </div>

          {/* Course Name */}
          <div>
            <label className="text-slate-700 font-semibold block mb-1">
              Course / Branch:
            </label>
            <input
              type="text"
              name="course_name"
              value={formData.course_name}
              onChange={handleChange}
              className="w-full p-2.5 border border-slate-300 rounded focus:outline-blue-600"
              required
            />
          </div>

          {/* Existing Intake */}
          <div>
            <label className="text-slate-700 font-semibold block mb-1">
              Existing Sanctioned Intake:
            </label>
            <input
              type="number"
              name="existing_intake"
              value={formData.existing_intake}
              onChange={handleChange}
              className="w-full p-2.5 border border-slate-300 rounded focus:outline-blue-600 font-mono"
              required
            />
          </div>

          {/* Requested Intake */}
          <div>
            <label className="text-slate-700 font-semibold block mb-1">
              Requested Intake for Academic Year:
            </label>
            <input
              type="number"
              name="requested_intake"
              value={formData.requested_intake}
              onChange={handleChange}
              className="w-full p-2.5 border border-slate-300 rounded focus:outline-blue-600 font-mono"
              required
            />
          </div>
        </div>

        {/* Contact Details */}
        <div className="pt-4 border-t border-slate-200">
          <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">
            Authorized Contact Information
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div>
              <label className="text-slate-600 block mb-1 font-medium">Contact Person:</label>
              <input
                type="text"
                name="contact_person"
                value={formData.contact_person}
                onChange={handleChange}
                className="w-full p-2 border border-slate-300 rounded focus:outline-blue-600"
                required
              />
            </div>
            <div>
              <label className="text-slate-600 block mb-1 font-medium">Contact Email:</label>
              <input
                type="email"
                name="contact_email"
                value={formData.contact_email}
                onChange={handleChange}
                className="w-full p-2 border border-slate-300 rounded focus:outline-blue-600"
                required
              />
            </div>
            <div>
              <label className="text-slate-600 block mb-1 font-medium">Contact Phone:</label>
              <input
                type="text"
                name="contact_phone"
                value={formData.contact_phone}
                onChange={handleChange}
                className="w-full p-2 border border-slate-300 rounded focus:outline-blue-600"
                required
              />
            </div>
          </div>
        </div>

        {/* ---------------- SUPPORTING DOCUMENTS SECTION ---------------- */}
        <div className="pt-6 border-t border-slate-200 space-y-5">
          <div>
            <div className="flex items-center gap-2">
              <UploadCloud className="w-5 h-5 text-blue-600" />
              <h3 className="text-base font-bold text-slate-900">Supporting Documents</h3>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Upload the documents required for your application. VerifAI will process the submitted evidence and flag items requiring review.
            </p>
          </div>

          {/* Dynamic Category Document Checklist Card */}
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-200">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                  Regulatory Document Checklist
                </span>
                <span className="text-[10px] bg-blue-100 text-blue-800 font-semibold px-2 py-0.5 rounded-full">
                  {formData.category.replace(/_/g, " ")}
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-slate-500">Mandatory Requirements:</span>
                <span className="font-bold text-slate-800 font-mono">
                  {satisfiedRequired.length} of {requiredRules.length} attached ({progressPercent}%)
                </span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
              <div
                className={`h-full transition-all duration-300 ${
                  progressPercent === 100 ? "bg-emerald-500" : "bg-blue-600"
                }`}
                style={{ width: `${progressPercent}%` }}
              />
            </div>

            {/* Checklist Items */}
            <div className="space-y-2 pt-1">
              {applicableRules.map((rule) => {
                const attached = stagedFiles.find((sf) => sf.docType === rule.document_type);
                const isSatisfied = Boolean(attached);

                return (
                  <div
                    key={rule.rule_code}
                    className={`flex flex-col sm:flex-row sm:items-center justify-between p-2.5 rounded border text-xs gap-2 transition-colors ${
                      isSatisfied
                        ? "bg-white border-emerald-200"
                        : rule.is_required
                        ? "bg-white border-amber-200"
                        : "bg-white border-slate-200"
                    }`}
                  >
                    <div className="flex-1 space-y-0.5">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-semibold text-slate-900">{rule.requirement_name}</span>
                        <span className="font-mono text-[10px] text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">
                          {rule.rule_code}
                        </span>
                        {rule.is_required ? (
                          <span className="text-[10px] font-bold text-red-700 bg-red-50 border border-red-100 px-1.5 py-0.2 rounded">
                            Required
                          </span>
                        ) : (
                          <span className="text-[10px] font-medium text-slate-600 bg-slate-100 px-1.5 py-0.2 rounded">
                            Optional
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-500 leading-normal">{rule.description}</p>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      {isSatisfied ? (
                        <div className="flex items-center gap-1.5 text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded text-[11px] font-medium">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                          <span className="truncate max-w-[140px] sm:max-w-[180px]">
                            {attached?.file.name}
                          </span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <span
                            className={`text-[11px] px-2 py-0.5 rounded font-medium ${
                              rule.is_required
                                ? "text-amber-800 bg-amber-50 border border-amber-200"
                                : "text-slate-500 bg-slate-100"
                            }`}
                          >
                            {rule.is_required ? "Missing Document" : "Not Attached"}
                          </span>
                          <button
                            type="button"
                            onClick={() => triggerUploadForRequirement(rule.document_type)}
                            className="inline-flex items-center gap-1 px-2 py-1 bg-white hover:bg-slate-50 text-blue-600 border border-blue-200 rounded text-[11px] font-semibold transition-colors"
                          >
                            <Plus className="w-3 h-3" />
                            <span>Attach</span>
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Drag & Drop File Upload Area */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-lg p-6 sm:p-8 text-center cursor-pointer transition-colors ${
              isDragging
                ? "border-blue-500 bg-blue-50"
                : "border-slate-300 hover:border-slate-400 bg-slate-50/50 hover:bg-slate-50"
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => handleFilesSelected(e.target.files)}
              multiple
              accept=".pdf,.png,.jpg,.jpeg,.csv"
              className="hidden"
            />
            <div className="flex flex-col items-center justify-center space-y-2">
              <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                <UploadCloud className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-800">
                  <span className="text-blue-600 hover:underline">Click to browse</span> or drag and drop files here
                </p>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Supported formats: PDF, PNG, JPG, JPEG, CSV • Maximum 25MB per file
                </p>
              </div>
            </div>
          </div>

          {/* Staged Files List */}
          {stagedFiles.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                  Attached Files ({stagedFiles.length})
                </h4>
                <button
                  type="button"
                  onClick={() => setStagedFiles([])}
                  className="text-xs text-slate-500 hover:text-red-600 transition-colors"
                >
                  Clear all files
                </button>
              </div>

              <div className="divide-y divide-slate-200 border border-slate-200 rounded-lg overflow-hidden bg-white">
                {stagedFiles.map((staged) => (
                  <div
                    key={staged.id}
                    className="p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs hover:bg-slate-50/75 transition-colors"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      {getFileIcon(staged.file.name)}
                      <div className="min-w-0">
                        <p className="font-semibold text-slate-900 truncate">{staged.file.name}</p>
                        <p className="text-[11px] text-slate-400 font-mono">
                          {formatBytes(staged.file.size)}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2.5 flex-wrap sm:flex-nowrap">
                      {/* Document Type Selector */}
                      <div className="flex items-center gap-1.5">
                        <label className="text-[11px] text-slate-500 font-medium">Type:</label>
                        <select
                          value={staged.docType}
                          onChange={(e) => handleUpdateFileType(staged.id, e.target.value)}
                          className="text-xs py-1 px-2 border border-slate-300 rounded bg-white text-slate-800 focus:outline-blue-600 font-medium max-w-[210px]"
                        >
                          {Object.entries(DOCUMENT_TYPE_LABELS).map(([val, label]) => (
                            <option key={val} value={val}>
                              {label}
                            </option>
                          ))}
                        </select>
                      </div>

                      {staged.isAutoDetected ? (
                        <span className="text-[10px] font-medium text-blue-700 bg-blue-50 border border-blue-100 px-1.5 py-0.5 rounded whitespace-nowrap">
                          Auto-detected
                        </span>
                      ) : (
                        <span className="text-[10px] font-medium text-slate-700 bg-slate-100 px-1.5 py-0.5 rounded whitespace-nowrap">
                          Manual
                        </span>
                      )}

                      <button
                        type="button"
                        onClick={() => handleRemoveFile(staged.id)}
                        className="p-1 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                        title="Remove file"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Submission Progress Display */}
        {progressMessage && (
          <div className="p-3 bg-blue-50 text-blue-800 text-xs rounded border border-blue-200 flex items-center gap-2.5">
            <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin shrink-0" />
            <span className="font-medium">{progressMessage}</span>
          </div>
        )}

        {/* Submission Actions */}
        <div className="pt-4 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3">
          <div className="text-xs text-slate-500">
            {stagedFiles.length === 0 ? (
              <span>No files attached yet. You may save draft or attach files for instant verification.</span>
            ) : (
              <span>
                {stagedFiles.length} file(s) attached •{" "}
                {progressPercent === 100
                  ? "All mandatory requirements satisfied"
                  : `${requiredRules.length - satisfiedRequired.length} mandatory requirement(s) pending`}
              </span>
            )}
          </div>

          <div className="flex items-center gap-3">
            <button
              type="button"
              disabled={loading}
              onClick={() => handleSubmit(false)}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold rounded-md transition-colors disabled:opacity-50"
            >
              <Save className="w-4 h-4 text-slate-500" />
              <span>Save as Draft</span>
            </button>

            <button
              type="button"
              disabled={loading}
              onClick={() => handleSubmit(true)}
              className="inline-flex items-center gap-1.5 px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-md shadow-xs transition-colors disabled:opacity-50"
            >
              <FileCheck2 className="w-4 h-4" />
              <span>{loading ? "Processing..." : "Create & Submit for Scrutiny"}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
