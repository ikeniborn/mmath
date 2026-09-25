import { useState, type FormEvent } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api, ApiError, type Player } from '../../api';

export default function PlayerSettings({ players, onChange }: { players: Player[]; onChange: () => Promise<void> }) {
  const { id } = useParams();
  const player = players.find(item => item.id === id);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);
  if (!player) return <section><h2>Профиль не найден</h2><Link to="/">Назад</Link></section>;
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
      setError(bands ? `Для выбранных тем фиксированный уровень должен быть одним из: ${bands.join(', ')}.` : 'Настройки не сохранены. Проверьте пароль и выберите хотя бы одну тему.');
    }
  }
  return <section className="settings"><Link to="/">← К выбору ребёнка</Link><h2>Настройки: {player.name}</h2><form className="card" onSubmit={save}><label>Имя<input name="name" defaultValue={player.name} required maxLength={40} /></label><label>Возраст<select name="age" defaultValue={player.age}>{[5,6,7,8,9,10].map(age => <option key={age}>{age}</option>)}</select></label><fieldset><legend>Темы</legend>{([['addition','Сложение'],['subtraction','Вычитание'],['multiplication','Умножение']] as const).map(([value,label]) => <label className="check" key={value}><input type="checkbox" name="topics" value={value} defaultChecked={player.topics.includes(value)} />{label}</label>)}</fieldset><label>Сложность<select name="mode" defaultValue={player.mode}><option value="automatic">Автоматически</option><option value="fixed">Фиксированная</option></select></label><label>Начальный уровень<select name="difficulty_band" defaultValue={player.difficulty_band ?? 0}>{[0,1,2,3,4].map(band => <option key={band} value={band}>{band}</option>)}</select></label><label>Оформление<select name="theme" defaultValue={player.theme}><option value="flowers">Цветы</option><option value="dolls">Куклы</option><option value="cars">Машинки</option><option value="construction">Стройтехника</option></select></label><label>Длительность занятия<select name="session_minutes" defaultValue={player.session_minutes}><option value="5">5 минут</option><option value="10">10 минут</option><option value="15">15 минут</option></select></label><label>Пароль родителя для сохранения<input name="password" type="password" autoComplete="current-password" required /></label>{error && <p role="alert">{error}</p>}{saved && <p role="status">Настройки сохранены</p>}<button type="submit">Сохранить</button></form></section>;
}
