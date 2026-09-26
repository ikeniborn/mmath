import { expect, test, type Page } from '@playwright/test';
import { registerWithChild } from './helpers';

/** Answers whatever picture-mode task is on screen the way a child would: by tapping. Correctness is the server's business. */
async function answerByTapping(page: Page) {
  const done = page.getByRole('button', { name: 'Готово' });
  if (await done.count()) {
    const objects = page.getByRole('button', { name: /^Предмет \d+$/ });
    const count = await objects.count();
    if (count) { for (let index = 0; index < count; index++) await objects.nth(index).click(); }
    else await page.getByRole('button', { name: 'Добавить' }).click();
    await done.click();
    return;
  }
  const towers = page.getByRole('button', { name: /^Башня \d+$/ });
  if (await towers.count()) {
    const count = await towers.count();
    for (let index = 0; index < count; index++) await towers.nth(index).click();
    return;
  }
  for (const name of [/^Фигура 1$/, /^Кучка 1$/, /^Да$/, /^Карточка 1$/]) {
    const button = page.getByRole('button', { name });
    if (await button.count()) { await button.first().click(); return; }
  }
  throw new Error('no tappable input on screen');
}

test('a four-year-old plays a six-task round by taps only, gets a sticker and starts again', async ({ page }) => {
  await registerWithChild(page, 'early', '4');
  await page.getByRole('link', { name: 'Начать' }).click();
  for (let task = 1; task <= 6; task++) {
    await expect(page.getByRole('heading', { name: `Задача ${task} из 6` })).toBeVisible();
    await expect(page.getByRole('group', { name: 'Клавиатура' })).toHaveCount(0);  // never the keypad
    await answerByTapping(page);
    await page.getByRole('button', { name: task === 6 ? 'Завершить' : 'Дальше' }).click();
  }
  await expect(page.getByRole('heading', { name: 'Занятие завершено' })).toBeVisible();
  await expect(page.locator('.sticker-new')).toBeVisible();
  await expect(page.getByRole('img', { name: 'flowers-1' })).toBeVisible();
  await page.getByRole('button', { name: 'Ещё!' }).click();
  await expect(page.getByRole('heading', { name: 'Задача 1 из 6' })).toBeVisible();
  await page.getByRole('link', { name: 'Выйти к домику' }).click();
  await expect(page.getByText('Наклеек: 1')).toBeVisible();
});

test('a seven-year-old still sees the number pad, ten tasks and no scene', async ({ page }) => {
  await registerWithChild(page, 'older', '7');
  await page.getByRole('link', { name: 'Начать' }).click();
  await expect(page.getByRole('heading', { name: 'Задача 1 из 10' })).toBeVisible();
  await expect(page.getByRole('group', { name: 'Клавиатура' })).toBeVisible();
  await expect(page.locator('.task-picture')).toHaveCount(0);
  await expect(page.locator('.task-scene')).toHaveCount(0);
});

test('a parent switches a five-year-old to ten tasks and drops the early topic', async ({ page }) => {
  await registerWithChild(page, 'settings', '5');
  await page.getByRole('link', { name: 'Другой ребёнок' }).click();
  await page.getByRole('link', { name: 'Настройки' }).click();
  await expect(page.getByLabel('Малышам')).toBeChecked();
  await page.getByLabel('Малышам').uncheck();
  await page.getByLabel('Задач в раунде').selectOption('10');
  await page.getByLabel('Пароль родителя для сохранения').fill('correct horse battery staple');
  await page.getByRole('button', { name: 'Сохранить' }).click();
  await expect(page.getByRole('status')).toBeVisible();
  await page.getByRole('link', { name: '← К выбору ребёнка' }).click();
  await page.getByRole('link', { name: 'Играть' }).click();
  await page.getByRole('link', { name: 'Начать' }).click();
  await expect(page.getByRole('heading', { name: 'Задача 1 из 10' })).toBeVisible();
});
