"use client";

import React, { useState } from "react";
import { useAuth } from "@/lib/authContext";
import { api } from "@/lib/api";
import {
  Settings,
  RefreshCw,
  Database,
  Shield,
  FileText,
  UserCheck,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  Lock,
  Layers,
  Info,
} from "lucide-react";

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const [reseeding, setReseeding] = useState(false);
  const [reseedMsg, setReseedMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const handleReseed = async () => {
    if (!confirm("This will reset the SQLite/PostgreSQL prototype database and reseed all 8 demonstration scenarios and sample PDFs. Proceed?")) {
      return;
    }

    setReseeding(true);
    setReseedMsg(null);
    try {
      const res = await api.resetDemoSeed();
      setReseedMsg({ type: "success", text: res.message || "Demonstration database successfully reset and reseeded." });
    } catch (err: any) {
      setReseedMsg({ type: "error", text: err.message || "Failed to reset demo database." });
    } finally {
      setReseeding(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">System Settings & Administration</h1>
          <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-900 border border-blue-200">
            PROTOTYPE v1.0.0
          </span>
        </div>
        <p className="text-sm text-slate-500 mt-1">
          Configure prototype operational parameters, inspect security constraints, and manage demonstration datasets.
        </p>
      </div>

      {/* Mandatory Prototype Regulatory Notice */}
      <div className="p-4 bg-slate-900 text-white rounded-xl shadow-xs space-y-2">
        <div className="flex items-center gap-2 text-amber-400 font-bold text-xs uppercase tracking-wider">
          <Shield className="w-4 h-4" />
          <span>Independent Prototype Declaration</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          <strong>AICTE SmartVerify</strong> is an independent academic and technical prototype developed for Smart India Hackathon 2026 (Problem Statement SIH26261).
          It is <strong>not</strong> an official AICTE production system. All institutional names, PIDs, approval letters, and issuing authority verification checks are
          synthetic and simulated for demonstration and audit evaluation only.
        </p>
      </div>

      {/* Demo Dataset Management */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2.5 bg-blue-50 text-blue-700 rounded-lg">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">Demonstration Dataset Management</h2>
              <p className="text-xs text-slate-500">
                Restore the database to its pristine state with the 8 canonical SIH test scenarios.
              </p>
            </div>
          </div>

          <button
            onClick={handleReseed}
            disabled={reseeding}
            className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-lg shadow-xs transition-colors disabled:opacity-50"
          >
            {reseeding ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
            <span>Reset & Reseed Demo Data</span>
          </button>
        </div>

        {reseedMsg && (
          <div
            className={`p-3 rounded-lg text-xs font-medium border flex items-center gap-2 ${
              reseedMsg.type === "success"
                ? "bg-emerald-50 border-emerald-200 text-emerald-800"
                : "bg-red-50 border-red-200 text-red-800"
            }`}
          >
            {reseedMsg.type === "success" ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-red-600 shrink-0" />
            )}
            <span>{reseedMsg.text}</span>
          </div>
        )}

        <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 text-xs space-y-2">
          <div className="font-bold text-slate-800">Seeded Scrutiny Demonstration Scenarios:</div>
          <ol className="list-decimal list-inside space-y-1 text-slate-600 pl-1">
            <li><strong>SIH26-APP-001:</strong> Clean Compliant Application (All mandatory documents satisfied)</li>
            <li><strong>SIH26-APP-002:</strong> Missing Required Document (Missing State Board NOC)</li>
            <li><strong>SIH26-APP-003:</strong> Expired Document (NOC certificate validity lapsed)</li>
            <li><strong>SIH26-APP-004:</strong> Application vs Document Field Mismatch (Requested intake exceeds document approval)</li>
            <li><strong>SIH26-APP-005:</strong> Synthetic Institutional Record Mismatch (Built-up area below registered portal records)</li>
            <li><strong>SIH26-APP-006:</strong> Duplicate Document Anomaly (Identical SHA-256 binary hash across multiple requirements)</li>
            <li><strong>SIH26-APP-007:</strong> Mock Authority Verification Mismatch (State Board registry records conflicting PID)</li>
            <li><strong>SIH26-APP-008:</strong> Multi-Finding Complex Dossier (Compound deficiencies across faculty ratio, intake, and dates)</li>
          </ol>
        </div>
      </div>

      {/* Role-Based Authentication Identity & Server Enforcement */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2.5 bg-purple-50 text-purple-700 rounded-lg">
              <UserCheck className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">Authenticated Account Identity & Access Control</h2>
              <p className="text-xs text-slate-500">
                Server-enforced role authorization. To change persona, sign in with separate credentials.
              </p>
            </div>
          </div>
          <button
            onClick={logout}
            className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-slate-100 hover:bg-rose-50 text-slate-700 hover:text-rose-600 border border-slate-200 hover:border-rose-200 transition-colors"
          >
            Sign Out / Switch Account
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          <div
            className={`p-4 rounded-xl border text-left transition-all ${
              user?.role === "INSTITUTION"
                ? "border-blue-600 bg-blue-50/50 shadow-xs ring-1 ring-blue-600"
                : "border-slate-200 bg-slate-50/60 opacity-80"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-900">Institution Account</span>
              {user?.role === "INSTITUTION" && (
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-600 text-white">CURRENT ACTIVE</span>
              )}
            </div>
            <div className="text-[11px] font-mono text-slate-500 mb-2">Login: principal@ditm.edu.in</div>
            <p className="text-xs text-slate-500 leading-relaxed">
              Create applications, upload PDFs, respond to evidence clarification requests, and view deficiencies. Tenant isolated to own institution.
            </p>
          </div>

          <div
            className={`p-4 rounded-xl border text-left transition-all ${
              user?.role === "REVIEWER"
                ? "border-purple-600 bg-purple-50/50 shadow-xs ring-1 ring-purple-600"
                : "border-slate-200 bg-slate-50/60 opacity-80"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-900">Scrutiny Reviewer</span>
              {user?.role === "REVIEWER" && (
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-purple-600 text-white">CURRENT ACTIVE</span>
              )}
            </div>
            <div className="text-[11px] font-mono text-slate-500 mb-2">Login: scrutiny.officer@aicte.gov.in</div>
            <p className="text-xs text-slate-500 leading-relaxed">
              Access scrutiny queue, inspect evidence snippets, correct OCR values, request evidence, or escalate findings.
            </p>
          </div>

          <div
            className={`p-4 rounded-xl border text-left transition-all ${
              user?.role === "ADMIN"
                ? "border-slate-800 bg-slate-100 shadow-xs ring-1 ring-slate-800"
                : "border-slate-200 bg-slate-50/60 opacity-80"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-900">System Administrator</span>
              {user?.role === "ADMIN" && (
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-900 text-white">CURRENT ACTIVE</span>
              )}
            </div>
            <div className="text-[11px] font-mono text-slate-500 mb-2">Login: admin@aicte.gov.in</div>
            <p className="text-xs text-slate-500 leading-relaxed">
              Configure compliance rules, toggle checklist requirements, audit all events, and manage prototype data.
            </p>
          </div>
        </div>
      </div>

      {/* Pipeline Engines Status */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2.5 bg-emerald-50 text-emerald-700 rounded-lg">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">AI & Document Processing Engine Status</h2>
            <p className="text-xs text-slate-500">
              Operational parameters of the multi-tier OCR and validation subsystem.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-2">
            <div className="font-bold text-slate-900 flex items-center justify-between">
              <span>Text Extraction Subsystem</span>
              <span className="text-[11px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold">
                ONLINE
              </span>
            </div>
            <p className="text-slate-600 leading-relaxed">
              <strong>Primary Tier:</strong> Native PyMuPDF text stream extraction for searchable regulatory PDFs.
            </p>
            <p className="text-slate-600 leading-relaxed">
              <strong>Secondary Tier:</strong> Scanned image OCR fallback via Tesseract/PaddleOCR adapter with graceful fallback.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-2">
            <div className="font-bold text-slate-900 flex items-center justify-between">
              <span>File Storage Security Abstraction</span>
              <span className="text-[11px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold">
                ENFORCED
              </span>
            </div>
            <p className="text-slate-600 leading-relaxed">
              Files are stored outside web roots under unique UUID hashes with strict MIME/extension verification and SHA-256 fingerprinting.
            </p>
            <p className="text-slate-600 leading-relaxed">
              Downloads require authenticated role verification and are served via streaming safe endpoints.
            </p>
          </div>
        </div>
      </div>

      {/* Production Hardening Considerations */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2.5 bg-amber-50 text-amber-700 rounded-lg">
            <Lock className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">Production Transition Architecture</h2>
            <p className="text-xs text-slate-500">
              Requirements for transitioning this independent MVP to state/national regulatory production.
            </p>
          </div>
        </div>

        <div className="text-xs text-slate-600 space-y-2 leading-relaxed">
          <p>
            • <strong>Database:</strong> Transition from SQLite dev fallback to high-availability PostgreSQL with replication and read replicas.
          </p>
          <p>
            • <strong>Object Storage:</strong> Swap local filesystem storage with S3/GCS compliant storage backed by KMS client-side encryption.
          </p>
          <p>
            • <strong>Asynchronous Worker Queue:</strong> Execute OCR, SHA-256 fingerprinting, and heavy document classification via Celery / Redis background workers.
          </p>
          <p>
            • <strong>Authorized Issuing Gateways:</strong> Replace simulated adapters with authentic signed digital signature verification (e.g. DigiLocker, e-Sanad).
          </p>
        </div>
      </div>
    </div>
  );
}
