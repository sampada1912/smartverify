"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Shield,
  Lock,
  Mail,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  FileSearch,
  Scale,
  History,
} from "lucide-react";
import { useAuth } from "@/lib/authContext";

interface DemoAccount {
  label: string;
  role: string;
  usernameOrEmail: string;
  password: string;
  badge: string;
  description: string;
}

const DEMO_ACCOUNTS: DemoAccount[] = [
  {
    label: "Scrutiny Officer",
    role: "REVIEWER",
    usernameOrEmail: "scrutiny.officer@aicte.gov.in",
    password: "password123",
    badge: "Official Scrutiny",
    description: "Evaluates institutional applications, audits findings, and communicates deficiencies.",
  },
  {
    label: "Institution Principal",
    role: "INSTITUTION",
    usernameOrEmail: "principal@ditm.edu.in",
    password: "password123",
    badge: "Delhi Inst. Tech.",
    description: "Submits approval requests, uploads statutory evidence, and responds to inquiries.",
  },
  {
    label: "System Administrator",
    role: "ADMIN",
    usernameOrEmail: "admin@aicte.gov.in",
    password: "password123",
    badge: "System Governance",
    description: "Configures regulatory compliance rules, inspects audit trails, and manages tenants.",
  },
];

export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated, isLoading, role } = useAuth();

  const [usernameOrEmail, setUsernameOrEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Redirect users away from login if they already have an active verified session
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      if (role === "REVIEWER") {
        router.replace("/review-queue");
      } else if (role === "INSTITUTION") {
        router.replace("/applications");
      } else {
        router.replace("/");
      }
    }
  }, [isAuthenticated, isLoading, role, router]);

  const redirectRoleUser = (userRole: string) => {
    if (userRole === "REVIEWER") {
      router.push("/review-queue");
    } else if (userRole === "INSTITUTION") {
      router.push("/applications");
    } else {
      router.push("/");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!usernameOrEmail.trim()) {
      setError("Please enter your email or username.");
      return;
    }
    if (!password) {
      setError("Please enter your password.");
      return;
    }

    setIsSubmitting(true);
    try {
      const authData = await login(usernameOrEmail.trim(), password);
      redirectRoleUser(authData.role);
    } catch (err: any) {
      setError(err?.message || "Authentication failed. Please verify your credentials.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSelectDemo = (account: DemoAccount) => {
    setUsernameOrEmail(account.usernameOrEmail);
    setPassword(account.password);
    setError(null);
  };

  const handleQuickLogin = async (account: DemoAccount) => {
    setUsernameOrEmail(account.usernameOrEmail);
    setPassword(account.password);
    setError(null);
    setIsSubmitting(true);
    try {
      const authData = await login(account.usernameOrEmail, account.password);
      redirectRoleUser(authData.role);
    } catch (err: any) {
      setError(err?.message || "Failed to sign in with demo account.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex flex-col lg:flex-row bg-[#f8fafc]">
      {/* Left Column: Brand & Regulatory Mission (Desktop only) */}
      <div className="hidden lg:flex lg:w-1/2 bg-[#0b192c] text-white p-12 flex-col justify-between relative overflow-hidden border-r border-slate-800">
        {/* Subtle background glow */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl -ml-20 -mb-20 pointer-events-none" />

        {/* Top Header */}
        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-xl tracking-tight text-white">AICTE SmartVerify</span>
                <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded bg-blue-900/80 text-blue-200 border border-blue-700/60">
                  SIH26261 MVP
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">Regulatory Scrutiny & Document Verification Platform</p>
            </div>
          </div>
        </div>

        {/* Center Editorial / Value Proposition */}
        <div className="relative z-10 my-auto py-8 space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-950/60 border border-blue-800/80 text-blue-300 text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5 text-blue-400" />
            <span>Smart India Hackathon 2026 Problem Statement SIH26261</span>
          </div>

          <h1 className="text-3xl xl:text-4xl font-bold tracking-tight text-white leading-tight">
            Intelligent application validation and compliance review.
          </h1>

          <p className="text-sm xl:text-base text-slate-300 leading-relaxed max-w-lg">
            Review institutional applications, validate supporting evidence and investigate compliance findings through an explainable, auditable workflow.
          </p>

          {/* Feature Highlights */}
          <div className="grid grid-cols-1 gap-3.5 pt-2">
            <div className="flex items-start gap-3 p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="p-2 rounded-lg bg-blue-900/40 text-blue-400 shrink-0">
                <FileSearch className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-xs font-semibold text-white">AI Document Ingestion & Verification</h2>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Automated OCR, SHA-256 duplicate detection, and cross-referencing against authority registries.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="p-2 rounded-lg bg-blue-900/40 text-blue-400 shrink-0">
                <Scale className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-xs font-semibold text-white">AICTE Handbook Compliance Engine</h2>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Automated evaluation of faculty ratios, land norms, TER fees, and prerequisite accreditations.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="p-2 rounded-lg bg-blue-900/40 text-blue-400 shrink-0">
                <History className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-xs font-semibold text-white">Immutable Audit Trail & Zero Auto-Approval</h2>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Append-only decision ledger preserving human authority and reviewer accountability.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Prototype Disclaimer */}
        <div className="relative z-10 pt-4 border-t border-slate-800/80">
          <div className="flex items-center gap-2 text-xs text-amber-300/90">
            <AlertCircle className="w-4 h-4 shrink-0 text-amber-400" />
            <span>
              SmartVerify is an independent demonstration prototype, not an official production AICTE system.
            </span>
          </div>
        </div>
      </div>

      {/* Right Column: Authentication Form & Demo Accounts */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-10 lg:p-12 overflow-y-auto">
        <div className="w-full max-w-md space-y-6">
          {/* Mobile Brand Header */}
          <div className="lg:hidden flex items-center gap-3 pb-4 border-b border-slate-200">
            <div className="w-10 h-10 rounded-xl bg-[#0b192c] flex items-center justify-center text-white shadow-xs">
              <Shield className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <span className="font-bold text-lg text-slate-900">AICTE SmartVerify</span>
              <p className="text-xs text-slate-500">Regulatory Verification Platform</p>
            </div>
          </div>

          <div>
            <h2 className="text-2xl font-bold tracking-tight text-slate-900">Sign in to your account</h2>
            <p className="text-xs text-slate-500 mt-1">
              Enter your credentials to access the regulatory scrutiny and compliance platform.
            </p>
          </div>

          {/* Error Message Alert */}
          {error && (
            <div
              role="alert"
              className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start gap-2.5 shadow-2xs"
            >
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <div className="flex-1 font-medium leading-relaxed">{error}</div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="usernameOrEmail" className="block text-xs font-semibold text-slate-700 mb-1.5">
                Email Address or Username
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  id="usernameOrEmail"
                  type="text"
                  autoComplete="username"
                  required
                  value={usernameOrEmail}
                  onChange={(e) => setUsernameOrEmail(e.target.value)}
                  placeholder="e.g. scrutiny.officer@aicte.gov.in"
                  className="w-full pl-10 pr-3.5 py-2.5 bg-white border border-slate-200 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:ring-2 focus:ring-blue-600 focus:border-transparent transition-all"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label htmlFor="password" className="block text-xs font-semibold text-slate-700">
                  Password
                </label>
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full pl-10 pr-10 py-2.5 bg-white border border-slate-200 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:ring-2 focus:ring-blue-600 focus:border-transparent transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 focus:outline-hidden"
                  title={showPassword ? "Hide password" : "Show password"}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg shadow-sm focus:outline-hidden focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 transition-all disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Authenticating...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick-Fill Demo Personas (Evaluation Tool for Hackathon Judges) */}
          <div className="pt-4 border-t border-slate-200 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                Demo Accounts for Evaluation
              </span>
              <span className="text-[10px] text-slate-400 font-medium">1-Click Sign In</span>
            </div>

            <div className="space-y-2">
              {DEMO_ACCOUNTS.map((acc) => (
                <div
                  key={acc.role}
                  className="p-3 rounded-xl border border-slate-200 bg-white hover:border-blue-300 hover:bg-blue-50/40 transition-all text-left flex items-center justify-between gap-3 group"
                >
                  <div
                    className="flex-1 cursor-pointer"
                    onClick={() => handleSelectDemo(acc)}
                    title="Click to fill form with these credentials"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-slate-900 group-hover:text-blue-700 transition-colors">
                        {acc.label}
                      </span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-medium border border-slate-200">
                        {acc.badge}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">{acc.usernameOrEmail}</p>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleQuickLogin(acc)}
                    disabled={isSubmitting}
                    className="shrink-0 px-2.5 py-1 text-xs font-semibold rounded-md bg-slate-100 hover:bg-blue-600 text-slate-700 hover:text-white transition-all shadow-2xs"
                  >
                    Enter &rarr;
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Mobile disclaimer */}
          <div className="lg:hidden p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 text-[11px] leading-relaxed flex items-start gap-2">
            <AlertCircle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
            <span>
              SmartVerify is an independent demonstration prototype, not an official production AICTE system.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
