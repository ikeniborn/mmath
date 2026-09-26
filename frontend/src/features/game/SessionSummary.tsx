import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, type Player, type ProgressView, type SessionSnapshot } from '../../api';
import { Sticker } from '../../assets/themes';
import { useT } from '../../i18n';

export default function SessionSummary({ player, snapshot, headingRef, onAgain }: { player: Player; snapshot: SessionSnapshot; headingRef: React.RefObject<HTMLHeadingElement | null>; onAgain: () => void }) {
  const { t } = useT();
  const [rewards, setRewards] = useState<ProgressView['rewards'] | null>(null);
  useEffect(() => {
    api<ProgressView>(`/players/${player.id}/progress?limit=1`).then(progress => setRewards(progress.rewards)).catch(() => setRewards(null));
  }, [player.id, snapshot.id]);
  // A round earns a reward when at least half of its tasks were answered; the server derived the latest sticker code.
  const earned = snapshot.answered_count * 2 >= snapshot.total_problems && rewards?.latest ? rewards.latest : null;
  return <section className="game">
    <h2 ref={headingRef} tabIndex={-1}>{t('summary.title')}</h2>
    <p role="status">{t('summary.text', { name: player.name, answered: snapshot.answered_count, total: snapshot.total_problems, correct: snapshot.correct_count })}</p>
    {earned && <div className="sticker-new"><Sticker code={earned} className="sticker-big" /><p>{t('summary.sticker')}</p></div>}
    <button type="button" onClick={onAgain}>{t('summary.again')}</button>
    <Link className="button secondary" to={`/children/${player.id}`}>{t('summary.home')}</Link>
  </section>;
}
