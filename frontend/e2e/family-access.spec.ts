import { expect, test } from '@playwright/test';

test('parent entry fits a narrow phone viewport', async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 700 });
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Вход для родителя' })).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  expect(overflow).toBe(false);
  const size = await page.getByRole('button', { name: 'Войти' }).boundingBox();
  expect(size?.height).toBeGreaterThanOrEqual(48);
});

test('parent creates a child and saves fixed difficulty', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Нет аккаунта? Зарегистрироваться' }).click();
  await page.getByLabel('Электронная почта').fill(`family-${Date.now()}@example.com`);
  await page.getByLabel('Пароль', { exact: true }).fill('correct horse battery staple');
  await page.getByRole('button', { name: 'Зарегистрироваться' }).click();
  await expect(page.getByRole('heading', { name: 'Кто сегодня считает?' })).toBeVisible();
  await page.getByLabel('Имя').fill('Маша');
  await page.getByLabel('Возраст').selectOption('7');
  await page.getByRole('button', { name: 'Создать профиль' }).click();
  await expect(page.getByRole('heading', { name: 'Маша' })).toBeVisible();
  await page.getByRole('link', { name: 'Настройки' }).click();
  await page.getByLabel('Сложность').selectOption('fixed');
  await page.getByLabel('Пароль родителя для сохранения').fill('correct horse battery staple');
  await page.getByRole('button', { name: 'Сохранить' }).click();
  await expect(page.getByRole('status')).toHaveText('Настройки сохранены');
});
