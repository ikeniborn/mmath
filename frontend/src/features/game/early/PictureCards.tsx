import type { Theme } from '../../../api';
import { ThemeIcon } from '../../../assets/themes';
import { useT } from '../../../i18n';
import styles from './Early.module.css';

type Props = { options: number[]; theme: Theme; kind: 'number' | 'icon'; disabled: boolean; onChoose: (value: number) => void };

/** Three equal cards; a number card shows the numeral and as many dots, an icon card shows the theme object. Nothing marks the correct one. */
export default function PictureCards({ options, theme, kind, disabled, onChoose }: Props) {
  const { t } = useT();
  return <div className={styles.cards} role="group" aria-label={t('early.cards')}>
    {options.map((value, index) => <button type="button" key={`${value}-${index}`} className={styles.card} disabled={disabled} aria-label={t('early.card', { n: index + 1 })} onClick={() => onChoose(value)}>
      {kind === 'icon' ? <ThemeIcon theme={theme} icon={value} className={styles.cardIcon} /> : <><span className={styles.cardNumber}>{value}</span><span className={styles.dots} aria-hidden="true">{Array.from({ length: value }, (_, dot) => <i key={dot} />)}</span></>}
    </button>)}
  </div>;
}
