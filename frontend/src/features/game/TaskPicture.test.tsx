import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import type { PublicProblem } from '../../api';
import TaskPicture, { pictureKind } from './TaskPicture';

afterEach(cleanup);
const base = { id: 'p', ordinal: 1, skill: 'addition', band: 0 };
const add = { ...base, operation: 'addition', operand_a: 3, operand_b: 2, kind: 'result', prompt: null } as PublicProblem;

test('picture mode decides the scene; outside picture mode and for large numbers there is none', () => {
  expect(pictureKind(add, true)).toBe('add');
  expect(pictureKind(add, false)).toBeNull();
  expect(pictureKind({ ...add, operand_a: 8, operand_b: 7 }, true)).toBeNull();
  expect(pictureKind({ ...add, operation: 'multiplication' }, true)).toBeNull();
});

test('addition fills a basket, subtraction fades the leaving part, missing hides the blanked objects behind a garage', () => {
  const { container: sum } = render(<TaskPicture problem={add} theme="cars" picture />);
  expect(sum.querySelectorAll('.task-picture svg').length).toBe(5);
  expect(sum.querySelector('.task-picture')?.textContent).toBe('+');
  expect(sum.querySelector('[data-basket]')).toBeTruthy();
  expect(sum.querySelector('.task-picture')?.getAttribute('aria-hidden')).toBe('true');
  const { container: diff } = render(<TaskPicture problem={{ ...add, operation: 'subtraction', operand_a: 5, operand_b: 2 }} theme="flowers" picture />);
  expect(diff.querySelectorAll('.task-picture svg').length).toBe(5);
  expect(diff.querySelectorAll('.task-picture [class*="faded"]').length).toBe(2);
  const { container: missing } = render(<TaskPicture problem={{ ...add, kind: 'missing', operand_a: 3, operand_b: null, prompt: { blank: 'b', result: 5 } }} theme="construction" picture />);
  expect(missing.querySelectorAll('.task-picture svg').length).toBe(3);
  expect(missing.querySelectorAll('.task-picture [class*="cell"]').length).toBe(2);
  expect(missing.querySelector('[data-garage]')).toBeTruthy();
});

test('compare draws two tappable piles and a same card; the piles submit 1 / -1, the card 0', () => {
  const onAnswer = vi.fn();
  render(<TaskPicture problem={{ ...add, skill: 'compare', operation: 'compare', kind: 'compare', operand_a: 3, operand_b: 5, prompt: { left: '3', right: '5' } }} theme="cars" picture onAnswer={onAnswer} disabled={false} />);
  const piles = screen.getAllByRole('button', { name: /кучка/i });
  expect(piles[0].querySelectorAll('svg').length).toBe(3);
  expect(piles[1].querySelectorAll('svg').length).toBe(5);
  fireEvent.click(piles[1]);
  expect(onAnswer).toHaveBeenCalledWith(-1);
  fireEvent.click(screen.getByRole('button', { name: 'Одинаково' }));
  expect(onAnswer).toHaveBeenLastCalledWith(0);
});

test('parity draws pairs with the odd one out and Yes/No cards', () => {
  const onAnswer = vi.fn();
  const { container } = render(<TaskPicture problem={{ ...add, skill: 'odd_even', operation: 'parity', kind: 'parity', operand_a: 5, operand_b: 0, prompt: { value: 5 } }} theme="flowers" picture onAnswer={onAnswer} disabled={false} />);
  expect(container.querySelectorAll('[data-pair]').length).toBe(3);
  expect(container.querySelectorAll('[data-pair] svg').length).toBe(5);
  fireEvent.click(screen.getByRole('button', { name: 'Нет' }));
  expect(onAnswer).toHaveBeenCalledWith(1);
});

test('neighbour draws three carriages with the asked one empty', () => {
  const { container } = render(<TaskPicture problem={{ ...add, skill: 'neighbour_one', operand_a: 4, operand_b: 1 }} theme="cars" picture />);
  const carriages = container.querySelectorAll('[data-carriage]');
  expect(carriages.length).toBe(3);
  expect(Array.from(carriages).map(node => node.textContent)).toEqual(['3', '4', '?']);
  const { container: minus } = render(<TaskPicture problem={{ ...add, skill: 'neighbour_one', operation: 'subtraction', operand_a: 4, operand_b: 1 }} theme="cars" picture />);
  expect(Array.from(minus.querySelectorAll('[data-carriage]')).map(node => node.textContent)).toEqual(['?', '4', '5']);
});
