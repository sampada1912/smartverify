"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Application } from "@/lib/types";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatDate } from "@/lib/utils";
import {
  Search,
  Filter,
  Plus,
  Files,
  Building,
  AlertTriangle,
  ChevronRight,
  ShieldCheck,
} from "lucide-react";

export default function ApplicationsListPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("");
  const [validationStatus, setValidationStatus] = useState("");

  const loadApps = async () => {
    setLoading(true);
    try {
      const data = await api.listApplications({
        search: search || undefined,
        category: category || undefined,
        status: status || undefined,
        validation_status: validationStatus || undefined,
      });
      setApplications(data.items);
      setTotal(data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApps();
  }, [category, status, validationStatus]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadApps();
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Institutional Applications Directory
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Browse and filter regulatory applications under scrutiny, with automated discrepancy indicators.
          </p>
        </div>
        <Link
          href="/applications/new"
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-semibold shadow-xs transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>New Application</span>
        </Link>
      </div>

      {/* Search & Filters */}
      <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by Institution Name, Permanent Institute ID, Application ID, or Course..."
              className="w-full pl-9 pr-4 py-2 text-xs border border-slate-300 rounded-md bg-slate-50/50 focus:outline-blue-600 font-medium"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-md text-xs font-semibold transition-colors"
          >
            Search
          </button>
        </form>

        <div className="flex flex-wrap items-center gap-3 text-xs pt-2 border-t border-slate-100">
          <div className="flex items-center gap-1.5">
            <span className="text-slate-500 font-medium">Category:</span>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="p-1.5 border border-slate-300 rounded-md bg-white font-medium text-slate-800 focus:outline-blue-600"
            >
              <option value="">All Categories</option>
              <option value="EXTENSION_OF_APPROVAL">Extension of Approval (EoA)</option>
              <option value="INCREASE_IN_INTAKE">Increase in Intake</option>
              <option value="NEW_INSTITUTION">New Institution</option>
              <option value="NEW_PROGRAMME">New Programme</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-slate-500 font-medium">Processing Status:</span>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="p-1.5 border border-slate-300 rounded-md bg-white font-medium text-slate-800 focus:outline-blue-600"
            >
              <option value="">All Statuses</option>
              <option value="DRAFT">Draft</option>
              <option value="SUBMITTED">Submitted</option>
              <option value="UNDER_SCRUTINY">Under Scrutiny</option>
              <option value="DEFICIENCIES_COMMUNICATED">Deficiencies Communicated</option>
              <option value="SCRUTINY_COMPLETED">Scrutiny Completed</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-slate-500 font-medium">Scrutiny State:</span>
            <select
              value={validationStatus}
              onChange={(e) => setValidationStatus(e.target.value)}
              className="p-1.5 border border-slate-300 rounded-md bg-white font-medium text-slate-800 focus:outline-blue-600"
            >
              <option value="">All Validation States</option>
              <option value="CLEAN">Clean (No Findings)</option>
              <option value="DEFICIENCIES_DETECTED">Deficiencies Detected</option>
              <option value="HIGH_RISK">High Risk</option>
              <option value="NOT_EVALUATED">Not Evaluated</option>
            </select>
          </div>

          {(category || status || validationStatus || search) && (
            <button
              type="button"
              onClick={() => {
                setCategory("");
                setStatus("");
                setValidationStatus("");
                setSearch("");
              }}
              className="ml-auto text-blue-600 hover:text-blue-800 text-xs font-semibold"
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* Applications Table */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/50 flex justify-between items-center text-xs text-slate-500">
          <span>Showing <strong>{applications.length}</strong> of <strong>{total}</strong> applications</span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-400 text-xs">Loading application records...</div>
        ) : applications.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-xs">
            No institutional applications found matching criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="px-5 py-3">App ID</th>
                  <th className="px-5 py-3">Institution Name & ID</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Intake (Base &rarr; Req)</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Scrutiny State</th>
                  <th className="px-4 py-3">Open Findings</th>
                  <th className="px-5 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-800">
                {applications.map((app) => (
                  <tr key={app.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-5 py-3 font-mono font-bold text-slate-700">
                      {app.id}
                    </td>
                    <td className="px-5 py-3 font-medium text-slate-900">
                      <div className="font-semibold text-slate-900">{app.institution_name}</div>
                      <span className="text-[11px] font-mono text-slate-500">
                        PID: {app.institution_id} &bull; {app.course_name}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-600 font-medium">
                      {app.category.replace(/_/g, " ")}
                    </td>
                    <td className="px-4 py-3 font-mono">
                      <span>{app.existing_intake}</span> &rarr;{" "}
                      <span className={app.requested_intake > app.existing_intake ? "font-bold text-blue-700" : ""}>
                        {app.requested_intake}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={app.status} type="application" />
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={app.validation_status} type="validation" />
                    </td>
                    <td className="px-4 py-3">
                      {app.open_findings_count && app.open_findings_count > 0 ? (
                        <span className="inline-flex items-center gap-1 font-bold text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
                          <AlertTriangle className="w-3 h-3 text-rose-600" />
                          <span>{app.open_findings_count} Issue(s)</span>
                        </span>
                      ) : (
                        <span className="text-slate-400">None</span>
                      )}
                    </td>
                    <td className="px-5 py-3 text-right">
                      <Link
                        href={`/applications/${app.id}`}
                        className="inline-flex items-center gap-1 px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded text-xs font-semibold transition-colors"
                      >
                        <span>Inspect</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </Link>
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
