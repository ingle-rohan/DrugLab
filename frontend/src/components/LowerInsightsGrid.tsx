import React from "react";
import { ShieldCheck, BookOpen, ExternalLink, Activity, Pill } from "lucide-react";
import { EvidenceBadge } from "./EvidenceBadge";
import { ChemicalStructure } from "./ChemicalStructure";

interface LowerInsightsGridProps {
  onOpenCompatibility: () => void;
  onSelectDrug: (name: string) => void;
}

export const LowerInsightsGrid: React.FC<LowerInsightsGridProps> = ({
  onOpenCompatibility,
  onSelectDrug,
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {/* 1. Drug-Excipient Compatibility Gauge & Matrix */}
      <div className="p-4 rounded-xl bg-[#0c162f] border border-slate-800/80 flex flex-col justify-between shadow-sm text-left">
        <div>
          <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Drug-Excipient Compatibility</span>
            </h3>
            <button
              onClick={onOpenCompatibility}
              className="text-[11px] font-medium text-blue-400 hover:text-blue-300"
            >
              View all →
            </button>
          </div>

          {/* Compatibility Highlight Card */}
          <div className="flex items-center justify-between p-3 my-3 rounded-xl bg-gradient-to-r from-emerald-950/40 via-[#0d1c3a] to-slate-900 border border-emerald-500/20">
            <div className="flex items-center gap-3">
              <div className="relative w-12 h-12 rounded-full border-4 border-emerald-500/30 border-t-emerald-400 flex items-center justify-center font-extrabold text-xs text-emerald-300 shrink-0 shadow-lg shadow-emerald-500/10">
                92%
              </div>
              <div>
                <div className="text-xs font-bold text-slate-100">
                  Ibuprofen + HPMC
                </div>
                <div className="text-[10px] text-slate-400 mt-0.5 leading-snug">
                  Good compatibility for oral solid dosage forms.
                </div>
              </div>
            </div>

            {/* 3D Capsule Cluster visual */}
            <div className="hidden sm:flex flex-col items-center justify-center p-1.5 rounded-lg bg-blue-950/40 border border-blue-500/20 text-blue-400">
              <Pill className="w-5 h-5 -rotate-45" />
            </div>
          </div>

          {/* Mini Table */}
          <div className="space-y-1.5 text-xs">
            <div className="flex items-center justify-between py-1.5 border-b border-slate-800/40 text-slate-300">
              <span className="font-medium">HPMC</span>
              <span className="text-emerald-400 font-semibold text-[11px]">● Excellent</span>
              <span className="text-[10px] text-emerald-400 font-medium">● High</span>
            </div>
            <div className="flex items-center justify-between py-1.5 border-b border-slate-800/40 text-slate-300">
              <span className="font-medium">Microcrystalline Cellulose</span>
              <span className="text-emerald-400 font-semibold text-[11px]">● Good</span>
              <span className="text-[10px] text-emerald-400 font-medium">● High</span>
            </div>
            <div className="flex items-center justify-between py-1.5 border-b border-slate-800/40 text-slate-300">
              <span className="font-medium">Lactose Monohydrate</span>
              <span className="text-cyan-400 font-semibold text-[11px]">● Good</span>
              <span className="text-[10px] text-amber-400 font-medium">● Medium</span>
            </div>
          </div>
        </div>

        <button
          onClick={onOpenCompatibility}
          className="text-xs font-semibold text-blue-400 hover:text-blue-300 pt-3 flex items-center gap-1"
        >
          <span>View detailed compatibility report</span>
          <span>→</span>
        </button>
      </div>

      {/* 2. Preformulation Insights */}
      <div className="p-4 rounded-xl bg-[#0c162f] border border-slate-800/80 flex flex-col justify-between shadow-sm text-left">
        <div>
          <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
              <Activity className="w-4 h-4 text-blue-400" />
              <span>Preformulation Insights</span>
            </h3>
            <button
              onClick={() => onSelectDrug("Ibuprofen")}
              className="text-[11px] font-medium text-blue-400 hover:text-blue-300"
            >
              View all →
            </button>
          </div>

          <div className="my-2 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-slate-100">Ibuprofen</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[10px] font-bold">
                  BCS Class II
                </span>
                <span className="px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-[10px] font-bold">
                  LogP 3.97
                </span>
              </div>
            </div>

            {/* Molecule skeletal drawing box */}
            <div className="w-full py-1.5 bg-slate-900/60 rounded-lg border border-slate-800/80 flex items-center justify-center">
              <ChemicalStructure name="Ibuprofen" width={110} height={44} className="text-blue-400/90" />
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2 rounded-lg bg-slate-900/60 border border-slate-800">
                <div className="text-[10px] text-slate-400">Molecular Weight</div>
                <div className="font-semibold text-slate-200 mt-0.5">206.28 g/mol</div>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <div className="text-[10px] text-slate-400">Melting Point</div>
                <div className="font-semibold text-slate-200 mt-0.5">75 - 77 °C</div>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <div className="text-[10px] text-slate-400">pKa (COOH)</div>
                <div className="font-semibold text-slate-200 mt-0.5">4.91</div>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <div className="text-[10px] text-slate-400">Solubility (water)</div>
                <div className="font-semibold text-slate-200 mt-0.5">21 mg/L</div>
              </div>
            </div>
          </div>
        </div>

        <button
          onClick={() => onSelectDrug("Ibuprofen")}
          className="text-xs font-semibold text-blue-400 hover:text-blue-300 pt-3 flex items-center gap-1"
        >
          <span>View full profile</span>
          <span>→</span>
        </button>
      </div>

      {/* 3. Latest Literature & Evidence */}
      <div className="p-4 rounded-xl bg-[#0c162f] border border-slate-800/80 flex flex-col justify-between shadow-sm text-left">
        <div>
          <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
              <BookOpen className="w-4 h-4 text-purple-400" />
              <span>Latest Literature & Evidence</span>
            </h3>
            <span className="text-[11px] font-medium text-blue-400 hover:text-blue-300 cursor-pointer">
              View all →
            </span>
          </div>

          <div className="divide-y divide-slate-800/50 mt-1 space-y-1">
            <div className="py-2">
              <div className="flex items-center justify-between">
                <div className="text-xs font-semibold text-slate-200 hover:text-blue-400 cursor-pointer line-clamp-1">
                  Efficacy of Ibuprofen in Pain Management
                </div>
                <span className="px-1.5 py-0.5 text-[9px] rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 shrink-0 ml-2">
                  Level B
                </span>
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                Journal of Pain Research • 2024
              </div>
            </div>

            <div className="py-2">
              <div className="flex items-center justify-between">
                <div className="text-xs font-semibold text-slate-200 hover:text-blue-400 cursor-pointer line-clamp-1">
                  Formulation Strategies for Poorly Soluble Drugs
                </div>
                <span className="px-1.5 py-0.5 text-[9px] rounded bg-blue-500/10 text-blue-400 border border-blue-500/30 shrink-0 ml-2">
                  Level B
                </span>
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                Pharmaceutics • 2023
              </div>
            </div>

            <div className="py-2">
              <div className="flex items-center justify-between">
                <div className="text-xs font-semibold text-slate-200 hover:text-blue-400 cursor-pointer line-clamp-1">
                  Biowaiver Monograph for Acetaminophen
                </div>
                <span className="px-1.5 py-0.5 text-[9px] rounded bg-blue-500/10 text-blue-400 border border-blue-500/30 shrink-0 ml-2">
                  Level B
                </span>
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                Journal of Pharmaceutical Sciences • 2006
              </div>
            </div>
          </div>
        </div>

        <div className="text-xs font-semibold text-blue-400 hover:text-blue-300 pt-3 flex items-center gap-1 cursor-pointer">
          <span>Search 3,210 literature citations (pgvector)</span>
          <span>→</span>
        </div>
      </div>
    </div>
  );
};
