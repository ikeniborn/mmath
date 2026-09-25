import { expect, test } from '@playwright/test';

test.use({ locale: 'en-US' });

test('an English browser gets English copy and the switch to Russian persists across reloads', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Parent sign-in' })).toBeVisible();
  await expect(page.locator('html')).toHaveAttribute('lang', 'en');
  await page.getByRole('button', { name: 'Переключить на русский' }).click();
  await expect(page.getByRole('heading', { name: 'Вход для родителя' })).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Вход для родителя' })).toBeVisible();
  await expect(page.locator('html')).toHaveAttribute('lang', 'ru');
  await page.getByRole('button', { name: 'Switch to English' }).click();
  await page.getByRole('button', { name: 'No account? Register' }).click();
  await page.getByLabel('Email').fill(`lang-${Date.now()}@example.com`);
  await page.getByLabel('Password', { exact: true }).fill('correct horse battery staple');
  await page.getByRole('button', { name: 'Register' }).click();
  await expect(page.getByRole('heading', { name: 'Who is counting today?' })).toBeVisible();
  await page.getByLabel('Name').fill('Sam');
  await page.getByLabel('Theme').selectOption('cars');
  await page.getByRole('button', { name: 'Create profile' }).click();
  await page.getByRole('link', { name: 'Play' }).click();
  await expect(page.getByText(/difficulty adjusts automatically · Cars/)).toBeVisible();
  await page.getByRole('link', { name: 'Start' }).click();
  await expect(page.getByRole('heading', { name: 'Task 1 of 10' })).toBeVisible();
  await page.getByRole('button', { name: 'Hint' }).click();
  await expect(page.getByRole('img', { name: /Hint:/ })).toBeVisible();
});
