import type { PublicProblem } from '../../../api';

export const EARLY_KINDS = new Set(['count', 'match', 'subitize', 'pattern', 'frame', 'order', 'share', 'pick']);
export type Item = { x: number; y: number; icon: number };
export type PickItem = { shape: 'circle' | 'square' | 'triangle' | 'star'; size: number };

const record = (problem: PublicProblem) => (problem.prompt ?? {}) as Record<string, unknown>;
export const isEarly = (problem: PublicProblem) => EARLY_KINDS.has(problem.kind);
export const itemsOf = (problem: PublicProblem) => (record(problem).items as Item[] | undefined) ?? [];
export const pickItemsOf = (problem: PublicProblem) => (record(problem).items as PickItem[] | undefined) ?? [];
export const optionsOf = (problem: PublicProblem): number[] | null => (record(problem).options as number[] | undefined) ?? null;
export const numberOf = (problem: PublicProblem, key: string, fallback = 0) => Number(record(problem)[key] ?? fallback);
export const listOf = (problem: PublicProblem, key: string) => (record(problem)[key] as number[] | undefined) ?? [];
