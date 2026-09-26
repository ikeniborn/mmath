import { useEffect, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api, type Player, type ProgressView, type SessionSnapshot } from '../../api';
import { Sticker } from '../../assets/themes';
import { useT } from '../../i18n';

const SHELF = 8;

export default function ChildHome({ players }: { players: Player[] }) {
  const { t, name } = useT();
  const { id = '' } = useParams();
  const player = players.find(item => item.id === id);
  const [active, setActive] = useState<SessionSnapshot | null | undefined>(undefined);
  const [rewards, setRewards] = useState<ProgressView['rewards'] | null>(null);
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => { heading.current?.focus(); }, [player?.id]);
  useEffect(() => {
    if (!player) return;
    api<SessionSnapshot | null>(`/sessions?player_id=${player.id}`).then(setActive).catch(() => setActive(null));
    api<ProgressView>(`/players/${player.id}/progress?limit=1`).then(progress => setRewards(progress.rewards)).catch(() => setRewards(null));
  }, [player?.id]);
  if (!player) return <section><h2>{t('notFound.title')}</h2><Link to="/">{t('notFound.back')}</Link></section>;
  const mode = player.mode === 'fixed' ? t('home.modeFixed', { band: player.difficulty_band ?? 0 }) : t('home.modeAuto');
  return <section className="home">
    <h2 ref={heading} tabIndex={-1}>{t('home.greeting', { name: player.name })}</h2>
    {active ? <p>{t('home.unfinished', { n: active.current_problem?.ordinal ?? active.answered_count, total: active.total_problems })}</p> : <p>{t('home.summary', { minutes: player.session_minutes, mode, theme: name('theme', player.theme) })}</p>}
    {rewards && rewards.count > 0 && <div className="shelf" aria-label={t('home.stickers', { n: rewards.count })}>
      <p>{t('home.stickers', { n: rewards.count })}</p>
      <ul>{Array.from({ length: Math.min(rewards.count, SHELF) }, (_, index) => <li key={index}><Sticker code={`${player.theme}-${index + 1}`} /></li>)}</ul>
    </div>}
    <div className="actions">
      <Link className="button big" to={`/children/${player.id}/play`}>{active ? t('home.resume') : t('home.start')}</Link>
      <Link className="button secondary" to={`/children/${player.id}/progress`}>{t('home.progress')}</Link>
      <Link className="button secondary" to="/">{t('home.other')}</Link>
    </div>
  </section>;
}
