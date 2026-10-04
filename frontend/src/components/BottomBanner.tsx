import React from "react";
import { Sparkles, ArrowRight } from "lucide-react";

interface Props {
  onOpenAI: () => void;
}

export const BottomBanner: React.FC<Props> = ({ onOpenAI }) => {
  return (
    <div className="rounded-2xl p-5 bg-gradient-to-r from-blue-900/60 via-indigo-950/70 to-blue-950/80 border border-blue-500/30 flex flex-col md:flex-row items-center justify-between gap-4 shadow-xl">
      <div className="flex items-center gap-4 text-left">
        <div className="w-12 h-12 rounded-xl bg-blue-600/20 text-blue-400 flex items-center justify-center shrink-0 border border-blue-500/30 shadow-inner">
          <Sparkles className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <div className="text-sm font-extrabold text-white">
            Accelerate Your Research with DrugLab AI
          </div>
          <div className="text-xs text-slate-300 mt-0.5">
            Get evidence-based answers, drug insights, and formulation recommendations — powered by Kaggle data and advanced AI.
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4 shrink-0">
        <button
          onClick={onOpenAI}
          className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-lg shadow-blue-600/30 transition-all flex items-center gap-2"
        >
          <span>Try DrugLab AI</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>

        <div className="hidden sm:flex items-center gap-1.5 text-[11px] text-slate-400 font-mono">
          <span>Science</span>
          <span>•</span>
          <span>Data</span>
          <span>•</span>
          <span>Better Health</span>
        </div>
      </div>
    </div>
  );
};
