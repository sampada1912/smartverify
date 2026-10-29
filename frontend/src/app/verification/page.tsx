"use client";

import React, { useEffect, useState } from "react";
import { MockAuthorityRecord, Application, VerificationResult } from "@/lib/types";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatDate } from "@/lib/utils";
import {
  ShieldCheck,
  Search,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Layers,
  Building2,
  ExternalLink,
  PlayCircle,
  RefreshCw,
  Info,
  Database,
  ArrowRight,
  Code,
} from "lucide-react";

export default function VerificationPage() {
  const [mockRecords, setMockRecords] = useState<MockAuthorityRecord[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  // Inquiry form state
  const [selectedAppId, setSelectedAppId] = useState("");
  const [authorityName, setAuthorityName] = useState("STATE_TECHNICAL_BOARD_MOCK");
  const [certNumber, setCertNumber] = useState("");
  const [verifying, setVerifying] = useState(false);
  const [inquiryResult, setInquiryResult] = useState<VerificationResult | null>(null);
  const [inquiryError, setInquiryError] = useState<string | null>(null);

  // Table search
  const [tableSearch, setTableSearch] = useState("");

  const fetchData = async () => {
    setLoading(true);
    try {
      const [records, apps] = await Promise.all([
        api.listMockAuthorityRecords(),
        api.getApplications(),
      ]);
      setMockRecords(records);
      setApplications(apps);
      if (apps.length > 0 && !selectedAppId) {
        setSelectedAppId(apps[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleTestInquiry = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!certNumber.trim() || !selectedAppId) return;

    setVerifying(true);
    setInquiryResult(null);
    setInquiryError(null);
    try {
      const res = await api.triggerVerification(selectedAppId, certNumber.trim(), authorityName);
      setInquiryResult(res);
    } catch (err: any) {
      setInquiryError(err.message || "Authority verification query failed");
    } finally {
      setVerifying(false);
    }
  };

  const populateFromRecord = (rec: MockAuthorityRecord) => {
    setCertNumber(rec.certificate_number);
    setAuthorityName(rec.authority_name);
    // Find an application matching the institution if possible
    const match = applications.find((a) => a.institution_id === rec.institution_id);
    if (match) {
      setSelectedAppId(match.id);
    }
    // Scroll to test console
    window.scrollTo({ top: 180, behavior: "smooth" });
  };

  const filteredRecords = mockRecords.filter((r) => {
    if (!tableSearch.trim()) return true;
    const q = tableSearch.toLowerCase();
    return (
      r.certificate_number.toLowerCase().includes(q) ||
      r.institution_name.toLowerCase().includes(q) ||
      r.institution_id.toLowerCase().includes(q) ||
      r.authority_name.toLowerCase().includes(q) ||
      r.doc_type.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Authorized Source Verification Adapter
            </h1>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-900 border border-amber-300">
              SIMULATED ADAPTER
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Pluggable verification interface querying state boards, universities, and issuing authority registries.
          </p>
        </div>

        <button
          onClick={fetchData}
          className="inline-flex items-center gap-2 px-3 py-2 border border-slate-200 bg-white rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-xs"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Adapter Registry</span>
        </button>
      </div>

      {/* Regulatory Prototype Disclaimer */}
      <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 flex items-start gap-3">
        <Info className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-bold">Demonstration Integration Architecture</p>
          <p className="text-amber-800 leading-relaxed">
            All verification calls below execute against seeded demonstration records via the extensible Python
            <code className="bg-amber-100 px-1.5 py-0.5 rounded text-amber-950 font-mono text-[11px] mx-1">
              BaseVerificationAdapter
            </code>
            service. No real AICTE or external government databases are accessed without formal authorization and API credentials.
          </p>
        </div>
      </div>

      {/* Interactive Verification Sandbox Console */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
        <div className="flex items-center gap-2 mb-4">
          <PlayCircle className="w-5 h-5 text-blue-700" />
          <h2 className="text-base font-bold text-slate-900">Interactive Inquiry Sandbox</h2>
        </div>
        <p className="text-xs text-slate-500 mb-6">
          Query an issuing authority for an application document and observe deterministic regulatory comparison.
        </p>

        <form onSubmit={handleTestInquiry} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Target Application Dossier
              </label>
              <select
                value={selectedAppId}
                onChange={(e) => setSelectedAppId(e.target.value)}
                className="w-full text-xs border border-slate-300 rounded-lg p-2.5 bg-white text-slate-800 focus:outline-hidden focus:ring-1 focus:ring-blue-500"
              >
                {applications.map((app) => (
                  <option key={app.id} value={app.id}>
                    {app.id} — {app.institution_name.substring(0, 32)} (PID: {app.institution_id})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Authorized Issuing Authority
              </label>
              <select
                value={authorityName}
                onChange={(e) => setAuthorityName(e.target.value)}
                className="w-full text-xs border border-slate-300 rounded-lg p-2.5 bg-white text-slate-800 focus:outline-hidden focus:ring-1 focus:ring-blue-500"
              >
                <option value="STATE_TECHNICAL_BOARD_MOCK">State Board of Technical Education (Mock)</option>
                <option value="UNIVERSITY_AFFILIATION_PORTAL_MOCK">State Affiliating University Portal (Mock)</option>
                <option value="DIRECTORATE_TECHNICAL_EDUCATION_MOCK">Directorate of Technical Education (Mock)</option>
                <option value="CENTRAL_LAND_REVENUE_PORTAL_MOCK">Central Revenue & Land Registry (Mock)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Certificate / Reference Number
              </label>
              <input
                type="text"
                placeholder="e.g. NOC-2024-MH-4421, EOA-2023-AICTE-1001"
                value={certNumber}
                onChange={(e) => setCertNumber(e.target.value)}
                required
                className="w-full text-xs border border-slate-300 rounded-lg p-2.5 text-slate-800 font-mono focus:outline-hidden focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="flex items-center justify-between pt-2">
            <div className="text-xs text-slate-500 flex items-center gap-2">
              <span>Quick Test Certificates:</span>
              <button
                type="button"
                onClick={() => setCertNumber("NOC-2024-MH-4421")}
                className="font-mono text-[11px] px-2 py-0.5 bg-slate-100 hover:bg-slate-200 rounded text-slate-700"
              >
                NOC-2024-MH-4421 (Valid)
              </button>
              <button
                type="button"
                onClick={() => setCertNumber("AFF-2023-PU-9912")}
                className="font-mono text-[11px] px-2 py-0.5 bg-slate-100 hover:bg-slate-200 rounded text-slate-700"
              >
                AFF-2023-PU-9912 (Mismatch)
              </button>
              <button
                type="button"
                onClick={() => setCertNumber("NOC-EXP-2021-99")}
                className="font-mono text-[11px] px-2 py-0.5 bg-slate-100 hover:bg-slate-200 rounded text-slate-700"
              >
                NOC-EXP-2021-99 (Expired)
              </button>
            </div>

            <button
              type="submit"
              disabled={verifying || !certNumber.trim() || !selectedAppId}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold rounded-lg shadow-xs transition-colors disabled:opacity-50"
            >
              {verifying ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <ShieldCheck className="w-3.5 h-3.5" />
              )}
              <span>Execute Authority Query</span>
            </button>
          </div>
        </form>

        {inquiryError && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-800 rounded-lg text-xs font-medium">
            {inquiryError}
          </div>
        )}

        {inquiryResult && (
          <div className="mt-6 p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Authority Verification Result
              </span>
              <span className="text-[10px] font-mono font-bold bg-amber-100 text-amber-900 px-2 py-0.5 rounded border border-amber-300">
                SIMULATED RESPONSE
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-white p-4 rounded-lg border border-slate-200 text-xs">
              <div>
                <span className="text-slate-400 block text-[11px]">Authority</span>
                <span className="font-semibold text-slate-900">{inquiryResult.authority_name}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[11px]">Certificate Number</span>
                <span className="font-mono font-bold text-slate-900">{inquiryResult.certificate_number}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[11px]">Verification Outcome</span>
                <div className="mt-1">
                  <StatusBadge status={inquiryResult.status} />
                </div>
              </div>
              <div>
                <span className="text-slate-400 block text-[11px]">Check Timestamp</span>
                <span className="text-slate-600">{formatDate(inquiryResult.check_timestamp)}</span>
              </div>
            </div>

            {inquiryResult.mismatch_details && (
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900">
                <strong>Discrepancy Details: </strong>
                {inquiryResult.mismatch_details}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Seeded Issuing Authority Records Registry Table */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-slate-700" />
            <h2 className="text-base font-bold text-slate-900">
              Mock Issuing Authority Registry
            </h2>
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
              {mockRecords.length} Seeded Records
            </span>
          </div>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search certificate, PID, authority..."
              value={tableSearch}
              onChange={(e) => setTableSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </div>

        {loading ? (
          <div className="py-12 text-center">
            <div className="w-7 h-7 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            <p className="text-xs text-slate-500 font-medium">Loading simulated authority registry...</p>
          </div>
        ) : filteredRecords.length === 0 ? (
          <div className="py-12 text-center text-slate-500 bg-slate-50 rounded-lg border border-dashed border-slate-200 text-xs">
            No mock authority records match your search filter.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-2.5 px-3">Certificate Number</th>
                  <th className="py-2.5 px-3">Issuing Authority</th>
                  <th className="py-2.5 px-3">Registered Institution</th>
                  <th className="py-2.5 px-3">Document Type</th>
                  <th className="py-2.5 px-3">Authority Status</th>
                  <th className="py-2.5 px-3">Validity</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {filteredRecords.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-3">
                      <span className="font-mono font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                        {r.certificate_number}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-medium text-slate-800">
                      {r.authority_name}
                    </td>
                    <td className="py-3 px-3">
                      <div className="font-semibold text-slate-900">{r.institution_name}</div>
                      <div className="text-[11px] text-slate-500 font-mono">PID: {r.institution_id}</div>
                    </td>
                    <td className="py-3 px-3 text-slate-600 font-medium">
                      {r.doc_type}
                    </td>
                    <td className="py-3 px-3">
                      <span
                        className={`text-[11px] font-semibold px-2 py-0.5 rounded border ${
                          r.status === "ACTIVE" || r.status === "VALID"
                            ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                            : r.status === "EXPIRED"
                            ? "bg-amber-50 text-amber-800 border-amber-200"
                            : "bg-red-50 text-red-800 border-red-200"
                        }`}
                      >
                        {r.status}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-slate-500">
                      {r.expiry_date ? formatDate(r.expiry_date) : "Permanent"}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => populateFromRecord(r)}
                        className="inline-flex items-center gap-1 px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-xs font-semibold transition-colors"
                      >
                        <span>Test in Sandbox</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Integration Technical Reference */}
      <div className="bg-slate-900 text-white rounded-xl p-6 shadow-xs space-y-3">
        <div className="flex items-center gap-2">
          <Code className="w-5 h-5 text-blue-400" />
          <h3 className="text-sm font-bold">Authorized Systems Adapter Architecture</h3>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          The Python backend implements a strict adapter pattern via
          <code className="bg-slate-800 text-blue-300 px-1.5 py-0.5 rounded font-mono text-[11px] mx-1">
            VerificationAdapter
          </code>
          supporting timeout controls, deterministic simulation states, and audit trails. When an authorized external
          REST/SOAP/API gateway (such as DigiLocker or State University Portals) is provisioned with signed credentials,
          a subclass of
          <code className="bg-slate-800 text-blue-300 px-1.5 py-0.5 rounded font-mono text-[11px] mx-1">
            BaseVerificationAdapter
          </code>
          is registered without modifying core regulatory rules or workflow persistence.
        </p>
      </div>
    </div>
  );
}
