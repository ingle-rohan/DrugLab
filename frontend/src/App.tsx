import React, { useState, useEffect } from "react";
import { Sidebar, NavItem } from "./components/Sidebar";
import { Header } from "./components/Header";
import { HeroSection } from "./components/HeroSection";
import { StatCards } from "./components/StatCards";
import { MidSectionGrid } from "./components/MidSectionGrid";
import { LowerInsightsGrid } from "./components/LowerInsightsGrid";
import { DrugLabAIAssistant } from "./components/DrugLabAIAssistant";
import { EvidenceLevelGuide } from "./components/EvidenceLevelGuide";
import { IndianPharmaSpotlight } from "./components/IndianPharmaSpotlight";
import { BottomBanner } from "./components/BottomBanner";
import { DrugProfileModal } from "./components/DrugProfileModal";
import { CompatibilityCheckerModal } from "./components/CompatibilityCheckerModal";
import { searchDrugs, listExcipients } from "./services/api";
import { DrugSummary, ExcipientRead } from "./types";
import { EvidenceBadge } from "./components/EvidenceBadge";
import { Pill, FlaskRound as Flask, Search, ChevronRight } from "lucide-react";

export function App() {
  const [activeTab, setActiveTab] = useState<NavItem>("dashboard");
  const [searchQuery, setSearchQuery] = useState("");
  const [darkMode, setDarkMode] = useState(true);

  // Modals state
  const [selectedDrug, setSelectedDrug] = useState<string | null>(null);
  const [isCompatModalOpen, setIsCompatModalOpen] = useState(false);

  // Drugs & Excipients catalog state for secondary tabs
  const [catalogDrugs, setCatalogDrugs] = useState<DrugSummary[]>([]);
  const [catalogExcipients, setCatalogExcipients] = useState<ExcipientRead[]>([]);
  const [catalogLoading, setCatalogLoading] = useState(false);

  useEffect(() => {
    if (activeTab === "drugs") {
      setCatalogLoading(true);
      searchDrugs(searchQuery)
        .then((res) => setCatalogDrugs(res.items))
        .finally(() => setCatalogLoading(false));
    } else if (activeTab === "excipients") {
      setCatalogLoading(true);
      listExcipients(searchQuery)
        .then((res) => setCatalogExcipients(res.items))
        .finally(() => setCatalogLoading(false));
    }
  }, [activeTab, searchQuery]);

  const handleGlobalSearch = () => {
    if (!searchQuery.trim()) return;
    // Check if the search matches a drug directly
    setSelectedDrug(searchQuery.trim());
  };

  return (
    <div className="flex min-h-screen bg-[#070e1e] text-slate-100 font-sans">
      {/* 1. Left Navigation Sidebar */}
      <Sidebar activeTab={activeTab} onSelectTab={setActiveTab} />

      {/* 2. Main Body Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onSearchSubmit={handleGlobalSearch}
          darkMode={darkMode}
          onToggleTheme={() => setDarkMode(!darkMode)}
          onOpenAI={() => {
            const el = document.getElementById("ai-assistant-widget");
            el?.scrollIntoView({ behavior: "smooth" });
          }}
        />

        <main className="flex-1 p-6 overflow-y-auto">
          {activeTab === "dashboard" && (
            <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 max-w-[1600px] mx-auto">
              {/* Primary 8-col Center Feed */}
              <div className="xl:col-span-8 space-y-6">
                <HeroSection
                  searchQuery={searchQuery}
                  onSearchChange={setSearchQuery}
                  onSearchSubmit={handleGlobalSearch}
                  onSelectChip={(term) => setSelectedDrug(term)}
                />

                <StatCards />

                <MidSectionGrid
                  onSelectDrug={(name) => setSelectedDrug(name)}
                  onOpenCompatibility={() => setIsCompatModalOpen(true)}
                  onOpenComparison={() => setSelectedDrug("Ibuprofen")}
                  onOpenIndianPharma={() => setSelectedDrug("Amoxicillin")}
                />

                <LowerInsightsGrid
                  onOpenCompatibility={() => setIsCompatModalOpen(true)}
                  onSelectDrug={(name) => setSelectedDrug(name)}
                />

                <BottomBanner
                  onOpenAI={() => {
                    const el = document.getElementById("ai-assistant-widget");
                    el?.scrollIntoView({ behavior: "smooth" });
                  }}
                />
              </div>

              {/* Secondary 4-col Right Rail */}
              <div className="xl:col-span-4 space-y-6" id="ai-assistant-widget">
                <DrugLabAIAssistant />
                <EvidenceLevelGuide />
                <IndianPharmaSpotlight
                  onOpenIndianPharma={() => setSelectedDrug("Amoxicillin")}
                />
              </div>
            </div>
          )}

          {/* DRUGS CATALOG TAB */}
          {activeTab === "drugs" && (
            <div className="max-w-6xl mx-auto space-y-4 text-left">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div>
                  <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
                    <Pill className="w-5 h-5 text-blue-400" />
                    <span>Verified Pharmaceutical API Catalog</span>
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">
                    Source-linked active pharmaceutical ingredients with CAS, ATC, and pKa profiles.
                  </p>
                </div>
                <div className="text-xs text-slate-400">
                  Total Records: <strong>{catalogDrugs.length}</strong>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {catalogDrugs.map((d) => (
                  <div
                    key={d.id}
                    onClick={() => setSelectedDrug(d.generic_name)}
                    className="p-4 rounded-xl bg-[#0c162f] border border-slate-800/80 hover:border-blue-500/50 cursor-pointer transition-all space-y-2 group shadow-sm"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-base font-bold text-white group-hover:text-blue-400 transition-colors">
                        {d.generic_name} ({d.form_tag})
                      </span>
                      {d.identity_evidence_level && (
                        <EvidenceBadge level={d.identity_evidence_level} />
                      )}
                    </div>
                    <div className="text-xs text-slate-400">
                      {d.therapeutic_class || "Analgesic / Anti-inflammatory"}
                    </div>
                    <div className="flex items-center gap-4 text-xs font-mono text-slate-300 pt-1">
                      <span>Formula: {d.molecular_formula || "N/A"}</span>
                      <span>MW: {d.molecular_weight} g/mol</span>
                      <span>CAS: {d.cas_number}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* EXCIPIENTS TAB */}
          {activeTab === "excipients" && (
            <div className="max-w-6xl mx-auto space-y-4 text-left">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div>
                  <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
                    <Flask className="w-5 h-5 text-emerald-400" />
                    <span>Excipient Library & Functionality Standards</span>
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">
                    Compendial inactive ingredients, concentration ranges, and compatibility constraints.
                  </p>
                </div>
                <div className="text-xs text-slate-400">
                  Total Excipients: <strong>{catalogExcipients.length}</strong>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {catalogExcipients.map((e) => (
                  <div
                    key={e.id}
                    onClick={() => setIsCompatModalOpen(true)}
                    className="p-4 rounded-xl bg-[#0c162f] border border-slate-800/80 hover:border-emerald-500/50 cursor-pointer transition-all space-y-2 group shadow-sm"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-base font-bold text-white group-hover:text-emerald-400 transition-colors">
                        {e.name}
                      </span>
                      <EvidenceBadge level={e.evidence_level} />
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {e.functions.map((f) => (
                        <span
                          key={f}
                          className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-mono"
                        >
                          {f}
                        </span>
                      ))}
                    </div>
                    <p className="text-xs text-slate-300 leading-snug">
                      {e.applications}
                    </p>
                    <div className="text-[11px] text-slate-400 pt-1 flex items-center justify-between">
                      <span>
                        Typical Conc: {e.typical_conc_min_pct}% - {e.typical_conc_max_pct}% ({e.typical_conc_basis})
                      </span>
                      <span>CAS: {e.cas_number}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* OTHER TABS FALLBACK TO DASHBOARD OR SPECIFIC VIEWS */}
          {["preformulation", "compatibility", "literature", "comparison", "formulation", "indian_pharma", "regulatory", "ai_assistant"].includes(
            activeTab
          ) &&
            activeTab !== "dashboard" &&
            activeTab !== "drugs" &&
            activeTab !== "excipients" && (
              <div className="max-w-4xl mx-auto py-12 text-center space-y-4">
                <div className="text-lg font-bold text-white uppercase tracking-wider">
                  {activeTab.replace("_", " ")} Module Active
                </div>
                <p className="text-xs text-slate-400">
                  Select a drug to inspect detailed {activeTab.replace("_", " ")} datasets or click below.
                </p>
                <div className="flex items-center justify-center gap-3">
                  <button
                    onClick={() => setSelectedDrug("Ibuprofen")}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold"
                  >
                    Open Ibuprofen Profile
                  </button>
                  <button
                    onClick={() => setIsCompatModalOpen(true)}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold"
                  >
                    Open Compatibility Checker
                  </button>
                </div>
              </div>
            )}
        </main>
      </div>

      {/* Full Drug Profile Modal */}
      <DrugProfileModal
        drugNameOrId={selectedDrug}
        onClose={() => setSelectedDrug(null)}
      />

      {/* Interactive Compatibility Evaluator Modal */}
      <CompatibilityCheckerModal
        isOpen={isCompatModalOpen}
        onClose={() => setIsCompatModalOpen(false)}
      />
    </div>
  );
}

export default App;
