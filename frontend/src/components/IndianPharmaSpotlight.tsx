import React from "react";
import { Flag, ArrowRight, Building2, CheckCircle2 } from "lucide-react";

interface Props {
  onOpenIndianPharma: () => void;
}

export const IndianPharmaSpotlight: React.FC<Props> = ({ onOpenIndianPharma }) => {
  return (
    <div className="p-4 rounded-xl bg-[#0c162f] border border-slate-800/80 text-left shadow-sm">
      <div className="pb-2.5 mb-3 border-b border-slate-800/60 flex items-center justify-between">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
          <Flag className="w-3.5 h-3.5 text-orange-400" />
          <span>Indian Pharma Spotlight</span>
        </h3>
        <button
          onClick={onOpenIndianPharma}
          className="text-[11px] font-medium text-blue-400 hover:text-blue-300"
        >
          View all →
        </button>
      </div>

      <div className="p-3 rounded-xl bg-gradient-to-r from-orange-950/20 via-slate-900 to-slate-900 border border-orange-500/20 mb-3">
        <div className="flex items-center justify-between">
          <div className="text-base font-extrabold text-white flex items-center gap-1.5">
            <span>Cipla</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400 inline" />
          </div>
          <span className="text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
            Market Cap: ₹1.2T
          </span>
        </div>
        <p className="text-[11px] text-slate-400 mt-1 leading-snug">
          Leading Indian multinational pharmaceutical company with certified WHO-GMP and US FDA approved facilities. Key brands include Novamox and Azee.
        </p>
      </div>

      <div className="grid grid-cols-3 gap-2 text-center text-xs">
        <div className="p-2 rounded-lg bg-slate-900/60 border border-slate-800">
          <div className="font-extrabold text-sm text-slate-100">250K+</div>
          <div className="text-[9px] text-slate-400 uppercase mt-0.5 font-medium">
            Products
          </div>
        </div>
        <div className="p-2 rounded-lg bg-slate-900/60 border border-slate-800">
          <div className="font-extrabold text-sm text-slate-100">1.8K+</div>
          <div className="text-[9px] text-slate-400 uppercase mt-0.5 font-medium">
            Manufacturers
          </div>
        </div>
        <div className="p-2 rounded-lg bg-slate-900/60 border border-slate-800">
          <div className="font-extrabold text-sm text-slate-100">12K+</div>
          <div className="text-[9px] text-slate-400 uppercase mt-0.5 font-medium">
            Brands
          </div>
        </div>
      </div>
    </div>
  );
};
