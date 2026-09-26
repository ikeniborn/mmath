import type { Theme } from '../../api';

/** Theme objects for the early tasks. Task 6 replaces the glyph bodies with the drawn SVG set; the props stay. */
const FALLBACK: Record<Theme, string[]> = { flowers: ['🌸', '🌼', '🌷', '🌻'], dolls: ['🪆', '🎀', '🧸', '🎈'], cars: ['🚗', '🚙', '🚌', '🚲'], construction: ['🚜', '🚧', '🏗️', '🧱'] };

export function ThemeIcon({ theme, icon, className = '' }: { theme: Theme; icon: number; className?: string }) {
  return <span className={className} aria-hidden="true">{FALLBACK[theme][icon % 4]}</span>;
}

const FILL: Record<string, string> = { circle: '#dd7a14', square: '#126d67', triangle: '#a52b20', star: '#c7b46a' };

export function Shape({ shape, size }: { shape: string; size: number }) {
  const px = 24 + size * 12;
  const fill = FILL[shape] ?? '#697b83';
  const body = shape === 'circle' ? <circle cx="50" cy="50" r="45" fill={fill} />
    : shape === 'square' ? <rect x="8" y="8" width="84" height="84" rx="8" fill={fill} />
    : shape === 'triangle' ? <polygon points="50,6 94,90 6,90" fill={fill} />
    : <polygon points="50,5 61,38 96,38 68,58 79,92 50,72 21,92 32,58 4,38 39,38" fill={fill} />;
  return <svg viewBox="0 0 100 100" width={px} height={px} aria-hidden="true" data-shape={shape}>{body}</svg>;
}
