import { useEffect, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api, type Player, type ProgressView } from '../../api';
import { useT } from '../../i18n';

export default function ProgressPage({ players }: { players: Player[] }) {
  const { t, name, lang } = useT();
  const { id = '' } = useParams();
  const player = players.find(item => item.id === id);
  const [progress, setProgress] = useState<ProgressView | null>(null);
  const [error, setError] = useState('');
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => { heading.current?.focus(); }, [player?.id]);
  useEffect(() => {
    if (!player) return;
    api<ProgressView>(`/players/${player.id}/progress?limit=10`).then(setProgress).catch(() => setError(t('progress.error')));
  }, [player?.id]);
  if (!player) return <section><h2>{t('notFound.title')}</h2><Link to="/">{t('notFound.back')}</Link></section>;
  return <section className="progress">
    <Link to={`/children/${player.id}`}>{t('progress.back')}</Link>
    <h2 ref={heading} tabIndex={-1}>{t('progress.title', { name: player.name })}</h2>
    {error && <p role="alert">{error}</p>}
    {progress && progress.skills.length === 0 && <p>{t('progress.empty')}</p>}
    {progress && progress.skills.length > 0 && <table className="card"><caption>{t('progress.skills')}</caption><thead><tr><th scope="col">{t('progress.skill')}</th><th scope="col">{t('progress.level')}</th><th scope="col">{t('progress.solved')}</th><th scope="col">{t('progress.correct')}</th><th scope="col">{t('progress.mastery')}</th></tr></thead><tbody>
      {progress.skills.map(skill => <tr key={skill.skill}><th scope="row">{name('skill', skill.skill)}</th><td>{skill.band}</td><td>{skill.attempts}</td><td>{skill.correct}</td><td>{skill.mastery === null ? '—' : `${Math.round(skill.mastery * 100)}%`}</td></tr>)}
    </tbody></table>}
    {progress && progress.sessions.length > 0 && <><h3>{t('progress.sessions')}</h3><ul className="sessions">{progress.sessions.map(session => <li key={session.id} className="card"><span>{new Date(session.started_at).toLocaleDateString(lang === 'ru' ? 'ru-RU' : 'en-GB')}</span><span>{session.state === 'finished' ? t('progress.finished') : t('progress.unfinished')}</span><span>{t('progress.stats', { answered: session.answered_count, correct: session.correct_count })}</span><span>{session.settings.mode === 'fixed' ? t('progress.modeFixed', { band: session.settings.difficulty_band as number }) : t('progress.modeAuto')}</span></li>)}</ul></>}
  </section>;
}
