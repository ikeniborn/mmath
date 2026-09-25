import { useEffect, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api, type Player, type ProgressView } from '../../api';
import { SKILL_NAME } from '../game/labels';

export default function ProgressPage({ players }: { players: Player[] }) {
  const { id = '' } = useParams();
  const player = players.find(item => item.id === id);
  const [progress, setProgress] = useState<ProgressView | null>(null);
  const [error, setError] = useState('');
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => { heading.current?.focus(); }, [player?.id]);
  useEffect(() => {
    if (!player) return;
    api<ProgressView>(`/players/${player.id}/progress?limit=10`).then(setProgress).catch(() => setError('Не удалось загрузить успехи. Попробуйте позже.'));
  }, [player?.id]);
  if (!player) return <section><h2>Профиль не найден</h2><Link to="/">Назад</Link></section>;
  return <section className="progress">
    <Link to={`/children/${player.id}`}>← К домику</Link>
    <h2 ref={heading} tabIndex={-1}>Успехи: {player.name}</h2>
    {error && <p role="alert">{error}</p>}
    {progress && progress.skills.length === 0 && <p>Пока нет решённых задач. Начни занятие — и здесь появится прогресс.</p>}
    {progress && progress.skills.length > 0 && <table className="card"><caption>Навыки</caption><thead><tr><th scope="col">Навык</th><th scope="col">Уровень</th><th scope="col">Решено</th><th scope="col">Верно</th><th scope="col">Прогресс</th></tr></thead><tbody>
      {progress.skills.map(skill => <tr key={skill.skill}><th scope="row">{SKILL_NAME[skill.skill] ?? skill.skill}</th><td>{skill.band}</td><td>{skill.attempts}</td><td>{skill.correct}</td><td>{skill.mastery === null ? '—' : `${Math.round(skill.mastery * 100)}%`}</td></tr>)}
    </tbody></table>}
    {progress && progress.sessions.length > 0 && <><h3>Занятия</h3><ul className="sessions">{progress.sessions.map(session => <li key={session.id} className="card"><span>{new Date(session.started_at).toLocaleDateString('ru-RU')}</span><span>{session.state === 'finished' ? 'Завершено' : 'Не закончено'}</span><span>решено {session.answered_count}, верно {session.correct_count}</span><span>{session.settings.mode === 'fixed' ? `фиксированный уровень ${session.settings.difficulty_band}` : 'автоматически'}</span></li>)}</ul></>}
  </section>;
}
