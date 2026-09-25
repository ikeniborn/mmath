import type { SessionSnapshot } from '../../api';

type Props = { snapshot: SessionSnapshot; note: string; onAdvance: () => void };

export default function Feedback({ snapshot, note, onAdvance }: Props) {
  const feedback = snapshot.feedback;
  if (!feedback) return null;
  const last = snapshot.answered_count >= snapshot.total_problems || snapshot.active_ms >= snapshot.time_limit_ms;
  return <div className="feedback">
    <p role="status" aria-live="polite">{feedback.correct ? 'Верно! Так держать.' : `Пока не так. Правильный ответ: ${feedback.correct_answer}.`}{note && ` ${note}`}</p>
    <button type="button" className="primary" onClick={onAdvance}>{last ? 'Завершить' : 'Дальше'}</button>
  </div>;
}
