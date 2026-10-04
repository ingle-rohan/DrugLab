import React from "react";
import {
  ShieldCheck,
  FileCheck2,
  Sparkles,
  RefreshCw,
  Search,
  ArrowRight,
  Atom,
} from "lucide-react";
import { MoleculeHeroGraphic } from "./MoleculeHeroGraphic";

interface HeroSectionProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onSearchSubmit: () => void;
  onSelectChip: (term: string) => void;
}

const CHIPS = [
  "Ibuprofen",
  "Paracetamol",
  "Amoxicillin",
  "Azithromycin",
  "Lactose",
  "HPMC",
  "Formulation BCS II",
  "Magnesium Stearate",
];

export const HeroSection: React.FC<HeroSectionProps> = ({
  searchQuery,
  onSearchChange,
  onSearchSubmit,
  onSelectChip,
}) => {
  return (
    <div className="space-y-4">
      {/* Dynamic Gradient Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#0d1a38] via-[#102450] to-[#0c1836] border border-blue-500/20 p-7 shadow-xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 right-32 w-64 h-64 bg-cyan-500/10 rounded-full blur-2xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="max-w-xl space-y-3 text-left">
            <div className="text-xs font-semibold text-blue-400 flex items-center gap-1.5">
              <span>Welcome back, Shubham</span>
              <span>👋</span>
            </div>

            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight leading-tight">
              Your Pharmaceutical{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-300 to-indigo-300">
                Research Companion
              </span>
            </h1>

            <p className="text-xs md:text-sm text-slate-300 font-normal leading-relaxed">
              Explore, analyze and build better medicines with verified compendial data,
              multi-parameter preformulation profiles, and AI-driven compatibility intelligence.
            </p>

            {/* Verification Pills */}
            <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] font-medium text-slate-300">
              <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900/60 border border-slate-700/60 text-cyan-300">
                <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                Trusted Sources
              </span>
              <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900/60 border border-slate-700/60 text-emerald-300">
                <FileCheck2 className="w-3.5 h-3.5 text-emerald-400" />
                Evidence-Based (A-E)
              </span>
              <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900/60 border border-slate-700/60 text-indigo-300">
                <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                AI-Powered RAG
              </span>
              <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900/60 border border-slate-700/60 text-slate-300">
                <RefreshCw className="w-3.5 h-3.5 text-blue-400" />
                Always Up-to-Date
              </span>
            </div>
          </div>

          {/* Right Quote Callout & Graphic */}
          <div className="hidden lg:flex items-center gap-2">
            <MoleculeHeroGraphic />
            <div className="flex flex-col items-end text-right p-4 rounded-xl bg-slate-900/40 border border-slate-800/80 backdrop-blur-sm max-w-[200px]">
              <div className="w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center mb-2 shadow-inner">
                <Atom className="w-5 h-5 animate-spin-slow" />
              </div>
              <div className="text-[11px] font-semibold text-slate-200 italic leading-snug">
                "Better information. Faster decisions. Healthier tomorrows."
              </div>
              <div className="text-[9px] text-blue-400/80 mt-1 font-medium">
                DrugLab Core v1.0
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Search Bar Card */}
      <div className="p-4 rounded-2xl bg-[#0d162d] border border-slate-800/90 shadow-lg space-y-3">
        <div className="flex items-center gap-3">
          <div className="flex-1 relative flex items-center">
            <Search className="w-5 h-5 text-slate-400 absolute left-4 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && onSearchSubmit()}
              placeholder="Search for drugs, excipients, formulations, CAS numbers, or ask DrugLab AI..."
              className="w-full bg-[#121c38] text-slate-100 placeholder-slate-400 text-sm pl-12 pr-4 py-3 rounded-xl border border-slate-700/70 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
            />
          </div>
          <button
            onClick={onSearchSubmit}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-sm font-semibold shadow-lg shadow-blue-600/30 transition-all flex items-center gap-2"
          >
            <span>Search</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        {/* Popular chips */}
        <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400 pt-1">
          <span className="text-[11px] font-semibold text-slate-500 mr-1">
            Quick Lookup:
          </span>
          {CHIPS.map((chip) => (
            <button
              key={chip}
              onClick={() => onSelectChip(chip)}
              className="px-2.5 py-1 rounded-lg bg-slate-800/60 hover:bg-blue-600/20 hover:text-blue-300 text-slate-300 border border-slate-700/50 transition-colors text-xs font-medium"
            >
              {chip}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
