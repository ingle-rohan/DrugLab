import React from "react";
import { Pill, FlaskRound as Flask, FileText, BookOpen, ArrowUpRight } from "lucide-react";

export const StatCards: React.FC = () => {
  const stats = [
    {
      label: "Total Drugs",
      value: "12,540",
      change: "+ 12%",
      changePeriod: "vs. last month",
      icon: Pill,
      iconColor: "text-blue-400",
      iconBg: "bg-blue-500/10 border-blue-500/20",
    },
    {
      label: "Excipient Records",
      value: "1,280",
      change: "+ 8%",
      changePeriod: "vs. last month",
      icon: Flask,
      iconColor: "text-emerald-400",
      iconBg: "bg-emerald-500/10 border-emerald-500/20",
    },
    {
      label: "Evidence Records",
      value: "8,420",
      change: "+ 15%",
      changePeriod: "vs. last month",
      icon: FileText,
      iconColor: "text-purple-400",
      iconBg: "bg-purple-500/10 border-purple-500/20",
    },
    {
      label: "Literature Sources",
      value: "3,210",
      change: "+ 10%",
      changePeriod: "vs. last month",
      icon: BookOpen,
      iconColor: "text-amber-400",
      iconBg: "bg-amber-500/10 border-amber-500/20",
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((s) => {
        const Icon = s.icon;
        return (
          <div
            key={s.label}
            className="p-4 rounded-xl bg-[#0c162f] border border-slate-800/80 hover:border-slate-700 transition-all flex items-start gap-4 shadow-sm"
          >
            <div
              className={`p-3 rounded-xl border flex items-center justify-center shrink-0 ${s.iconBg}`}
            >
              <Icon className={`w-5 h-5 ${s.iconColor}`} />
            </div>

            <div className="space-y-1 text-left">
              <div className="text-xl font-extrabold text-white tracking-tight">
                {s.value}
              </div>
              <div className="text-xs font-medium text-slate-400">{s.label}</div>
              <div className="flex items-center gap-1 text-[11px] font-semibold text-emerald-400 pt-0.5">
                <ArrowUpRight className="w-3 h-3" />
                <span>{s.change}</span>
                <span className="text-[10px] text-slate-400 font-normal">
                  {s.changePeriod}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
