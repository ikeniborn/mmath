import type { Theme } from '../../api';

/** One counter icon per theme; a second icon marks the other operand or the removed part. */
export const THEME_ICONS: Record<Theme, [string, string]> = { flowers: ['🌸', '🌼'], dolls: ['🪆', '🎀'], cars: ['🚗', '🚙'], construction: ['🚜', '🚧'] };
