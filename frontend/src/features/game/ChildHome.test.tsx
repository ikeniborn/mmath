import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { expect, test, vi } from 'vitest';
import ChildHome from './ChildHome';

const player = { id: 'p1', name: 'Маша', age: 7, avatar: 'star' as const, topics: ['addition' as const], mode: 'automatic' as const, difficulty_band: 1, session_minutes: 10 as const };

test('child home offers Resume when an unfinished session exists and Start otherwise', async () => {
  const fetchMock = vi.fn().mockResolvedValueOnce(new Response(null, { status: 204 }));
  vi.stubGlobal('fetch', fetchMock);
  render(<MemoryRouter initialEntries={['/children/p1']}><Routes><Route path="/children/:id" element={<ChildHome players={[player]} />} /></Routes></MemoryRouter>);
  await waitFor(() => expect(screen.getByRole('link', { name: 'Начать' })).toBeTruthy());
  fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({ id: 's', answered_count: 3, total_problems: 10, current_problem: { ordinal: 4 } }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
  render(<MemoryRouter initialEntries={['/children/p1']}><Routes><Route path="/children/:id" element={<ChildHome players={[player]} />} /></Routes></MemoryRouter>);
  await waitFor(() => expect(screen.getByRole('link', { name: 'Продолжить' })).toBeTruthy());
  vi.unstubAllGlobals();
});
