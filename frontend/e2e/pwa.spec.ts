import { expect, test } from '@playwright/test';
import { readAnswer, registerWithChild } from './helpers';

const ALLOWED = /^(\/offline\.html|\/manifest\.webmanifest|\/icons\/.*|\/assets\/.*)$/;

test('install metadata is present and the worker caches only the public shell', async ({ page, context }) => {
  await registerWithChild(page, 'pwa');
  const manifestHref = await page.locator('link[rel="manifest"]').getAttribute('href');
  expect(manifestHref).toBe('/manifest.webmanifest');
  const manifest = await (await context.request.get('/manifest.webmanifest')).json();
  expect(manifest.display).toBe('standalone');
  expect(manifest.icons.map((icon: { sizes: string }) => icon.sizes)).toEqual(['192x192', '512x512']);
  for (const icon of manifest.icons) expect((await context.request.get(icon.src)).ok()).toBe(true);
  await page.waitForFunction(() => navigator.serviceWorker.controller !== null || navigator.serviceWorker.getRegistrations().then(list => list.length > 0), null, { timeout: 15000 });
  await page.getByRole('link', { name: 'Начать' }).click();
  await expect(page.getByRole('heading', { name: 'Задача 1 из 10' })).toBeVisible();
  const answer = await readAnswer(page);
  for (const digit of String(answer)) await page.getByRole('button', { name: digit, exact: true }).click();
  await page.getByRole('button', { name: 'Ответить' }).click();
  await expect(page.getByRole('heading', { name: 'Верно!' })).toBeVisible();
  const entries: string[] = await page.evaluate(async () => {
    const keys = await caches.keys();
    const urls: string[] = [];
    for (const key of keys) for (const request of await (await caches.open(key)).keys()) urls.push(new URL(request.url).pathname);
    return urls;
  });
  expect(entries.length).toBeGreaterThan(0);
  for (const path of entries) expect(path, path).toMatch(ALLOWED);
  expect(entries.some(path => path.startsWith('/api/'))).toBe(false);
  const keys: string[] = await page.evaluate(() => caches.keys());
  expect(keys.every(key => key.startsWith('mmath-shell-'))).toBe(true);
});

test('offline launch after logout explains the connection need and exposes no child data', async ({ page, context }) => {
  await registerWithChild(page, 'offline');
  await page.waitForFunction(() => navigator.serviceWorker.controller !== null, null, { timeout: 15000 });
  await page.getByRole('button', { name: 'Выйти' }).click();
  await expect(page.getByRole('heading', { name: 'Вход для родителя' })).toBeVisible();
  await context.setOffline(true);
  await page.goto('/children/anything/play').catch(() => {});
  await expect(page.getByRole('heading', { name: 'Нужно подключение' })).toBeVisible();
  const body = await page.locator('body').innerText();
  expect(body).not.toContain('Миша');
  expect(body).not.toContain('@example.com');
  const stored = await page.evaluate(() => sessionStorage.getItem('mmath.pending-submission'));
  expect(stored).toBeNull();
  await context.setOffline(false);
  await page.getByRole('button', { name: 'Повторить' }).click();
  await expect(page.getByRole('heading', { name: 'Вход для родителя' })).toBeVisible();
});

test('a transient disconnect keeps the pending answer and the app recovers', async ({ page, context }) => {
  await registerWithChild(page, 'transient');
  await page.getByRole('link', { name: 'Начать' }).click();
  await expect(page.getByRole('heading', { name: 'Задача 1 из 10' })).toBeVisible();
  const answer = await readAnswer(page);
  await context.setOffline(true);
  for (const digit of String(answer)) await page.getByRole('button', { name: digit, exact: true }).click();
  await page.getByRole('button', { name: 'Ответить' }).click();
  await expect(page.getByRole('status')).toContainText('Нет связи');
  expect(await page.evaluate(() => sessionStorage.getItem('mmath.pending-submission'))).not.toBeNull();
  await context.setOffline(false);
  await page.getByRole('button', { name: 'Повторить' }).click();
  await expect(page.getByRole('heading', { name: 'Верно!' })).toBeVisible();
});
