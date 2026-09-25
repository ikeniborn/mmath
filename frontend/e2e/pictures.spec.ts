import { expect, test } from '@playwright/test';
import { readOperands, registerWithChild } from './helpers';

test('a five-year-old sees the task drawn with theme objects and can play on after the summary', async ({ page }) => {
  await registerWithChild(page, 'pic', '5');
  await page.getByRole('link', { name: 'Начать' }).click();
  await expect(page.getByRole('heading', { name: 'Задача 1 из 10' })).toBeVisible();
  const [a, b] = await readOperands(page);
  const picture = page.locator('.task-picture');
  await expect(picture).toBeVisible();
  expect(await picture.locator('span').count()).toBe(a + b + 1); // both groups plus the plus sign
  await page.getByRole('button', { name: 'Закончить занятие' }).click();
  await expect(page.getByRole('heading', { name: 'Занятие завершено' })).toBeVisible();
  await page.getByRole('button', { name: 'Ещё!' }).click();
  await expect(page.getByRole('heading', { name: 'Задача 1 из 10' })).toBeVisible();
});
