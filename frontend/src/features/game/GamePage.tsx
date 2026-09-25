import { useEffect, useReducer, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api, ApiError, type AttemptResult, type HintResult, type Player, type SessionSnapshot } from '../../api';
import { uuidv7 } from '../../uuid';
import Feedback from './Feedback';
import Hint from './Hint';
import NumberPad from './NumberPad';
import SessionSummary from './SessionSummary';
import { clearPending, loadPending, savePending, type PendingSubmission } from './pendingSubmission';
import { gameReducer, initialState } from './sessionReducer';
import { expression as formatExpression } from './labels';
import { useT } from '../../i18n';

/** Foreground time for the current task: counts only while the tab is visible. */
function useActiveTimer(problemId: string | undefined) {
  const accumulated = useRef(0);
  const visibleSince = useRef<number | null>(document.visibilityState === 'visible' ? Date.now() : null);
  useEffect(() => { accumulated.current = 0; visibleSince.current = document.visibilityState === 'visible' ? Date.now() : null; }, [problemId]);
  useEffect(() => {
    const onChange = () => {
      if (document.visibilityState === 'visible') visibleSince.current = Date.now();
      else if (visibleSince.current !== null) { accumulated.current += Date.now() - visibleSince.current; visibleSince.current = null; }
    };
    document.addEventListener('visibilitychange', onChange);
    return () => document.removeEventListener('visibilitychange', onChange);
  }, []);
  return () => accumulated.current + (visibleSince.current === null ? 0 : Date.now() - visibleSince.current);
}

