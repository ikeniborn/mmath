import type { HintView, Theme } from '../../api';
import { useT } from '../../i18n';
import styles from './Hint.module.css';
import { THEME_ICONS } from './labels';

/** Renders the deterministic scaffold from the operands with the child's chosen icons. The answer is never part of the payload. */
export default function Hint({ hint, theme }: { hint: HintView; theme: Theme }) {
  const { t } = useT();
  const [iconA, iconB] = THEME_ICONS[theme];
  const params = { a: hint.operand_a, b: hint.operand_b };
  const icons = (count: number, icon: string, faded = false) => Array.from({ length: count }, (_, index) => <span key={index} className={`${styles.icon} ${faded ? styles.faded : ''}`} aria-hidden="true">{icon}</span>);
  if (hint.kind === 'counters' && hint.operation === 'subtraction') {
    return <div className={styles.hint} role="img" aria-label={t('hint.sub', params)}>
      <div className={styles.row}>{icons(hint.operand_a - hint.operand_b, iconA)}{icons(hint.operand_b, iconA, true)}</div>
    </div>;
  }
  if (hint.kind === 'counters') {
    return <div className={styles.hint} role="img" aria-label={t('hint.add', params)}>
      <div className={styles.row}>{icons(hint.operand_a, iconA)}</div>
      <div className={styles.row}>{icons(hint.operand_b, iconB)}</div>
    </div>;
  }
  if (hint.kind === 'pairs') {
    return <div className={styles.hint} role="img" aria-label={t('hint.pairs', { a: hint.operand_a })}>
      <div className={styles.row}>{Array.from({ length: hint.operand_a }, (_, index) => <span key={index} className={`${styles.icon} ${index % 2 ? styles.pairGap : ''}`} aria-hidden="true">{index % 2 ? iconB : iconA}</span>)}</div>
    </div>;
  }
  if (hint.kind === 'groups') {
    return <div className={styles.hint} role="img" aria-label={t('hint.groups', params)}>
      {Array.from({ length: hint.operand_b }, (_, row) => <div key={row} className={styles.row}>{icons(hint.operand_a, row % 2 ? iconB : iconA)}</div>)}
    </div>;
  }
  if (hint.kind === 'ten_frame') {
    const subtraction = hint.operation === 'subtraction';
    const first = subtraction ? hint.operand_a - hint.operand_b : hint.operand_a;
    const cells = Array.from({ length: 20 }, (_, index) => index < first ? styles.filledA : index < first + hint.operand_b ? (subtraction ? styles.removed : styles.filledB) : '');
    return <div className={styles.hint} role="img" aria-label={t(subtraction ? 'hint.tenSub' : 'hint.tenAdd', params)}><div className={styles.frame}>{cells.map((fill, index) => <span key={index} className={`${styles.cell} ${fill}`} />)}</div></div>;
  }
  const step = hint.scale > 100 ? 100 : hint.scale > 20 ? 5 : 1;
  const ticks = Array.from({ length: hint.scale / step + 1 }, (_, index) => index * step);
  const direction = t(hint.operation === 'subtraction' ? 'hint.back' : 'hint.forward');
  return <div className={styles.hint} role="img" aria-label={t('hint.line', { ...params, direction })}>
    <div className={styles.line}>{ticks.map(tick => <span key={tick} className={`${styles.tick} ${tick === hint.operand_a ? styles.start : ''}`}>{tick}</span>)}</div>
    <p className={styles.jump}>{t('hint.lineText', { ...params, direction })}</p>
  </div>;
}
