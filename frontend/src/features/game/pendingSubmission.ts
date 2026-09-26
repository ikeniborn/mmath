/** Exactly one in-flight answer per tab, kept until the server acknowledges it. Not an offline queue. */
const KEY = 'mmath.pending-submission';

export type PendingSubmission = {
  player_id: string;
  session_id: string;
  command: { submission_id: string; problem_id: string; answer: number; response_ms: number | null; expected_version: number };
};

export function savePending(pending: PendingSubmission) { sessionStorage.setItem(KEY, JSON.stringify(pending)); }
export function clearPending() { sessionStorage.removeItem(KEY); }

export function loadPending(playerId: string): PendingSubmission | null {
  const raw = sessionStorage.getItem(KEY);
  if (!raw) return null;
  try {
    const pending = JSON.parse(raw) as PendingSubmission;
    if (pending.player_id !== playerId) { clearPending(); return null; }
    return pending;
  } catch { clearPending(); return null; }
}
