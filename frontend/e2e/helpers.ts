import { expect, type Page } from '@playwright/test';

export async function registerWithChild(page: Page, prefix: string) {
  await page.goto('/');
  await page.getByRole('button', { name: 'Нет аккаунта? Зарегистрироваться' }).click();
  await page.getByLabel('Электронная почта').fill(`${prefix}-${Date.now()}@example.com`);
  await page.getByLabel('Пароль', { exact: true }).fill('correct horse battery staple');
  await page.getByRole('button', { name: 'Зарегистрироваться' }).click();
  await page.getByLabel('Имя').fill('Миша');
  await page.getByLabel('Возраст').selectOption('6');
  await page.getByRole('button', { name: 'Создать профиль' }).click();
  await page.getByRole('link', { name: 'Играть' }).click();
  await expect(page.getByRole('heading', { name: 'Привет, Миша!' })).toBeVisible();
}

export async function readOperands(page: Page): Promise<[number, number]> {
  const text = await page.locator('.expression').innerText();
  const [a, b] = text.split('=')[0].split(/[+−×]/).map(part => Number(part.trim()));
  return [a, b];
}

export async function readAnswer(page: Page): Promise<number> {
  const text = await page.locator('.expression').innerText();
  const [left] = text.split('=');
  const [a, b] = left.split(/[+−×]/).map(part => Number(part.trim()));
  return left.includes('−') ? a - b : left.includes('×') ? a * b : a + b;
}
