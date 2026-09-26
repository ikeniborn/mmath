import { useT } from '../../i18n';
import styles from './NumberPad.module.css';

type Props = { disabled: boolean; canSubmit: boolean; onDigit: (digit: string) => void; onErase: () => void; onSubmit: () => void };

export default function NumberPad({ disabled, canSubmit, onDigit, onErase, onSubmit }: Props) {
  const { t } = useT();
  return <div className={styles.pad} role="group" aria-label={t('pad.label')}>
    {['1','2','3','4','5','6','7','8','9','0'].map(digit => <button type="button" className={styles.key} key={digit} disabled={disabled} onClick={() => onDigit(digit)}>{digit}</button>)}
    <button type="button" className={styles.key} disabled={disabled} onClick={onErase}>{t('pad.erase')}</button>
    <button type="button" className={`${styles.key} ${styles.primary}`} disabled={disabled || !canSubmit} onClick={onSubmit}>{t('pad.submit')}</button>
  </div>;
}
