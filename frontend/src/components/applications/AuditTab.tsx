"use client";

import React, { useEffect, useState } from "react";
import { AuditEvent } from "@/lib/types";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { History, User, Activity, Clock, Shield } from "lucide-react";

interface AuditTabProps {
  applicationId: string;
}

export function AuditTab({ applicationId }: AuditTabProps) {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchAudit() {
      try {
        const data = await api.searchAuditTrail({ application_id: applicationId });
        setEvents(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchAudit();
  }, [applicationId]);

  return (
    <div className="space-y-6">
      <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-xs flex justify-between items-center">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <History className="w-4 h-4 text-blue-600" />
            <span>Traceable Audit History ({events.length} Events)</span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Cryptographically sealed, append-only regulatory event log for this application.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-400 text-xs">Loading audit events...</div>
      ) : events.length === 0 ? (
        <div className="bg-white p-8 text-center text-slate-400 text-sm border border-slate-200 rounded-lg">
          No audit entries recorded for this application yet.
        </div>
      ) : (
        <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
          {events.map((ev) => (
            <div key={ev.id} className="relative group">
              {/* Dot */}
              <div className="absolute -left-6 top-1.5 w-3.5 h-3.5 rounded-full border-2 border-white bg-blue-600 shadow-xs" />

              <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs space-y-1.5">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-slate-800 uppercase px-2 py-0.5 rounded bg-slate-100">
                      {ev.action.replace(/_/g, " ")}
                    </span>
                    <span className="text-xs text-slate-500">
                      by <strong className="text-slate-800">{ev.actor_id}</strong> ({ev.actor_role})
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono">
                    {formatDate(ev.timestamp)}
                  </span>
                </div>

                {ev.details && (
                  <p className="text-xs text-slate-700 leading-relaxed font-sans">{ev.details}</p>
                )}

                {(ev.before_state || ev.after_state) && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] font-mono mt-2 pt-2 border-t border-slate-100">
                    {ev.before_state && (
                      <div className="bg-slate-50 p-2 rounded text-slate-600">
                        <span className="font-semibold block text-slate-400 mb-0.5">Prior State:</span>
                        <span>{ev.before_state}</span>
                      </div>
                    )}
                    {ev.after_state && (
                      <div className="bg-blue-50/50 p-2 rounded text-blue-900">
                        <span className="font-semibold block text-blue-700 mb-0.5">Updated State:</span>
                        <span>{ev.after_state}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
