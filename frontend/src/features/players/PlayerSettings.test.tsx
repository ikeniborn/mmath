import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, expect, test, vi } from 'vitest';
import type { Player } from '../../api';
import PlayerSettings from './PlayerSettings';

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
const player: Player = { id: 'p1', name: 'Маша', age: 4, avatar: 'star', topics: ['early', 'addition'], mode: 'automatic', difficulty_band: 0, session_minutes: 10, theme: 'cars', round_tasks: 6 };

test('the settings form sends round_tasks and keeps the early topic', async () => {
  const bodies: unknown[] = [];
  vi.stubGlobal('fetch', vi.fn(async (_url: string, init?: RequestInit) => { bodies.push(init?.body ? JSON.parse(String(init.body)) : null); return new Response(init?.method === 'PATCH' ? JSON.stringify(player) : null, { status: init?.method === 'PATCH' ? 200 : 204, headers: { 'Content-Type': 'application/json' } }); }));
  render(<MemoryRouter initialEntries={['/children/p1/settings']}><Routes><Route path="/children/:id/settings" element={<PlayerSettings players={[player]} onChange={async () => {}} />} /></Routes></MemoryRouter>);
  const round = screen.getByLabelText('Задач в раунде') as HTMLSelectElement;
  expect(round.value).toBe('6');
  expect((screen.getByLabelText('Малышам') as HTMLInputElement).checked).toBe(true);
  fireEvent.change(round, { target: { value: '10' } });
  fireEvent.change(screen.getByLabelText('Пароль родителя для сохранения'), { target: { value: 'correct horse battery staple' } });
  fireEvent.submit(round.closest('form')!);
  await waitFor(() => expect(bodies.length).toBe(2));
  expect(bodies[1]).toMatchObject({ round_tasks: 10, topics: ['early', 'addition'] });
});
