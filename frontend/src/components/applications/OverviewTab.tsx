"use client";

import React, { useState } from "react";
import { Application } from "@/lib/types";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatDate } from "@/lib/utils";
import { api } from "@/lib/api";
import {
  Building2,
  Calendar,
  GraduationCap,
  Users,
  Mail,
  Phone,
  CheckCircle2,
  AlertTriangle,
  PlayCircle,
  FileCheck,
} from "lucide-react";

interface OverviewTabProps {
  application: Application;
  onRefresh: () => void;
}

export function OverviewTab({ application: app, onRefresh }: OverviewTabProps) {
  const [submitting, setSubmitting] = useState(false);
  const [validating, setValidating] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const handleSubmit = async () => {
    setSubmitting(true);
    setMsg(null);
    try {
      await api.submitApplication(app.id);
      setMsg("Application formally submitted for regulatory scrutiny.");
      onRefresh();
    } catch (err: any) {
      setMsg(err.message || "Submission failed");
    } finally {
      setSubmitting(false);
    }
  };

  const handleValidate = async () => {
    setValidating(true);
    setMsg(null);
    try {
      await api.triggerValidation(app.id);
      await api.evaluateCompliance(app.id);
      setMsg("Scrutiny validation and compliance checks completed.");
      onRefresh();
    } catch (err: any) {
      setMsg(err.message || "Validation failed");
    } finally {
      setValidating(false);
    }
  };

  return (
    <div className="space-y-6">
      {msg && (
        <div className="p-3 bg-blue-50 text-blue-800 border border-blue-200 rounded-lg text-xs font-medium">
          {msg}
        </div>
      )}

      {/* Primary Status Card */}
      <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              Application ID: {app.id}
            </span>
            <span className="text-slate-300">•</span>
            <span className="text-xs text-slate-500">{app.category.replace(/_/g, " ")}</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900">{app.institution_name}</h2>
          <div className="flex items-center gap-3 mt-3">
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-slate-500">Processing Status:</span>
              <StatusBadge status={app.status} type="application" />
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-slate-500">Scrutiny State:</span>
              <StatusBadge status={app.validation_status} type="validation" />
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={handleValidate}
            disabled={validating}
            className="inline-flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold rounded-md shadow-xs transition-colors"
          >
            <PlayCircle className="w-4 h-4 text-blue-400" />
            <span>{validating ? "Running..." : "Run AI Scrutiny"}</span>
          </button>

          {app.status === "DRAFT" && (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={submitting}
              className="inline-flex items-center gap-1.5 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-md shadow-xs transition-colors"
            >
              <FileCheck className="w-4 h-4" />
              <span>{submitting ? "Submitting..." : "Submit Application"}</span>
            </button>
          )}
        </div>
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Institutional & Programme Details */}
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-xs space-y-4">
          <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2 flex items-center gap-2">
            <Building2 className="w-4 h-4 text-blue-600" />
            <span>Institutional Profile</span>
          </h3>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <span className="text-slate-500 block mb-0.5">Permanent Institute ID</span>
              <span className="font-mono font-semibold text-slate-800">{app.institution_id}</span>
            </div>
            <div>
              <span className="text-slate-500 block mb-0.5">Academic Session</span>
              <span className="font-semibold text-slate-800">{app.academic_year}</span>
            </div>
            <div>
              <span className="text-slate-500 block mb-0.5">Programme</span>
              <span className="font-semibold text-slate-800">{app.programme.replace(/_/g, " ")}</span>
            </div>
            <div>
              <span className="text-slate-500 block mb-0.5">Sanctioned Course</span>
              <span className="font-semibold text-slate-800">{app.course_name}</span>
            </div>
            <div>
              <span className="text-slate-500 block mb-0.5">Existing Approved Intake</span>
              <span className="font-semibold text-slate-800">{app.existing_intake} Seats</span>
            </div>
            <div>
              <span className="text-slate-500 block mb-0.5">Requested Intake</span>
              <span className="font-semibold text-blue-700">{app.requested_intake} Seats</span>
            </div>
          </div>
        </div>

        {/* Contact & Submission Metadata */}
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-xs space-y-4">
          <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2 flex items-center gap-2">
            <Users className="w-4 h-4 text-blue-600" />
            <span>Authorized Contact Details</span>
          </h3>

          <div className="grid grid-cols-1 gap-2.5 text-xs">
            <div>
              <span className="text-slate-500 block mb-0.5">Authorized Representative</span>
              <span className="font-semibold text-slate-800">{app.contact_person}</span>
            </div>
            <div className="flex items-center gap-2 text-slate-700">
              <Mail className="w-3.5 h-3.5 text-slate-400" />
              <span>{app.contact_email}</span>
            </div>
            <div className="flex items-center gap-2 text-slate-700">
              <Phone className="w-3.5 h-3.5 text-slate-400" />
              <span>{app.contact_phone}</span>
            </div>
            <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-slate-500">
              <span>Submitted Date:</span>
              <span className="font-medium text-slate-800">{formatDate(app.submission_date)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
