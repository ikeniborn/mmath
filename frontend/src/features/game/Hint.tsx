import type { HintView } from '../../api';
import styles from './Hint.module.css';

/** Renders the deterministic scaffold from the operands. The answer is never part of the payload. */
export default function Hint({ hint }: { hint: HintView }) {
  const label = `Подсказка: ${hint.operand_a} и ещё ${hint.operand_b}`;
  if (hint.kind === 'counters') {
    return <div className={styles.hint} role="img" aria-label={label}>
      <div className={styles.row}>{Array.from({ length: hint.operand_a }, (_, index) => <span key={`a${index}`} className={styles.dot} />)}</div>
      <div className={styles.row}>{Array.from({ length: hint.operand_b }, (_, index) => <span key={`b${index}`} className={`${styles.dot} ${styles.dotB}`} />)}</div>
    </div>;
  }
  if (hint.kind === 'ten_frame') {
    const cells = Array.from({ length: 20 }, (_, index) => index < hint.operand_a ? styles.filledA : index < hint.operand_a + hint.operand_b ? styles.filledB : '');
    return <div className={styles.hint} role="img" aria-label={`${label}. Сначала заполни десяток`}><div className={styles.frame}>{cells.map((fill, index) => <span key={index} className={`${styles.cell} ${fill}`} />)}</div></div>;
  }
  const step = hint.scale > 20 ? 5 : 1;
  const ticks = Array.from({ length: hint.scale / step + 1 }, (_, index) => index * step);
  return <div className={styles.hint} role="img" aria-label={`${label}. Начни с ${hint.operand_a} и сделай ${hint.operand_b} шагов вперёд`}>
    <div className={styles.line}>{ticks.map(tick => <span key={tick} className={`${styles.tick} ${tick === hint.operand_a ? styles.start : ''}`}>{tick}</span>)}</div>
    <p className={styles.jump}>Начни с {hint.operand_a}, шагни вперёд на {hint.operand_b}.</p>
  </div>;
}
