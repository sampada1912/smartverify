import React from "react";
import { FindingSeverity } from "@/lib/types";
import { cn } from "@/lib/utils";

interface SeverityBadgeProps {
  severity: FindingSeverity | string;
  className?: string;
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  let styles = "bg-slate-100 text-slate-700 border-slate-300";

  switch (severity) {
    case "CRITICAL":
    case "HIGH":
      styles = "bg-red-50 text-red-700 border-red-300 font-bold";
      break;
    case "MEDIUM":
      styles = "bg-amber-50 text-amber-800 border-amber-300 font-semibold";
      break;
    case "LOW":
      styles = "bg-blue-50 text-blue-700 border-blue-200 font-medium";
      break;
    case "INFO":
    default:
      styles = "bg-slate-50 text-slate-600 border-slate-200";
      break;
  }

  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-0.5 rounded text-[11px] uppercase tracking-wider border",
        styles,
        className
      )}
    >
      {severity}
    </span>
  );
}
