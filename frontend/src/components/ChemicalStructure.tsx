import React from "react";

interface ChemicalStructureProps {
  name: string;
  className?: string;
  width?: number;
  height?: number;
}

/**
 * Skeletal Chemical Structures for key pharmaceutical APIs
 * Clean, high-contrast SVG representations matching the blueprint line drawings.
 */
export const ChemicalStructure: React.FC<ChemicalStructureProps> = ({
  name,
  className = "text-slate-400 group-hover:text-blue-400 transition-colors",
  width = 64,
  height = 42,
}) => {
  const normalized = name.toLowerCase().trim();

  // Ibuprofen (2-(4-(2-methylpropyl)phenyl)propanoic acid)
  // Isobutyl group -- Phenyl ring -- CH(CH3)-COOH
  if (normalized.includes("ibuprofen")) {
    return (
      <svg
        viewBox="0 0 100 50"
        width={width}
        height={height}
        className={className}
        fill="none"
        stroke="currentColor"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {/* Isobutyl tail */}
        <line x1="6" y1="12" x2="16" y2="24" />
        <line x1="6" y1="36" x2="16" y2="24" />
        <line x1="16" y1="24" x2="28" y2="24" />

        {/* Benzene ring */}
        <polygon points="28,24 35,13 49,13 56,24 49,35 35,35" />
        {/* Inner double bonds */}
        <line x1="36" y1="17" x2="48" y2="17" strokeWidth="1.5" />
        <line x1="53" y1="24" x2="48" y2="32" strokeWidth="1.5" />
        <line x1="37" y1="32" x2="31" y2="24" strokeWidth="1.5" />

        {/* Propionic acid head */}
        <line x1="56" y1="24" x2="68" y2="24" />
        <line x1="68" y1="24" x2="74" y2="35" /> {/* Methyl */}
        <line x1="68" y1="24" x2="78" y2="13" /> {/* Carbonyl branch */}
        <line x1="77" y1="11" x2="88" y2="11" /> {/* C=O double bond */}
        <line x1="78" y1="14" x2="88" y2="14" />
        <line x1="78" y1="13" x2="85" y2="24" /> {/* -OH */}
        <text
          x="88"
          y="27"
          fill="currentColor"
          fontSize="8"
          stroke="none"
          fontFamily="sans-serif"
          fontWeight="bold"
        >
          OH
        </text>
      </svg>
    );
  }

  // Paracetamol (N-(4-hydroxyphenyl)acetamide)
  // HO-Phenyl-NH-CO-CH3
  if (normalized.includes("paracetamol") || normalized.includes("acetaminophen")) {
    return (
      <svg
        viewBox="0 0 95 48"
        width={width}
        height={height}
        className={className}
        fill="none"
        stroke="currentColor"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {/* HO- */}
        <text
          x="2"
          y="28"
          fill="currentColor"
          fontSize="8"
          stroke="none"
          fontFamily="sans-serif"
          fontWeight="bold"
        >
          HO
        </text>
        <line x1="16" y1="24" x2="26" y2="24" />

        {/* Phenyl ring */}
        <polygon points="26,24 33,13 47,13 54,24 47,35 33,35" />
        <line x1="34" y1="17" x2="46" y2="17" strokeWidth="1.5" />
        <line x1="51" y1="24" x2="46" y2="32" strokeWidth="1.5" />
        <line x1="35" y1="32" x2="29" y2="24" strokeWidth="1.5" />

        {/* -NH-COCH3 */}
        <line x1="54" y1="24" x2="62" y2="24" />
        <text
          x="63"
          y="27"
          fill="currentColor"
          fontSize="7"
          stroke="none"
          fontFamily="sans-serif"
          fontWeight="bold"
        >
          NH
        </text>
        <line x1="76" y1="24" x2="84" y2="17" />
        <line x1="84" y1="17" x2="94" y2="23" /> {/* methyl */}
        <line x1="82" y1="17" x2="82" y2="6" strokeWidth="1.5" /> {/* =O */}
        <line x1="85" y1="17" x2="85" y2="6" strokeWidth="1.5" />
        <text
          x="80"
          y="6"
          fill="currentColor"
          fontSize="7"
          stroke="none"
          fontFamily="sans-serif"
          fontWeight="bold"
        >
          O
        </text>
      </svg>
    );
  }

  // Amoxicillin (Beta-lactam + Thiazolidine fused penam ring)
  if (normalized.includes("amoxicillin")) {
    return (
      <svg
        viewBox="0 0 100 50"
        width={width}
        height={height}
        className={className}
        fill="none"
        stroke="currentColor"
        strokeWidth="2.0"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {/* Hydroxyphenyl ring */}
        <polygon points="12,25 18,15 28,15 34,25 28,35 18,35" />
        <line x1="19" y1="19" x2="27" y2="19" strokeWidth="1.4" />
        <line x1="31" y1="25" x2="27" y2="32" strokeWidth="1.4" />

        {/* Linker to beta-lactam */}
        <line x1="34" y1="25" x2="42" y2="25" />
        <line x1="42" y1="25" x2="46" y2="17" />
        <line x1="46" y1="17" x2="55" y2="20" />

        {/* Penam core: 4-membered beta-lactam fused to 5-membered thiazolidine */}
        <rect x="55" y="16" width="14" height="14" rx="1" />
        <line x1="53" y1="23" x2="49" y2="23" strokeWidth="1.5" />
        <line x1="53" y1="20" x2="49" y2="20" strokeWidth="1.5" />

        {/* Thiazolidine ring */}
        <polygon points="69,16 80,18 84,28 75,32 69,30" />
        <text
          x="75"
          y="23"
          fill="currentColor"
          fontSize="7"
          stroke="none"
          fontFamily="sans-serif"
          fontWeight="bold"
        >
          S
        </text>

        {/* Carboxylic acid tail */}
        <line x1="75" y1="32" x2="83" y2="40" />
        <text
          x="84"
          y="44"
          fill="currentColor"
          fontSize="6"
          stroke="none"
          fontFamily="sans-serif"
          fontWeight="bold"
        >
          COOH
        </text>
      </svg>
    );
  }

  // Azithromycin (15-membered azalide ring)
  if (normalized.includes("azithromycin")) {
    return (
      <svg
        viewBox="0 0 100 50"
        width={width}
        height={height}
        className={className}
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {/* Large 15-membered macrocycle simplified */}
        <ellipse cx="46" cy="25" rx="26" ry="18" strokeDasharray="3 2" />
        <circle cx="28" cy="18" r="3" />
        <circle cx="64" cy="18" r="3" />
        <circle cx="56" cy="38" r="3" />
        <circle cx="36" cy="38" r="3" />

        {/* Cladinose and Desosamine sugar rings */}
        <circle cx="78" cy="15" r="9" />
        <circle cx="80" cy="36" r="8" />

        <text
          x="74"
          y="17"
          fill="currentColor"
          fontSize="6"
          stroke="none"
          fontFamily="sans-serif"
          fontWeight="bold"
        >
          NMe
        </text>
        <text
          x="42"
          y="28"
          fill="currentColor"
          fontSize="7"
          stroke="none"
          fontFamily="sans-serif"
          fontWeight="bold"
        >
          Macrolide
        </text>
      </svg>
    );
  }

  // Default fallback: Aspirin / General aromatic molecule
  return (
    <svg
      viewBox="0 0 80 45"
      width={width}
      height={height}
      className={className}
      fill="none"
      stroke="currentColor"
      strokeWidth="2.0"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polygon points="25,22 33,10 49,10 57,22 49,34 33,34" />
      <line x1="34" y1="14" x2="48" y2="14" strokeWidth="1.5" />
      <line x1="53" y1="22" x2="48" y2="30" strokeWidth="1.5" />
      <line x1="34" y1="30" x2="29" y2="22" strokeWidth="1.5" />
      <line x1="57" y1="22" x2="68" y2="22" />
      <line x1="68" y1="22" x2="74" y2="12" />
      <line x1="49" y1="34" x2="55" y2="42" />
    </svg>
  );
};
