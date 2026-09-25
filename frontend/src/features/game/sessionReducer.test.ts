import { expect, test } from 'vitest';
import type { SessionSnapshot } from '../../api';
import { acceptSnapshot, gameReducer, initialState } from './sessionReducer';

const base: SessionSnapshot = { id: 's', player_id: 'p', version: 3, state: 'active', phase: 'answer', current_problem: { id: 'q1', ordinal: 1, skill: 'addition', band: 0, operation: 'addition', operand_a: 2, operand_b: 3 }, feedback: null, hint: null, last_attempt_id: null, active_ms: 0, time_limit_ms: 600000, settings: { mode: 'automatic', difficulty_band: 0, topics: ['addition'], session_minutes: 10 }, answered_count: 0, correct_count: 0, total_problems: 10 };

test('an older snapshot never replaces a newer one', () => {
  const newer = { ...base, version: 4 };
  expect(acceptSnapshot(newer, base)).toBe(newer);
  expect(acceptSnapshot(base, newer)).toBe(newer);
  const state = gameReducer({ ...initialState, snapshot: newer, status: 'ready' }, { type: 'snapshot', snapshot: base });
  expect(state.snapshot?.version).toBe(4);
});

test('entry survives same-problem refresh and resets on a new problem', () => {
  let state = gameReducer(initialState, { type: 'snapshot', snapshot: base });
  state = gameReducer(state, { type: 'digit', digit: '5' });
  state = gameReducer(state, { type: 'snapshot', snapshot: { ...base, version: 3 } });
  expect(state.entry).toBe('5');
  state = gameReducer(state, { type: 'snapshot', snapshot: { ...base, version: 5, current_problem: { ...base.current_problem!, id: 'q2', ordinal: 2 } } });
  expect(state.entry).toBe('');
});

test('digits are ignored outside the answer phase and score is never updated optimistically', () => {
  const feedback = gameReducer(initialState, { type: 'snapshot', snapshot: { ...base, phase: 'feedback' } });
  expect(gameReducer(feedback, { type: 'digit', digit: '1' }).entry).toBe('');
  const submitting = gameReducer(gameReducer(initialState, { type: 'snapshot', snapshot: base }), { type: 'submitting' });
  expect(gameReducer(submitting, { type: 'digit', digit: '1' }).entry).toBe('');
  expect(submitting.snapshot?.correct_count).toBe(0);
});
