import { cleanup, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, expect, test, vi } from 'vitest';
import type { Player, SessionSnapshot } from '../../api';
import SessionSummary from './SessionSummary';

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
const player: Player = { id: 'p1', name: 'Маша', age: 4, avatar: 'star', topics: ['early'], mode: 'automatic', difficulty_band: 0, session_minutes: 10, theme: 'cars', round_tasks: 6 };
const finished = { id: 's1', player_id: 'p1', version: 9, state: 'finished', phase: 'answer', current_problem: null, feedback: null, hint: null, last_attempt_id: null, active_ms: 0, time_limit_ms: 600000, settings: { mode: 'automatic', difficulty_band: 0, topics: ['early'], session_minutes: 10, round_tasks: 6, picture_mode: true }, answered_count: 6, correct_count: 5, total_problems: 6 } as SessionSnapshot;
const progress = (count: number) => new Response(JSON.stringify({ skills: [], sessions: [], total_sessions: count, rewards: { count, latest: count ? `cars-${count}` : null } }), { status: 200, headers: { 'Content-Type': 'application/json' } });

test('a finished round shows the latest sticker of the theme', async () => {
  vi.stubGlobal('fetch', vi.fn(async () => progress(3)));
  render(<MemoryRouter><SessionSummary player={player} snapshot={finished} headingRef={{ current: null }} onAgain={() => {}} /></MemoryRouter>);
  await waitFor(() => expect(screen.getByRole('img', { name: 'cars-3' })).toBeTruthy());
  expect(screen.getByText('Новая наклейка!')).toBeTruthy();
});

test('an abandoned round shows no sticker', async () => {
  vi.stubGlobal('fetch', vi.fn(async () => progress(3)));
  render(<MemoryRouter><SessionSummary player={player} snapshot={{ ...finished, answered_count: 2 }} headingRef={{ current: null }} onAgain={() => {}} /></MemoryRouter>);
  await waitFor(() => expect(screen.getByRole('button', { name: 'Ещё!' })).toBeTruthy());
  expect(screen.queryByText('Новая наклейка!')).toBeNull();
});
