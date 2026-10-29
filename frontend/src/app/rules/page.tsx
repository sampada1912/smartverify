"use client";

import React, { useEffect, useState } from "react";
import { ComplianceRule, ChecklistRule } from "@/lib/types";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/authContext";
import { SeverityBadge } from "@/components/ui/SeverityBadge";
import { Modal } from "@/components/ui/Modal";
import {
  Scale,
  FileCheck,
  CheckCircle2,
  AlertTriangle,
  Edit3,
  ToggleLeft,
  ToggleRight,
  Shield,
  Layers,
  Info,
  RefreshCw,
  Search,
} from "lucide-react";

export default function RulesManagementPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<"compliance" | "checklist">("compliance");
  const [complianceRules, setComplianceRules] = useState<ComplianceRule[]>([]);
  const [checklistRules, setChecklistRules] = useState<ChecklistRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  // Edit Compliance Rule Modal state
  const [editingCompRule, setEditingCompRule] = useState<ComplianceRule | null>(null);
  const [compDescription, setCompDescription] = useState("");
  const [compEnabled, setCompEnabled] = useState(true);
  const [savingComp, setSavingComp] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);

  // Edit Checklist Rule Modal state
  const [editingChecklistRule, setEditingChecklistRule] = useState<ChecklistRule | null>(null);
  const [chkDescription, setChkDescription] = useState("");
  const [chkRequired, setChkRequired] = useState(true);
  const [chkActive, setChkActive] = useState(true);
  const [savingChk, setSavingChk] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [comp, chk] = await Promise.all([
        api.listComplianceRules(),
        api.listChecklistRules(),
      ]);
      setComplianceRules(comp);
      setChecklistRules(chk);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleToggleCompliance = async (rule: ComplianceRule) => {
    try {
      const updated = await api.updateComplianceRule(rule.rule_id, {
        is_enabled: !rule.is_enabled,
      });
      setComplianceRules((prev) =>
        prev.map((r) => (r.rule_id === rule.rule_id ? updated : r))
      );
    } catch (err: any) {
      alert(err.message || "Failed to update compliance rule");
    }
  };

  const handleToggleChecklist = async (rule: ChecklistRule) => {
    try {
      const updated = await api.updateChecklistRule(rule.rule_code, {
        is_active: !rule.is_active,
      });
      setChecklistRules((prev) =>
        prev.map((r) => (r.rule_code === rule.rule_code ? updated : r))
      );
    } catch (err: any) {
      alert(err.message || "Failed to update checklist rule");
    }
  };

  const openEditComp = (r: ComplianceRule) => {
    setEditingCompRule(r);
    setCompDescription(r.description);
    setCompEnabled(r.is_enabled);
    setModalError(null);
  };

  const saveEditComp = async () => {
    if (!editingCompRule) return;
    setSavingComp(true);
    setModalError(null);
    try {
      const updated = await api.updateComplianceRule(editingCompRule.rule_id, {
        description: compDescription,
        is_enabled: compEnabled,
      });
      setComplianceRules((prev) =>
        prev.map((r) => (r.rule_id === editingCompRule.rule_id ? updated : r))
      );
      setEditingCompRule(null);
    } catch (err: any) {
      setModalError(err.message || "Failed to save rule updates");
    } finally {
      setSavingComp(false);
    }
  };

  const openEditChk = (r: ChecklistRule) => {
    setEditingChecklistRule(r);
    setChkDescription(r.description);
    setChkRequired(r.is_required);
    setChkActive(r.is_active);
    setModalError(null);
  };

  const saveEditChk = async () => {
    if (!editingChecklistRule) return;
    setSavingChk(true);
    setModalError(null);
    try {
      const updated = await api.updateChecklistRule(editingChecklistRule.rule_code, {
        description: chkDescription,
        is_required: chkRequired,
        is_active: chkActive,
      });
      setChecklistRules((prev) =>
        prev.map((r) => (r.rule_code === editingChecklistRule.rule_code ? updated : r))
      );
      setEditingChecklistRule(null);
    } catch (err: any) {
      setModalError(err.message || "Failed to save checklist updates");
    } finally {
      setSavingChk(false);
    }
  };

  const filteredCompliance = complianceRules.filter((r) => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return (
      r.rule_id.toLowerCase().includes(q) ||
      r.rule_name.toLowerCase().includes(q) ||
      r.description.toLowerCase().includes(q) ||
      r.required_evidence_type.toLowerCase().includes(q)
    );
  });

  const filteredChecklist = checklistRules.filter((r) => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return (
      r.rule_code.toLowerCase().includes(q) ||
      r.requirement_name.toLowerCase().includes(q) ||
      r.document_type.toLowerCase().includes(q) ||
      r.category.toLowerCase().includes(q)
    );
  });

  const isAdmin = user?.role === "ADMIN";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Regulatory Scrutiny Rules & Checklists
            </h1>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-900 border border-blue-200">
              DATABASE CONFIGURED
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Configurable regulatory evaluation rules and category-driven document requirements.
          </p>
        </div>

        <button
          onClick={fetchData}
          className="inline-flex items-center gap-2 px-3 py-2 border border-slate-200 bg-white rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-xs"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Rules</span>
        </button>
      </div>

      {/* Disclaimers & Notice */}
      <div className="p-4 bg-slate-100 border border-slate-300 rounded-xl text-xs text-slate-800 flex items-start gap-3">
        <Info className="w-5 h-5 text-slate-600 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-bold">Illustrative Regulatory Rule Engine</p>
          <p className="text-slate-600 leading-relaxed">
            These rules are stored dynamically in PostgreSQL/SQLite and evaluated deterministically against applications.
            They represent an illustrative implementation for Extension of Approval (EoA) and must receive authorized regulatory approval before production use.
            {!isAdmin && (
              <span className="block mt-1 font-semibold text-amber-700">
                You are currently viewing in read-only mode. Switch to Administrator role via the top header to enable or edit rules.
              </span>
            )}
          </p>
        </div>
      </div>

      {/* Tabs & Search */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab("compliance")}
              className={`px-3.5 py-2 text-xs font-semibold rounded-lg transition-colors flex items-center gap-2 ${
                activeTab === "compliance"
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              <Scale className="w-3.5 h-3.5" />
              <span>Compliance Evaluation Rules ({complianceRules.length})</span>
            </button>

            <button
              onClick={() => setActiveTab("checklist")}
              className={`px-3.5 py-2 text-xs font-semibold rounded-lg transition-colors flex items-center gap-2 ${
                activeTab === "checklist"
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              <FileCheck className="w-3.5 h-3.5" />
              <span>Category Document Checklists ({checklistRules.length})</span>
            </button>
          </div>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search rule code, name, category..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </div>

        {loading ? (
          <div className="py-12 text-center">
            <div className="w-7 h-7 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            <p className="text-xs text-slate-500 font-medium">Loading rules engine configuration...</p>
          </div>
        ) : activeTab === "compliance" ? (
          /* Compliance Rules Table */
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-2.5 px-3">Rule ID</th>
                  <th className="py-2.5 px-3">Rule Name & Logic</th>
                  <th className="py-2.5 px-3">Applicability</th>
                  <th className="py-2.5 px-3">Evidence Required</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">Status</th>
                  {isAdmin && <th className="py-2.5 px-3 text-right">Configure</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {filteredCompliance.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-3">
                      <span className="font-mono font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                        {r.rule_id}
                      </span>
                    </td>

                    <td className="py-3 px-3 max-w-sm">
                      <div className="font-bold text-slate-900">{r.rule_name}</div>
                      <div className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">
                        {r.description}
                      </div>
                    </td>

                    <td className="py-3 px-3">
                      <span className="font-medium px-2 py-0.5 bg-slate-100 text-slate-700 rounded text-[11px] border border-slate-200">
                        {r.category_condition}
                      </span>
                    </td>

                    <td className="py-3 px-3 text-slate-600 font-medium">
                      {r.required_evidence_type}
                    </td>

                    <td className="py-3 px-3">
                      <SeverityBadge severity={r.severity as any} />
                    </td>

                    <td className="py-3 px-3">
                      {isAdmin ? (
                        <button
                          onClick={() => handleToggleCompliance(r)}
                          className="flex items-center gap-1.5 focus:outline-hidden"
                        >
                          {r.is_enabled ? (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                              <span>Active</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-bold bg-slate-100 text-slate-500 border border-slate-200">
                              <span>Disabled</span>
                            </span>
                          )}
                        </button>
                      ) : (
                        <span
                          className={`text-[11px] font-bold px-2 py-0.5 rounded border ${
                            r.is_enabled
                              ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                              : "bg-slate-100 text-slate-500 border-slate-200"
                          }`}
                        >
                          {r.is_enabled ? "Active" : "Disabled"}
                        </span>
                      )}
                    </td>

                    {isAdmin && (
                      <td className="py-3 px-3 text-right">
                        <button
                          onClick={() => openEditComp(r)}
                          className="inline-flex items-center gap-1 px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-xs font-semibold transition-colors"
                        >
                          <Edit3 className="w-3 h-3" />
                          <span>Edit</span>
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          /* Checklist Rules Table */
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-2.5 px-3">Rule Code</th>
                  <th className="py-2.5 px-3">Requirement Name</th>
                  <th className="py-2.5 px-3">Document Type</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Requirement Level</th>
                  <th className="py-2.5 px-3">Status</th>
                  {isAdmin && <th className="py-2.5 px-3 text-right">Configure</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {filteredChecklist.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-3">
                      <span className="font-mono font-bold text-slate-800 bg-slate-100 px-2 py-0.5 rounded border border-slate-300">
                        {r.rule_code}
                      </span>
                    </td>

                    <td className="py-3 px-3 max-w-sm">
                      <div className="font-bold text-slate-900">{r.requirement_name}</div>
                      <div className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">
                        {r.description}
                      </div>
                    </td>

                    <td className="py-3 px-3">
                      <span className="font-mono text-[11px] text-blue-700 bg-blue-50 px-2 py-0.5 rounded">
                        {r.document_type}
                      </span>
                    </td>

                    <td className="py-3 px-3 font-medium text-slate-700">
                      {r.category}
                    </td>

                    <td className="py-3 px-3">
                      <span
                        className={`text-[11px] font-bold px-2 py-0.5 rounded border ${
                          r.is_required
                            ? "bg-red-50 text-red-700 border-red-200"
                            : "bg-slate-100 text-slate-600 border-slate-200"
                        }`}
                      >
                        {r.is_required ? "Mandatory" : "Optional"}
                      </span>
                    </td>

                    <td className="py-3 px-3">
                      {isAdmin ? (
                        <button
                          onClick={() => handleToggleChecklist(r)}
                          className="flex items-center gap-1.5 focus:outline-hidden"
                        >
                          {r.is_active ? (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                              <span>Active</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-bold bg-slate-100 text-slate-500 border border-slate-200">
                              <span>Disabled</span>
                            </span>
                          )}
                        </button>
                      ) : (
                        <span
                          className={`text-[11px] font-bold px-2 py-0.5 rounded border ${
                            r.is_active
                              ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                              : "bg-slate-100 text-slate-500 border-slate-200"
                          }`}
                        >
                          {r.is_active ? "Active" : "Disabled"}
                        </span>
                      )}
                    </td>

                    {isAdmin && (
                      <td className="py-3 px-3 text-right">
                        <button
                          onClick={() => openEditChk(r)}
                          className="inline-flex items-center gap-1 px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-xs font-semibold transition-colors"
                        >
                          <Edit3 className="w-3 h-3" />
                          <span>Edit</span>
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Edit Compliance Rule Modal */}
      {editingCompRule && (
        <Modal
          isOpen={true}
          onClose={() => setEditingCompRule(null)}
          title={`Configure Compliance Rule: ${editingCompRule.rule_id}`}
          subtitle={editingCompRule.rule_name}
        >
          <div className="space-y-4">
            {modalError && (
              <div className="p-3 bg-red-50 border border-red-200 text-red-800 rounded-lg text-xs">
                {modalError}
              </div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Rule Description & Regulatory Citation
              </label>
              <textarea
                rows={3}
                value={compDescription}
                onChange={(e) => setCompDescription(e.target.value)}
                className="w-full text-xs border border-slate-300 rounded-lg p-2.5 text-slate-800 focus:outline-hidden focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div className="flex items-center gap-3">
              <label className="text-xs font-bold text-slate-700">Rule Active Status:</label>
              <button
                type="button"
                onClick={() => setCompEnabled(!compEnabled)}
                className={`px-3 py-1 rounded text-xs font-bold border transition-colors ${
                  compEnabled
                    ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                    : "bg-slate-100 text-slate-500 border-slate-300"
                }`}
              >
                {compEnabled ? "Active & Enforced" : "Disabled"}
              </button>
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t border-slate-200">
              <button
                type="button"
                onClick={() => setEditingCompRule(null)}
                className="px-3.5 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={savingComp}
                onClick={saveEditComp}
                className="px-4 py-2 text-xs font-semibold bg-blue-700 hover:bg-blue-800 text-white rounded-lg disabled:opacity-50"
              >
                {savingComp ? "Saving..." : "Save Rule Configuration"}
              </button>
            </div>
          </div>
        </Modal>
      )}

      {/* Edit Checklist Rule Modal */}
      {editingChecklistRule && (
        <Modal
          isOpen={true}
          onClose={() => setEditingChecklistRule(null)}
          title={`Configure Checklist Requirement: ${editingChecklistRule.rule_code}`}
          subtitle={editingChecklistRule.requirement_name}
        >
          <div className="space-y-4">
            {modalError && (
              <div className="p-3 bg-red-50 border border-red-200 text-red-800 rounded-lg text-xs">
                {modalError}
              </div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Requirement Description
              </label>
              <textarea
                rows={3}
                value={chkDescription}
                onChange={(e) => setChkDescription(e.target.value)}
                className="w-full text-xs border border-slate-300 rounded-lg p-2.5 text-slate-800 focus:outline-hidden focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Enforcement Level:
                </label>
                <select
                  value={chkRequired ? "true" : "false"}
                  onChange={(e) => setChkRequired(e.target.value === "true")}
                  className="w-full text-xs border border-slate-300 rounded-lg p-2 text-slate-800 bg-white"
                >
                  <option value="true">Mandatory Document</option>
                  <option value="false">Optional Document</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Active Status:
                </label>
                <select
                  value={chkActive ? "true" : "false"}
                  onChange={(e) => setChkActive(e.target.value === "true")}
                  className="w-full text-xs border border-slate-300 rounded-lg p-2 text-slate-800 bg-white"
                >
                  <option value="true">Active in Checklist</option>
                  <option value="false">Disabled / Suspended</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t border-slate-200">
              <button
                type="button"
                onClick={() => setEditingChecklistRule(null)}
                className="px-3.5 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={savingChk}
                onClick={saveEditChk}
                className="px-4 py-2 text-xs font-semibold bg-blue-700 hover:bg-blue-800 text-white rounded-lg disabled:opacity-50"
              >
                {savingChk ? "Saving..." : "Save Checklist Configuration"}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
