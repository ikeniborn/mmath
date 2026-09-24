import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { expect, test } from 'vitest';
import PlayerPicker from './PlayerPicker';

test('child picker names the next action', () => {
  render(<MemoryRouter><PlayerPicker players={[]} onChange={async () => {}} /></MemoryRouter>);
  expect(screen.getByRole('heading', { name: 'Кто сегодня считает?' })).toBeTruthy();
  expect(screen.getByRole('button', { name: 'Создать профиль' })).toBeTruthy();
});
