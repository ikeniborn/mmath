import { expect, test } from 'vitest';
import { uuidv7 } from './uuid';

test('uuidv7 carries version 7, variant bits and the millisecond timestamp prefix', () => {
  const at = 1_800_000_000_000;
  const id = uuidv7(at);
  expect(id).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
  expect(parseInt(id.replace(/-/g, '').slice(0, 12), 16)).toBe(at);
  expect(uuidv7(at) < uuidv7(at + 1)).toBe(true);
});
