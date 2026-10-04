import React, { useEffect, useState } from "react";
import {
  X,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  FlaskConical,
  Loader2,
  CheckCircle2,
  ArrowRight,
} from "lucide-react";
import { checkCompatibility, searchDrugs, listExcipients } from "../services/api";
import { CompatibilityCheckResponse, DrugSummary, ExcipientRead } from "../types";
import { EvidenceBadge } from "./EvidenceBadge";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  defaultDrugId?: string;
}

export const CompatibilityCheckerModal: React.FC<Props> = ({
  isOpen,
  onClose,
  defaultDrugId,
}) => {
  const [drugs, setDrugs] = useState<DrugSummary[]>([]);
  const [excipients, setExcipients] = useState<ExcipientRead[]>([]);
  const [selectedDrug, setSelectedDrug] = useState<string>("");
  const [selectedExcipient, setSelectedExcipient] = useState<string>("");
  const [result, setResult] = useState<CompatibilityCheckResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    // Load available drugs and excipients
    searchDrugs("", undefined, undefined, 0, 50).then((res) => {
      setDrugs(res.items);
      if (res.items.length > 0 && !selectedDrug) {
        setSelectedDrug(defaultDrugId || res.items[0].id);
      }
    });

    listExcipients("", undefined, 0, 50).then((res) => {
      setExcipients(res.items);
      if (res.items.length > 0 && !selectedExcipient) {
        setSelectedExcipient(res.items[0].id);
      }
    });
  }, [isOpen, defaultDrugId]);

  if (!isOpen) return null;

  const handleEvaluate = async () => {
    if (!selectedDrug || !selectedExcipient) return;
    setLoading(true);
    setError(null);
    try {
      const data = await checkCompatibility(selectedDrug, selectedExcipient);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to evaluate compatibility");
    } finally {
      setLoading(false);
    }
  };

  const getVerdictBadge = (verdict: string) => {
    switch (verdict) {
      case "compatible_under_conditions":
        return {
          bg: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
          icon: CheckCircle2,
          text: "COMPATIBLE UNDER CONDITIONS",
        };
      case "potential_interaction":
        return {
          bg: "bg-amber-500/20 text-amber-400 border-amber-500/30",
          icon: AlertTriangle,
          text: "POTENTIAL INTERACTION DETECTED",
        };
      case "incompatible_under_conditions":
        return {
          bg: "bg-rose-500/20 text-rose-400 border-rose-500/30",
          icon: AlertTriangle,
          text: "INCOMPATIBLE UNDER CONDITIONS",
        };
      default:
        return {
          bg: "bg-slate-700/20 text-slate-400 border-slate-700/30",
          icon: HelpCircle,
          text: "INSUFFICIENT EVIDENCE",
        };
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-2xl bg-[#091224] border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden text-left flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 bg-[#0d1833] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-600/20 text-emerald-400 flex items-center justify-center font-bold">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-base font-extrabold text-white">
                Drug-Excipient Compatibility Engine
              </h2>
              <div className="text-xs text-slate-400">
                Condition-specific interaction evaluation backed by DSC, FTIR, and ICH stability studies
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white bg-slate-800/50 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-5 text-xs text-slate-300">
          {/* Drug & Excipient Selector */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
                Select Active Ingredient (API)
              </label>
              <select
                value={selectedDrug}
                onChange={(e) => setSelectedDrug(e.target.value)}
                className="w-full bg-[#121c38] text-slate-100 p-2.5 rounded-xl border border-slate-700/80 focus:outline-none focus:border-blue-500 font-semibold"
              >
                {drugs.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.generic_name} ({d.form_tag})
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
                Select Target Excipient
              </label>
              <select
                value={selectedExcipient}
                onChange={(e) => setSelectedExcipient(e.target.value)}
                className="w-full bg-[#121c38] text-slate-100 p-2.5 rounded-xl border border-slate-700/80 focus:outline-none focus:border-blue-500 font-semibold"
              >
                {excipients.map((e) => (
                  <option key={e.id} value={e.id}>
                    {e.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button
            onClick={handleEvaluate}
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-blue-600/30 transition-all flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Evaluating Evidence Matrix...</span>
              </>
            ) : (
              <>
                <span>Evaluate Compatibility</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>

          {error && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400">
              {error}
            </div>
          )}

          {/* Result Card */}
          {result && (
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  Engine Derived Verdict:
                </span>
                {(() => {
                  const badge = getVerdictBadge(result.verdict);
                  const Icon = badge.icon;
                  return (
                    <span
                      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-extrabold border ${badge.bg}`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      {badge.text}
                    </span>
                  );
                })()}
              </div>

              {result.evidence.length === 0 ? (
                <div className="p-3 bg-slate-800/40 rounded-lg text-slate-400">
                  No published compatibility studies found for this specific pair under standard experimental conditions.
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="text-[11px] font-bold text-slate-300">
                    Documented Evidence Records ({result.evidence.length}):
                  </div>
                  {result.evidence.map((ev) => (
                    <div
                      key={ev.id}
                      className="p-3 rounded-lg bg-[#0c162f] border border-slate-800 space-y-1.5"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-white">
                          Study Category: {ev.category.replace(/_/g, " ").toUpperCase()}
                        </span>
                        <EvidenceBadge level={ev.evidence_level} />
                      </div>
                      {ev.reported_interaction && (
                        <div className="text-amber-300 font-medium">
                          ⚠️ {ev.reported_interaction}
                        </div>
                      )}
                      {ev.possible_mechanism && (
                        <div className="text-slate-400">
                          <strong>Mechanism:</strong> {ev.possible_mechanism}
                        </div>
                      )}
                      {ev.conditions_summary && (
                        <div className="text-slate-300">
                          <strong>Conditions:</strong> {ev.conditions_summary}
                        </div>
                      )}
                      <div className="text-[10px] text-slate-400 flex items-center justify-between pt-1">
                        <span>Methods: {ev.methods.join(", ")}</span>
                        <span>Source: {ev.source?.name}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="p-2.5 rounded bg-blue-950/20 border border-blue-500/20 text-[10px] text-slate-400 italic">
                {result.disclaimer}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
