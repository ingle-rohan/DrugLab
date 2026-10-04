import React, { useState } from "react";
import {
  Bot,
  Send,
  Sparkles,
  ShieldCheck,
  ExternalLink,
  Loader2,
  AlertCircle,
  HelpCircle,
} from "lucide-react";
import { queryRAG } from "../services/api";
import { RAGResponse } from "../types";
import { EvidenceBadge } from "./EvidenceBadge";

interface Props {
  initialPrompt?: string;
}

const SAMPLE_PROMPTS = [
  "Which excipients are suitable for ibuprofen tablets?",
  "What happens if amoxicillin is formulated with lactose?",
  "What is the BCS classification and maximum dose of paracetamol?",
  "Tell me about Azithromycin dihydrate pKa and stability.",
];

export const DrugLabAIAssistant: React.FC<Props> = ({ initialPrompt = "" }) => {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<RAGResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAsk = async (textToQuery?: string) => {
    const q = textToQuery || prompt;
    if (!q.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const data = await queryRAG(q.trim());
      setResponse(data);
    } catch (err: any) {
      setError(err.message || "Failed to query DrugLab AI");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 rounded-xl bg-[#0c162f] border border-slate-800/80 text-left shadow-sm flex flex-col h-[520px]">
      {/* Header */}
      <div className="pb-3 border-b border-slate-800/60 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-blue-600/20 text-blue-400 flex items-center justify-center">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-white flex items-center gap-1.5">
              <span>DrugLab AI Assistant</span>
              <span className="flex items-center gap-1 text-[9px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.2 rounded font-semibold border border-emerald-500/20">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Online
              </span>
            </div>
            <div className="text-[10px] text-slate-400">RAG Provenance Engine</div>
          </div>
        </div>
      </div>

      {/* Message Output Area */}
      <div className="flex-1 overflow-y-auto py-3 space-y-3 pr-1 text-xs">
        {!response && !loading && (
          <div className="space-y-3">
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-slate-300 text-xs leading-relaxed">
              Hello! I'm <strong>DrugLab AI</strong>, your verified pharmaceutical research assistant. Ask me anything about APIs, excipient compatibility, BCS classifications, or dosage guidelines.
            </div>

            <div className="space-y-1.5">
              <div className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-cyan-400" />
                <span>Try asking:</span>
              </div>
              <div className="space-y-1.5">
                {SAMPLE_PROMPTS.map((p) => (
                  <button
                    key={p}
                    onClick={() => {
                      setPrompt(p);
                      handleAsk(p);
                    }}
                    className="w-full text-left p-2 rounded-lg bg-slate-900/40 hover:bg-blue-600/10 hover:border-blue-500/30 border border-slate-800 text-slate-300 hover:text-blue-300 transition-all text-[11px] leading-snug"
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center py-12 space-y-2 text-slate-400">
            <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
            <div className="text-xs font-medium">Synthesizing verified claims with pgvector...</div>
          </div>
        )}

        {error && (
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-start gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {response && !loading && (
          <div className="space-y-3">
            {/* User query indicator */}
            <div className="text-[11px] font-semibold text-blue-400 bg-blue-500/10 p-2 rounded-lg border border-blue-500/20">
              Q: {response.query}
            </div>

            {/* Structured Claims List */}
            <div className="space-y-2">
              <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                Verified Provenance Claims:
              </div>
              {response.claims.map((claim, idx) => (
                <div
                  key={idx}
                  className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-left space-y-1"
                >
                  <div className="flex items-center justify-between gap-1.5">
                    <EvidenceBadge level={claim.evidence_level} />
                    {claim.dispute_flag && (
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 font-bold">
                        DISPUTED
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-200 leading-snug">
                    {claim.statement}
                  </p>
                  <div className="text-[10px] text-slate-400 pt-0.5 flex items-center justify-between">
                    <span>Source: {claim.source_name}</span>
                    {claim.source_url && (
                      <a
                        href={claim.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-blue-400 hover:text-blue-300 inline-flex items-center gap-0.5"
                      >
                        <ExternalLink className="w-2.5 h-2.5" />
                        <span>Link</span>
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Literature Matches */}
            {response.literature_citations.length > 0 && (
              <div className="space-y-1.5 pt-1">
                <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  Literature Vector Matches:
                </div>
                {response.literature_citations.map((hit, idx) => (
                  <div
                    key={idx}
                    className="p-2 rounded bg-slate-900/50 border border-slate-800/80 text-[11px] space-y-0.5"
                  >
                    <div className="font-semibold text-slate-200 line-clamp-1">
                      {hit.reference.title}
                    </div>
                    <div className="text-slate-400 flex items-center justify-between text-[10px]">
                      <span>{hit.reference.journal}</span>
                      <span className="text-blue-400 font-mono">
                        Cosine Sim: {hit.cosine_similarity.toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input box */}
      <div className="pt-2 border-t border-slate-800/60 shrink-0">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAsk();
          }}
          className="relative flex items-center"
        >
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ask a question..."
            className="w-full bg-[#121c38] text-slate-100 placeholder-slate-400 text-xs pl-3 pr-10 py-2.5 rounded-xl border border-slate-700/60 focus:outline-none focus:border-blue-500 transition-all"
          />
          <button
            type="submit"
            disabled={loading || !prompt.trim()}
            className="absolute right-2 p-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg transition-colors shadow-sm"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
};
