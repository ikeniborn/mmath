import { expect, test } from '@playwright/test';
import { readAnswer, registerWithChild } from './helpers';

async function setTopics(page: import('@playwright/test').Page, topics: string[], band: string) {
  await page.goto('/');
  await page.getByRole('link', { name: 'Настройки' }).click();
  for (const topic of ['Сложение', 'Вычитание', 'Счёт и числа', 'Умножение', 'Деление', 'Сравнение']) {
    const box = page.getByLabel(topic);
    if (topics.includes(topic)) await box.check(); else await box.uncheck();
  }
  await page.getByLabel('Сложность').selectOption('fixed');
  await page.getByLabel('Начальный уровень').selectOption(band);
  await page.getByLabel('Пароль родителя для сохранения').fill('correct horse battery staple');
  await page.getByRole('button', { name: 'Сохранить' }).click();
  await expect(page.getByRole('status')).toHaveText('Настройки сохранены');
  await page.getByRole('link', { name: '← К выбору ребёнка' }).click();
  await page.getByRole('link', { name: 'Играть' }).click();
  await page.getByRole('link', { name: 'Начать' }).click();
}

test('comparison tasks are answered with sign buttons and graded', async ({ page }) => {
  await registerWithChild(page, 'compare');
  await setTopics(page, ['Сравнение'], '3');
  await expect(page.locator('.band')).toContainText('Сравнение');
  const text = await page.locator('.expression').innerText();
  const [left, right] = text.split('?').map(part => part.trim());
  const value = (expr: string) => { const tokens = expr.split(' '); let acc = Number(tokens[0]); for (let i = 1; i < tokens.length; i += 2) acc = tokens[i] === '+' ? acc + Number(tokens[i + 1]) : acc - Number(tokens[i + 1]); return acc; };
  const sign = value(left) < value(right) ? '<' : value(left) > value(right) ? '>' : '=';
  await expect(page.getByRole('group', { name: 'Варианты ответа' })).toBeVisible();
  await page.getByRole('button', { name: sign, exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Верно!' })).toBeVisible();
  await page.getByRole('button', { name: 'Дальше' }).click();
  await expect(page.getByRole('heading', { name: 'Задача 2 из 10' })).toBeVisible();
});

test('counting tasks: neighbours are typed, then odd/even and missing sign use buttons', async ({ page }) => {
  await registerWithChild(page, 'counting');
  await setTopics(page, ['Счёт и числа'], '4');
  const seen = new Set<string>();
  for (let index = 0; index < 8; index += 1) {
    await expect(page.getByRole('heading', { name: `Задача ${index + 1} из 10` })).toBeVisible();
    const heading = await page.locator('.band').innerText();
    seen.add(heading.split(' · ')[0]);
    const text = await page.locator('.expression').innerText();
    if (text.includes('чётное')) {
      const n = Number(text.match(/\d+/)?.[0]);
      await page.getByRole('button', { name: n % 2 ? 'Нечётное' : 'Чётное', exact: true }).click();
    } else if (/^\d+ \? \d+ = \d+$/.test(text.trim())) {
      const [a, , b, , result] = text.trim().split(' ').map(Number);
      await page.getByRole('button', { name: a + b === result ? '+' : a - b === result ? '−' : '×', exact: true }).click();
    } else {
      for (const digit of String(await readAnswer(page))) await page.getByRole('button', { name: digit, exact: true }).click();
      await page.getByRole('button', { name: 'Ответить' }).click();
    }
    await expect(page.getByRole('heading', { name: 'Верно!' })).toBeVisible();
    await page.getByRole('button', { name: /Дальше|Завершить/ }).click();
  }
  expect(seen.size).toBeGreaterThanOrEqual(3);
});

test('division and multiplication prompts including remainder are solvable from the screen', async ({ page }) => {
  await registerWithChild(page, 'division');
  await setTopics(page, ['Деление', 'Умножение'], '4');
  for (let index = 0; index < 10; index += 1) {
    await expect(page.getByRole('heading', { name: `Задача ${index + 1} из 10` })).toBeVisible();
    const text = (await page.locator('.expression').innerText()).trim();
    let answer: number;
    const remainder = text.match(/^(\d+) ÷ (\d+) — какой остаток\?$/);
    const quotient = text.match(/^(\d+) ÷ (\d+) — сколько целых раз\?$/);
    if (remainder) answer = Number(remainder[1]) % Number(remainder[2]);
    else if (quotient) answer = Math.floor(Number(quotient[1]) / Number(quotient[2]));
    else answer = await readAnswer(page);
    for (const digit of String(answer)) await page.getByRole('button', { name: digit, exact: true }).click();
    await page.getByRole('button', { name: 'Ответить' }).click();
    await expect(page.getByRole('heading', { name: 'Верно!' })).toBeVisible();
    await page.getByRole('button', { name: /Дальше|Завершить/ }).click();
  }
  await expect(page.getByRole('heading', { name: 'Занятие завершено' })).toBeVisible();
  await expect(page.getByRole('status')).toContainText('решено 10 из 10, верно 10');
});
