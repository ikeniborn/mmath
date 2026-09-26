import type { SessionSnapshot } from '../../api';
import { useT } from '../../i18n';
import { answerLabel } from './prompt';

type Props = { snapshot: SessionSnapshot; note: string; onAdvance: () => void };

export default function Feedback({ snapshot, note, onAdvance }: Props) {
  const { t } = useT();
  const feedback = snapshot.feedback;
  if (!feedback) return null;
  const last = snapshot.answered_count >= snapshot.total_problems || snapshot.active_ms >= snapshot.time_limit_ms;
  return <div className="feedback">
    <p role="status" aria-live="polite">{feedback.correct ? t('feedback.correct') : t('feedback.wrong', { answer: answerLabel(snapshot.current_problem, feedback.correct_answer, t) })}{note && ` ${note}`}</p>
    <button type="button" className="primary" onClick={onAdvance}>{last ? t('feedback.finish') : t('feedback.next')}</button>
  </div>;
}
