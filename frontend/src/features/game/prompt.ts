import type { PublicProblem } from '../../api';
import type { Key } from '../../i18n';

export const OPERATOR: Record<string, string> = { addition: '+', subtraction: '−', multiplication: '×', division: '÷', remainder: '÷' };
export const COMPARE_SIGNS: Record<number, string> = { [-1]: '<', 0: '=', 1: '>' };
export const OPERATOR_SIGNS = ['+', '−', '×'];

export type Translate = (key: Key, params?: Record<string, string | number>) => string;

/** Display parts of a task: strings plus one `null` slot where the child's answer goes (numeric kinds only). */
const EARLY_PROMPTS: Record<string, Key> = { count: 'prompt.count', match: 'prompt.match', subitize: 'prompt.subitize', pattern: 'prompt.pattern', frame: 'prompt.frame', order: 'prompt.order', share: 'prompt.share' };

export function promptParts(problem: PublicProblem, t: Translate, picture = false): (string | null)[] {
  const { kind, prompt } = problem;
  if (picture && kind === 'compare') return [t('prompt.comparePicture')];
  if (picture && kind === 'parity') return [t('prompt.parityPicture')];
  if (kind === 'pick') return [t(`prompt.pick.${String(prompt?.attribute)}.${String(prompt?.target)}` as Key)];
  if (EARLY_PROMPTS[kind]) return [t(EARLY_PROMPTS[kind])];
  const a = problem.operand_a ?? 0;  // null only for the blanked operand of a missing task, which is never rendered
  const b = problem.operand_b ?? 0;
  const op = OPERATOR[problem.operation] ?? '+';
  if (kind === 'missing') {
    const result = String(prompt?.result ?? '');
    return prompt?.blank === 'a' ? [null, ` ${op} ${b} = ${result}`] : [`${a} ${op} `, null, ` = ${result}`];
  }
  if (kind === 'chain') {
    const terms = (prompt?.terms as number[]) ?? [];
    const text = terms.map((term, index) => index === 0 ? String(term) : `${term < 0 ? '−' : '+'} ${Math.abs(term)}`).join(' ');
    return [`${text} = `, null];
  }
  if (kind === 'sequence') return [`${((prompt?.terms as number[]) ?? []).join(', ')}, `, null];
  if (kind === 'compare') return [`${prompt?.left} ? ${prompt?.right}`];
  if (kind === 'parity') return [t('prompt.parity', { n: Number(prompt?.value) })];
  if (kind === 'operator') return [`${a} ? ${b} = ${prompt?.result}`];
  if (problem.operation === 'remainder') return [`${t('prompt.remainder', { a, b })} `, null];
  if (prompt?.remainder) return [`${t('prompt.quotient', { a, b })} `, null];
  return [`${a} ${op} ${b} = `, null];
}

export function isChoice(problem: PublicProblem): boolean {
  return problem.kind === 'compare' || problem.kind === 'parity' || problem.kind === 'operator';
}

export function choices(problem: PublicProblem, t: Translate): { value: number; label: string }[] {
  if (problem.kind === 'compare') return [-1, 0, 1].map(value => ({ value, label: COMPARE_SIGNS[value] }));
  if (problem.kind === 'parity') return [{ value: 0, label: t('choice.even') }, { value: 1, label: t('choice.odd') }];
  return OPERATOR_SIGNS.map((label, value) => ({ value, label }));
}

/** Human label for a stored answer value, so feedback can show "<" instead of "-1". */
export function answerLabel(problem: PublicProblem | null | undefined, value: number, t: Translate): string {
  if (!problem) return String(value);
  if (problem.kind === 'compare') return COMPARE_SIGNS[value] ?? String(value);
  if (problem.kind === 'parity') return value === 0 ? t('choice.even') : t('choice.odd');
  if (problem.kind === 'operator') return OPERATOR_SIGNS[value] ?? String(value);
  return String(value);
}
