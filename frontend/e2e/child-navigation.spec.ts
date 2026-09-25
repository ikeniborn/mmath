import { expect, test } from '@playwright/test';
import { readAnswer, readOperands, registerWithChild } from './helpers';

for (const width of [320, 768, 1280]) {
  test(`journey at ${width}px: start, hint, keyboard answer, feedback, finish, home`, async ({ page }) => {
    await page.setViewportSize({ width, height: 800 });
    await registerWithChild(page, `nav${width}`);
    await page.getByRole('link', { name: 'Начать' }).click();
    await expect(page.getByRole('heading', { name: 'Задача 1 из 10' })).toBeFocused();
    const overflow = () => page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    expect(await overflow()).toBe(false);
    for (const name of ['1', 'Стереть', 'Подсказка']) {
      const box = await page.getByRole('button', { name, exact: true }).boundingBox();
      expect(box?.width, name).toBeGreaterThanOrEqual(48);
      expect(box?.height, name).toBeGreaterThanOrEqual(48);
    }
    await page.getByRole('button', { name: 'Подсказка' }).click();
    await expect(page.getByRole('img', { name: /Подсказка/ })).toBeVisible();
    expect(await overflow()).toBe(false);
    const answer = await readAnswer(page);
    await page.getByRole('heading', { name: 'Задача 1 из 10' }).focus();
    await page.keyboard.type('7');
    await page.keyboard.press('Backspace');
    await page.keyboard.type(String(answer));
    await expect(page.locator('.answer')).toHaveText(String(answer));
    await page.keyboard.press('Enter');
    await expect(page.getByRole('heading', { name: 'Верно!' })).toBeFocused();
    await expect(page.getByRole('status')).toContainText('Верно');
    await page.getByRole('button', { name: 'Дальше' }).click();
    await expect(page.getByRole('heading', { name: 'Задача 2 из 10' })).toBeVisible();
    await page.getByRole('button', { name: 'Закончить занятие' }).click();
    await expect(page.getByRole('heading', { name: 'Занятие завершено' })).toBeFocused();
    await expect(page.getByRole('status')).toContainText('решено 1 из 10, верно 1');
    await page.getByRole('link', { name: 'К домику' }).click();
    await expect(page.getByRole('link', { name: 'Начать' })).toBeVisible();
  });
}

test('layout stays usable at 200% zoom', async ({ page }) => {
  await page.setViewportSize({ width: 640, height: 800 });
  await registerWithChild(page, 'zoom');
  await page.getByRole('link', { name: 'Начать' }).click();
  await page.evaluate(() => { document.body.style.zoom = '2'; });
  await expect(page.getByRole('button', { name: 'Ответить' })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth)).toBe(false);
});
