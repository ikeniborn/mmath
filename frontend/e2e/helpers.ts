import { expect, type Page } from '@playwright/test';

export async function registerWithChild(page: Page, prefix: string, age = '6') {
  await page.goto('/');
  await page.getByRole('button', { name: 'Нет аккаунта? Зарегистрироваться' }).click();
  await page.getByLabel('Электронная почта').fill(`${prefix}-${Date.now()}@example.com`);
  await page.getByLabel('Пароль', { exact: true }).fill('correct horse battery staple');
  await page.getByRole('button', { name: 'Зарегистрироваться' }).click();
  await page.getByLabel('Имя').fill('Миша');
  await page.getByLabel('Возраст').selectOption(age);
  await page.getByRole('button', { name: 'Создать профиль' }).click();
  await page.getByRole('link', { name: 'Играть' }).click();
  await expect(page.getByRole('heading', { name: 'Привет, Миша!' })).toBeVisible();
}

export async function readOperands(page: Page): Promise<[number, number]> {
  const text = await page.locator('.expression').innerText();
  const [a, b] = text.split('=')[0].split(/[+−×]/).map(part => Number(part.trim()));
  return [a, b];
}

/** Solves the displayed numeric prompt: result, missing operand, chains and sequences. */
export async function readAnswer(page: Page): Promise<number> {
  const text = (await page.locator('.expression').innerText()).replace(/\s+/g, ' ').trim();
  if (text.includes(',')) {
    const terms = text.split(',').map(part => Number(part.trim())).filter(value => !Number.isNaN(value));
    return terms[terms.length - 1] + (terms[1] - terms[0]);
  }
  const [left, right] = text.split('=').map(part => part.trim());
  const tokens = left.split(' ');
  const apply = (acc: number, op: string, value: number) => op === '+' ? acc + value : op === '−' ? acc - value : op === '×' ? acc * value : Math.floor(acc / value);
  if (left.includes('?')) {
    const [a, op, b] = tokens;
    const result = Number(right);
    if (a === '?') return op === '+' ? result - Number(b) : op === '−' ? result + Number(b) : op === '×' ? result / Number(b) : result * Number(b);
    return op === '+' ? result - Number(a) : op === '−' ? Number(a) - result : op === '×' ? result / Number(a) : Number(a) / result;
  }
  let acc = Number(tokens[0]);
  for (let index = 1; index < tokens.length; index += 2) acc = apply(acc, tokens[index], Number(tokens[index + 1]));
  return acc;
}
