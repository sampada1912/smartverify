"use client";

import React, { useState } from "react";
import { Modal } from "@/components/ui/Modal";
import { ValidationFinding, FindingStatus } from "@/lib/types";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { SeverityBadge } from "@/components/ui/SeverityBadge";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import {
  AlertTriangle,
  CheckCircle2,
  ArrowUpRight,
  Send,
  HelpCircle,
  FileSearch,
  RotateCcw,
} from "lucide-react";

interface FindingDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  finding: ValidationFinding | null;
  onUpdated: () => void;
  onInspectEvidence?: (docId: string, finding: ValidationFinding) => void;
}

export function FindingDetailModal({
  isOpen,
  onClose,
  finding,
  onUpdated,
  onInspectEvidence,
}: FindingDetailModalProps) {
  const [activeAction, setActiveAction] = useState<"RESOLVE" | "ESCALATE" | "OVERRIDE" | "REQUEST" | null>(null);
  const [resolutionNotes, setResolutionNotes] = useState("");
  const [overrideStatus, setOverrideStatus] = useState<FindingStatus>("RESOLVED");
  const [overrideReason, setOverrideReason] = useState("");
  const [requestText, setRequestText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!finding) return null;

  const handleResolve = async (action: "RESOLVE" | "ESCALATE") => {
    if (!resolutionNotes.trim()) {
      setError("Please enter reviewer resolution notes.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await api.resolveFinding(finding.id, action, resolutionNotes);
      onUpdated();
      onClose();
    } catch (err: any) {
      setError(err.message || "Action failed");
    } finally {
      setLoading(false);
    }
  };

  const handleOverride = async () => {
    if (!overrideReason.trim() || overrideReason.trim().length < 5) {
      setError("A detailed mandatory justification is required for manual override.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await api.overrideFinding(finding.id, overrideStatus, overrideReason);
      onUpdated();
      onClose();
    } catch (err: any) {
      setError(err.message || "Override failed");
    } finally {
      setLoading(false);
    }
  };

  const handleRequestEvidence = async () => {
    if (!requestText.trim()) {
      setError("Please specify the additional evidence requested.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await api.createEvidenceRequest(finding.application_id, finding.id, requestText);
      onUpdated();
      onClose();
    } catch (err: any) {
      setError(err.message || "Evidence request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={finding.title}
      subtitle={`Finding ID: ${finding.id} • Category: ${finding.category.replace(/_/g, " ")}`}
      maxWidth="max-w-3xl"
    >
      <div className="space-y-5">
        {/* Badges & Status */}
        <div className="flex items-center gap-3">
          <SeverityBadge severity={finding.severity} />
          <StatusBadge status={finding.status} />
          <span className="text-xs text-slate-500 ml-auto">
            Detected: {formatDate(finding.detection_timestamp)}
          </span>
        </div>

        {/* Explanation */}
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
          <h4 className="text-xs font-bold uppercase text-slate-500 mb-1 tracking-wider">
            Scrutiny Finding Description
          </h4>
          <p className="text-sm text-slate-800 leading-relaxed">{finding.explanation}</p>
        </div>

        {/* Expected vs Observed Comparison */}
        {(finding.expected_value || finding.observed_value) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div className="p-3 bg-emerald-50/70 border border-emerald-200 rounded-lg">
              <span className="font-semibold text-emerald-800 block mb-1">Expected Standard / Value:</span>
              <span className="font-mono text-emerald-950">{finding.expected_value || "Regulatory Norm Requirement"}</span>
            </div>
            <div className="p-3 bg-rose-50/70 border border-rose-200 rounded-lg">
              <span className="font-semibold text-rose-800 block mb-1">Observed Value / State:</span>
              <span className="font-mono text-rose-950">{finding.observed_value || "Missing or Non-compliant"}</span>
            </div>
          </div>
        )}

        {/* Evidence Snippet */}
        {finding.evidence_snippet && (
          <div className="p-3 bg-amber-50/60 border border-amber-200 rounded-lg text-xs">
            <div className="flex items-center justify-between mb-1 font-semibold text-amber-800">
              <span>Document Evidence Snippet (Page {finding.page_number || 1})</span>
              {finding.document_id && onInspectEvidence && (
                <button
                  type="button"
                  onClick={() => onInspectEvidence(finding.document_id!, finding)}
                  className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 font-medium"
                >
                  <FileSearch className="w-3.5 h-3.5" />
                  <span>Inspect Document</span>
                </button>
              )}
            </div>
            <p className="font-mono text-slate-800 bg-white p-2 rounded border border-amber-200">
              {finding.evidence_snippet}
            </p>
          </div>
        )}

        {/* Recommended Action */}
        <div className="p-3 bg-blue-50/60 border border-blue-200 rounded-lg text-xs">
          <span className="font-semibold text-blue-900 block mb-1">Recommended Regulatory Action:</span>
          <p className="text-blue-950">{finding.recommended_action}</p>
        </div>

        {/* Prior Resolution / Override Details if already acted upon */}
        {finding.resolution_notes && (
          <div className="p-3 bg-slate-100 rounded-lg text-xs border border-slate-200">
            <span className="font-semibold text-slate-700 block mb-0.5">
              Reviewer Note ({finding.resolved_by || "Reviewer"} on {formatDate(finding.resolved_at)}):
            </span>
            <p className="text-slate-800">{finding.resolution_notes}</p>
          </div>
        )}

        {finding.override_reason && (
          <div className="p-3 bg-purple-50 rounded-lg text-xs border border-purple-200">
            <span className="font-semibold text-purple-900 block mb-0.5">
              Manual Override Justification ({finding.resolved_by || "Reviewer"} on {formatDate(finding.resolved_at)}):
            </span>
            <p className="text-purple-950">{finding.override_reason}</p>
          </div>
        )}

        {error && (
          <div className="p-3 bg-red-50 text-red-700 rounded-lg text-xs border border-red-200 font-medium">
            {error}
          </div>
        )}

        {/* Reviewer Action Buttons */}
        <div className="pt-2 border-t border-slate-200">
          {!activeAction ? (
            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={() => setActiveAction("RESOLVE")}
                className="inline-flex items-center gap-1.5 px-3 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-md text-xs font-semibold shadow-xs transition-colors"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Mark Resolved</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveAction("ESCALATE")}
                className="inline-flex items-center gap-1.5 px-3 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-md text-xs font-semibold shadow-xs transition-colors"
              >
                <ArrowUpRight className="w-4 h-4" />
                <span>Escalate Finding</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveAction("REQUEST")}
                className="inline-flex items-center gap-1.5 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-semibold shadow-xs transition-colors"
              >
                <Send className="w-4 h-4" />
                <span>Request Additional Evidence</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveAction("OVERRIDE")}
                className="inline-flex items-center gap-1.5 px-3 py-2 bg-slate-700 hover:bg-slate-800 text-white rounded-md text-xs font-semibold shadow-xs transition-colors ml-auto"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Manual Override</span>
              </button>
            </div>
          ) : (
            <div className="space-y-3 bg-slate-50 p-4 rounded-lg border border-slate-200">
              {activeAction === "RESOLVE" && (
                <div>
                  <h5 className="text-xs font-bold text-slate-800 mb-1">Resolve Finding</h5>
                  <textarea
                    value={resolutionNotes}
                    onChange={(e) => setResolutionNotes(e.target.value)}
                    placeholder="Enter resolution notes explaining how this finding was verified or satisfied..."
                    className="w-full text-xs p-2.5 border border-slate-300 rounded-md bg-white focus:outline-blue-500 min-h-[80px]"
                  />
                  <div className="flex gap-2 mt-2">
                    <button
                      type="button"
                      disabled={loading}
                      onClick={() => handleResolve("RESOLVE")}
                      className="px-3 py-1.5 bg-emerald-600 text-white text-xs font-semibold rounded-md shadow-xs hover:bg-emerald-700"
                    >
                      {loading ? "Submitting..." : "Confirm Resolution"}
                    </button>
                    <button
                      type="button"
                      onClick={() => setActiveAction(null)}
                      className="px-3 py-1.5 bg-slate-200 text-slate-700 text-xs font-medium rounded-md hover:bg-slate-300"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {activeAction === "ESCALATE" && (
                <div>
                  <h5 className="text-xs font-bold text-slate-800 mb-1">Escalate Finding for Committee Review</h5>
                  <textarea
                    value={resolutionNotes}
                    onChange={(e) => setResolutionNotes(e.target.value)}
                    placeholder="State reason for escalation to the Regional Hearing Committee or Scrutiny Board..."
                    className="w-full text-xs p-2.5 border border-slate-300 rounded-md bg-white focus:outline-blue-500 min-h-[80px]"
                  />
                  <div className="flex gap-2 mt-2">
                    <button
                      type="button"
                      disabled={loading}
                      onClick={() => handleResolve("ESCALATE")}
                      className="px-3 py-1.5 bg-amber-600 text-white text-xs font-semibold rounded-md shadow-xs hover:bg-amber-700"
                    >
                      {loading ? "Escalating..." : "Confirm Escalation"}
                    </button>
                    <button
                      type="button"
                      onClick={() => setActiveAction(null)}
                      className="px-3 py-1.5 bg-slate-200 text-slate-700 text-xs font-medium rounded-md hover:bg-slate-300"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {activeAction === "REQUEST" && (
                <div>
                  <h5 className="text-xs font-bold text-slate-800 mb-1">Request Additional Evidence from Institution</h5>
                  <textarea
                    value={requestText}
                    onChange={(e) => setRequestText(e.target.value)}
                    placeholder="Specify the exact certificate, clarification, or revised document required..."
                    className="w-full text-xs p-2.5 border border-slate-300 rounded-md bg-white focus:outline-blue-500 min-h-[80px]"
                  />
                  <div className="flex gap-2 mt-2">
                    <button
                      type="button"
                      disabled={loading}
                      onClick={handleRequestEvidence}
                      className="px-3 py-1.5 bg-blue-600 text-white text-xs font-semibold rounded-md shadow-xs hover:bg-blue-700"
                    >
                      {loading ? "Sending..." : "Transmit Evidence Inquiry"}
                    </button>
                    <button
                      type="button"
                      onClick={() => setActiveAction(null)}
                      className="px-3 py-1.5 bg-slate-200 text-slate-700 text-xs font-medium rounded-md hover:bg-slate-300"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {activeAction === "OVERRIDE" && (
                <div>
                  <h5 className="text-xs font-bold text-slate-800 mb-2">Reviewer Manual Status Override</h5>
                  <div className="mb-2">
                    <label className="text-xs text-slate-600 block mb-1 font-medium">New Status:</label>
                    <select
                      value={overrideStatus}
                      onChange={(e) => setOverrideStatus(e.target.value as FindingStatus)}
                      className="text-xs p-2 border border-slate-300 rounded-md bg-white focus:outline-blue-500 w-full"
                    >
                      <option value="RESOLVED">RESOLVED (Manual Verification)</option>
                      <option value="UNDER_REVIEW">UNDER_REVIEW (Requires Investigation)</option>
                      <option value="ESCALATED">ESCALATED (Hearing Committee)</option>
                      <option value="OPEN">OPEN (Reopen)</option>
                    </select>
                  </div>
                  <label className="text-xs text-slate-600 block mb-1 font-medium">
                    Mandatory Regulatory Justification:
                  </label>
                  <textarea
                    value={overrideReason}
                    onChange={(e) => setOverrideReason(e.target.value)}
                    placeholder="Enter formal justification for overriding this system finding..."
                    className="w-full text-xs p-2.5 border border-slate-300 rounded-md bg-white focus:outline-blue-500 min-h-[80px]"
                  />
                  <div className="flex gap-2 mt-2">
                    <button
                      type="button"
                      disabled={loading}
                      onClick={handleOverride}
                      className="px-3 py-1.5 bg-purple-700 text-white text-xs font-semibold rounded-md shadow-xs hover:bg-purple-800"
                    >
                      {loading ? "Saving Override..." : "Record Official Override"}
                    </button>
                    <button
                      type="button"
                      onClick={() => setActiveAction(null)}
                      className="px-3 py-1.5 bg-slate-200 text-slate-700 text-xs font-medium rounded-md hover:bg-slate-300"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </Modal>
  );
}
