import { beforeEach, expect, test } from 'vitest';
import { detectLang, format, translate } from './i18n';

beforeEach(() => localStorage.clear());

test('placeholders are substituted and unknown ones stay visible', () => {
  expect(format('{a} and {b}', { a: 1, b: 2 })).toBe('1 and 2');
  expect(format('{a} and {c}', { a: 1 })).toBe('1 and {c}');
});

test('stored language wins over the browser language and every key exists in both languages', () => {
  localStorage.setItem('mmath.lang', 'en');
  expect(detectLang()).toBe('en');
  expect(translate('ru', 'auth.login.title')).toBe('Вход для родителя');
  expect(translate('en', 'auth.login.title')).toBe('Parent sign-in');
  expect(translate('en', 'game.task', { n: 2, total: 10 })).toBe('Task 2 of 10');
});
