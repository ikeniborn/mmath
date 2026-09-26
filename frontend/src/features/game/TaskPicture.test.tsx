import { cleanup, render } from '@testing-library/react';
import { afterEach, expect, test } from 'vitest';
import type { PublicProblem } from '../../api';
import TaskPicture, { pictureKind } from './TaskPicture';

afterEach(cleanup);
const base = { id: 'p', ordinal: 1, skill: 'addition', band: 0 };
const add = { ...base, operation: 'addition', operand_a: 3, operand_b: 2, kind: 'result', prompt: null } as PublicProblem;

test('a five-year-old sees the objects of the task; older children and large numbers get no picture', () => {
  expect(pictureKind(add, 5)).toBe('add');
  expect(pictureKind(add, 6)).toBeNull();
  expect(pictureKind({ ...add, operand_a: 8, operand_b: 7 }, 4)).toBeNull();
  expect(pictureKind({ ...add, operation: 'multiplication' }, 4)).toBeNull();
});

test('addition shows both groups, subtraction fades the removed part, missing shows the known part and empty slots', () => {
  const { container: sum } = render(<TaskPicture problem={add} age={4} theme="cars" />);
  expect(sum.querySelector('.task-picture')?.textContent).toBe('🚗🚗🚗+🚙🚙');
  expect(sum.querySelector('.task-picture')?.getAttribute('aria-hidden')).toBe('true');
  const { container: diff } = render(<TaskPicture problem={{ ...add, operation: 'subtraction', operand_a: 5, operand_b: 2 }} age={4} theme="flowers" />);
  expect(diff.querySelectorAll('.task-picture span').length).toBe(5);
  expect(diff.querySelectorAll('.task-picture [class*="faded"]').length).toBe(2);
  const { container: missing } = render(<TaskPicture problem={{ ...add, kind: 'missing', operand_a: 3, operand_b: null, prompt: { blank: 'b', result: 5 } }} age={5} theme="construction" />);
  expect(missing.querySelector('.task-picture')?.textContent).toBe('🚜🚜🚜');
  expect(missing.querySelectorAll('.task-picture [class*="cell"]').length).toBe(2);
});
