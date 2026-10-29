"use client";

import React from "react";
import { ApplicationChecklistItem } from "@/lib/types";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { CheckCircle2, Clock, AlertCircle, FileCheck, Layers } from "lucide-react";

interface ChecklistTabProps {
  checklist: ApplicationChecklistItem[];
  onRefresh: () => void;
}

export function ChecklistTab({ checklist }: ChecklistTabProps) {
  const submittedCount = checklist.filter((c) => c.is_submitted).length;
  const satisfiedCount = checklist.filter((c) => c.validation_status === "SATISFIED").length;

  return (
    <div className="space-y-6">
      {/* Overview progress */}
      <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <FileCheck className="w-4 h-4 text-blue-600" />
            <span>Configurable Application Document Checklist</span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Backend-driven rules engine checklist based on application category.
          </p>
        </div>

        <div className="flex items-center gap-4 text-xs">
          <div>
            <span className="text-slate-500 block">Submitted:</span>
            <span className="font-bold text-slate-800">{submittedCount} of {checklist.length}</span>
          </div>
          <div className="w-px h-8 bg-slate-200" />
          <div>
            <span className="text-slate-500 block">Satisfied:</span>
            <span className="font-bold text-emerald-600">{satisfiedCount} of {checklist.length}</span>
          </div>
        </div>
      </div>

      {/* Checklist Table */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider">
              <tr>
                <th className="px-5 py-3">Code</th>
                <th className="px-4 py-3">Requirement Name</th>
                <th className="px-4 py-3">Document Type</th>
                <th className="px-4 py-3">Requirement</th>
                <th className="px-4 py-3">Submission</th>
                <th className="px-4 py-3">Validation Status</th>
                <th className="px-5 py-3">Explanation & Evidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-800">
              {checklist.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="px-5 py-3 font-mono font-bold text-slate-600">
                    {item.rule_code}
                  </td>
                  <td className="px-4 py-3 font-semibold text-slate-900">
                    {item.requirement_name}
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[11px]">
                      {item.document_type}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {item.is_required ? (
                      <span className="px-2 py-0.5 rounded font-bold text-[10px] uppercase bg-rose-50 text-rose-700 border border-rose-200">
                        Mandatory
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded font-medium text-[10px] uppercase bg-slate-100 text-slate-600">
                        Optional
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {item.is_submitted ? (
                      <span className="inline-flex items-center gap-1 text-emerald-700 font-medium text-[11px]">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                        <span>Submitted</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-amber-700 font-medium text-[11px]">
                        <Clock className="w-3.5 h-3.5 text-amber-500" />
                        <span>Pending</span>
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={item.validation_status} />
                  </td>
                  <td className="px-5 py-3 text-slate-600 max-w-xs">
                    <span className="block">{item.explanation || "—"}</span>
                    {item.evidence_summary && (
                      <span className="block text-[10px] text-slate-400 font-mono mt-0.5">
                        {item.evidence_summary}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
