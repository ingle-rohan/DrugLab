import React, { useEffect, useRef } from "react";
import {
  Search,
  Bell,
  Sun,
  Moon,
  Sparkles,
  Command,
} from "lucide-react";

interface HeaderProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onSearchSubmit: () => void;
  darkMode: boolean;
  onToggleTheme: () => void;
  onOpenAI: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  searchQuery,
  onSearchChange,
  onSearchSubmit,
  darkMode,
  onToggleTheme,
  onOpenAI,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handleGlobalKeyDown);
    return () => window.removeEventListener("keydown", handleGlobalKeyDown);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      onSearchSubmit();
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full h-16 bg-[#080e1e]/95 backdrop-blur border-b border-slate-800/80 px-6 flex items-center justify-between">
      {/* Search Input Bar */}
      <div className="flex-1 max-w-2xl relative">
        <div className="relative flex items-center">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 pointer-events-none" />
          <input
            ref={inputRef}
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search drugs, CAS, excipients, formulations, or ask DrugLab AI..."
            className="w-full bg-[#0d162d] text-slate-100 placeholder-slate-400 text-sm pl-10 pr-24 py-2 rounded-xl border border-slate-700/60 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all shadow-inner"
          />
          <div
            onClick={() => inputRef.current?.focus()}
            className="absolute right-3 flex items-center gap-1.5 text-xs text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700/50 cursor-pointer hover:text-slate-200"
          >
            <Command className="w-3 h-3" />
            <span>K</span>
          </div>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-4 ml-6">
        <button
          onClick={onOpenAI}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-blue-500/20 transition-all"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Ask AI</span>
        </button>

        <div className="relative">
          <button className="p-2 text-slate-400 hover:text-slate-200 bg-slate-800/40 hover:bg-slate-800/80 rounded-lg transition-colors border border-slate-700/40 relative">
            <Bell className="w-4 h-4" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-rose-500 rounded-full" />
          </button>
        </div>

        <button
          onClick={onToggleTheme}
          className="p-2 text-slate-400 hover:text-slate-200 bg-slate-800/40 hover:bg-slate-800/80 rounded-lg transition-colors border border-slate-700/40"
          title="Toggle light/dark theme"
        >
          {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* User Avatar */}
        <div className="flex items-center gap-3 pl-3 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center font-bold text-xs text-white shadow-md">
            SK
          </div>
          <div className="hidden lg:block text-left">
            <div className="text-xs font-semibold text-slate-200">
              Shubham Kharate
            </div>
            <div className="text-[10px] text-slate-400 font-medium">Researcher</div>
          </div>
        </div>
      </div>
    </header>
  );
};
