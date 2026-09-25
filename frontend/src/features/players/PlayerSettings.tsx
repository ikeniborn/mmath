import { useState, type FormEvent } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api, ApiError, type Player } from '../../api';
import { useT } from '../../i18n';
import ThemeSelect from './ThemeSelect';

const TOPICS = ['addition', 'subtraction', 'counting', 'multiplication', 'division', 'comparison'] as const;

export default function PlayerSettings({ players, onChange }: { players: Player[]; onChange: () => Promise<void> }) {
  const { t, name } = useT();
  const { id } = useParams();
  const player = players.find(item => item.id === id);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);
  if (!player) return <section><h2>{t('notFound.title')}</h2><Link to="/">{t('notFound.back')}</Link></section>;
  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!player) return;
    const form = new FormData(event.currentTarget);
    setError(''); setSaved(false);
    try {
      await api('/auth/confirm-password', 'POST', { password: form.get('password') });
      await api(`/players/${player.id}`, 'PATCH', { name: form.get('name'), age: Number(form.get('age')), topics: form.getAll('topics'), mode: form.get('mode'), difficulty_band: Number(form.get('difficulty_band')), session_minutes: Number(form.get('session_minutes')), theme: form.get('theme') });
      await onChange(); setSaved(true);
    } catch (cause) {
      const bands = cause instanceof ApiError && cause.code === 'unsupported_difficulty' ? (cause.detail.supported_bands as number[] | undefined) : undefined;
      setError(bands ? t('settings.unsupported', { bands: bands.join(', ') }) : t('settings.error'));
    }
  }
  return <section className="settings"><Link to="/">{t('settings.back')}</Link><h2>{t('settings.title', { name: player.name })}</h2><form className="card" onSubmit={save}><label>{t('picker.name')}<input name="name" defaultValue={player.name} required maxLength={40} /></label><label>{t('picker.age')}<select name="age" defaultValue={player.age}>{[5,6,7,8,9,10].map(age => <option key={age}>{age}</option>)}</select></label><fieldset><legend>{t('settings.topics')}</legend>{TOPICS.map(value => <label className="check" key={value}><input type="checkbox" name="topics" value={value} defaultChecked={player.topics.includes(value)} />{name('topic', value)}</label>)}</fieldset><label>{t('settings.mode')}<select name="mode" defaultValue={player.mode}><option value="automatic">{t('settings.auto')}</option><option value="fixed">{t('settings.fixed')}</option></select></label><label>{t('settings.band')}<select name="difficulty_band" defaultValue={player.difficulty_band ?? 0}>{[0,1,2,3,4].map(band => <option key={band} value={band}>{band}</option>)}</select></label><ThemeSelect defaultValue={player.theme} /><label>{t('settings.minutes')}<select name="session_minutes" defaultValue={player.session_minutes}>{[5, 10, 15].map(minutes => <option key={minutes} value={minutes}>{t('settings.minutesValue', { n: minutes })}</option>)}</select></label><label>{t('settings.password')}<input name="password" type="password" autoComplete="current-password" required /></label>{error && <p role="alert">{error}</p>}{saved && <p role="status">{t('settings.saved')}</p>}<button type="submit">{t('settings.save')}</button></form></section>;
}
