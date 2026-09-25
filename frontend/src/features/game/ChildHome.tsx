import { useEffect, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api, type Player, type SessionSnapshot } from '../../api';

export default function ChildHome({ players }: { players: Player[] }) {
  const { id = '' } = useParams();
  const player = players.find(item => item.id === id);
  const [active, setActive] = useState<SessionSnapshot | null | undefined>(undefined);
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => { heading.current?.focus(); }, [player?.id]);
  useEffect(() => {
    if (!player) return;
    api<SessionSnapshot | null>(`/sessions?player_id=${player.id}`).then(setActive).catch(() => setActive(null));
  }, [player?.id]);
  if (!player) return <section><h2>Профиль не найден</h2><Link to="/">Назад</Link></section>;
  return <section className="home">
    <h2 ref={heading} tabIndex={-1}>Привет, {player.name}!</h2>
    {active ? <p>Есть незаконченное занятие: задача {active.current_problem?.ordinal ?? active.answered_count} из {active.total_problems}.</p> : <p>Сегодня: сложение. {player.session_minutes} минут.</p>}
    <div className="actions">
      <Link className="button big" to={`/children/${player.id}/play`}>{active ? 'Продолжить' : 'Начать'}</Link>
      <Link className="button secondary" to="/">Другой ребёнок</Link>
    </div>
  </section>;
}
