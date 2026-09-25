import { Link } from 'react-router-dom';
import type { Player, SessionSnapshot } from '../../api';

export default function SessionSummary({ player, snapshot, headingRef }: { player: Player; snapshot: SessionSnapshot; headingRef: React.RefObject<HTMLHeadingElement | null> }) {
  return <section className="game">
    <h2 ref={headingRef} tabIndex={-1}>Занятие завершено</h2>
    <p role="status">{player.name}, решено {snapshot.answered_count} из {snapshot.total_problems}, верно {snapshot.correct_count}. Молодец!</p>
    <Link className="button" to={`/children/${player.id}`}>К домику</Link>
  </section>;
}
