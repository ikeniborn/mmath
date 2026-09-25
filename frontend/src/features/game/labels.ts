import type { Theme } from '../../api';

export const OPERATOR: Record<string, string> = { addition: '+', subtraction: '−', multiplication: '×' };
/** One counter icon per theme; a second icon marks the other operand or the removed part. */
export const THEME_ICONS: Record<Theme, [string, string]> = { flowers: ['🌸', '🌼'], dolls: ['🪆', '🎀'], cars: ['🚗', '🚙'], construction: ['🚜', '🚧'] };

export function expression(operation: string, a: number, b: number): string { return `${a} ${OPERATOR[operation] ?? '+'} ${b}`; }
export function compute(operation: string, a: number, b: number): number { return operation === 'subtraction' ? a - b : operation === 'multiplication' ? a * b : a + b; }
