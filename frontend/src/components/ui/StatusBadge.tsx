import React from "react";
import { CheckCircle2, AlertTriangle, AlertCircle, Clock, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: string;
  type?: "application" | "validation" | "compliance" | "verification";
  className?: string;
}

export function StatusBadge({ status, type = "validation", className }: StatusBadgeProps) {
  let colorStyles = "bg-slate-100 text-slate-700 border-slate-300";
  let Icon = FileText;

  switch (status) {
    case "CLEAN":
    case "PASS":
    case "VERIFIED":
    case "RESOLVED":
    case "SCRUTINY_COMPLETED":
    case "SATISFIED":
      colorStyles = "bg-emerald-50 text-emerald-800 border-emerald-300";
      Icon = CheckCircle2;
      break;

    case "DEFICIENCIES_DETECTED":
    case "FAIL":
    case "HIGH_RISK":
    case "MISMATCH_DETECTED":
    case "EXPIRED":
    case "ESCALATED":
      colorStyles = "bg-rose-50 text-rose-800 border-rose-300";
      Icon = AlertCircle;
      break;

    case "UNDER_REVIEW":
    case "UNDER_SCRUTINY":
    case "WARNING":
    case "DEFICIENCIES_COMMUNICATED":
    case "PENDING_REVIEW":
    case "MANUAL_REVIEW_REQUIRED":
    case "REQUESTED_INFORMATION":
    case "NEEDS_REVIEW":
      colorStyles = "bg-amber-50 text-amber-800 border-amber-300";
      Icon = AlertTriangle;
      break;

    case "DRAFT":
    case "NOT_EVALUATED":
    case "NOT_APPLICABLE":
    case "VERIFICATION_PENDING":
    default:
      colorStyles = "bg-slate-100 text-slate-700 border-slate-200";
      Icon = Clock;
      break;
  }

  const label = status.replace(/_/g, " ");

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border shadow-2xs tracking-wide uppercase",
        colorStyles,
        className
      )}
    >
      <Icon className="w-3.5 h-3.5" />
      <span>{label}</span>
    </span>
  );
}
