"use client";

import React from "react";
import Link from "next/link";
import { Shield, User as UserIcon, LogOut } from "lucide-react";
import { useAuth } from "@/lib/authContext";
 
export function Navbar() {
  const { user, role, logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 bg-[#0b192c] text-white border-b border-slate-800/80 shadow-xs">
      <div className="flex items-center justify-between px-6 py-2.5">
        {/* Brand / Logo */}
        <div className="flex items-center gap-4">
          <Link href="/" className="flex items-center gap-3 group focus:outline-hidden">
            <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-xs group-hover:bg-blue-500 transition-colors">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-base tracking-tight text-white">AICTE SmartVerify</span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-blue-900/90 text-blue-200 border border-blue-700/60">
                  SIH26261 MVP
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">Regulatory Scrutiny & Document Verification Platform</p>
            </div>
          </Link>
        </div>

        {/* Right Controls: Read-only Authenticated Role Badge & Profile */}
        <div className="flex items-center gap-3">
          {/* Read-only Authenticated Role Indicator */}
          <div className="flex items-center gap-2 px-3 py-1 bg-slate-800/90 border border-slate-700/80 rounded-lg">
            <span className="text-[11px] text-slate-400 font-medium">Role:</span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded text-white bg-blue-600/90 border border-blue-500/50 shadow-2xs">
              {role === "INSTITUTION" ? "Institution" : role === "REVIEWER" ? "Reviewer" : "Admin"}
            </span>
          </div>

          {/* User profile info */}
          <div className="flex items-center gap-2.5 pl-3 border-l border-slate-800">
            <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
              <UserIcon className="w-4 h-4 text-blue-400" />
            </div>
            <div className="hidden md:block text-left">
              <div className="text-xs font-semibold text-slate-100">{user?.full_name || "Demonstration User"}</div>
              <div className="text-[11px] text-slate-400 flex items-center gap-1.5">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                <span>{role}</span>
                {user?.institution_id && <span className="text-slate-500">({user.institution_id})</span>}
              </div>
            </div>

            {/* Sign Out Button */}
            <button
              onClick={logout}
              title="Sign Out"
              className="ml-2 p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800/80 rounded-md transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
