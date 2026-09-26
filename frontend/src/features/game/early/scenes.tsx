import { useEffect, useState } from 'react';
import type { PublicProblem, Theme } from '../../../api';
import { Shape, ThemeIcon } from '../../../assets/themes';
import { useT } from '../../../i18n';
import styles from './Early.module.css';
import PictureCards from './PictureCards';
import { itemsOf, listOf, numberOf, optionsOf, pickItemsOf, type Item } from './types';

export type SceneProps = { problem: PublicProblem; theme: Theme; disabled: boolean; onAnswer: (value: number) => void };

function Grid({ items, theme, marked, onTap, hidden = false, label }: { items: Item[]; theme: Theme; marked?: Set<number>; onTap?: (index: number) => void; hidden?: boolean; label: string }) {
  return <div className={`task-scene ${styles.grid}`} data-hidden={hidden ? 'true' : undefined}>
    {items.map((item, index) => {
      const style = { gridColumn: item.x + 1, gridRow: item.y + 1 };
      const content = <ThemeIcon theme={theme} icon={item.icon} className={`${styles.object} ${marked?.has(index) ? styles.marked : ''}`} />;
      return onTap
        ? <button type="button" key={index} style={style} data-object className={styles.objectButton} aria-label={`${label} ${index + 1}`} aria-pressed={marked?.has(index) ?? false} onClick={() => onTap(index)}>{content}</button>
        : <span key={index} style={style} data-object className={styles.objectButton}>{hidden ? null : content}</span>;
    })}
  </div>;
}

export function CountScene({ problem, theme, disabled, onAnswer }: SceneProps) {
  const { t } = useT();
  const items = itemsOf(problem);
  const [marked, setMarked] = useState<Set<number>>(new Set());
  useEffect(() => setMarked(new Set()), [problem.id]);
  const toggle = (index: number) => setMarked(current => { const next = new Set(current); if (next.has(index)) next.delete(index); else next.add(index); return next; });
  return <>
    <Grid items={items} theme={theme} marked={marked} onTap={disabled ? undefined : toggle} label={t('early.object')} />
    <p className={styles.counter} aria-live="polite">{marked.size}</p>
    <button type="button" className={styles.done} disabled={disabled || marked.size === 0} onClick={() => onAnswer(marked.size)}>{t('early.done')}</button>
  </>;
}

export function MatchScene({ problem, theme, disabled, onAnswer }: SceneProps) {
  const { t } = useT();
  const items = itemsOf(problem);
  const [tray, setTray] = useState(0);
  useEffect(() => setTray(0), [problem.id]);
  const trayItems: Item[] = Array.from({ length: tray }, (_, index) => ({ x: index % 5, y: Math.floor(index / 5), icon: 1 }));
  return <>
    <Grid items={items} theme={theme} label={t('early.object')} />
    <div className={styles.tray}>
      <Grid items={trayItems} theme={theme} onTap={disabled ? undefined : () => setTray(count => Math.max(0, count - 1))} label={t('early.trayObject')} />
      <button type="button" className={styles.plus} disabled={disabled || tray >= 10} aria-label={t('early.add')} onClick={() => setTray(count => count + 1)}>+</button>
    </div>
    <button type="button" className={styles.done} disabled={disabled || tray === 0} onClick={() => onAnswer(tray)}>{t('early.done')}</button>
  </>;
}

export function QuickLook({ problem, theme, disabled, onAnswer }: SceneProps) {
  const { t } = useT();
  const [hidden, setHidden] = useState(false);
  useEffect(() => {
    setHidden(false);
    const timer = setTimeout(() => setHidden(true), numberOf(problem, 'reveal_ms', 1500));
    return () => clearTimeout(timer);
  }, [problem.id]);
  return <>
    <Grid items={itemsOf(problem)} theme={theme} hidden={hidden} label={t('early.object')} />
    <PictureCards options={optionsOf(problem) ?? []} theme={theme} kind="number" disabled={disabled} onChoose={onAnswer} />
  </>;
}

export function PatternRow({ problem, theme, disabled, onAnswer }: SceneProps) {
  return <>
    <div className={`task-scene ${styles.row}`}>{listOf(problem, 'sequence').map((icon, index) => <ThemeIcon key={index} theme={theme} icon={icon} className={styles.object} />)}<span className={styles.slot}>?</span></div>
    <PictureCards options={optionsOf(problem) ?? []} theme={theme} kind="icon" disabled={disabled} onChoose={onAnswer} />
  </>;
}

export function FiveFrame({ problem, theme, disabled, onAnswer }: SceneProps) {
  const size = numberOf(problem, 'size', 5), filled = numberOf(problem, 'filled', 0);
  return <>
    <div className={`task-scene ${styles.frame}`}>{Array.from({ length: size }, (_, index) => <span key={index} className={styles.cell} data-cell={index < filled ? 'filled' : 'empty'}>{index < filled ? <ThemeIcon theme={theme} icon={0} className={styles.object} /> : null}</span>)}</div>
    <PictureCards options={optionsOf(problem) ?? []} theme={theme} kind="number" disabled={disabled} onChoose={onAnswer} />
  </>;
}

export function OrderTowers({ problem, theme, disabled, onAnswer }: SceneProps) {
  const { t } = useT();
  const heights = listOf(problem, 'heights');
  const [taps, setTaps] = useState<number[]>([]);
  useEffect(() => setTaps([]), [problem.id]);
  const tap = (index: number) => {
    if (taps.includes(index)) return;
    const next = [...taps, index];
    setTaps(next);
    if (next.length === heights.length) onAnswer(Number(next.map(i => i + 1).join('')));
  };
  return <>
    <div className={`task-scene ${styles.towers}`}>{heights.map((height, index) => <button type="button" key={index} className={styles.tower} disabled={disabled || taps.includes(index)} aria-label={`${t('early.tower')} ${index + 1}`} onClick={() => tap(index)}>
      {Array.from({ length: height }, (_, block) => <ThemeIcon key={block} theme={theme} icon={0} className={styles.block} />)}
      {taps.includes(index) && <span className={styles.badge}>{taps.indexOf(index) + 1}</span>}
    </button>)}</div>
    <button type="button" className="secondary" disabled={disabled || taps.length === 0} onClick={() => setTaps([])}>{t('early.reset')}</button>
  </>;
}

export function ShareScene({ problem, theme, disabled, onAnswer }: SceneProps) {
  const total = numberOf(problem, 'total'), friends = numberOf(problem, 'friends');
  return <>
    <div className={`task-scene ${styles.row}`}>{Array.from({ length: total }, (_, index) => <ThemeIcon key={index} theme={theme} icon={1} className={styles.object} />)}</div>
    <div className={styles.row}>{Array.from({ length: friends }, (_, index) => <ThemeIcon key={index} theme={theme} icon={2} className={styles.friend} />)}</div>
    <PictureCards options={optionsOf(problem) ?? []} theme={theme} kind="number" disabled={disabled} onChoose={onAnswer} />
  </>;
}

export function PickScene({ problem, disabled, onAnswer }: SceneProps) {
  const { t } = useT();
  return <div className={`task-scene ${styles.row}`}>{pickItemsOf(problem).map((item, index) => <button type="button" key={index} className={styles.pick} disabled={disabled} aria-label={`${t('early.shape')} ${index + 1}`} onClick={() => onAnswer(index)}><Shape shape={item.shape} size={item.size} /></button>)}</div>;
}
