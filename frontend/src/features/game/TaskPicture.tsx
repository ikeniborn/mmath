import type { PublicProblem, Theme } from '../../api';
import styles from './Hint.module.css';
import { THEME_ICONS } from './labels';

export const PICTURE_MAX_AGE = 5;
const LIMIT = 10;

/** Which picture a task gets for a young child: counting objects for small addition and subtraction, nothing otherwise. */
export function pictureKind(problem: PublicProblem, age: number): 'add' | 'sub' | 'missing' | null {
  if (age > PICTURE_MAX_AGE) return null;
  const { operand_a: a, operand_b: b, kind, operation, prompt } = problem;
  if (kind === 'result' && a !== null && b !== null) {
    if (operation === 'addition' && a + b <= LIMIT) return 'add';
    if (operation === 'subtraction' && a <= LIMIT) return 'sub';
  }
  if (kind === 'missing' && operation === 'addition' && typeof prompt?.result === 'number' && prompt.result <= LIMIT) return 'missing';
  return null;
}

/** Objects of the child's theme drawn with the task itself, so a 4–5-year-old counts pictures instead of reading numerals. Decorative: the expression stays the accessible text. */
export default function TaskPicture({ problem, age, theme }: { problem: PublicProblem; age: number; theme: Theme }) {
  const kind = pictureKind(problem, age);
  if (!kind) return null;
  const [iconA, iconB] = THEME_ICONS[theme];
  const icons = (count: number, icon: string, className = '') => Array.from({ length: count }, (_, index) => <span key={`${icon}${index}`} className={`${styles.icon} ${className}`}>{icon}</span>);
  const a = problem.operand_a ?? 0;
  const b = problem.operand_b ?? 0;
  if (kind === 'add') {
    return <div className={`task-picture ${styles.hint}`} aria-hidden="true" data-kind="add"><div className={styles.row}>{icons(a, iconA)}<span className={styles.icon}>+</span>{icons(b, iconB)}</div></div>;
  }
  if (kind === 'sub') {
    return <div className={`task-picture ${styles.hint}`} aria-hidden="true" data-kind="sub"><div className={styles.row}>{icons(a - b, iconA)}{icons(b, iconA, styles.faded)}</div></div>;
  }
  const known = problem.prompt?.blank === 'a' ? b : a;
  const total = Number(problem.prompt?.result ?? 0);
  return <div className={`task-picture ${styles.hint}`} aria-hidden="true" data-kind="missing"><div className={styles.row}>{icons(known, iconA)}{Array.from({ length: Math.max(0, total - known) }, (_, index) => <span key={`slot${index}`} className={`${styles.icon} ${styles.cell}`} />)}</div></div>;
}
