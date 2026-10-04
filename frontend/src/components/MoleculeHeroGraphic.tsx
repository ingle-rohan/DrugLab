import React from "react";

export const MoleculeHeroGraphic: React.FC = () => {
  return (
    <div className="relative w-72 h-44 pointer-events-none select-none">
      <svg
        viewBox="0 0 280 180"
        className="w-full h-full drop-shadow-[0_10px_25px_rgba(59,130,246,0.3)]"
        fill="none"
      >
        <defs>
          {/* Blue sphere gradient */}
          <radialGradient id="blueSphere" cx="35%" cy="35%" r="65%">
            <stop offset="0%" stopColor="#93c5fd" />
            <stop offset="45%" stopColor="#3b82f6" />
            <stop offset="100%" stopColor="#1e3a8a" />
          </radialGradient>

          {/* Cyan sphere gradient */}
          <radialGradient id="cyanSphere" cx="35%" cy="35%" r="65%">
            <stop offset="0%" stopColor="#a5f3fc" />
            <stop offset="50%" stopColor="#06b6d4" />
            <stop offset="100%" stopColor="#0e7490" />
          </radialGradient>

          {/* Purple/Violet sphere gradient */}
          <radialGradient id="purpleSphere" cx="35%" cy="35%" r="65%">
            <stop offset="0%" stopColor="#d8b4fe" />
            <stop offset="50%" stopColor="#8b5cf6" />
            <stop offset="100%" stopColor="#4c1d95" />
          </radialGradient>

          {/* Bond gradient */}
          <linearGradient id="bondGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#60a5fa" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#a5b4fc" stopOpacity="0.8" />
          </linearGradient>

          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Covalent bonds */}
        <line x1="80" y1="90" x2="140" y2="60" stroke="url(#bondGrad)" strokeWidth="6" strokeLinecap="round" />
        <line x1="140" y1="60" x2="200" y2="85" stroke="url(#bondGrad)" strokeWidth="6" strokeLinecap="round" />
        <line x1="140" y1="60" x2="135" y2="130" stroke="url(#bondGrad)" strokeWidth="5" strokeLinecap="round" />
        <line x1="200" y1="85" x2="245" y2="50" stroke="url(#bondGrad)" strokeWidth="5" strokeLinecap="round" />
        <line x1="200" y1="85" x2="215" y2="140" stroke="url(#bondGrad)" strokeWidth="5" strokeLinecap="round" />
        <line x1="80" y1="90" x2="45" y2="130" stroke="url(#bondGrad)" strokeWidth="5" strokeLinecap="round" />
        <line x1="80" y1="90" x2="50" y2="45" stroke="url(#bondGrad)" strokeWidth="4" strokeLinecap="round" />

        {/* Secondary background atoms */}
        <circle cx="50" cy="45" r="11" fill="url(#cyanSphere)" opacity="0.85" filter="url(#glow)" />
        <circle cx="45" cy="130" r="14" fill="url(#purpleSphere)" opacity="0.9" />
        <circle cx="135" cy="130" r="15" fill="url(#blueSphere)" />
        <circle cx="215" cy="140" r="13" fill="url(#cyanSphere)" />
        <circle cx="245" cy="50" r="16" fill="url(#purpleSphere)" filter="url(#glow)" />

        {/* Primary foreground atoms */}
        <circle cx="80" cy="90" r="20" fill="url(#blueSphere)" filter="url(#glow)" />
        <circle cx="140" cy="60" r="24" fill="url(#cyanSphere)" filter="url(#glow)" />
        <circle cx="200" cy="85" r="22" fill="url(#blueSphere)" filter="url(#glow)" />

        {/* Floating Capsule pill 1 */}
        <g transform="translate(160, 105) rotate(32)">
          <rect x="0" y="0" width="22" height="11" rx="5.5" fill="#3b82f6" />
          <rect x="22" y="0" width="22" height="11" rx="5.5" fill="#e0e7ff" />
          <line x1="22" y1="0" x2="22" y2="11" stroke="#1e293b" strokeWidth="0.5" />
        </g>

        {/* Floating Capsule pill 2 */}
        <g transform="translate(100, 135) rotate(-24) scale(0.8)">
          <rect x="0" y="0" width="20" height="10" rx="5" fill="#a855f7" />
          <rect x="20" y="0" width="20" height="10" rx="5" fill="#ffffff" />
        </g>
      </svg>
    </div>
  );
};
