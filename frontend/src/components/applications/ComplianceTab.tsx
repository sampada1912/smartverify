"use client";

import React, { useState } from "react";
import { ComplianceEvaluation } from "@/lib/types";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { Scale, CheckCircle2, AlertTriangle, AlertCircle, RefreshCw } from "lucide-react";

interface ComplianceTabProps {
  applicationId: string;
  evaluations: ComplianceEvaluation[];
  onRefresh: () => void;
}

export function ComplianceTab({ applicationId, evaluations, onRefresh }: ComplianceTabProps) {
  const [evaluating, setEvaluating] = useState(false);

  const handleReevaluate = async () => {
    setEvaluating(true);
    try {
      await api.evaluateCompliance(applicationId);
      onRefresh();
    } catch (err) {
      console.error(err);
    } finally {
      setEvaluating(false);
    }
  };

  const passCount = evaluations.filter((e) => e.status === "PASS").length;
  const failCount = evaluations.filter((e) => e.status === "FAIL").length;
  const warningCount = evaluations.filter((e) => e.status === "WARNING" || e.status === "NEEDS_REVIEW").length;

  return (
    <div className="space-y-6">
      {/* Header & Metrics */}
      <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Scale className="w-4 h-4 text-blue-600" />
            <span>Category-Based Compliance Rule Evaluations</span>
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Deterministic evaluations cross-referencing statutory norms, extracted document fields, and authority registers.
          </p>
        </div>

        <button
          type="button"
          onClick={handleReevaluate}
          disabled={evaluating}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-900 text-white rounded-md text-xs font-semibold shadow-xs transition-colors shrink-0"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${evaluating ? "animate-spin" : ""}`} />
          <span>{evaluating ? "Evaluating..." : "Re-evaluate Rules"}</span>
        </button>
      </div>

      {/* Evaluations List */}
      <div className="space-y-3">
        {evaluations.length === 0 ? (
          <div className="bg-white p-8 text-center text-slate-400 text-sm border border-slate-200 rounded-lg">
            No compliance evaluations yet. Click Re-evaluate Rules above.
          </div>
        ) : (
          evaluations.map((ev) => (
            <div
              key={ev.id}
              className="bg-white p-5 rounded-lg border border-slate-200 shadow-xs space-y-2.5"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                    {ev.rule_id}
                  </span>
                  <h4 className="font-bold text-sm text-slate-900">{ev.rule_name}</h4>
                </div>
                <StatusBadge status={ev.status} type="compliance" />
              </div>

              <p className="text-xs text-slate-700 leading-relaxed">{ev.explanation}</p>

              {ev.evidence_summary && (
                <div className="p-2.5 bg-slate-50 rounded border border-slate-200 text-xs text-slate-600 font-mono">
                  <span className="font-bold text-slate-700 block mb-0.5">Applied Evidence:</span>
                  <span>{ev.evidence_summary}</span>
                </div>
              )}

              <div className="text-[11px] text-slate-400 pt-1 border-t border-slate-100 flex justify-between">
                <span>Rule Engine: Configurable Deterministic Evaluator</span>
                <span>Evaluated: {formatDate(ev.evaluated_at)}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
