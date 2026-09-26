import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { api, type Player } from '../../api';
import { useT } from '../../i18n';
import ThemeSelect from './ThemeSelect';

export default function PlayerPicker({ players, onChange }: { players: Player[]; onChange: () => Promise<void> }) {
  const { t } = useT();
  const [error, setError] = useState('');
  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const element = event.currentTarget;  // React nulls currentTarget once the handler yields
    const form = new FormData(element);
    try {
      await api('/players', 'POST', { name: form.get('name'), age: Number(form.get('age')), theme: form.get('theme') });
      await onChange();
      element.reset();
      setError('');
    } catch { setError(t('picker.error')); }
  }
  return <section aria-labelledby="children-title"><h2 id="children-title">{t('picker.title')}</h2><div className="tiles">{players.map(player => <article className="card" key={player.id}><span className="avatar" aria-hidden="true">{player.avatar === 'star' ? '★' : '✦'}</span><h3>{player.name}</h3><p>{t('picker.card', { age: player.age, mode: player.mode === 'automatic' ? t('picker.auto') : t('picker.fixed') })}</p><div className="actions"><Link className="button" to={`/children/${player.id}`}>{t('picker.play')}</Link><Link className="button secondary" to={`/children/${player.id}/settings`}>{t('picker.settings')}</Link></div></article>)}</div><div className="card new-child"><h3>{t('picker.add')}</h3><form onSubmit={create}><label>{t('picker.name')}<input name="name" maxLength={40} required /></label><label>{t('picker.age')}<select name="age" defaultValue="7">{[4,5,6,7,8,9,10].map(age => <option key={age}>{age}</option>)}</select></label><ThemeSelect defaultValue="flowers" />{error && <p role="alert">{error}</p>}<button type="submit">{t('picker.create')}</button></form></div></section>;
}
