import React from "react";
import {
  LayoutDashboard,
  Pill,
  FlaskRound as Flask,
  Beaker,
  ShieldCheck,
  BookOpen,
  Scale,
  Brain,
  Flag,
  ShieldAlert,
  Bot,
  Bookmark,
  Briefcase,
  Code2,
  Settings,
  HelpCircle,
  Database,
} from "lucide-react";

export type NavItem =
  | "dashboard"
  | "drugs"
  | "excipients"
  | "preformulation"
  | "compatibility"
  | "literature"
  | "comparison"
  | "formulation"
  | "indian_pharma"
  | "regulatory"
  | "ai_assistant";

interface SidebarProps {
  activeTab: NavItem;
  onSelectTab: (tab: NavItem) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
}) => {
  return (
    <aside className="w-64 bg-[#070d1d] border-r border-slate-800/80 flex flex-col justify-between h-screen sticky top-0 select-none overflow-y-auto">
      <div>
        {/* Brand Logo Header */}
        <div className="p-5 flex items-center gap-3 border-b border-slate-800/60">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 via-blue-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/20 text-white font-bold">
            <Pill className="w-5 h-5 -rotate-45" />
          </div>
          <div>
            <div className="font-extrabold text-lg text-white tracking-tight leading-none flex items-center gap-1">
              Drug<span className="text-blue-400">Lab</span>
            </div>
            <div className="text-[10px] text-slate-400 font-medium tracking-wide mt-1">
              Smarter Research, Better Medicines.
            </div>
          </div>
        </div>

        {/* Navigation Categories */}
        <div className="px-3 py-4 space-y-6">
          {/* Main Dashboard item */}
          <div>
            <button
              onClick={() => onSelectTab("dashboard")}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                activeTab === "dashboard"
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-600/30"
                  : "text-slate-300 hover:text-white hover:bg-slate-800/50"
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>Dashboard</span>
            </button>
          </div>

          {/* Section: DRUG INFORMATION LIBRARY */}
          <div>
            <div className="px-3 mb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Drug Information Library
            </div>
            <nav className="space-y-1">
              <button
                onClick={() => onSelectTab("drugs")}
                className={`w-full flex items-center gap-3 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
                  activeTab === "drugs"
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                }`}
              >
                <Pill className="w-4 h-4" />
                <span>Drugs Catalog</span>
              </button>

              <button
                onClick={() => onSelectTab("excipients")}
                className={`w-full flex items-center gap-3 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
                  activeTab === "excipients"
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                }`}
              >
                <Flask className="w-4 h-4" />
                <span>Excipient Library</span>
              </button>

              <button
                onClick={() => onSelectTab("preformulation")}
                className={`w-full flex items-center gap-3 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
                  activeTab === "preformulation"
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                }`}
              >
                <Beaker className="w-4 h-4" />
                <span>Preformulation</span>
              </button>

              <button
                onClick={() => onSelectTab("compatibility")}
                className={`w-full flex items-center gap-3 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
                  activeTab === "compatibility"
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                }`}
              >
                <ShieldCheck className="w-4 h-4" />
                <span>Compatibility</span>
              </button>

              <button
                onClick={() => onSelectTab("literature")}
                className={`w-full flex items-center gap-3 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
                  activeTab === "literature"
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                }`}
              >
                <BookOpen className="w-4 h-4" />
                <span>Literature & Evidence</span>
              </button>

              <button
                onClick={() => onSelectTab("comparison")}
                className={`w-full flex items-center gap-3 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
                  activeTab === "comparison"
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                }`}
              >
                <Scale className="w-4 h-4" />
                <span>Drug Comparison</span>
              </button>
            </nav>
          </div>

          {/* Section: PHARMACEUTICAL R&D PLATFORM */}
          <div>
            <div className="px-3 mb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Pharmaceutical R&D Platform
            </div>
            <nav className="space-y-1">
              <button
                onClick={() => onSelectTab("formulation")}
                className={`w-full flex items-center gap-3 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
                  activeTab === "formulation"
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                }`}
              >
                <Brain className="w-4 h-4" />
                <span>Formulation Intelligence</span>
              </button>

              <button
                onClick={() => onSelectTab("indian_pharma")}
                className={`w-full flex items-center gap-3 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
                  activeTab === "indian_pharma"
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                }`}
              >
                <Flag className="w-4 h-4 text-orange-400" />
                <span>Indian Pharma</span>
              </button>

              <button
                onClick={() => onSelectTab("regulatory")}
                className={`w-full flex items-center gap-3 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
                  activeTab === "regulatory"
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                }`}
              >
                <ShieldAlert className="w-4 h-4" />
                <span>Safety & Regulatory</span>
              </button>

              <button
                onClick={() => onSelectTab("ai_assistant")}
                className={`w-full flex items-center gap-3 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
                  activeTab === "ai_assistant"
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                }`}
              >
                <Bot className="w-4 h-4 text-cyan-400" />
                <span>Pharma AI Assistant</span>
              </button>
            </nav>
          </div>

          {/* Section: TOOLS & RESOURCES */}
          <div>
            <div className="px-3 mb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Tools & Resources
            </div>
            <nav className="space-y-1">
              <div className="flex items-center gap-3 px-3.5 py-2 text-xs text-slate-400 hover:text-slate-200 cursor-pointer">
                <Bookmark className="w-4 h-4" />
                <span>Saved Items</span>
              </div>
              <div className="flex items-center gap-3 px-3.5 py-2 text-xs text-slate-400 hover:text-slate-200 cursor-pointer">
                <Briefcase className="w-4 h-4" />
                <span>My Workspace</span>
              </div>
              <a
                href="/docs"
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-3 px-3.5 py-2 text-xs text-slate-400 hover:text-slate-200 cursor-pointer"
              >
                <Code2 className="w-4 h-4" />
                <span>API Access (Swagger)</span>
              </a>
            </nav>
          </div>
        </div>
      </div>

      {/* Footer Branding & Kaggle Badge */}
      <div className="p-4 border-t border-slate-800/80 space-y-3">
        <div className="flex items-center justify-between text-xs text-slate-400 px-1">
          <div className="flex items-center gap-2 hover:text-slate-200 cursor-pointer">
            <Settings className="w-3.5 h-3.5" />
            <span>Settings</span>
          </div>
          <div className="flex items-center gap-2 hover:text-slate-200 cursor-pointer">
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Help</span>
          </div>
        </div>

        <div className="p-2.5 rounded-xl bg-gradient-to-r from-blue-950/50 to-slate-900 border border-slate-800/80 flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-cyan-600/20 text-cyan-400 flex items-center justify-center font-bold text-xs">
            K
          </div>
          <div>
            <div className="text-[11px] font-bold text-slate-200">
              Powered by Kaggle
            </div>
            <div className="text-[9px] text-slate-400">
              Datasets • Notebooks • ML Models
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};
