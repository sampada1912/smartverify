"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { AuditEvent } from "@/lib/types";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import {
  History,
  Search,
  Filter,
  User,
  Activity,
  Shield,
  Layers,
  ArrowRight,
  RefreshCw,
  ExternalLink,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Info,
} from "lucide-react";

export default function AuditTrailPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState("");
  const [actionFilter, setActionFilter] = useState("ALL");
  const [entityFilter, setEntityFilter] = useState("ALL");

  const [selectedEvent, setSelectedEvent] = useState<AuditEvent | null>(null);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const data = await api.searchAuditTrail({
        action: actionFilter !== "ALL" ? actionFilter : undefined,
        entity_type: entityFilter !== "ALL" ? entityFilter : undefined,
        search: search.trim() ? search.trim() : undefined,
      });
      setEvents(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [actionFilter, entityFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchEvents();
  };

  const getActionColor = (action: string) => {
    if (action.includes("OVERRIDE") || action.includes("ESCALATE")) {
      return "bg-red-50 text-red-700 border-red-200";
    }
    if (action.includes("VERIFICATION")) {
      return "bg-purple-50 text-purple-700 border-purple-200";
    }
    if (action.includes("VALIDATION") || action.includes("COMPLIANCE")) {
      return "bg-blue-50 text-blue-700 border-blue-200";
    }
    if (action.includes("EVIDENCE")) {
      return "bg-amber-50 text-amber-800 border-amber-200";
    }
    if (action.includes("CORRECTION")) {
      return "bg-indigo-50 text-indigo-700 border-indigo-200";
    }
    return "bg-slate-100 text-slate-800 border-slate-200";
  };

  const totalEvents = events.length;
  const humanEvents = events.filter((e) => e.actor_id !== "system").length;
  const systemEvents = events.filter((e) => e.actor_id === "system").length;
  const overrideEvents = events.filter((e) => e.action.includes("OVERRIDE")).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Regulatory Scrutiny Audit Trail
            </h1>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-slate-900 text-white">
              IMMUTABLE LOG
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Complete, tamper-evident chronological record of all application submissions, OCR extractions, scrutiny findings, and committee decisions.
          </p>
        </div>

        <button
          onClick={fetchEvents}
          className="inline-flex items-center gap-2 px-3 py-2 border border-slate-200 bg-white rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-xs"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Trail</span>
        </button>
      </div>

      {/* Metrics Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="text-slate-400 text-xs font-medium">Total Events Recorded</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">{totalEvents}</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="text-slate-400 text-xs font-medium">Automated Scrutiny Events</div>
          <div className="text-2xl font-bold text-blue-700 mt-1">{systemEvents}</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="text-slate-400 text-xs font-medium">Human Committee Decisions</div>
          <div className="text-2xl font-bold text-slate-800 mt-1">{humanEvents}</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="text-slate-400 text-xs font-medium">Reviewer Status Overrides</div>
          <div className="text-2xl font-bold text-amber-600 mt-1">{overrideEvents}</div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2 relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search details, actor, application ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="w-full text-xs border border-slate-300 rounded-lg p-2 bg-white text-slate-700 focus:outline-hidden focus:ring-1 focus:ring-blue-500"
            >
              <option value="ALL">All Regulatory Actions</option>
              <option value="APPLICATION_CREATED">Application Created</option>
              <option value="APPLICATION_SUBMITTED">Application Submitted</option>
              <option value="DOCUMENT_UPLOADED">Document Uploaded</option>
              <option value="DOCUMENT_OCR_PROCESSED">OCR Processed</option>
              <option value="OCR_FIELD_CORRECTION">OCR Field Correction</option>
              <option value="SCRUTINY_VALIDATION_RUN">Validation Checks Run</option>
              <option value="COMPLIANCE_EVALUATION_RUN">Compliance Evaluated</option>
              <option value="FINDING_STATUS_UPDATE">Finding Status Updated</option>
              <option value="FINDING_MANUAL_OVERRIDE">Finding Overridden</option>
              <option value="EVIDENCE_REQUESTED">Evidence Requested</option>
              <option value="EVIDENCE_RESPONSE_SUBMITTED">Evidence Response</option>
              <option value="AUTHORITY_VERIFICATION_CHECK">Authority Verification</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={entityFilter}
              onChange={(e) => setEntityFilter(e.target.value)}
              className="w-full text-xs border border-slate-300 rounded-lg p-2 bg-white text-slate-700 focus:outline-hidden focus:ring-1 focus:ring-blue-500"
            >
              <option value="ALL">All Entity Types</option>
              <option value="APPLICATION">Application</option>
              <option value="DOCUMENT">Document</option>
              <option value="FIELD">Extracted Field</option>
              <option value="FINDING">Validation Finding</option>
              <option value="COMPLIANCE">Compliance Rule</option>
              <option value="VERIFICATION_RESULT">Verification Result</option>
              <option value="EVIDENCE_REQUEST">Evidence Request</option>
            </select>

            <button
              type="submit"
              className="px-3.5 py-2 bg-slate-900 text-white rounded-lg text-xs font-semibold hover:bg-slate-800 transition-colors shrink-0"
            >
              Search
            </button>
          </div>
        </form>

        {/* Audit Log Table */}
        {loading ? (
          <div className="py-12 text-center">
            <div className="w-7 h-7 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            <p className="text-xs text-slate-500 font-medium">Querying immutable audit log entries...</p>
          </div>
        ) : events.length === 0 ? (
          <div className="py-12 text-center text-slate-500 bg-slate-50 rounded-lg border border-dashed border-slate-200 text-xs">
            No audit records found matching your filter criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Actor & Role</th>
                  <th className="py-2.5 px-3">Action</th>
                  <th className="py-2.5 px-3">Entity & Target</th>
                  <th className="py-2.5 px-3">Audit Details & Rationale</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {events.map((evt) => (
                  <tr key={evt.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-3 text-slate-500 whitespace-nowrap font-mono text-[11px]">
                      {formatDate(evt.timestamp)}
                    </td>

                    <td className="py-3 px-3">
                      <div className="flex items-center gap-1.5">
                        <User className="w-3.5 h-3.5 text-slate-400" />
                        <span className="font-semibold text-slate-900">{evt.actor_id}</span>
                      </div>
                      <div className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">
                        {evt.actor_role}
                      </div>
                    </td>

                    <td className="py-3 px-3">
                      <span
                        className={`text-[11px] font-mono font-bold px-2 py-0.5 rounded border ${getActionColor(
                          evt.action
                        )}`}
                      >
                        {evt.action}
                      </span>
                    </td>

                    <td className="py-3 px-3">
                      <div className="text-slate-900 font-medium">{evt.entity_type}</div>
                      {evt.application_id && (
                        <Link
                          href={`/applications/${evt.application_id}`}
                          className="text-[11px] font-mono text-blue-700 hover:underline flex items-center gap-1 mt-0.5"
                        >
                          <span>{evt.application_id}</span>
                          <ExternalLink className="w-3 h-3 text-blue-500" />
                        </Link>
                      )}
                    </td>

                    <td className="py-3 px-3 max-w-md">
                      <div className="text-slate-800 leading-relaxed text-xs">
                        {evt.details}
                      </div>
                      {(evt.before_state || evt.after_state) && (
                        <div className="mt-1 flex items-center gap-2 text-[11px] font-mono bg-slate-100 p-1 rounded">
                          {evt.before_state && (
                            <span className="text-slate-500 line-through">
                              {evt.before_state}
                            </span>
                          )}
                          {evt.before_state && evt.after_state && <span>→</span>}
                          {evt.after_state && (
                            <span className="text-emerald-700 font-bold">
                              {evt.after_state}
                            </span>
                          )}
                        </div>
                      )}
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
