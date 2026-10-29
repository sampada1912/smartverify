"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { DashboardStats } from "@/lib/types";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatDate } from "@/lib/utils";
import {
  Files,
  FileCheck2,
  AlertTriangle,
  Clock,
  ShieldCheck,
  FileX,
  History,
  ArrowRight,
  TrendingUp,
  Building,
  CheckCircle2,
} from "lucide-react";

export default function DashboardOverviewPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  const loadStats = async () => {
    try {
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-16 text-slate-400 text-sm">
        Loading regulatory overview metrics...
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="p-8 text-center text-slate-500 bg-white rounded-lg border border-slate-200">
        Unable to load dashboard metrics. Verify that the backend service is running and accessible.
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Title & Context */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Regulatory Scrutiny Overview
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Real-time compliance validation, OCR extraction metrics, and document authentication status.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/applications/new"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-semibold shadow-xs transition-colors"
          >
            <span>Create Application</span>
          </Link>
        </div>
      </div>

      {/* 6 Key Enterprise Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {/* Total Apps */}
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Applications</span>
            <Files className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{stats.total_applications}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">Active across all categories</span>
        </div>

        {/* Submitted Apps */}
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Submitted</span>
            <FileCheck2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-emerald-700">{stats.submitted_applications}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">Under review or scrutiny</span>
        </div>

        {/* Apps Needing Review */}
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Requires Review</span>
            <AlertTriangle className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-bold text-amber-700">{stats.applications_needing_review}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">Deficiencies surfaced</span>
        </div>

        {/* Open Findings */}
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Open Findings</span>
            <AlertTriangle className="w-4 h-4 text-rose-600" />
          </div>
          <div className="text-2xl font-bold text-rose-700">{stats.open_findings_count}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">Scrutiny issues flagged</span>
        </div>

        {/* Missing Docs */}
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Missing Docs</span>
            <FileX className="w-4 h-4 text-rose-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{stats.missing_documents_count}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">Mandatory checklist gaps</span>
        </div>

        {/* Expired Docs */}
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Expired Docs</span>
            <Clock className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{stats.expired_documents_count}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">Validity lapse detected</span>
        </div>
      </div>

      {/* Distributions Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Verification Status Breakdown */}
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-blue-600" />
              <span>Simulated Authority Verification Distribution</span>
            </h3>
            <span className="text-[10px] uppercase font-bold text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200">
              SIMULATED ADAPTER
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {Object.entries(stats.verification_status_distribution).map(([statusKey, count]) => (
              <div key={statusKey} className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs">
                <span className="text-slate-500 block truncate">{statusKey.replace(/_/g, " ")}</span>
                <span className="text-lg font-bold text-slate-900 mt-1 block">{count}</span>
              </div>
            ))}
            {Object.keys(stats.verification_status_distribution).length === 0 && (
              <div className="col-span-3 text-center text-slate-400 text-xs py-4">
                No authority checks triggered yet.
              </div>
            )}
          </div>
        </div>

        {/* Application Category Distribution */}
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Building className="w-4 h-4 text-blue-600" />
              <span>Application Category Distribution</span>
            </h3>
            <Link href="/applications" className="text-xs text-blue-600 hover:underline font-medium">
              View all &rarr;
            </Link>
          </div>

          <div className="space-y-2.5">
            {Object.entries(stats.category_distribution).map(([catKey, count]) => (
              <div key={catKey} className="flex items-center justify-between text-xs">
                <span className="text-slate-700 font-medium">{catKey.replace(/_/g, " ")}</span>
                <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-800 font-bold">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Applications & Activity Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Applications Table (2 Cols) */}
        <div className="lg:col-span-2 bg-white rounded-lg border border-slate-200 shadow-xs overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/50 flex justify-between items-center">
            <h3 className="text-sm font-bold text-slate-900">Recent Applications</h3>
            <Link href="/applications" className="text-xs text-blue-600 hover:underline font-medium">
              Browse all applications
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="px-5 py-3">App ID</th>
                  <th className="px-4 py-3">Institution Name</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Scrutiny State</th>
                  <th className="px-5 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-800">
                {stats.recent_applications.map((app) => (
                  <tr key={app.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-5 py-3 font-mono font-bold text-slate-700">
                      {app.id}
                    </td>
                    <td className="px-4 py-3 font-semibold text-slate-900 max-w-[200px] truncate" title={app.institution_name}>
                      {app.institution_name}
                    </td>
                    <td className="px-4 py-3 text-slate-600 text-[11px]">
                      {app.category.replace(/_/g, " ")}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={app.status} type="application" />
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={app.validation_status} type="validation" />
                    </td>
                    <td className="px-5 py-3 text-right">
                      <Link
                        href={`/applications/${app.id}`}
                        className="text-blue-600 hover:text-blue-800 font-semibold"
                      >
                        Details &rarr;
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Activity Audit Feed (1 Col) */}
        <div className="bg-white rounded-lg border border-slate-200 shadow-xs overflow-hidden flex flex-col">
          <div className="px-5 py-4 border-b border-slate-200 bg-slate-50/50 flex justify-between items-center">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
              <History className="w-4 h-4 text-blue-600" />
              <span>Recent Activity Feed</span>
            </h3>
            <Link href="/audit" className="text-xs text-blue-600 hover:underline font-medium">
              Audit log
            </Link>
          </div>

          <div className="p-4 space-y-3.5 overflow-y-auto max-h-[380px]">
            {stats.recent_activity.map((event) => (
              <div key={event.id} className="text-xs border-b border-slate-100 pb-3 last:border-0 last:pb-0">
                <div className="flex items-center justify-between text-[11px] text-slate-400 mb-0.5 font-mono">
                  <span className="font-semibold text-slate-700">{event.action.replace(/_/g, " ")}</span>
                  <span>{formatDate(event.timestamp)}</span>
                </div>
                <p className="text-slate-800 leading-snug">{event.details || event.after_state || "Action recorded"}</p>
                <div className="text-[10px] text-slate-400 mt-1">
                  Actor: <span className="font-semibold text-slate-600">{event.actor_id}</span> ({event.actor_role})
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
