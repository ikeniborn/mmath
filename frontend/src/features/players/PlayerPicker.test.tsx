import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, expect, test, vi } from 'vitest';
import PlayerPicker from './PlayerPicker';

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });  // no vitest globals, so RTL does not clean up on its own

test('child picker names the next action', () => {
  render(<MemoryRouter><PlayerPicker players={[]} onChange={async () => {}} /></MemoryRouter>);
  expect(screen.getByRole('heading', { name: 'Кто сегодня считает?' })).toBeTruthy();
  expect(screen.getByRole('button', { name: 'Создать профиль' })).toBeTruthy();
});

test('a successful creation resets the form without an error', async () => {
  vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify({ id: 'c1' }), { status: 201, headers: { 'Content-Type': 'application/json' } })));
  const onChange = vi.fn(async () => {});
  render(<MemoryRouter><PlayerPicker players={[]} onChange={onChange} /></MemoryRouter>);
  const name = screen.getByRole('textbox', { name: 'Имя' }) as HTMLInputElement;
  fireEvent.change(name, { target: { value: 'Миша' } });
  fireEvent.submit(name.closest('form')!);
  await waitFor(() => expect(onChange).toHaveBeenCalledTimes(1));
  await waitFor(() => expect(name.value).toBe(''));
  expect(screen.queryByRole('alert')).toBeNull();
});