export default function GamePage({ players }: { players: Player[] }) {
  const { t, name } = useT();
  const { id = '' } = useParams();
  const player = players.find(item => item.id === id);
  const [state, dispatch] = useReducer(gameReducer, initialState);
  const [message, setMessage] = useState('');
  const heading = useRef<HTMLHeadingElement>(null);
  const { snapshot, entry, status } = state;
  const elapsed = useActiveTimer(snapshot?.current_problem?.id);

  function fail(cause: unknown) {
    dispatch({ type: 'offline' });
    setMessage(cause instanceof ApiError && cause.code !== 'request_failed' ? t('game.failed') : t('game.offlineText'));
  }

  async function submitPending(pending: PendingSubmission) {
    dispatch({ type: 'submitting' });
    try {
      const result = await api<AttemptResult>(`/sessions/${pending.session_id}/attempts`, 'POST', pending.command);
      clearPending();
      dispatch({ type: 'result', result });
      setMessage('');
    } catch (cause) {
      if (cause instanceof ApiError && cause.code === 'version_conflict' && cause.detail.snapshot) {
        clearPending();
        dispatch({ type: 'snapshot', snapshot: cause.detail.snapshot as SessionSnapshot });
        setMessage(t('game.reconciled'));
      } else if (cause instanceof ApiError && cause.code === 'submission_conflict') {
        clearPending();
        fail(cause);
      } else {
        dispatch({ type: 'offline' });
        setMessage(t('game.saved'));
      }
    }
  }

  async function load() {
    try {
      const started = await api<SessionSnapshot>('/sessions', 'POST', { player_id: id });
      dispatch({ type: 'snapshot', snapshot: started });
      const pending = loadPending(id);
      if (pending && pending.session_id === started.id) await submitPending(pending);
    } catch (cause) { fail(cause); }
  }

  useEffect(() => { if (player) void load(); }, [id, player?.id]);
  useEffect(() => { heading.current?.focus(); }, [snapshot?.phase, snapshot?.state, snapshot?.current_problem?.id]);

  if (!player) return <section><h2>{t('notFound.title')}</h2><Link to="/">{t('notFound.back')}</Link></section>;

  async function submit() {
    if (!snapshot?.current_problem || entry === '' || status !== 'ready') return;
    const pending: PendingSubmission = { player_id: id, session_id: snapshot.id, command: { submission_id: uuidv7(), problem_id: snapshot.current_problem.id, answer: Number(entry), response_ms: elapsed(), expected_version: snapshot.version } };
    savePending(pending);
    await submitPending(pending);
  }

  async function withSnapshot(call: () => Promise<SessionSnapshot>) {
    try { dispatch({ type: 'snapshot', snapshot: await call() }); setMessage(''); }
    catch (cause) {
      if (cause instanceof ApiError && cause.code === 'version_conflict' && cause.detail.snapshot) { dispatch({ type: 'snapshot', snapshot: cause.detail.snapshot as SessionSnapshot }); setMessage(t('game.refreshed')); }
      else fail(cause);
    }
  }

  const advance = () => snapshot?.last_attempt_id && withSnapshot(() => api<SessionSnapshot>(`/sessions/${snapshot.id}/advance`, 'POST', { attempt_id: snapshot.last_attempt_id, expected_version: snapshot.version }));
  const finish = () => snapshot && withSnapshot(() => api<SessionSnapshot>(`/sessions/${snapshot.id}/finish`, 'POST'));
  const hint = () => snapshot?.current_problem && withSnapshot(async () => (await api<HintResult>(`/sessions/${snapshot.id}/hint`, 'POST', { problem_id: snapshot.current_problem!.id, expected_version: snapshot.version })).session);

  function retry() {
    const pending = loadPending(id);
    if (pending && snapshot && pending.session_id === snapshot.id) void submitPending(pending); else void load();
  }

  if (!snapshot) return <section className="game"><h2 ref={heading} tabIndex={-1}>{status === 'offline' ? t('game.offline') : t('game.preparing')}</h2>{status === 'offline' && <><p role="alert">{message}</p><button type="button" onClick={retry}>{t('app.retry')}</button></>}</section>;
  if (snapshot.state === 'finished') return <SessionSummary player={player} snapshot={snapshot} headingRef={heading} />;

  const problem = snapshot.current_problem;
  const expression = problem ? formatExpression(problem.operation, problem.operand_a, problem.operand_b) : '';
  const answering = snapshot.phase === 'answer';
  return <section className="game" onKeyDown={event => {
    if (!answering || status !== 'ready') return;
    if (/^[0-9]$/.test(event.key)) dispatch({ type: 'digit', digit: event.key });
    else if (event.key === 'Backspace') dispatch({ type: 'erase' });
    else if (event.key === 'Enter') void submit();
  }}>
    <h2 ref={heading} tabIndex={-1}>{answering ? t('game.task', { n: problem?.ordinal ?? 0, total: snapshot.total_problems }) : (snapshot.feedback?.correct ? t('game.correct') : t('game.wrong'))}</h2>
    {problem && <p className="band">{t('game.level', { skill: name('skill', problem.skill), band: problem.band })}</p>}
    <p className="expression" aria-label={t('game.expression', { expression })}>{expression} = <span className="answer">{answering ? (entry || '?') : snapshot.feedback?.submitted_answer}</span></p>
    {answering && snapshot.hint && <Hint hint={snapshot.hint} theme={player.theme} />}
    {answering ? <>
      <p role="status" aria-live="polite">{message}</p>
      <NumberPad disabled={status !== 'ready'} canSubmit={entry !== ''} onDigit={digit => dispatch({ type: 'digit', digit })} onErase={() => dispatch({ type: 'erase' })} onSubmit={submit} />
      {!snapshot.hint && <button type="button" className="secondary" disabled={status !== 'ready'} onClick={hint}>{t('game.hint')}</button>}
    </> : <Feedback snapshot={snapshot} note={message} onAdvance={advance} />}
    {status === 'offline' && <button type="button" onClick={retry}>{t('app.retry')}</button>}
    <div className="game-footer"><button type="button" className="link" onClick={finish}>{t('game.finish')}</button><Link to={`/children/${player.id}`}>{t('game.exit')}</Link></div>
  </section>;
}
