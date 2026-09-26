import { expect, test, type Page } from '@playwright/test';
import { readAnswer, registerWithChild } from './helpers';

async function answer(page: Page, correct: boolean) {
  const value = (await readAnswer(page)) + (correct ? 0 : 100);
  for (const digit of String(value)) await page.getByRole('button', { name: digit, exact: true }).click();
  await page.getByRole('button', { name: 'Ответить' }).click();
  await page.getByRole('button', { name: /Дальше|Завершить/ }).click();
}

test('fixed difficulty keeps its band through errors and the progress page shows the skill', async ({ page }) => {
  await registerWithChild(page, 'fixed');
  await page.goto('/');
  await page.getByRole('link', { name: 'Настройки' }).click();
  await page.getByLabel('Сложность').selectOption('fixed');
  await page.getByLabel('Начальный уровень').selectOption('2');
  await page.getByLabel('Оформление').selectOption('construction');
  await page.getByLabel('Пароль родителя для сохранения').fill('correct horse battery staple');
  await page.getByRole('button', { name: 'Сохранить' }).click();
  await expect(page.getByRole('status')).toHaveText('Настройки сохранены');
  await page.getByRole('link', { name: '← К выбору ребёнка' }).click();
  await page.getByRole('link', { name: 'Играть' }).click();
  await expect(page.getByText(/фиксированный уровень 2 · Стройтехника/)).toBeVisible();
  await page.getByRole('link', { name: 'Начать' }).click();
  await expect(page.locator('.band')).toContainText('Уровень 2');
  for (let index = 0; index < 3; index += 1) await answer(page, false);
  await expect(page.locator('.band')).toContainText('Уровень 2');
  // Three errors in fixed mode recommend a hint: the next task arrives with the scaffold already shown.
  await expect(page.getByRole('img', { name: /Подсказка/ })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Подсказка' })).toHaveCount(0);
  await page.getByRole('link', { name: 'Выйти к домику' }).click();
  await page.getByRole('link', { name: 'Мои успехи' }).click();
  await expect(page.getByRole('heading', { name: 'Успехи: Миша' })).toBeFocused();
  await expect(page.getByRole('row', { name: /Сложение/ })).toContainText('3');
  await expect(page.getByText(/фиксированный уровень 2/)).toBeVisible();
});

test('unsupported fixed combination names the supported levels', async ({ page }) => {
  await registerWithChild(page, 'unsupported');
  await page.goto('/');
  await page.getByRole('link', { name: 'Настройки' }).click();
  await page.getByLabel('Сложение').uncheck();
  await page.getByLabel('Умножение').check();
  await page.getByLabel('Сложность').selectOption('fixed');
  await page.getByLabel('Начальный уровень').selectOption('0');
  await page.getByLabel('Пароль родителя для сохранения').fill('correct horse battery staple');
  await page.getByRole('button', { name: 'Сохранить' }).click();
  await expect(page.getByRole('alert')).toContainText('2, 3, 4');
});

test('automatic child sees themed counters in the hint', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Нет аккаунта? Зарегистрироваться' }).click();
  await page.getByLabel('Электронная почта').fill(`theme-${Date.now()}@example.com`);
  await page.getByLabel('Пароль', { exact: true }).fill('correct horse battery staple');
  await page.getByRole('button', { name: 'Зарегистрироваться' }).click();
  await page.getByLabel('Имя').fill('Оля');
  await page.getByLabel('Возраст').selectOption('6');  // ages 4-5 play in picture mode, where the scene itself is the hint
  await page.getByLabel('Оформление').selectOption('dolls');
  await page.getByRole('button', { name: 'Создать профиль' }).click();
  await page.getByRole('link', { name: 'Играть' }).click();
  await expect(page.getByText(/автоматически · Куклы/)).toBeVisible();
  await page.getByRole('link', { name: 'Начать' }).click();
  await page.getByRole('button', { name: 'Подсказка' }).click();
  await expect(page.getByRole('img', { name: /Подсказка/ })).toContainText('🪆');
});
