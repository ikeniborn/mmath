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
