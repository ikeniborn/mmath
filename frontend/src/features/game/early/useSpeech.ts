import { useCallback, useMemo } from 'react';
import type { Lang } from '../../../i18n';

const LOCALE: Record<Lang, string> = { ru: 'ru-RU', en: 'en-GB' };

/** Browser speech only; silent when the API or a matching voice is missing. Never records anything. */
export function useSpeech(lang: Lang) {
  const synth = typeof speechSynthesis === 'undefined' || !speechSynthesis ? null : speechSynthesis;
  const voice = useMemo(() => synth?.getVoices().find(item => item.lang.replace('_', '-').toLowerCase().startsWith(lang)) ?? null, [synth, lang]);
  const speak = useCallback((text: string) => {
    if (!synth || typeof SpeechSynthesisUtterance === 'undefined' || !text) return;
    synth.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = LOCALE[lang];
    if (voice) utterance.voice = voice as SpeechSynthesisVoice;
    utterance.rate = 0.9;
    synth.speak(utterance);
  }, [synth, voice, lang]);
  return { speak, supported: synth !== null };
}

/** What to say for a task: the early prompt as written, or the arithmetic read aloud without the "= ?" tail. */
export function spokenTask(parts: (string | null)[], lang: Lang, wrap: (expression: string) => string): string {
  const text = parts.map(part => part ?? '').join('').trim();
  if (!/[0-9]/.test(text)) return text;
  const expression = text.replace(/\s*=\s*\??\s*$/, '').replace(/\+/g, lang === 'ru' ? ' плюс ' : ' plus ').replace(/−/g, lang === 'ru' ? ' минус ' : ' minus ').replace(/×/g, lang === 'ru' ? ' умножить на ' : ' times ').replace(/\s+/g, ' ').trim();
  return wrap(expression);
}
