import { act, cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import type { PublicProblem } from '../../../api';
import EarlyTask, { hasEarlyInput } from './EarlyTask';

afterEach(cleanup);
const base = { id: 'p', ordinal: 1, band: 0, operand_a: 0, operand_b: 0 };
const items = [{ x: 0, y: 0, icon: 0 }, { x: 1, y: 0, icon: 0 }, { x: 2, y: 1, icon: 0 }];

test('count: tapping each object once and pressing done submits the count', () => {
  const onAnswer = vi.fn();
  render(<EarlyTask problem={{ ...base, skill: 'count_objects', operation: 'count', kind: 'count', prompt: { items } } as PublicProblem} theme="cars" onAnswer={onAnswer} disabled={false} />);
  const objects = screen.getAllByRole('button', { name: /предмет/i });
  expect(objects).toHaveLength(3);
  fireEvent.click(objects[0]); fireEvent.click(objects[0]); fireEvent.click(objects[2]);  // a second tap on the same object unmarks it
  expect(screen.getByText('1')).toBeTruthy();
  fireEvent.click(objects[0]);
  expect(screen.getByText('2')).toBeTruthy();
  fireEvent.click(screen.getByRole('button', { name: 'Готово' }));
  expect(onAnswer).toHaveBeenCalledWith(2);
});

test('subitize: the scene hides after reveal_ms and a card submits its value; cards never mark the answer', () => {
  vi.useFakeTimers();
  const onAnswer = vi.fn();
  const { container } = render(<EarlyTask problem={{ ...base, skill: 'quick_look', operation: 'subitize', kind: 'subitize', prompt: { items, reveal_ms: 1500, options: [4, 3, 5] } } as PublicProblem} theme="flowers" onAnswer={onAnswer} disabled={false} />);
  expect(container.querySelectorAll('[data-object]')).toHaveLength(3);
  act(() => { vi.advanceTimersByTime(1500); });
  vi.useRealTimers();
  expect(container.querySelector('[data-hidden="true"]')).toBeTruthy();
  const cards = screen.getAllByRole('button', { name: /карточка/i });
  expect(new Set(cards.map(card => card.className)).size).toBe(1);
  fireEvent.click(cards[1]);
  expect(onAnswer).toHaveBeenCalledWith(3);
});

test('order: tapping towers submits the tap order as one-based indices; reset clears', () => {
  const onAnswer = vi.fn();
  render(<EarlyTask problem={{ ...base, skill: 'order_size', operation: 'order', kind: 'order', prompt: { heights: [3, 1, 2] } } as PublicProblem} theme="construction" onAnswer={onAnswer} disabled={false} />);
  const towers = screen.getAllByRole('button', { name: /башня/i });
  fireEvent.click(towers[1]); fireEvent.click(screen.getByRole('button', { name: 'Сначала' })); fireEvent.click(towers[1]); fireEvent.click(towers[2]); fireEvent.click(towers[0]);
  expect(onAnswer).toHaveBeenCalledTimes(1);
  expect(onAnswer).toHaveBeenCalledWith(231);
});

test('pick and pattern submit indices; frame offers cards and draws filled and empty cells', () => {
  const onAnswer = vi.fn();
  render(<EarlyTask problem={{ ...base, skill: 'find_shape', operation: 'pick', kind: 'pick', prompt: { attribute: 'shape', target: 'circle', items: [{ shape: 'square', size: 2 }, { shape: 'circle', size: 1 }, { shape: 'triangle', size: 3 }] } } as PublicProblem} theme="dolls" onAnswer={onAnswer} disabled={false} />);
  fireEvent.click(screen.getAllByRole('button', { name: /фигура/i })[1]);
  expect(onAnswer).toHaveBeenLastCalledWith(1);
  cleanup();
  render(<EarlyTask problem={{ ...base, skill: 'what_next', operation: 'pattern', kind: 'pattern', prompt: { sequence: [0, 1, 0, 1, 0], options: [2, 1, 0] } } as PublicProblem} theme="dolls" onAnswer={onAnswer} disabled={false} />);
  fireEvent.click(screen.getAllByRole('button', { name: /карточка/i })[1]);
  expect(onAnswer).toHaveBeenLastCalledWith(1);
  cleanup();
  const frame = render(<EarlyTask problem={{ ...base, skill: 'five_frame', operation: 'frame', kind: 'frame', prompt: { size: 5, filled: 2, options: [3, 1, 4] } } as PublicProblem} theme="dolls" onAnswer={onAnswer} disabled={false} />);
  expect(frame.container.querySelectorAll('[data-cell="filled"]')).toHaveLength(2);
  expect(frame.container.querySelectorAll('[data-cell="empty"]')).toHaveLength(3);
});

test('a numeric task with options gets number cards; without options nothing replaces the keypad', () => {
  const onAnswer = vi.fn();
  const addition = { ...base, skill: 'addition', operation: 'addition', kind: 'result', operand_a: 2, operand_b: 3, prompt: { options: [6, 5, 4] } } as PublicProblem;
  expect(hasEarlyInput(addition)).toBe(true);
  expect(hasEarlyInput({ ...addition, prompt: null })).toBe(false);
  render(<EarlyTask problem={addition} theme="cars" onAnswer={onAnswer} disabled={false} />);
  fireEvent.click(screen.getAllByRole('button', { name: /карточка/i })[1]);
  expect(onAnswer).toHaveBeenCalledWith(5);
});
