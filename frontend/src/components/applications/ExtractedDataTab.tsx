"use client";

import React, { useState } from "react";
import { ExtractedField } from "@/lib/types";
import { api } from "@/lib/api";
import { Modal } from "@/components/ui/Modal";
import { Edit3, CheckCircle, Search, FileText } from "lucide-react";

interface ExtractedDataTabProps {
  fields: ExtractedField[];
  onRefresh: () => void;
}

export function ExtractedDataTab({ fields, onRefresh }: ExtractedDataTabProps) {
  const [selectedField, setSelectedField] = useState<ExtractedField | null>(null);
  const [correctedValue, setCorrectedValue] = useState("");
  const [justification, setJustification] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const openCorrectionModal = (f: ExtractedField) => {
    setSelectedField(f);
    setCorrectedValue(f.normalized_value || f.extracted_value);
    setJustification("");
    setError(null);
  };

  const handleSaveCorrection = async () => {
    if (!selectedField) return;
    if (!justification.trim() || justification.trim().length < 5) {
      setError("Please provide a formal justification for modifying the OCR extracted value.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await api.correctField(selectedField.id, correctedValue, justification);
      setSelectedField(null);
      onRefresh();
    } catch (err: any) {
      setError(err.message || "Failed to save correction");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg border border-slate-200 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/50 flex justify-between items-center">
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              Structured OCR Field Extractions ({fields.length})
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Deterministic regex and layout extraction with source provenance and confidence scores.
            </p>
          </div>
        </div>

        {fields.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-sm">
            No extracted fields yet. Upload supporting documents to process fields.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="px-5 py-3">Field Name</th>
                  <th className="px-4 py-3">Extracted Value</th>
                  <th className="px-4 py-3">Normalized Value</th>
                  <th className="px-4 py-3">Confidence</th>
                  <th className="px-4 py-3">Page</th>
                  <th className="px-4 py-3">Provenance Snippet</th>
                  <th className="px-5 py-3 text-right">Reviewer Correction</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-800">
                {fields.map((f) => (
                  <tr key={f.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-5 py-3 font-semibold text-slate-900">
                      {f.field_name.replace(/_/g, " ").toUpperCase()}
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-700">
                      {f.extracted_value}
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-mono px-2 py-0.5 bg-slate-100 rounded text-slate-900 font-semibold">
                        {f.normalized_value}
                      </span>
                      {f.is_corrected && (
                        <span className="ml-1 text-[10px] text-purple-700 font-semibold block">
                          [Reviewer Corrected by {f.corrected_by}]
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {(f.confidence * 100).toFixed(0)}%
                    </td>
                    <td className="px-4 py-3 text-slate-500">
                      Page {f.page_number}
                    </td>
                    <td className="px-4 py-3 font-mono text-[11px] text-slate-500 max-w-[200px] truncate" title={f.snippet || ""}>
                      {f.snippet || "—"}
                    </td>
                    <td className="px-5 py-3 text-right">
                      <button
                        type="button"
                        onClick={() => openCorrectionModal(f)}
                        className="inline-flex items-center gap-1 px-2.5 py-1 text-purple-700 bg-purple-50 hover:bg-purple-100 rounded font-medium transition-colors"
                      >
                        <Edit3 className="w-3 h-3" />
                        <span>Edit / Correct</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Reviewer Correction Modal */}
      <Modal
        isOpen={!!selectedField}
        onClose={() => setSelectedField(null)}
        title={`Reviewer Field Correction: ${selectedField?.field_name}`}
        subtitle="Modifications are permanently logged in the verifiable audit trail."
        maxWidth="max-w-md"
      >
        <div className="space-y-4 text-xs">
          <div>
            <label className="text-slate-600 font-semibold block mb-1">Original Extracted Value:</label>
            <div className="p-2 bg-slate-100 rounded font-mono text-slate-800">
              {selectedField?.extracted_value}
            </div>
          </div>

          <div>
            <label className="text-slate-700 font-semibold block mb-1">Corrected Value:</label>
            <input
              type="text"
              value={correctedValue}
              onChange={(e) => setCorrectedValue(e.target.value)}
              className="w-full p-2 border border-slate-300 rounded focus:outline-blue-600 font-mono"
            />
          </div>

          <div>
            <label className="text-slate-700 font-semibold block mb-1">
              Mandatory Correction Justification:
            </label>
            <textarea
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              placeholder="State regulatory reason or physical verification finding for correcting this value..."
              className="w-full p-2 border border-slate-300 rounded focus:outline-blue-600 min-h-[70px]"
            />
          </div>

          {error && <div className="p-2 bg-red-50 text-red-700 rounded border border-red-200">{error}</div>}

          <div className="flex justify-end gap-2 pt-2 border-t border-slate-200">
            <button
              type="button"
              onClick={() => setSelectedField(null)}
              className="px-3 py-1.5 text-slate-600 hover:bg-slate-100 rounded font-medium"
            >
              Cancel
            </button>
            <button
              type="button"
              disabled={loading}
              onClick={handleSaveCorrection}
              className="px-4 py-1.5 bg-purple-700 hover:bg-purple-800 text-white rounded font-semibold shadow-xs"
            >
              {loading ? "Recording..." : "Save Correction"}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
