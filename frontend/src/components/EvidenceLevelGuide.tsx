import React from "react";

export const EvidenceLevelGuide: React.FC = () => {
  const levels = [
    {
      level: "A",
      dot: "bg-emerald-400",
      title: "High Evidence (Level A)",
      desc: "Verified regulatory, pharmacopoeial, or statutory monograph (FDA, USP, IP, WHO).",
    },
    {
      level: "B",
      dot: "bg-blue-400",
      title: "Medium Evidence (Level B)",
      desc: "Peer-reviewed primary research or validated laboratory study.",
    },
    {
      level: "C",
      dot: "bg-amber-400",
      title: "Authority DB (Level C)",
      desc: "Curated chemical / biological databases (PubChem, ChEMBL).",
    },
    {
      level: "D",
      dot: "bg-purple-400",
      title: "Low Evidence (Level D)",
      desc: "Secondary review literature or compendium textbook.",
    },
    {
      level: "E",
      dot: "bg-rose-400",
      title: "Experimental / Directory (Level E)",
      desc: "Commercial directory listing, unverified supplier datum, or thesis.",
    },
  ];

  return (
    <div className="p-4 rounded-xl bg-[#0c162f] border border-slate-800/80 text-left shadow-sm">
      <div className="pb-2.5 mb-3 border-b border-slate-800/60 flex items-center justify-between">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
          Evidence Level Guide
        </h3>
        <span className="text-[10px] text-slate-500 font-mono">STRICT PROVENANCE</span>
      </div>

      <div className="space-y-2.5 text-xs">
        {levels.map((item) => (
          <div key={item.level} className="flex items-start gap-2.5">
            <span
              className={`w-2 h-2 rounded-full ${item.dot} mt-1 shrink-0 shadow-sm`}
            />
            <div>
              <div className="text-xs font-semibold text-slate-200">
                {item.title}
              </div>
              <div className="text-[10px] text-slate-400 leading-snug">
                {item.desc}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
