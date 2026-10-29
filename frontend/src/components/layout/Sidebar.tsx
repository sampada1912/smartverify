"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Files,
  ShieldCheck,
  Scale,
  ListFilter,
  History,
  Settings,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
} from "lucide-react";
import { useAuth } from "@/lib/authContext";

export function Sidebar() {
  const pathname = usePathname();
  const { role } = useAuth();
  const [collapsed, setCollapsed] = useState(false);

  // Role-specific navigation items
  const allNavigation = [
    { name: "Overview", href: "/", icon: LayoutDashboard, roles: ["ADMIN", "REVIEWER", "INSTITUTION"] },
    { name: role === "INSTITUTION" ? "My Applications" : "Applications", href: "/applications", icon: Files, roles: ["ADMIN", "REVIEWER", "INSTITUTION"] },
    { name: "Review Queue", href: "/review-queue", icon: ListFilter, roles: ["ADMIN", "REVIEWER"] },
    { name: "Document Verification", href: "/verification", icon: ShieldCheck, roles: ["ADMIN", "REVIEWER"] },
    { name: "Compliance Rules", href: "/rules", icon: Scale, roles: ["ADMIN"] },
    { name: "Audit Trail", href: "/audit", icon: History, roles: ["ADMIN", "REVIEWER", "INSTITUTION"] },
    { name: "Settings", href: "/settings", icon: Settings, roles: ["ADMIN"] },
  ];

  const navigation = allNavigation.filter((item) => item.roles.includes(role));

  return (
    <aside
      className={`relative bg-white border-r border-slate-200 transition-all duration-300 flex flex-col shrink-0 ${
        collapsed ? "w-18" : "w-64"
      }`}
    >
      {/* Navigation Links */}
      <div className="flex-1 py-4 px-3 space-y-1">
        {navigation.map((item) => {
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? "bg-blue-50 text-blue-700 font-semibold border-l-4 border-blue-600 pl-2"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/80"
              }`}
              title={collapsed ? item.name : undefined}
            >
              <Icon className={`w-5 h-5 shrink-0 ${isActive ? "text-blue-600" : "text-slate-500"}`} />
              {!collapsed && <span>{item.name}</span>}
            </Link>
          );
        })}
      </div>

      {/* Regulatory Notice Footer */}
      {!collapsed && (
        <div className="p-4 mx-3 mb-4 rounded-lg bg-slate-50 border border-slate-200 text-slate-500 text-[11px] leading-relaxed">
          <div className="flex items-center gap-1.5 font-semibold text-slate-700 mb-1">
            <ShieldAlert className="w-3.5 h-3.5 text-blue-600" />
            <span>Human In The Loop</span>
          </div>
          The validation engine advises and surfaces evidence. All regulatory determinations remain with authorized officials.
        </div>
      )}

      {/* Collapse Toggle */}
      <div className="p-3 border-t border-slate-200 flex justify-end">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-md transition-colors"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>
    </aside>
  );
}
