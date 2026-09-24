import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  use: { baseURL: 'http://127.0.0.1:5173', browserName: 'chromium' },
  webServer: [
    { command: 'MMATH_DATABASE_URL=postgresql+psycopg://mmath_test:mmath_test@127.0.0.1:55434/mmath_t1_test MMATH_ORIGIN=http://127.0.0.1:5173 MMATH_MODE=lan-http ../backend/.venv/bin/uvicorn mental_math.main:create_app --factory --app-dir ../backend --host 127.0.0.1 --port 8000', url: 'http://127.0.0.1:8000/openapi.json', reuseExistingServer: false, timeout: 30000 },
    { command: 'npm run dev -- --host 127.0.0.1', url: 'http://127.0.0.1:5173', reuseExistingServer: false, timeout: 30000 },
  ],
});
