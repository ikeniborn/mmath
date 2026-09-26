import { expect, test } from 'vitest';
import type { PublicProblem } from '../../api';
import { translate } from '../../i18n';
import { answerLabel, choices, isChoice, promptParts } from './prompt';

const t = (key: Parameters<typeof translate>[1], params?: Record<string, string | number>) => translate('ru', key, params);
const base = { id: 'p', ordinal: 1, skill: 'x', band: 1 };

test('prompts put the answer slot where the blank is and never include the answer', () => {
  expect(promptParts({ ...base, operation: 'addition', operand_a: 3, operand_b: 4, kind: 'result', prompt: null } as PublicProblem, t)).toEqual(['3 + 4 = ', null]);
  expect(promptParts({ ...base, operation: 'addition', operand_a: 3, operand_b: 7, kind: 'missing', prompt: { blank: 'a', result: 10 } } as PublicProblem, t)).toEqual([null, ' + 7 = 10']);
  expect(promptParts({ ...base, operation: 'addition', operand_a: 8, operand_b: 5, kind: 'chain', prompt: { terms: [8, 5, -3] } } as PublicProblem, t)).toEqual(['8 + 5 − 3 = ', null]);
  expect(promptParts({ ...base, operation: 'addition', operand_a: 15, operand_b: 5, kind: 'sequence', prompt: { terms: [5, 10, 15], step: 5 } } as PublicProblem, t)).toEqual(['5, 10, 15, ', null]);
  expect(promptParts({ ...base, operation: 'compare', operand_a: 7, operand_b: 8, kind: 'compare', prompt: { left: '3 + 4', right: '8' } } as PublicProblem, t)).toEqual(['3 + 4 ? 8']);
  expect(promptParts({ ...base, operation: 'remainder', operand_a: 74, operand_b: 9, kind: 'result', prompt: null } as PublicProblem, t)).toEqual(['74 ÷ 9 — какой остаток? ', null]);
});

test('choice kinds expose their options and feedback labels', () => {
  const compare = { ...base, operation: 'compare', operand_a: 1, operand_b: 2, kind: 'compare', prompt: { left: '1', right: '2' } } as PublicProblem;
  expect(isChoice(compare)).toBe(true);
  expect(choices(compare, t).map(choice => choice.label)).toEqual(['<', '=', '>']);
  expect(answerLabel(compare, -1, t)).toBe('<');
  const parity = { ...base, operation: 'parity', operand_a: 7, operand_b: 2, kind: 'parity', prompt: { value: 7 } } as PublicProblem;
  expect(choices(parity, t).map(choice => choice.label)).toEqual(['Чётное', 'Нечётное']);
  expect(answerLabel({ ...base, operation: 'addition', operand_a: 1, operand_b: 2, kind: 'result', prompt: null } as PublicProblem, 3, t)).toBe('3');
});
