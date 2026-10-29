"use client";

import React, { useState } from "react";
import { ValidationFinding, FindingSeverity, FindingStatus } from "@/lib/types";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { SeverityBadge } from "@/components/ui/SeverityBadge";
import { FindingDetailModal } from "@/components/findings/FindingDetailModal";
import { formatDate } from "@/lib/utils";
import {
  AlertTriangle,
  CheckCircle2,
  Filter,
  FileSearch,
  ExternalLink,
  ShieldAlert,
} from "lucide-react";

interface ValidationFindingsTabProps {
  findings: ValidationFinding[];
  onRefresh: () => void;
  onInspectEvidence?: (docId: string, finding: ValidationFinding) => void;
}

export function ValidationFindingsTab({
  findings,
  onRefresh,
  onInspectEvidence,
}: ValidationFindingsTabProps) {
  const [selectedFinding, setSelectedFinding] = useState<ValidationFinding | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>("ALL");
  const [filterStatus, setFilterStatus] = useState<string>("ALL");

  const filtered = findings.filter((f) => {
    if (filterSeverity !== "ALL" && f.severity !== filterSeverity) return false;
    if (filterStatus !== "ALL" && f.status !== filterStatus) return false;
    return true;
  });

  const highCount = findings.filter((f) => f.severity === "HIGH" && f.status !== "RESOLVED").length;
  const openCount = findings.filter((f) => f.status === "OPEN" || f.status === "UNDER_REVIEW").length;

  return (
    <div className="space-y-6">
      {/* Triage Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-500 font-semibold block uppercase tracking-wider">
              Total Identified Findings
            </span>
            <span className="text-2xl font-bold text-slate-900 mt-1 block">{findings.length}</span>
          </div>
          <ShieldAlert className="w-8 h-8 text-slate-400" />
        </div>

        <div className="bg-white p-4 rounded-lg border border-rose-200 shadow-xs flex items-center justify-between bg-rose-50/20">
          <div>
            <span className="text-xs text-rose-700 font-bold block uppercase tracking-wider">
              Critical / High Deficiencies
            </span>
            <span className="text-2xl font-bold text-rose-700 mt-1 block">{highCount}</span>
          </div>
          <AlertTriangle className="w-8 h-8 text-rose-500" />
        </div>

        <div className="bg-white p-4 rounded-lg border border-amber-200 shadow-xs flex items-center justify-between bg-amber-50/20">
          <div>
            <span className="text-xs text-amber-800 font-bold block uppercase tracking-wider">
              Pending Resolution / Review
            </span>
            <span className="text-2xl font-bold text-amber-800 mt-1 block">{openCount}</span>
          </div>
          <CheckCircle2 className="w-8 h-8 text-amber-500" />
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-500" />
          <span className="font-semibold text-slate-700">Filter Scrutiny Findings:</span>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="text-slate-500">Severity:</span>
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="p-1.5 bg-slate-50 border border-slate-300 rounded font-medium text-slate-800 focus:outline-blue-600"
            >
              <option value="ALL">All Severities</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
              <option value="INFO">Info</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-slate-500">Status:</span>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="p-1.5 bg-slate-50 border border-slate-300 rounded font-medium text-slate-800 focus:outline-blue-600"
            >
              <option value="ALL">All Statuses</option>
              <option value="OPEN">Open</option>
              <option value="UNDER_REVIEW">Under Review</option>
              <option value="REQUESTED_INFORMATION">Requested Evidence</option>
              <option value="RESOLVED">Resolved</option>
              <option value="ESCALATED">Escalated</option>
            </select>
          </div>
        </div>
      </div>

      {/* Findings List */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="bg-white p-8 text-center text-slate-400 text-sm border border-slate-200 rounded-lg">
            No validation findings matching the selected filters.
          </div>
        ) : (
          filtered.map((finding) => (
            <div
              key={finding.id}
              onClick={() => setSelectedFinding(finding)}
              className="bg-white p-5 rounded-lg border border-slate-200 hover:border-blue-400 hover:shadow-md transition-all cursor-pointer space-y-3"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <SeverityBadge severity={finding.severity} />
                  <span className="font-bold text-sm text-slate-900">{finding.title}</span>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={finding.status} />
                  <span className="text-xs text-slate-400 font-mono">{finding.id}</span>
                </div>
              </div>

              <p className="text-xs text-slate-600 leading-relaxed">{finding.explanation}</p>

              {(finding.expected_value || finding.observed_value) && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] pt-1">
                  <div className="bg-slate-50 p-2 rounded border border-slate-200 text-slate-700">
                    <span className="font-semibold text-slate-500 block">Expected:</span>
                    <span className="font-mono text-slate-900">{finding.expected_value || "Regulatory Compliance"}</span>
                  </div>
                  <div className="bg-rose-50/50 p-2 rounded border border-rose-200 text-rose-900">
                    <span className="font-semibold text-rose-700 block">Observed:</span>
                    <span className="font-mono text-rose-950">{finding.observed_value || "Discrepancy"}</span>
                  </div>
                </div>
              )}

              {finding.evidence_snippet && (
                <div className="text-[11px] font-mono p-2 bg-amber-50/70 text-amber-950 rounded border border-amber-200 truncate">
                  <span className="font-bold text-amber-900">Page {finding.page_number || 1} Evidence: </span>
                  {finding.evidence_snippet}
                </div>
              )}

              <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-[11px] text-slate-400">
                <span>Source: {finding.source_record || "Deterministic Scrutiny Engine"}</span>
                <span className="text-blue-600 font-semibold hover:underline">
                  Click to inspect & take regulatory action &rarr;
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Finding Detail & Action Modal */}
      <FindingDetailModal
        isOpen={!!selectedFinding}
        onClose={() => setSelectedFinding(null)}
        finding={selectedFinding}
        onUpdated={onRefresh}
        onInspectEvidence={onInspectEvidence}
      />
    </div>
  );
}
