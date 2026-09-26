import { renderHook } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import { spokenTask, useSpeech } from './useSpeech';

afterEach(() => { vi.unstubAllGlobals(); });

test('without speechSynthesis the hook is silent and reports unsupported', () => {
  vi.stubGlobal('speechSynthesis', undefined);
  const { result } = renderHook(() => useSpeech('ru'));
  expect(result.current.supported).toBe(false);
  expect(() => result.current.speak('Сколько?')).not.toThrow();
});

test('with a matching voice the hook cancels the previous utterance and speaks in the current language', () => {
  const speak = vi.fn(), cancel = vi.fn();
  vi.stubGlobal('speechSynthesis', { speak, cancel, getVoices: () => [{ lang: 'ru-RU', name: 'Milena' }, { lang: 'en-GB', name: 'Daniel' }] });
  vi.stubGlobal('SpeechSynthesisUtterance', class { text: string; lang = ''; voice: unknown = null; rate = 1; constructor(text: string) { this.text = text; } });
  const { result } = renderHook(() => useSpeech('ru'));
  result.current.speak('Сколько машинок?');
  expect(cancel).toHaveBeenCalled();
  expect(speak.mock.calls[0][0]).toMatchObject({ text: 'Сколько машинок?', lang: 'ru-RU', voice: { name: 'Milena' } });
});

test('spoken task reads arithmetic aloud and leaves early prompts as written', () => {
  expect(spokenTask(['3 + 2 = ', null], 'ru', e => `Сколько будет ${e}?`)).toBe('Сколько будет 3 плюс 2?');
  expect(spokenTask(['5 − 1 = ', null], 'en', e => `What is ${e}?`)).toBe('What is 5 minus 1?');
  expect(spokenTask(['Сколько здесь предметов?'], 'ru', e => e)).toBe('Сколько здесь предметов?');
});
