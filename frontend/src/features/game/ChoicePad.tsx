import { useT } from '../../i18n';
import styles from './NumberPad.module.css';

type Props = { options: { value: number; label: string }[]; disabled: boolean; onChoose: (value: number) => void };

/** Sign / parity / operator answers: one tap submits, no free-text entry. */
export default function ChoicePad({ options, disabled, onChoose }: Props) {
  const { t } = useT();
  return <div className={styles.pad} role="group" aria-label={t('pad.choices')}>
    {options.map(option => <button type="button" className={`${styles.key} ${styles.choice}`} key={option.value} disabled={disabled} onClick={() => onChoose(option.value)}>{option.label}</button>)}
  </div>;
}
