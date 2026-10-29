"use client";

import React from "react";
import { Modal } from "@/components/ui/Modal";
import { DocumentItem, ValidationFinding } from "@/lib/types";
import { api } from "@/lib/api";
import { formatBytes, formatDate } from "@/lib/utils";
import { FileText, ExternalLink, Hash, CheckCircle, AlertTriangle, Layers } from "lucide-react";

interface EvidenceViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  document: DocumentItem | null;
  finding?: ValidationFinding | null;
}

export function EvidenceViewerModal({
  isOpen,
  onClose,
  document: doc,
  finding,
}: EvidenceViewerModalProps) {
  if (!doc) return null;

  const viewUrl = api.getDocumentViewUrl(doc.id);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Document Inspection: ${doc.original_filename}`}
      subtitle={`Document ID: ${doc.id} • Classified as ${doc.doc_type} (${(doc.classification_confidence * 100).toFixed(0)}% confidence)`}
      maxWidth="max-w-4xl"
    >
      <div className="space-y-6">
        {/* Linked Finding Banner if opened from a finding */}
        {finding && (
          <div className="p-4 rounded-lg bg-amber-50 border border-amber-200">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <div className="text-xs uppercase font-bold text-amber-800 tracking-wider">
                  Associated Finding: {finding.title}
                </div>
                <p className="text-sm text-amber-900 mt-1">{finding.explanation}</p>
                {finding.evidence_snippet && (
                  <div className="mt-2.5 p-2 bg-white rounded border border-amber-300 font-mono text-xs text-slate-800">
                    <span className="text-slate-400 select-none">Snippet (Page {finding.page_number || 1}): </span>
                    <mark className="bg-amber-200 text-amber-900 px-1 py-0.5 rounded">
                      {finding.evidence_snippet}
                    </mark>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Metadata Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 bg-slate-50 border border-slate-200 rounded-lg text-xs">
          <div>
            <span className="text-slate-500 block mb-0.5">Classification</span>
            <span className="font-semibold text-slate-800">{doc.doc_type}</span>
          </div>
          <div>
            <span className="text-slate-500 block mb-0.5">File Size</span>
            <span className="font-semibold text-slate-800">{formatBytes(doc.file_size_bytes)}</span>
          </div>
          <div>
            <span className="text-slate-500 block mb-0.5">Pages</span>
            <span className="font-semibold text-slate-800">{doc.page_count} page(s)</span>
          </div>
          <div>
            <span className="text-slate-500 block mb-0.5">OCR Engine</span>
            <span className="font-semibold text-slate-800">{doc.ocr_engine_used}</span>
          </div>
          <div className="col-span-2 sm:col-span-4 pt-2 border-t border-slate-200 flex items-center gap-2">
            <Hash className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-500">SHA-256 Fingerprint:</span>
            <span className="font-mono text-slate-700 select-all truncate">{doc.sha256_hash}</span>
          </div>
        </div>

        {/* Actions & Preview Link */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-slate-500" />
            <span className="text-sm font-semibold text-slate-800">Document Stream & Text Inspector</span>
          </div>
          <a
            href={viewUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-medium transition-colors shadow-xs"
          >
            <span>Open Original File in New Tab</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>

        {/* Extracted Text Viewer */}
        <div className="border border-slate-200 rounded-lg overflow-hidden">
          <div className="bg-slate-100 px-4 py-2 border-b border-slate-200 text-xs font-semibold text-slate-700 flex justify-between items-center">
            <span>OCR Extracted Text Buffer</span>
            <span className="text-slate-500 text-[11px] font-normal">
              Status: {doc.ocr_status}
            </span>
          </div>
          <div className="p-4 bg-slate-900 text-slate-200 font-mono text-xs max-h-80 overflow-y-auto whitespace-pre-wrap leading-relaxed select-text">
            {doc.extracted_text_preview || "No readable text content extracted from this document."}
          </div>
        </div>
      </div>
    </Modal>
  );
}
