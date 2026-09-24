import type { components } from './api-types';

export type Session = components['schemas']['SessionView'];
export type Player = components['schemas']['PlayerView'];

let csrf = '';

export async function api<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  const response = await fetch(`/api/v1${path}`, {
    method,
    credentials: 'same-origin',
    headers: { ...(body ? { 'Content-Type': 'application/json' } : {}), ...(method !== 'GET' ? { 'X-CSRF-Token': csrf } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = response.status === 204 ? null : await response.json();
  if (!response.ok) throw new Error(typeof data?.detail?.code === 'string' ? data.detail.code : 'request_failed');
  if (data && typeof data.csrf_token === 'string') csrf = data.csrf_token;
  return data as T;
}

export async function bootstrap(): Promise<Session> { return api<Session>('/auth/session'); }
export function clearCsrf() { csrf = ''; }
