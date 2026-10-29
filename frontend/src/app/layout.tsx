import type { Metadata } from "next";
import { Suspense } from "react";
import "./globals.css";
import { AuthProvider } from "@/lib/authContext";
import { AppShell } from "@/components/layout/AppShell";

export const metadata: Metadata = {
  title: "AICTE SmartVerify — SIH26261 Regulatory Platform",
  description:
    "AI-Powered Application Validation, Document Authentication and Regulatory Compliance Verification MVP for Smart India Hackathon.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#f8fafc] text-slate-900 min-h-screen font-sans antialiased selection:bg-blue-100 selection:text-blue-900">
        <Suspense fallback={null}>
          <AuthProvider>
            <AppShell>{children}</AppShell>
          </AuthProvider>
        </Suspense>
      </body>
    </html>
  );
}
