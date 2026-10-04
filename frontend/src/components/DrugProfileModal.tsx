import React, { useEffect, useState } from "react";
import {
  X,
  Pill,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  Activity,
  Layers,
  FileText,
  Building,
  ExternalLink,
  Loader2,
} from "lucide-react";
import { getDrugProfile } from "../services/api";
import { DrugProfile } from "../types";
import { EvidenceBadge } from "./EvidenceBadge";

interface Props {
  drugNameOrId: string | null;
  onClose: () => void;
}

export const DrugProfileModal: React.FC<Props> = ({ drugNameOrId, onClose }) => {
  const [profile, setProfile] = useState<DrugProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<
    "overview" | "preformulation" | "bcs" | "dosing" | "compatibility" | "brands" | "conflicts"
  >("overview");

  useEffect(() => {
    if (!drugNameOrId) return;
    setLoading(true);
    getDrugProfile(drugNameOrId)
      .then(setProfile)
      .catch((err) => console.error("Failed to load drug profile", err))
      .finally(() => setLoading(false));
  }, [drugNameOrId]);

  if (!drugNameOrId) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-4xl max-h-[90vh] bg-[#091224] border border-slate-700/80 rounded-2xl shadow-2xl flex flex-col overflow-hidden text-left">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 bg-[#0d1833] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold">
              <Pill className="w-6 h-6 -rotate-45" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-extrabold text-white">
                  {profile?.generic_name || drugNameOrId}
                </h2>
                {profile?.identity_evidence_level && (
                  <EvidenceBadge level={profile.identity_evidence_level} />
                )}
                {profile?.form_tag && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-mono">
                    {profile.form_tag}
                  </span>
                )}
              </div>
              <div className="text-xs text-slate-400 mt-0.5">
                {profile?.therapeutic_class || "Pharmaceutical API"} • Formula:{" "}
                <span className="font-mono text-slate-200">
                  {profile?.molecular_formula || "N/A"}
                </span>
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

        {/* Tab Navigation */}
        <div className="flex items-center gap-1 px-5 border-b border-slate-800 bg-[#0a1329] text-xs font-semibold overflow-x-auto shrink-0">
          {[
            { id: "overview", label: "Overview & Identity" },
            { id: "preformulation", label: `Preformulation (${profile?.preformulation_metrics.length || 0})` },
            { id: "bcs", label: `BCS Classification (${profile?.bcs_assessments.length || 0})` },
            { id: "dosing", label: `Dosing Ceilings (${profile?.dose_guidelines.length || 0})` },
            { id: "compatibility", label: `Compatibility (${profile?.compatibilities.length || 0})` },
            { id: "brands", label: `Indian Brands (${profile?.indian_brands.length || 0})` },
            { id: "conflicts", label: `Conflicts (${profile?.conflicts.length || 0})` },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-3 px-3 border-b-2 transition-all shrink-0 ${
                activeTab === tab.id
                  ? "border-blue-500 text-blue-400 bg-blue-500/5"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-slate-300 text-xs">
          {loading ? (
            <div className="py-20 flex flex-col items-center justify-center gap-3 text-slate-400">
              <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
              <span>Fetching verified pharmaceutical record...</span>
            </div>
          ) : profile ? (
            <>
              {/* Tab 1: Overview */}
              {activeTab === "overview" && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                      <div className="text-[10px] text-slate-400">CAS Number</div>
                      <div className="font-mono text-sm font-semibold text-white mt-0.5">
                        {profile.cas_number || "N/A"}
                      </div>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                      <div className="text-[10px] text-slate-400">ATC Code</div>
                      <div className="font-mono text-sm font-semibold text-white mt-0.5">
                        {profile.atc_code || "N/A"}
                      </div>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                      <div className="text-[10px] text-slate-400">Molecular Weight</div>
                      <div className="font-mono text-sm font-semibold text-white mt-0.5">
                        {profile.molecular_weight} g/mol
                      </div>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                      <div className="text-[10px] text-slate-400">UNII</div>
                      <div className="font-mono text-sm font-semibold text-white mt-0.5">
                        {profile.unii || "N/A"}
                      </div>
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                      Mechanism of Action & Pharmacology
                    </h4>
                    <p className="text-slate-200 leading-relaxed">
                      {profile.mechanism_of_action || "Mechanism not recorded."}
                    </p>
                    <p className="text-slate-400 leading-relaxed">
                      {profile.pharmacological_action}
                    </p>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2 font-mono text-[11px]">
                    <div className="text-xs font-sans font-bold uppercase tracking-wider text-slate-400">
                      Chemical Descriptors
                    </div>
                    <div className="break-all">
                      <span className="text-slate-400">InChIKey: </span>
                      <span className="text-blue-300">{profile.inchikey || "N/A"}</span>
                    </div>
                    <div className="break-all">
                      <span className="text-slate-400">Isomeric SMILES: </span>
                      <span className="text-cyan-300">{profile.smiles_isomeric || "N/A"}</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Stereocentres: </span>
                      <span className="text-amber-300">{profile.stereocentre_count ?? "N/A"}</span>
                      {profile.stereochemistry_note && (
                        <p className="font-sans text-xs text-slate-400 mt-1">
                          {profile.stereochemistry_note}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 2: Preformulation Metrics */}
              {activeTab === "preformulation" && (
                <div className="space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Experimental & Computed Preformulation Parameters
                  </h4>
                  <div className="divide-y divide-slate-800 rounded-xl bg-slate-900/60 border border-slate-800 overflow-hidden">
                    {profile.preformulation_metrics.map((m) => (
                      <div key={m.id} className="p-3 flex items-start justify-between gap-4">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-slate-100 uppercase tracking-wide">
                              {m.metric_type}
                            </span>
                            <EvidenceBadge level={m.evidence_level} />
                            {m.ionizable_group && (
                              <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                                {m.ionizable_group}
                              </span>
                            )}
                          </div>
                          <div className="text-sm font-extrabold text-blue-400">
                            {m.value_numeric !== undefined
                              ? `${m.value_numeric} ${m.unit || ""}`
                              : `${m.value_min} - ${m.value_max} ${m.unit || ""}`}
                          </div>
                          {m.notes && (
                            <div className="text-[11px] text-slate-400">{m.notes}</div>
                          )}
                          <div className="text-[10px] text-slate-400 flex items-center gap-3">
                            {m.temperature_c && <span>Temp: {m.temperature_c} °C</span>}
                            {m.ph && <span>pH: {m.ph}</span>}
                            {m.method && <span>Method: {m.method}</span>}
                          </div>
                        </div>

                        <div className="text-right text-[10px] text-slate-400 shrink-0">
                          <div>Source: {m.source?.name}</div>
                          {m.source_locator && <div>{m.source_locator}</div>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 3: BCS Classification */}
              {activeTab === "bcs" && (
                <div className="space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Biopharmaceutics Classification System (Dose Dependent & Disputed)
                  </h4>
                  <div className="space-y-3">
                    {profile.bcs_assessments.map((bcs) => (
                      <div
                        key={bcs.id}
                        className={`p-4 rounded-xl border ${
                          bcs.is_disputed
                            ? "bg-amber-950/20 border-amber-500/30"
                            : "bg-slate-900/60 border-slate-800"
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-base font-extrabold text-white">
                              BCS Class {bcs.bcs_class}
                            </span>
                            {bcs.is_disputed && (
                              <span className="text-[10px] font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30">
                                DISPUTED
                              </span>
                            )}
                            <EvidenceBadge level={bcs.evidence_level} />
                          </div>
                          <span className="text-xs font-mono text-slate-400">
                            Dose: {bcs.dose_mg_min} - {bcs.dose_mg_max} mg
                          </span>
                        </div>
                        <div className="text-xs font-semibold text-blue-400 mt-1">
                          Framework: {bcs.framework}
                        </div>
                        <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                          <strong>Solubility Basis:</strong> {bcs.solubility_basis}
                        </p>
                        <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                          <strong>Permeability Basis:</strong> {bcs.permeability_basis}
                        </p>
                        {bcs.rationale && (
                          <p className="text-xs text-slate-400 mt-2 italic">
                            Rationale: {bcs.rationale}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 4: Dosing Guidelines */}
              {activeTab === "dosing" && (
                <div className="space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Regulatory Dosing Guidelines & Safety Ceilings
                  </h4>
                  <div className="space-y-3">
                    {profile.dose_guidelines.map((dg) => (
                      <div
                        key={dg.id}
                        className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2 font-bold text-slate-200">
                            <span>{dg.population}</span>
                            <span className="text-slate-400 font-normal">
                              ({dg.route})
                            </span>
                            <EvidenceBadge level={dg.evidence_level} />
                          </div>
                          <span className="text-xs font-bold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
                            Ceiling: {dg.max_daily_dose_mg} mg/24h
                          </span>
                        </div>
                        <p className="text-xs text-slate-100 font-medium leading-relaxed">
                          {dg.regimen_text}
                        </p>
                        <div className="text-[11px] text-slate-400 flex items-center justify-between pt-1">
                          <span>Jurisdiction: {dg.jurisdiction}</span>
                          <span>Source: {dg.source?.name}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 5: Compatibility */}
              {activeTab === "compatibility" && (
                <div className="space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Drug-Excipient Compatibility Matrix
                  </h4>
                  <div className="divide-y divide-slate-800 rounded-xl bg-slate-900/60 border border-slate-800 overflow-hidden">
                    {profile.compatibilities.map((comp) => {
                      const isPotential = comp.category === "potential_interaction";
                      const isIncompat = comp.category === "incompatible_under_conditions";
                      return (
                        <div
                          key={comp.id}
                          className={`p-3 space-y-1.5 ${
                            isPotential || isIncompat ? "bg-amber-950/10" : ""
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-sm text-white">
                              {comp.excipient?.name}
                            </span>
                            <div className="flex items-center gap-2">
                              <span
                                className={`text-[11px] font-bold px-2 py-0.5 rounded ${
                                  isIncompat
                                    ? "bg-rose-500/20 text-rose-400"
                                    : isPotential
                                    ? "bg-amber-500/20 text-amber-400"
                                    : "bg-emerald-500/20 text-emerald-400"
                                }`}
                              >
                                {comp.category.replace(/_/g, " ").toUpperCase()}
                              </span>
                              <EvidenceBadge level={comp.evidence_level} />
                            </div>
                          </div>
                          {comp.reported_interaction && (
                            <div className="text-xs font-medium text-amber-300">
                              ⚠️ {comp.reported_interaction}
                            </div>
                          )}
                          {comp.possible_mechanism && (
                            <div className="text-[11px] text-slate-400">
                              Mechanism: {comp.possible_mechanism}
                            </div>
                          )}
                          <div className="text-[10px] text-slate-400 flex items-center justify-between pt-1">
                            <span>Methods: {comp.methods.join(", ")}</span>
                            {comp.conditions_summary && (
                              <span>{comp.conditions_summary}</span>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Tab 6: Indian Brands */}
              {activeTab === "brands" && (
                <div className="space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Marketed Formulations in India (CDSCO Registered)
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {profile.indian_brands.map((b) => (
                      <div
                        key={b.id}
                        className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-sm text-white">
                            {b.brand_name}
                          </span>
                          <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">
                            {b.verification_status}
                          </span>
                        </div>
                        <div className="text-xs text-blue-400 font-medium">
                          {b.manufacturer}
                        </div>
                        <div className="text-[11px] text-slate-400">
                          {b.strength} • {b.dosage_form} ({b.pack_size})
                        </div>
                        <div className="text-[11px] text-emerald-400 font-bold flex items-center justify-between pt-1">
                          <span>MRP: ₹{b.mrp_inr ?? "N/A"}</span>
                          <span className="text-[10px] text-slate-400">
                            Ref: {b.cdsco_approval_ref || "Directory"}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 7: Conflicts & Missing Data */}
              {activeTab === "conflicts" && (
                <div className="space-y-4">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    First-Class Dispute Logs (Section 30)
                  </h4>
                  {profile.conflicts.length === 0 ? (
                    <div className="p-4 rounded-xl bg-slate-900/40 text-slate-400 text-center">
                      No unresolved conflicts registered for this drug.
                    </div>
                  ) : (
                    profile.conflicts.map((c) => (
                      <div
                        key={c.id}
                        className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30 space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-amber-300">
                            Disputed Field: [{c.field_name}]
                          </span>
                          <span className="text-[10px] uppercase font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded">
                            Confidence: {c.confidence}
                          </span>
                        </div>
                        <p className="text-xs text-slate-200">{c.claim}</p>
                        {c.difference && (
                          <div className="text-[11px] text-slate-400">
                            <strong>Observed Difference:</strong> {c.difference}
                          </div>
                        )}
                        {c.current_interpretation && (
                          <div className="text-[11px] text-slate-300 bg-slate-900/60 p-2 rounded-lg border border-slate-800">
                            <strong>Interpretation:</strong> {c.current_interpretation}
                          </div>
                        )}
                      </div>
                    ))
                  )}

                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 pt-3">
                    Explicit Missing Data Registry (Section 31)
                  </h4>
                  {profile.missing_data.map((m) => (
                    <div
                      key={m.id}
                      className="p-3 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1"
                    >
                      <div className="font-semibold text-slate-200 text-xs">
                        Missing: [{m.field_name}]
                      </div>
                      <p className="text-slate-400 text-[11px]">{m.statement}</p>
                      <div className="text-blue-400 text-[10px]">
                        Suggested Next Step: {m.suggested_next_step}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12 text-slate-400">
              Unable to load drug profile.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
