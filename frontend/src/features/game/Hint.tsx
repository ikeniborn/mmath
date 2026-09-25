import type { HintView, Theme } from '../../api';
import styles from './Hint.module.css';
import { THEME_ICONS } from './labels';

/** Renders the deterministic scaffold from the operands with the child's chosen icons. The answer is never part of the payload. */
export default function Hint({ hint, theme }: { hint: HintView; theme: Theme }) {
  const [iconA, iconB] = THEME_ICONS[theme];
  const icons = (count: number, icon: string, faded = false) => Array.from({ length: count }, (_, index) => <span key={index} className={`${styles.icon} ${faded ? styles.faded : ''}`} aria-hidden="true">{icon}</span>);
  if (hint.kind === 'counters' && hint.operation === 'subtraction') {
    return <div className={styles.hint} role="img" aria-label={`Подсказка: было ${hint.operand_a}, убираем ${hint.operand_b}`}>
      <div className={styles.row}>{icons(hint.operand_a - hint.operand_b, iconA)}{icons(hint.operand_b, iconA, true)}</div>
    </div>;
  }
  if (hint.kind === 'counters') {
    return <div className={styles.hint} role="img" aria-label={`Подсказка: ${hint.operand_a} и ещё ${hint.operand_b}`}>
      <div className={styles.row}>{icons(hint.operand_a, iconA)}</div>
      <div className={styles.row}>{icons(hint.operand_b, iconB)}</div>
    </div>;
  }
  if (hint.kind === 'groups') {
    return <div className={styles.hint} role="img" aria-label={`Подсказка: ${hint.operand_b} ряда по ${hint.operand_a}`}>
      {Array.from({ length: hint.operand_b }, (_, row) => <div key={row} className={styles.row}>{icons(hint.operand_a, row % 2 ? iconB : iconA)}</div>)}
    </div>;
  }
  if (hint.kind === 'ten_frame') {
    const first = hint.operation === 'subtraction' ? hint.operand_a - hint.operand_b : hint.operand_a;
    const second = hint.operation === 'subtraction' ? hint.operand_b : hint.operand_b;
    const cells = Array.from({ length: 20 }, (_, index) => index < first ? styles.filledA : index < first + second ? (hint.operation === 'subtraction' ? styles.removed : styles.filledB) : '');
    const label = hint.operation === 'subtraction' ? `Подсказка: было ${hint.operand_a}, убираем ${hint.operand_b} через десяток` : `Подсказка: ${hint.operand_a} и ещё ${hint.operand_b}. Сначала заполни десяток`;
    return <div className={styles.hint} role="img" aria-label={label}><div className={styles.frame}>{cells.map((fill, index) => <span key={index} className={`${styles.cell} ${fill}`} />)}</div></div>;
  }
  const step = hint.scale > 20 ? 5 : 1;
  const ticks = Array.from({ length: hint.scale / step + 1 }, (_, index) => index * step);
  const back = hint.operation === 'subtraction';
  return <div className={styles.hint} role="img" aria-label={`Подсказка: начни с ${hint.operand_a} и сделай ${hint.operand_b} шагов ${back ? 'назад' : 'вперёд'}`}>
    <div className={styles.line}>{ticks.map(tick => <span key={tick} className={`${styles.tick} ${tick === hint.operand_a ? styles.start : ''}`}>{tick}</span>)}</div>
    <p className={styles.jump}>Начни с {hint.operand_a}, шагни {back ? 'назад' : 'вперёд'} на {hint.operand_b}.</p>
  </div>;
}
