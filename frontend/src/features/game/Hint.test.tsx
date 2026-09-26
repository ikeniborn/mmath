import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import Hint from './Hint';

test('counters use the chosen theme icons and never show the answer', () => {
  render(<Hint theme="cars" hint={{ kind: 'counters', operation: 'addition', operand_a: 3, operand_b: 2, scale: 10 }} />);
  const image = screen.getByRole('img', { name: 'Подсказка: 3 и ещё 2' });
  expect(image.textContent).toBe('🚗🚗🚗🚙🚙');
  expect(image.textContent).not.toContain('5');
});

test('subtraction counters fade the removed part and construction theme applies', () => {
  render(<Hint theme="construction" hint={{ kind: 'counters', operation: 'subtraction', operand_a: 4, operand_b: 1, scale: 10 }} />);
  expect(screen.getByRole('img', { name: 'Подсказка: было 4, убираем 1' }).textContent).toBe('🚜🚜🚜🚜');
});


test('target scaffold marks both ends and never writes the gap or the quotient', () => {
  render(<Hint theme="flowers" hint={{ kind: 'target', operation: 'addition', operand_a: 7, operand_b: 10, scale: 10 }} />);
  const gap = screen.getByRole('img', { name: 'Подсказка: от 7 до 10 — сколько шагов?' });
  expect(gap.textContent).toContain('Дойди от 7 до 10');
  expect(gap.textContent).not.toMatch(/\b3\b/);
  render(<Hint theme="flowers" hint={{ kind: 'target', operation: 'division', operand_a: 2, operand_b: 36, scale: 50 }} />);
  const jumps = screen.getByRole('img', { name: 'Подсказка: прыгай по 2 до 36 — сколько прыжков?' });
  expect(jumps.textContent).not.toMatch(/\b18\b/);
});
