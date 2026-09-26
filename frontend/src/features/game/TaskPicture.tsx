import type { PublicProblem, Theme } from '../../api';
import { ThemeIcon } from '../../assets/themes';
import { useT } from '../../i18n';
import hintStyles from './Hint.module.css';
import styles from './TaskPicture.module.css';

const LIMIT = 10;
export type PictureKind = 'add' | 'sub' | 'missing' | 'compare' | 'parity' | 'neighbour';

/** Which scene a picture-mode task gets: only small quantities, only when the session runs in picture mode. */
export function pictureKind(problem: PublicProblem, picture: boolean): PictureKind | null {
  if (!picture) return null;
  const { operand_a: a, operand_b: b, kind, operation, prompt, skill } = problem;
  if (kind === 'compare' && a !== null && b !== null && a <= LIMIT && b <= LIMIT) return 'compare';
  if (kind === 'parity' && Number(prompt?.value) <= LIMIT) return 'parity';
  if (skill === 'neighbour_one' && a !== null && a <= LIMIT) return 'neighbour';
  if (kind === 'result' && a !== null && b !== null) {
    if (operation === 'addition' && a + b <= LIMIT) return 'add';
    if (operation === 'subtraction' && a <= LIMIT) return 'sub';
  }
  if (kind === 'missing' && operation === 'addition' && typeof prompt?.result === 'number' && prompt.result <= LIMIT) return 'missing';
  return null;
}

type Props = { problem: PublicProblem; theme: Theme; picture: boolean; disabled?: boolean; onAnswer?: (value: number) => void };

/** Objects of the child's theme drawn with the task, so a 4–5-year-old counts pictures instead of reading numerals.
 * Compare and parity scenes are also the input (tap a pile, Yes/No); the rest stay decorative and the expression remains the accessible text. */
export default function TaskPicture({ problem, theme, picture, disabled = false, onAnswer = () => {} }: Props) {
  const { t } = useT();
  const kind = pictureKind(problem, picture);
  if (!kind) return null;
  const icons = (count: number, icon: number, className = '') => Array.from({ length: count }, (_, index) => <ThemeIcon key={`${icon}${index}`} theme={theme} icon={icon} className={`${hintStyles.icon} ${className}`} />);
  const a = problem.operand_a ?? 0;
  const b = problem.operand_b ?? 0;
  const wrap = (content: React.ReactNode, extra = '') => <div className={`task-picture ${hintStyles.hint} ${extra}`} aria-hidden={kind === 'compare' || kind === 'parity' ? undefined : 'true'} data-kind={kind}>{content}</div>;
  if (kind === 'add') {
    return wrap(<div className={`${hintStyles.row} ${styles.basket}`} data-basket>{icons(a, 0)}<span className={hintStyles.icon}>+</span>{icons(b, 1)}</div>);
  }
  if (kind === 'sub') {
    return wrap(<div className={hintStyles.row}>{icons(a - b, 0)}{icons(b, 0, `${hintStyles.faded} ${styles.leaving}`)}</div>);
  }
  if (kind === 'missing') {
    const known = problem.prompt?.blank === 'a' ? b : a;
    const total = Number(problem.prompt?.result ?? 0);
    return wrap(<div className={hintStyles.row}>{icons(known, 0)}<span className={styles.garage} data-garage>{Array.from({ length: Math.max(0, total - known) }, (_, index) => <span key={`slot${index}`} className={`${hintStyles.icon} ${hintStyles.cell}`} />)}</span></div>);
  }
  if (kind === 'neighbour') {
    const asked = problem.operation === 'addition' ? a + 1 : a - 1;
    const carriages = [a - 1, a, a + 1].filter(value => value >= 0);  // the asked neighbour is the empty carriage
    return wrap(<div className={styles.train}>{carriages.map(value => <span key={value} className={styles.carriage} data-carriage={value === asked ? 'empty' : 'number'}>{value === asked ? '?' : value}</span>)}</div>);
  }
  if (kind === 'parity') {
    const value = Number(problem.prompt?.value ?? 0);
    return wrap(<>
      <div className={hintStyles.row}>{Array.from({ length: Math.ceil(value / 2) }, (_, pair) => <span key={pair} className={styles.pair} data-pair>{icons(pair * 2 + 1 < value ? 2 : 1, pair % 2)}</span>)}</div>
      <div className={styles.choices} role="group" aria-label={t('early.cards')}>
        <button type="button" className={styles.choice} disabled={disabled} onClick={() => onAnswer(0)}>{t('early.yes')}</button>
        <button type="button" className={styles.choice} disabled={disabled} onClick={() => onAnswer(1)}>{t('early.no')}</button>
      </div>
    </>, styles.interactive);
  }
  return wrap(<>
    <div className={styles.piles}>
      <button type="button" className={styles.pile} disabled={disabled} aria-label={`${t('early.pile')} 1`} onClick={() => onAnswer(1)}>{icons(a, 0)}</button>
      <button type="button" className={styles.pile} disabled={disabled} aria-label={`${t('early.pile')} 2`} onClick={() => onAnswer(-1)}>{icons(b, 1)}</button>
    </div>
    <button type="button" className={styles.choice} disabled={disabled} onClick={() => onAnswer(0)}>{t('early.same')}</button>
  </>, styles.interactive);
}
