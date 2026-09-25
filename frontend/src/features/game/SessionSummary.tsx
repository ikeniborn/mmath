import { Link } from 'react-router-dom';
import type { Player, SessionSnapshot } from '../../api';
import { useT } from '../../i18n';

export default function SessionSummary({ player, snapshot, headingRef, onAgain }: { player: Player; snapshot: SessionSnapshot; headingRef: React.RefObject<HTMLHeadingElement | null>; onAgain: () => void }) {
  const { t } = useT();
  return <section className="game">
    <h2 ref={headingRef} tabIndex={-1}>{t('summary.title')}</h2>
    <p role="status">{t('summary.text', { name: player.name, answered: snapshot.answered_count, total: snapshot.total_problems, correct: snapshot.correct_count })}</p>
    <button type="button" onClick={onAgain}>{t('summary.again')}</button>
    <Link className="button secondary" to={`/children/${player.id}`}>{t('summary.home')}</Link>
  </section>;
}
