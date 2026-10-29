"use client";

import React, { useState, useRef } from "react";
import { DocumentItem, ValidationFinding } from "@/lib/types";
import { api } from "@/lib/api";
import { formatBytes, formatDate } from "@/lib/utils";
import { EvidenceViewerModal } from "@/components/evidence/EvidenceViewerModal";
import {
  Upload,
  FileText,
  ExternalLink,
  ShieldCheck,
  CheckCircle,
  AlertCircle,
  Eye,
  FileSearch,
} from "lucide-react";

interface DocumentsTabProps {
  applicationId: string;
  documents: DocumentItem[];
  onRefresh: () => void;
}

export function DocumentsTab({ applicationId, documents, onRefresh }: DocumentsTabProps) {
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    setUploadError(null);
    try {
      const fileList = Array.from(files);
      await api.uploadDocuments(applicationId, fileList);
      onRefresh();
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err: any) {
      setUploadError(err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Box */}
      <div className="bg-white p-6 rounded-lg border-2 border-dashed border-slate-300 hover:border-blue-500 transition-colors text-center">
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.png,.jpg,.jpeg"
          onChange={handleFileChange}
          className="hidden"
          id="file-upload-input"
          disabled={uploading}
        />
        <label
          htmlFor="file-upload-input"
          className="cursor-pointer flex flex-col items-center justify-center"
        >
          <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
            <Upload className="w-6 h-6" />
          </div>
          <span className="text-sm font-semibold text-slate-900">
            {uploading ? "Processing and Extracting OCR Text..." : "Upload Regulatory Documents"}
          </span>
          <span className="text-xs text-slate-500 mt-1">
            Supports PDF, PNG, and JPEG up to 25MB. Files are cryptographically fingerprinted (SHA-256) and verified.
          </span>
        </label>
        {uploadError && (
          <div className="mt-3 p-2 bg-red-50 text-red-700 text-xs rounded border border-red-200">
            {uploadError}
          </div>
        )}
      </div>

      {/* Document Table */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/50 flex justify-between items-center">
          <h3 className="text-sm font-bold text-slate-900">
            Uploaded Evidentiary Documents ({documents.length})
          </h3>
        </div>

        {documents.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-sm">
            No documents uploaded yet. Upload required verification files above.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="px-5 py-3">Document / File</th>
                  <th className="px-4 py-3">Classified Type</th>
                  <th className="px-4 py-3">Confidence</th>
                  <th className="px-4 py-3">OCR Status</th>
                  <th className="px-4 py-3">SHA-256 Fingerprint</th>
                  <th className="px-4 py-3">Upload Date</th>
                  <th className="px-5 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-800">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-5 py-3 font-medium text-slate-900">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-blue-600 shrink-0" />
                        <div>
                          <span className="font-semibold">{doc.original_filename}</span>
                          <span className="block text-[10px] text-slate-400">
                            {formatBytes(doc.file_size_bytes)} &bull; {doc.page_count} page(s)
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-800 border border-blue-200 font-semibold">
                        {doc.doc_type}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-medium text-slate-700">
                        {(doc.classification_confidence * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700">
                        <CheckCircle className="w-3 h-3 text-emerald-500" />
                        <span>{doc.ocr_status}</span>
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-[10px] text-slate-500 max-w-[140px] truncate" title={doc.sha256_hash}>
                      {doc.sha256_hash}
                    </td>
                    <td className="px-4 py-3 text-slate-500">
                      {formatDate(doc.uploaded_at)}
                    </td>
                    <td className="px-5 py-3 text-right space-x-2">
                      <button
                        type="button"
                        onClick={() => setSelectedDoc(doc)}
                        className="inline-flex items-center gap-1 px-2.5 py-1 text-slate-700 bg-slate-100 hover:bg-slate-200 rounded font-medium transition-colors"
                      >
                        <FileSearch className="w-3 h-3" />
                        <span>Inspect</span>
                      </button>
                      <a
                        href={api.getDocumentViewUrl(doc.id)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 px-2.5 py-1 text-blue-700 bg-blue-50 hover:bg-blue-100 rounded font-medium transition-colors"
                      >
                        <ExternalLink className="w-3 h-3" />
                        <span>View</span>
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Evidence Viewer Modal */}
      <EvidenceViewerModal
        isOpen={!!selectedDoc}
        onClose={() => setSelectedDoc(null)}
        document={selectedDoc}
      />
    </div>
  );
}
