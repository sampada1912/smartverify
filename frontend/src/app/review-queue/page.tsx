"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Application } from "@/lib/types";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/authContext";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatDate } from "@/lib/utils";
import {
  Inbox,
  AlertTriangle,
  Clock,
  CheckCircle2,
  Filter,
  Search,
  ExternalLink,
  ShieldAlert,
  ArrowRight,
  Building2,
  RefreshCw,
  FileCheck,
} from "lucide-react";

export default function ReviewQueuePage() {
  const { user } = useAuth();
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterPriority, setFilterPriority] = useState<"ALL" | "HIGH" | "DEFICIENCY" | "MY_QUEUE">("ALL");
  const [search, setSearch] = useState("");

  const fetchData = async () => {
    setLoading(true);
    try {
      const data = await api.getApplications();
      setApplications(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Filter applications that are relevant to review queue
  const queueApps = applications.filter((app) => {
    // Basic search match
    if (search.trim()) {
      const q = search.toLowerCase();
      const match =
        app.id.toLowerCase().includes(q) ||
        app.institution_name.toLowerCase().includes(q) ||
        app.institution_id.toLowerCase().includes(q) ||
        app.programme.toLowerCase().includes(q);
      if (!match) return false;
    }

    const hasHighFindings = (app.high_findings_count || 0) > 0;
    const hasOpenFindings = (app.open_findings_count || 0) > 0;

    if (filterPriority === "HIGH") {
      return hasHighFindings;
    }
    if (filterPriority === "DEFICIENCY") {
      return (
        app.status === "DEFICIENCIES_COMMUNICATED" ||
        hasOpenFindings
      );
    }
    if (filterPriority === "MY_QUEUE") {
      return user?.role === "REVIEWER" && app.status !== "DRAFT";
    }

    // Default "ALL" in review queue: everything submitted or with open findings
    return app.status !== "DRAFT" || hasOpenFindings;
  });

  const totalInQueue = applications.filter((a) => a.status !== "DRAFT").length;
  const highSeverityCount = applications.filter((a) => (a.high_findings_count || 0) > 0).length;
  const awaitingEvidenceCount = applications.filter(
    (a) => a.status === "DEFICIENCIES_COMMUNICATED"
  ).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Scrutiny Review Queue</h1>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-100 text-blue-800">
              Regulatory Triage
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Prioritized worklist of technical institution applications requiring scrutiny committee examination.
          </p>
        </div>

        <button
          onClick={fetchData}
          className="inline-flex items-center gap-2 px-3 py-2 border border-slate-200 bg-white rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-xs"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Queue</span>
        </button>
      </div>

      {/* Metrics Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex items-center gap-4">
          <div className="p-3 bg-blue-50 text-blue-700 rounded-lg shrink-0">
            <Inbox className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{totalInQueue}</div>
            <div className="text-xs font-medium text-slate-500">Applications in Active Queue</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex items-center gap-4">
          <div className="p-3 bg-red-50 text-red-700 rounded-lg shrink-0">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-red-600">{highSeverityCount}</div>
            <div className="text-xs font-medium text-slate-500">Critical / High Deficiencies</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex items-center gap-4">
          <div className="p-3 bg-amber-50 text-amber-700 rounded-lg shrink-0">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-amber-600">{awaitingEvidenceCount}</div>
            <div className="text-xs font-medium text-slate-500">Awaiting Evidence Clarification</div>
          </div>
        </div>
      </div>

      {/* Search & Tabs */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Priority filter pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
            <button
              onClick={() => setFilterPriority("ALL")}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors whitespace-nowrap ${
                filterPriority === "ALL"
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              All Queue Items ({applications.filter((a) => a.status !== "DRAFT").length})
            </button>
            <button
              onClick={() => setFilterPriority("HIGH")}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors whitespace-nowrap flex items-center gap-1.5 ${
                filterPriority === "HIGH"
                  ? "bg-red-700 text-white"
                  : "bg-red-50 text-red-700 hover:bg-red-100"
              }`}
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>High Priority Mismatches ({highSeverityCount})</span>
            </button>
            <button
              onClick={() => setFilterPriority("DEFICIENCY")}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors whitespace-nowrap flex items-center gap-1.5 ${
                filterPriority === "DEFICIENCY"
                  ? "bg-amber-600 text-white"
                  : "bg-amber-50 text-amber-700 hover:bg-amber-100"
              }`}
            >
              <Clock className="w-3.5 h-3.5" />
              <span>Deficiency / Evidence Pending ({awaitingEvidenceCount})</span>
            </button>
            <button
              onClick={() => setFilterPriority("MY_QUEUE")}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors whitespace-nowrap ${
                filterPriority === "MY_QUEUE"
                  ? "bg-blue-700 text-white"
                  : "bg-blue-50 text-blue-700 hover:bg-blue-100"
              }`}
            >
              Assigned to Reviewer
            </button>
          </div>

          {/* Search bar */}
          <div className="relative w-full md:w-72">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search by ID, institution, PID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Queue Table */}
        {loading ? (
          <div className="py-12 text-center">
            <div className="w-7 h-7 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            <p className="text-xs text-slate-500 font-medium">Loading triage queue...</p>
          </div>
        ) : queueApps.length === 0 ? (
          <div className="py-12 text-center text-slate-500 bg-slate-50 rounded-lg border border-dashed border-slate-200">
            <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
            <p className="text-sm font-semibold text-slate-700">No applications pending scrutiny in this category</p>
            <p className="text-xs text-slate-400 mt-1">All applications under this filter have been addressed.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-2.5 px-3">Application ID</th>
                  <th className="py-2.5 px-3">Institution & PID</th>
                  <th className="py-2.5 px-3">Category & AY</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Open Deficiencies</th>
                  <th className="py-2.5 px-3">Submission Date</th>
                  <th className="py-2.5 px-3 text-right">Scrutiny Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {queueApps.map((app) => {
                  const openCount = app.open_findings_count || 0;
                  const highCount = app.high_findings_count || 0;

                  return (
                    <tr key={app.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 px-3">
                        <Link
                          href={`/applications/${app.id}`}
                          className="font-mono font-bold text-blue-700 hover:text-blue-900 hover:underline flex items-center gap-1.5"
                        >
                          <span>{app.id}</span>
                        </Link>
                      </td>

                      <td className="py-3 px-3">
                        <div className="font-semibold text-slate-900">{app.institution_name}</div>
                        <div className="text-[11px] text-slate-500 font-mono">PID: {app.institution_id}</div>
                      </td>

                      <td className="py-3 px-3">
                        <span className="font-medium text-slate-800">{app.category}</span>
                        <div className="text-[11px] text-slate-400">AY {app.academic_year}</div>
                      </td>

                      <td className="py-3 px-3">
                        <StatusBadge status={app.status} />
                      </td>

                      <td className="py-3 px-3">
                        {openCount === 0 ? (
                          <span className="inline-flex items-center gap-1 text-[11px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-medium border border-emerald-200">
                            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                            <span>No Open Deficiencies</span>
                          </span>
                        ) : (
                          <div className="flex items-center gap-1.5">
                            <span
                              className={`text-[11px] font-bold px-2 py-0.5 rounded border ${
                                highCount > 0
                                  ? "bg-red-50 text-red-700 border-red-200"
                                  : "bg-amber-50 text-amber-800 border-amber-200"
                              }`}
                            >
                              {openCount} Deficienc{openCount > 1 ? "ies" : "y"}
                            </span>
                            {highCount > 0 && (
                              <span className="text-[10px] uppercase font-bold text-red-600 bg-red-100 px-1 rounded">
                                High
                              </span>
                            )}
                          </div>
                        )}
                      </td>

                      <td className="py-3 px-3 text-slate-500">
                        {formatDate(app.submission_date)}
                      </td>

                      <td className="py-3 px-3 text-right">
                        <Link
                          href={`/applications/${app.id}`}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded text-xs font-medium transition-colors"
                        >
                          <span>Review Dossier</span>
                          <ArrowRight className="w-3 h-3" />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
