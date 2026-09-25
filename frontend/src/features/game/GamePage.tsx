import { useEffect, useReducer, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api, ApiError, type AttemptResult, type Player, type SessionSnapshot } from '../../api';
import { uuidv7 } from '../../uuid';
import { clearPending, loadPending, savePending, type PendingSubmission } from './pendingSubmission';
import { gameReducer, initialState } from './sessionReducer';

export default function GamePage({ players }: { players: Player[] }) {
  const { id = '' } = useParams();
  const player = players.find(item => item.id === id);
  const [state, dispatch] = useReducer(gameReducer, initialState);
  const [message, setMessage] = useState('');
  const activeFrom = useRef(Date.now());
  const heading = useRef<HTMLHeadingElement>(null);
  const { snapshot, entry, status } = state;

  async function submitPending(pending: PendingSubmission) {
    dispatch({ type: 'submitting' });
    try {
      const result = await api<AttemptResult>(`/sessions/${pending.session_id}/attempts`, 'POST', pending.command);
      clearPending();
      dispatch({ type: 'result', result });
      setMessage(result.correct ? 'Верно!' : `Правильный ответ: ${result.feedback.correct_answer}`);
    } catch (cause) {
      if (cause instanceof ApiError && cause.code === 'version_conflict' && cause.detail.snapshot) {
        clearPending();
        dispatch({ type: 'snapshot', snapshot: cause.detail.snapshot as SessionSnapshot });
        setMessage('Ответ уже принят на другом экране. Продолжаем с сохранённого места.');
      } else if (cause instanceof ApiError && cause.code === 'submission_conflict') {
        clearPending();
        dispatch({ type: 'offline' });
        setMessage('Ответ не удалось согласовать. Обновите страницу.');
      } else {
        dispatch({ type: 'offline' });
        setMessage('Нет связи. Ответ сохранён, нажмите «Повторить».');
      }
    }
  }

  async function load() {
    try {
      const started = await api<SessionSnapshot>('/sessions', 'POST', { player_id: id });
      dispatch({ type: 'snapshot', snapshot: started });
      activeFrom.current = Date.now();
      const pending = loadPending(id);
      if (pending && pending.session_id === started.id) await submitPending(pending);
    } catch { dispatch({ type: 'offline' }); setMessage('Нет связи с сервером. Нажмите «Повторить».'); }
  }

  useEffect(() => { if (player) void load(); }, [id, player?.id]);
  useEffect(() => { heading.current?.focus(); }, [snapshot?.phase, snapshot?.state]);

  if (!player) return <section><h2>Профиль не найден</h2><Link to="/">Назад</Link></section>;

  async function submit() {
    if (!snapshot?.current_problem || entry === '' || status !== 'ready') return;
    const pending: PendingSubmission = { player_id: id, session_id: snapshot.id, command: { submission_id: uuidv7(), problem_id: snapshot.current_problem.id, answer: Number(entry), response_ms: Date.now() - activeFrom.current, expected_version: snapshot.version } };
    savePending(pending);
    await submitPending(pending);
  }

  async function advance() {
    if (!snapshot?.last_attempt_id) return;
    try {
      const next = await api<SessionSnapshot>(`/sessions/${snapshot.id}/advance`, 'POST', { attempt_id: snapshot.last_attempt_id, expected_version: snapshot.version });
      dispatch({ type: 'snapshot', snapshot: next });
      activeFrom.current = Date.now();
      setMessage('');
    } catch { dispatch({ type: 'offline' }); setMessage('Нет связи с сервером. Нажмите «Повторить».'); }
  }

  async function finish() {
    if (!snapshot) return;
    try { dispatch({ type: 'snapshot', snapshot: await api<SessionSnapshot>(`/sessions/${snapshot.id}/finish`, 'POST') }); setMessage(''); }
    catch { dispatch({ type: 'offline' }); setMessage('Нет связи с сервером. Нажмите «Повторить».'); }
  }

  function retry() {
    const pending = loadPending(id);
    if (pending && snapshot && pending.session_id === snapshot.id) void submitPending(pending); else void load();
  }

  if (!snapshot) return <section className="game"><h2 ref={heading} tabIndex={-1}>{status === 'offline' ? 'Нет связи' : 'Готовим задачу…'}</h2>{status === 'offline' && <><p role="alert">{message}</p><button onClick={retry}>Повторить</button></>}</section>;

  if (snapshot.state === 'finished') return <section className="game"><h2 ref={heading} tabIndex={-1}>Занятие завершено</h2><p role="status">{player.name}, решено {snapshot.answered_count} из {snapshot.total_problems}, верно {snapshot.correct_count}. Молодец!</p><Link className="button" to="/">К выбору ребёнка</Link></section>;

  const problem = snapshot.current_problem;
  const expression = problem ? `${problem.operand_a} + ${problem.operand_b}` : '';
  return <section className="game" onKeyDown={event => {
    if (snapshot.phase !== 'answer') return;
    if (/^[0-9]$/.test(event.key)) dispatch({ type: 'digit', digit: event.key });
    else if (event.key === 'Backspace') dispatch({ type: 'erase' });
    else if (event.key === 'Enter') void submit();
  }}>
    <h2 ref={heading} tabIndex={-1}>{snapshot.phase === 'answer' ? `Задача ${problem?.ordinal} из ${snapshot.total_problems}` : (snapshot.feedback?.correct ? 'Верно!' : 'Пока не так')}</h2>
    <p className="expression" aria-label={`Пример: ${expression}`}>{expression} = <span className="answer">{snapshot.phase === 'answer' ? (entry || '?') : snapshot.feedback?.submitted_answer}</span></p>
    <p role="status" aria-live="polite">{snapshot.phase === 'feedback' ? (snapshot.feedback?.correct ? 'Верно!' : `Правильный ответ: ${snapshot.feedback?.correct_answer}`) : message}</p>
    {snapshot.phase === 'answer' && <div className="keypad" aria-label="Клавиатура">{['1','2','3','4','5','6','7','8','9','0'].map(digit => <button type="button" key={digit} disabled={status !== 'ready'} onClick={() => dispatch({ type: 'digit', digit })}>{digit}</button>)}<button type="button" disabled={status !== 'ready'} onClick={() => dispatch({ type: 'erase' })}>Стереть</button><button type="button" className="primary" disabled={status !== 'ready' || entry === ''} onClick={submit}>Ответить</button></div>}
    {snapshot.phase === 'feedback' && <button type="button" className="primary" onClick={advance}>{snapshot.answered_count >= snapshot.total_problems ? 'Завершить' : 'Дальше'}</button>}
    {status === 'offline' && <button type="button" onClick={retry}>Повторить</button>}
    <div className="game-footer"><button type="button" className="link" onClick={finish}>Закончить занятие</button><Link to="/">Выйти к выбору ребёнка</Link></div>
  </section>;
}
