import { fireEvent, render, screen } from '@testing-library/react';
import { expect, test, vi } from 'vitest';
import NumberPad from './NumberPad';

test('keypad exposes every digit, erase and a submit that waits for an entry', () => {
  const onDigit = vi.fn();
  render(<NumberPad disabled={false} canSubmit={false} onDigit={onDigit} onErase={() => {}} onSubmit={() => {}} />);
  for (const digit of '0123456789') expect(screen.getByRole('button', { name: digit })).toBeTruthy();
  fireEvent.click(screen.getByRole('button', { name: '7' }));
  expect(onDigit).toHaveBeenCalledWith('7');
  expect((screen.getByRole('button', { name: 'Ответить' }) as HTMLButtonElement).disabled).toBe(true);
  expect(screen.getByRole('button', { name: 'Стереть' })).toBeTruthy();
});
