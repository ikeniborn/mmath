import type { Theme } from '../../api';
import { useT } from '../../i18n';

export const THEMES: Theme[] = ['flowers', 'dolls', 'cars', 'construction'];

export default function ThemeSelect({ defaultValue }: { defaultValue: Theme }) {
  const { t, name } = useT();
  return <label>{t('picker.theme')}<select name="theme" defaultValue={defaultValue}>{THEMES.map(theme => <option key={theme} value={theme}>{name('theme', theme)}</option>)}</select></label>;
}
