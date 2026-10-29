"use client";

import React, { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/authContext";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  const isLoginPage = pathname === "/login";

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated && !isLoginPage) {
        router.replace("/login");
      } else if (isAuthenticated && isLoginPage) {
        router.replace("/");
      }
    }
  }, [isAuthenticated, isLoading, isLoginPage, router]);

  // If on login page, render full viewport without app shell
  if (isLoginPage) {
    return <>{children}</>;
  }

  // Authenticated app layout: always render {children} so Next.js instant navigation can validate the route segment tree
  return (
    <div className="min-h-screen flex flex-col bg-[#f8fafc] text-slate-900 font-sans">
      <Navbar />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-[#f8fafc]">
          <div className="max-w-7xl mx-auto space-y-6">{children}</div>
        </main>
      </div>
    </div>
  );
}
