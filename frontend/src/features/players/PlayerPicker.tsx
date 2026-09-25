import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { api, type Player } from '../../api';

export default function PlayerPicker({ players, onChange }: { players: Player[]; onChange: () => Promise<void> }) {
  const [error, setError] = useState('');
  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      await api('/players', 'POST', { name: form.get('name'), age: Number(form.get('age')), topics: ['addition'] });
      await onChange();
      event.currentTarget.reset();
    } catch { setError('Не удалось создать профиль. Проверьте данные.'); }
  }
  return <section aria-labelledby="children-title"><h2 id="children-title">Кто сегодня считает?</h2><div className="tiles">{players.map(player => <article className="card" key={player.id}><span className="avatar" aria-hidden="true">{player.avatar === 'star' ? '★' : '✦'}</span><h3>{player.name}</h3><p>{player.age} лет · {player.mode === 'automatic' ? 'Автоматическая сложность' : 'Фиксированная сложность'}</p><div className="actions"><Link className="button" to={`/children/${player.id}`}>Играть</Link><Link className="button secondary" to={`/children/${player.id}/settings`}>Настройки</Link></div></article>)}</div><div className="card new-child"><h3>Добавить ребёнка</h3><form onSubmit={create}><label>Имя<input name="name" maxLength={40} required /></label><label>Возраст<select name="age" defaultValue="7">{[5,6,7,8,9,10].map(age => <option key={age}>{age}</option>)}</select></label>{error && <p role="alert">{error}</p>}<button type="submit">Создать профиль</button></form></div></section>;
}
