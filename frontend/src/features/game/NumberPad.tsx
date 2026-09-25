import styles from './NumberPad.module.css';

type Props = { disabled: boolean; canSubmit: boolean; onDigit: (digit: string) => void; onErase: () => void; onSubmit: () => void };

export default function NumberPad({ disabled, canSubmit, onDigit, onErase, onSubmit }: Props) {
  return <div className={styles.pad} role="group" aria-label="Клавиатура">
    {['1','2','3','4','5','6','7','8','9','0'].map(digit => <button type="button" className={styles.key} key={digit} disabled={disabled} onClick={() => onDigit(digit)}>{digit}</button>)}
    <button type="button" className={styles.key} disabled={disabled} onClick={onErase}>Стереть</button>
    <button type="button" className={`${styles.key} ${styles.primary}`} disabled={disabled || !canSubmit} onClick={onSubmit}>Ответить</button>
  </div>;
}
