import React from "react";
import { EvidenceLevel } from "../types";

interface Props {
  level: EvidenceLevel;
  showText?: boolean;
}

const LEVEL_STYLES: Record<
  EvidenceLevel,
  { bg: string; text: string; border: string; label: string; dot: string }
> = {
  A: {
    bg: "bg-emerald-500/10",
    text: "text-emerald-400",
    border: "border-emerald-500/30",
    label: "Level A • Regulatory",
    dot: "bg-emerald-400",
  },
  B: {
    bg: "bg-blue-500/10",
    text: "text-blue-400",
    border: "border-blue-500/30",
    label: "Level B • Primary Research",
    dot: "bg-blue-400",
  },
  C: {
    bg: "bg-amber-500/10",
    text: "text-amber-400",
    border: "border-amber-500/30",
    label: "Level C • Authority DB",
    dot: "bg-amber-400",
  },
  D: {
    bg: "bg-purple-500/10",
    text: "text-purple-400",
    border: "border-purple-500/30",
    label: "Level D • Secondary Source",
    dot: "bg-purple-400",
  },
  E: {
    bg: "bg-rose-500/10",
    text: "text-rose-400",
    border: "border-rose-500/30",
    label: "Level E • Commercial Listing",
    dot: "bg-rose-400",
  },
};

export const EvidenceBadge: React.FC<Props> = ({ level, showText = true }) => {
  const config = LEVEL_STYLES[level] || LEVEL_STYLES.C;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium border ${config.bg} ${config.text} ${config.border}`}
      title={config.label}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
      {showText ? (
        <span>
          <strong className="font-semibold">[{level}]</strong> {config.label.split("•")[1]?.trim()}
        </span>
      ) : (
        <strong>[{level}]</strong>
      )}
    </span>
  );
};
