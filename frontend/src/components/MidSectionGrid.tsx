import React from "react";
import {
  ChevronRight,
  TrendingUp,
  Scale,
  ShieldCheck,
  FlaskConical,
  Flag,
  ArrowRight,
} from "lucide-react";
import { EvidenceBadge } from "./EvidenceBadge";
import { ChemicalStructure } from "./ChemicalStructure";

interface MidSectionGridProps {
  onSelectDrug: (name: string) => void;
  onOpenCompatibility: () => void;
  onOpenComparison: () => void;
  onOpenIndianPharma: () => void;
}

export const MidSectionGrid: React.FC<MidSectionGridProps> = ({
  onSelectDrug,
  onOpenCompatibility,
  onOpenComparison,
  onOpenIndianPharma,
}) => {
  const recentDrugs = [
    {
      name: "Ibuprofen",
      formula: "C₁₃H₁₈O₂",
      therapeutic: "NSAID • Analgesic",
      evidence: "A" as const,
    },
    {
      name: "Paracetamol",
      formula: "C₈H₉NO₂",
      therapeutic: "Analgesic • Antipyretic",
      evidence: "A" as const,
    },
    {
      name: "Amoxicillin",
      formula: "C₁₆H₁₉N₃O₅S",
      therapeutic: "Antibacterial • Beta-lactam",
      evidence: "A" as const,
    },
    {
      name: "Azithromycin",
      formula: "C₃₈H₇₂N₂O₁₂",
      therapeutic: "Antibacterial • Macrolide",
      evidence: "A" as const,
    },
  ];

  const popularSearches = [
    { rank: 1, term: "Ibuprofen excipients", count: "1.2K searches" },
    { rank: 2, term: "Paracetamol dosage forms", count: "980 searches" },
    { rank: 3, term: "Amoxicillin Maillard lactose", count: "842 searches" },
    { rank: 4, term: "HPMC sustained release", count: "756 searches" },
    { rank: 5, term: "Azithromycin BCS Class II/IV", count: "692 searches" },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {/* 1. Recently Viewed Drugs */}
      <div className="p-4 rounded-xl bg-[#0c162f] border border-slate-800/80 flex flex-col justify-between shadow-sm">
        <div>
          <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Recently Viewed Drugs
            </h3>
            <span className="text-[11px] font-medium text-blue-400 hover:text-blue-300 cursor-pointer">
              View all →
            </span>
          </div>

          <div className="divide-y divide-slate-800/50 mt-1">
            {recentDrugs.map((d) => (
              <div
                key={d.name}
                onClick={() => onSelectDrug(d.name)}
                className="py-2.5 flex items-center justify-between group hover:bg-slate-800/30 px-2 rounded-lg cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-12 h-9 rounded-lg bg-slate-900/60 border border-slate-800/80 flex items-center justify-center p-1 shrink-0">
                    <ChemicalStructure name={d.name} width={40} height={26} />
                  </div>
                  <div className="text-left space-y-0.5">
                    <div className="text-sm font-semibold text-slate-100 group-hover:text-blue-400 transition-colors flex items-center gap-2">
                      <span>{d.name}</span>
                      <span className="text-[11px] font-mono font-normal text-slate-400">
                        {d.formula}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-400">{d.therapeutic}</div>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <EvidenceBadge level={d.evidence} showText={false} />
                  <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-slate-300 group-hover:translate-x-0.5 transition-all" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 2. Popular Searches */}
      <div className="p-4 rounded-xl bg-[#0c162f] border border-slate-800/80 flex flex-col justify-between shadow-sm">
        <div>
          <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
              <span>Popular Searches</span>
              <TrendingUp className="w-3.5 h-3.5 text-blue-400" />
            </h3>
            <span className="text-[11px] font-medium text-blue-400 hover:text-blue-300 cursor-pointer">
              View all →
            </span>
          </div>

          <div className="divide-y divide-slate-800/50 mt-1">
            {popularSearches.map((item) => (
              <div
                key={item.term}
                onClick={() => onSelectDrug(item.term.split(" ")[0])}
                className="py-2.5 flex items-center justify-between group hover:bg-slate-800/30 px-2 rounded-lg cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="w-5 h-5 rounded-md bg-slate-800/90 text-slate-400 font-bold text-xs flex items-center justify-center">
                    {item.rank}
                  </span>
                  <div className="text-left">
                    <div className="text-xs font-semibold text-slate-200 group-hover:text-blue-400 transition-colors">
                      {item.term}
                    </div>
                    <div className="text-[10px] text-slate-400">{item.count}</div>
                  </div>
                </div>
                <TrendingUp className="w-3.5 h-3.5 text-slate-500 group-hover:text-blue-400 transition-colors" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 3. Quick Actions */}
      <div className="p-4 rounded-xl bg-[#0c162f] border border-slate-800/80 flex flex-col justify-between shadow-sm">
        <div>
          <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Quick Actions
            </h3>
          </div>

          <div className="space-y-2 mt-2">
            <button
              onClick={onOpenComparison}
              className="w-full p-2.5 rounded-xl bg-[#111e3f] hover:bg-[#162752] border border-indigo-500/20 flex items-center justify-between transition-all group"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
                  <Scale className="w-4 h-4" />
                </div>
                <div className="text-left">
                  <div className="text-xs font-bold text-slate-100 group-hover:text-indigo-300">
                    Drug Comparison
                  </div>
                  <div className="text-[10px] text-slate-400">
                    Compare pKa, BCS & dosing
                  </div>
                </div>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-slate-300" />
            </button>

            <button
              onClick={onOpenCompatibility}
              className="w-full p-2.5 rounded-xl bg-[#111e3f] hover:bg-[#162752] border border-emerald-500/20 flex items-center justify-between transition-all group"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <div className="text-left">
                  <div className="text-xs font-bold text-slate-100 group-hover:text-emerald-300">
                    Compatibility Check
                  </div>
                  <div className="text-[10px] text-slate-400">
                    Check API ↔ Excipient interactions
                  </div>
                </div>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-slate-300" />
            </button>

            <button
              onClick={() => onSelectDrug("Ibuprofen")}
              className="w-full p-2.5 rounded-xl bg-[#111e3f] hover:bg-[#162752] border border-cyan-500/20 flex items-center justify-between transition-all group"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
                  <FlaskConical className="w-4 h-4" />
                </div>
                <div className="text-left">
                  <div className="text-xs font-bold text-slate-100 group-hover:text-cyan-300">
                    Formulation Builder
                  </div>
                  <div className="text-[10px] text-slate-400">
                    Solid dosage optimization
                  </div>
                </div>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-slate-300" />
            </button>

            <button
              onClick={onOpenIndianPharma}
              className="w-full p-2.5 rounded-xl bg-[#111e3f] hover:bg-[#162752] border border-amber-500/20 flex items-center justify-between transition-all group"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
                  <Flag className="w-4 h-4" />
                </div>
                <div className="text-left">
                  <div className="text-xs font-bold text-slate-100 group-hover:text-amber-300">
                    Indian Pharma Directory
                  </div>
                  <div className="text-[10px] text-slate-400">
                    CDSCO brands & manufacturers
                  </div>
                </div>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-slate-300" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
