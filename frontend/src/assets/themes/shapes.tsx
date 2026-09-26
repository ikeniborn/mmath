import type { ReactNode } from 'react';

/** Hand-drawn flat objects, one 100x100 viewBox each. Colours come from the app palette; no external artwork. */
export const FLOWERS: ReactNode[] = [
  <g key="daisy"><circle cx="50" cy="50" r="14" fill="#e8b21c" />{[0, 45, 90, 135, 180, 225, 270, 315].map(angle => <ellipse key={angle} cx="50" cy="22" rx="9" ry="16" fill="#f6f1e3" stroke="#c7b46a" strokeWidth="2" transform={`rotate(${angle} 50 50)`} />)}<circle cx="50" cy="50" r="14" fill="#e8b21c" /></g>,
  <g key="tulip"><path d="M50 92 V54" stroke="#3f7d4b" strokeWidth="5" strokeLinecap="round" /><path d="M50 70 C38 72 30 64 30 56 C40 58 46 62 50 70 Z" fill="#3f7d4b" /><path d="M30 44 V26 L40 36 L50 20 L60 36 L70 26 V44 C70 56 60 62 50 62 C40 62 30 56 30 44 Z" fill="#d94a6a" /></g>,
  <g key="sunflower"><path d="M50 94 V60" stroke="#3f7d4b" strokeWidth="5" strokeLinecap="round" />{[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330].map(angle => <ellipse key={angle} cx="50" cy="26" rx="7" ry="14" fill="#f2b31a" transform={`rotate(${angle} 50 46)`} />)}<circle cx="50" cy="46" r="13" fill="#6b3f1d" /></g>,
  <g key="leaf"><path d="M20 80 C20 40 50 16 84 16 C84 50 60 80 20 80 Z" fill="#5aa35e" /><path d="M24 76 L78 22" stroke="#2f6b35" strokeWidth="3" strokeLinecap="round" /></g>,
];

export const DOLLS: ReactNode[] = [
  <g key="doll"><path d="M30 92 C26 62 34 48 50 48 C66 48 74 62 70 92 Z" fill="#d94a6a" /><circle cx="50" cy="32" r="16" fill="#f4d1b5" /><path d="M34 30 C36 16 64 16 66 30 C58 24 42 24 34 30 Z" fill="#6b3f1d" /><circle cx="44" cy="32" r="2" fill="#333" /><circle cx="56" cy="32" r="2" fill="#333" /></g>,
  <g key="bow"><path d="M50 50 L14 30 V70 Z" fill="#e05a8c" /><path d="M50 50 L86 30 V70 Z" fill="#e05a8c" /><circle cx="50" cy="50" r="9" fill="#b83a6a" /></g>,
  <g key="bear"><circle cx="30" cy="26" r="10" fill="#a56a3a" /><circle cx="70" cy="26" r="10" fill="#a56a3a" /><circle cx="50" cy="42" r="24" fill="#c98a4b" /><ellipse cx="50" cy="50" rx="9" ry="7" fill="#f0d3a8" /><circle cx="50" cy="48" r="3" fill="#333" /><circle cx="41" cy="38" r="2.5" fill="#333" /><circle cx="59" cy="38" r="2.5" fill="#333" /><rect x="30" y="64" width="40" height="28" rx="12" fill="#c98a4b" /></g>,
  <g key="balloon"><ellipse cx="50" cy="38" rx="24" ry="30" fill="#3f8fd1" /><path d="M46 68 L50 74 L54 68 Z" fill="#3f8fd1" /><path d="M50 74 C44 82 56 88 50 96" stroke="#555" strokeWidth="2" fill="none" /></g>,
];

export const CARS: ReactNode[] = [
  <g key="car"><path d="M12 62 L22 44 L38 34 H66 L78 44 L90 50 V68 H12 Z" fill="#d9534f" /><rect x="40" y="38" width="22" height="12" rx="2" fill="#cfe8f5" /><circle cx="30" cy="70" r="9" fill="#333" /><circle cx="72" cy="70" r="9" fill="#333" /></g>,
  <g key="bus"><rect x="10" y="26" width="80" height="44" rx="6" fill="#f2b31a" /><rect x="16" y="34" width="14" height="14" fill="#cfe8f5" /><rect x="36" y="34" width="14" height="14" fill="#cfe8f5" /><rect x="56" y="34" width="14" height="14" fill="#cfe8f5" /><circle cx="28" cy="74" r="8" fill="#333" /><circle cx="72" cy="74" r="8" fill="#333" /></g>,
  <g key="truck"><rect x="8" y="34" width="50" height="34" fill="#4c8bd1" /><path d="M58 44 H80 L90 56 V68 H58 Z" fill="#2f5f96" /><rect x="64" y="48" width="12" height="9" fill="#cfe8f5" /><circle cx="24" cy="72" r="8" fill="#333" /><circle cx="76" cy="72" r="8" fill="#333" /></g>,
  <g key="bike"><circle cx="26" cy="66" r="16" fill="none" stroke="#333" strokeWidth="5" /><circle cx="74" cy="66" r="16" fill="none" stroke="#333" strokeWidth="5" /><path d="M26 66 L44 38 H64 L74 66 M44 38 L52 66 H26 M60 30 L64 38" stroke="#3f7d4b" strokeWidth="5" fill="none" strokeLinecap="round" /></g>,
];

export const CONSTRUCTION: ReactNode[] = [
  <g key="excavator"><rect x="16" y="50" width="44" height="22" rx="4" fill="#f2b31a" /><rect x="22" y="36" width="20" height="16" rx="3" fill="#f2b31a" /><rect x="26" y="40" width="10" height="8" fill="#cfe8f5" /><path d="M56 52 L78 30 L86 36 L70 56 Z" fill="#c68a12" /><path d="M84 36 L94 46 L86 56 Z" fill="#555" /><rect x="12" y="72" width="52" height="12" rx="6" fill="#333" /></g>,
  <g key="cone"><path d="M36 84 L48 20 H52 L64 84 Z" fill="#f2731a" /><path d="M42 54 L58 54 L60 64 L40 64 Z" fill="#f6f1e3" /><rect x="26" y="82" width="48" height="8" rx="3" fill="#f2731a" /></g>,
  <g key="crane"><rect x="46" y="30" width="8" height="60" fill="#f2b31a" /><path d="M20 30 H84 L50 18 Z" fill="#f2b31a" /><path d="M22 32 V54" stroke="#555" strokeWidth="2" /><path d="M16 54 H28 L22 62 Z" fill="#555" /><rect x="30" y="86" width="40" height="8" rx="3" fill="#333" /></g>,
  <g key="brick"><rect x="12" y="34" width="76" height="34" rx="3" fill="#c0503a" /><path d="M12 51 H88 M40 34 V51 M64 51 V68" stroke="#f6f1e3" strokeWidth="3" /></g>,
];

export const BADGE_COLORS = ['#f6d36b', '#9fd8c9', '#f4b6c2', '#b9d3f5'];
