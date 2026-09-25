import { expect, test, type Page } from '@playwright/test';

async function registerWithChild(page: Page) {
  await page.goto('/');
  await page.getByRole('button', { name: 'Нет аккаунта? Зарегистрироваться' }).click();
  await page.getByLabel('Электронная почта').fill(`lesson-${Date.now()}@example.com`);
  await page.getByLabel('Пароль', { exact: true }).fill('correct horse battery staple');
  await page.getByRole('button', { name: 'Зарегистрироваться' }).click();
  await page.getByLabel('Имя').fill('Миша');
  await page.getByLabel('Возраст').selectOption('6');
  await page.getByRole('button', { name: 'Создать профиль' }).click();
  await page.getByRole('link', { name: 'Играть' }).click();
  await page.getByRole('link', { name: 'Начать' }).click();
  await expect(page.getByRole('heading', { name: /Задача 1 из/ })).toBeVisible();
}

async function answerCurrent(page: Page, correct: boolean) {
  const text = await page.locator('.expression').innerText();
  const [a, b] = text.split('=')[0].split('+').map(part => Number(part.trim()));
  const answer = a + b + (correct ? 0 : 1);
  for (const digit of String(answer)) await page.getByRole('button', { name: digit, exact: true }).click();
  await page.getByRole('button', { name: 'Ответить' }).click();
}

test('child answers, sees feedback, resumes after reload and finishes', async ({ page }) => {
  await registerWithChild(page);
  await answerCurrent(page, true);
  await expect(page.getByRole('heading', { name: 'Верно!' })).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Верно!' })).toBeVisible();
  await page.getByRole('button', { name: 'Дальше' }).click();
  await expect(page.getByRole('heading', { name: /Задача 2 из/ })).toBeVisible();
  await answerCurrent(page, false);
  await expect(page.getByRole('heading', { name: 'Пока не так' })).toBeVisible();
  await expect(page.getByRole('status')).toContainText('Правильный ответ');
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Пока не так' })).toBeVisible();
  await page.getByRole('button', { name: 'Дальше' }).click();
  await expect(page.getByRole('heading', { name: /Задача 3 из/ })).toBeVisible();
  await page.getByRole('button', { name: 'Закончить занятие' }).click();
  await expect(page.getByRole('heading', { name: 'Занятие завершено' })).toBeVisible();
  await expect(page.getByRole('status')).toContainText('решено 2 из 10, верно 1');
  await page.getByRole('link', { name: 'К домику' }).click();
  await page.getByRole('link', { name: 'Начать' }).click();
  await expect(page.getByRole('heading', { name: /Задача 1 из/ })).toBeVisible();
});

test('a pending answer stored before a lost response is reconciled without double grading', async ({ page }) => {
  await registerWithChild(page);
  await page.route('**/api/v1/sessions/*/attempts', route => route.abort('connectionfailed'), { times: 1 });
  await answerCurrent(page, true);
  await expect(page.getByRole('status')).toContainText('Нет связи');
  await page.getByRole('button', { name: 'Повторить' }).click();
  await expect(page.getByRole('heading', { name: 'Верно!' })).toBeVisible();
  const stored = await page.evaluate(() => sessionStorage.getItem('mmath.pending-submission'));
  expect(stored).toBeNull();
});
