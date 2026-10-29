"use client";

import React, { useState } from "react";
import { VerificationResult, VerificationStatus } from "@/lib/types";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { ShieldCheck, Search, AlertCircle, CheckCircle2, AlertTriangle, Layers } from "lucide-react";

interface VerificationTabProps {
  applicationId: string;
  results: VerificationResult[];
  onRefresh: () => void;
}

export function VerificationTab({ applicationId, results, onRefresh }: VerificationTabProps) {
  const [certNumber, setCertNumber] = useState("");
  const [authority, setAuthority] = useState("STATE_TECHNICAL_BOARD_MOCK");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleManualVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!certNumber.trim()) return;

    setLoading(true);
    setError(null);
    try {
      await api.triggerVerification(applicationId, certNumber.trim(), authority);
      setCertNumber("");
      onRefresh();
    } catch (err: any) {
      setError(err.message || "Verification inquiry failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Disclaimer Banner */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
        <div className="text-xs text-blue-900 leading-relaxed">
          <span className="font-bold block uppercase tracking-wider text-blue-950 mb-0.5">
            Configurable Authorized-Source Verification Adapter (SIMULATED)
          </span>
          All verification requests are evaluated against deterministic synthetic issuing authority records for demonstration purposes. Results are explicitly labeled as <span className="font-bold uppercase tracking-wider text-blue-700">SIMULATED</span> to prevent confusion with official council or government portals.
        </div>
      </div>

      {/* Manual Verification Form */}
      <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-xs">
        <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
          <Search className="w-4 h-4 text-blue-600" />
          <span>Execute Authority Certificate Verification</span>
        </h3>

        <form onSubmit={handleManualVerify} className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label className="text-xs text-slate-500 font-semibold block mb-1">
              Issuing Authority:
            </label>
            <select
              value={authority}
              onChange={(e) => setAuthority(e.target.value)}
              className="w-full text-xs p-2 border border-slate-300 rounded-md bg-white focus:outline-blue-600 font-medium"
            >
              <option value="STATE_TECHNICAL_BOARD_MOCK">State Technical Directorate (Mock)</option>
              <option value="ACCREDITATION_BOARD_MOCK">National Board of Accreditation (Mock)</option>
              <option value="AFFILIATING_UNIVERSITY_MOCK">Affiliating Technical University (Mock)</option>
            </select>
          </div>

          <div>
            <label className="text-xs text-slate-500 font-semibold block mb-1">
              Certificate / Letter / NOC Reference:
            </label>
            <input
              type="text"
              value={certNumber}
              onChange={(e) => setCertNumber(e.target.value)}
              placeholder="e.g. NOC-2025-99882 or NBA-TIER1-4491"
              className="w-full text-xs p-2 border border-slate-300 rounded-md bg-white focus:outline-blue-600 font-mono"
            />
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading || !certNumber.trim()}
              className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-semibold shadow-xs disabled:opacity-50 transition-colors"
            >
              {loading ? "Querying Register..." : "Run Authority Check"}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-3 p-2 bg-red-50 text-red-700 rounded text-xs border border-red-200">
            {error}
          </div>
        )}
      </div>

      {/* Verification History Table */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/50 flex justify-between items-center">
          <h3 className="text-sm font-bold text-slate-900">
            Recorded Authority Verification Results ({results.length})
          </h3>
        </div>

        {results.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-sm">
            No verification queries recorded yet. Enter a reference number above to test.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="px-5 py-3">Issuing Authority</th>
                  <th className="px-4 py-3">Reference / Cert Number</th>
                  <th className="px-4 py-3">Outcome</th>
                  <th className="px-4 py-3">Discrepancy / Details</th>
                  <th className="px-4 py-3">Environment</th>
                  <th className="px-5 py-3 text-right">Verification Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-800">
                {results.map((res) => (
                  <tr key={res.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-5 py-3 font-semibold text-slate-900">
                      {res.authority_name.replace(/_/g, " ")}
                    </td>
                    <td className="px-4 py-3 font-mono font-medium text-slate-700">
                      {res.certificate_number}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={res.status} type="verification" />
                    </td>
                    <td className="px-4 py-3 text-slate-600 max-w-xs">
                      {res.mismatch_details || (
                        <span className="text-emerald-700 font-medium">Record Active & Authenticated</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-purple-50 text-purple-700 border border-purple-200">
                        SIMULATED
                      </span>
                    </td>
                    <td className="px-5 py-3 text-right text-slate-500">
                      {formatDate(res.check_timestamp)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
