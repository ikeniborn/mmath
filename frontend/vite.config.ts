import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { execSync } from 'node:child_process';

function buildId(): string {
  try { return execSync('git rev-parse --short HEAD', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim() + (process.env.VITE_ENABLE_SW ? '-dev' : ''); } catch { return String(Date.now()); }
}

export default defineConfig({
  plugins: [react()],
  define: { __MMATH_BUILD_ID__: JSON.stringify(buildId()) },
  server: { proxy: { '/api': 'http://127.0.0.1:8000' } },
  test: { environment: 'jsdom', include: ['src/**/*.test.ts', 'src/**/*.test.tsx'] },
});
