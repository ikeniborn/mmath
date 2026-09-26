import type { ReactNode } from 'react';
import type { Theme } from '../../api';
import { BADGE_COLORS, CARS, CONSTRUCTION, DOLLS, FLOWERS } from './shapes';

const OBJECTS: Record<Theme, ReactNode[]> = { flowers: FLOWERS, dolls: DOLLS, cars: CARS, construction: CONSTRUCTION };

/** One drawn object of the child's theme; `icon` cycles through the four objects. Decorative: the accessible text lives elsewhere. */
export function ThemeIcon({ theme, icon, className = '' }: { theme: Theme; icon: number; className?: string }) {
  return <svg viewBox="0 0 100 100" className={`theme-icon ${className}`} aria-hidden="true" data-icon={icon % 4}>{OBJECTS[theme][icon % 4]}</svg>;
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

/** A sticker is a theme object on a badge; code `<theme>-<1..8>`: stickers 1–4 sit on circles, 5–8 on stars. */
export function Sticker({ code, className = '' }: { code: string; className?: string }) {
  const [theme, rawIndex] = code.split('-') as [Theme, string];
  const index = Math.max(1, Number(rawIndex) || 1);
  const object = OBJECTS[theme]?.[(index - 1) % 4] ?? null;
  const color = BADGE_COLORS[(index - 1) % 4];
  const star = index > 4;
  return <svg viewBox="0 0 100 100" className={`sticker ${className}`} role="img" aria-label={code} data-sticker={code}>
    {star ? <polygon points="50,2 62,36 98,36 69,58 80,94 50,72 20,94 31,58 2,36 38,36" fill={color} stroke="#c7b46a" strokeWidth="2" /> : <circle cx="50" cy="50" r="48" fill={color} stroke="#c7b46a" strokeWidth="2" />}
    <g transform="translate(22 24) scale(0.56)">{object}</g>
  </svg>;
}
