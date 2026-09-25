import type { components } from './api-types';

export type Session = components['schemas']['SessionView'];
export type Player = components['schemas']['PlayerView'];
export type SessionSnapshot = components['schemas']['SessionSnapshot'];
export type AttemptResult = components['schemas']['AttemptResult'];
export type PublicProblem = components['schemas']['PublicProblem'];

export class ApiError extends Error {
  constructor(public code: string, public detail: Record<string, unknown> = {}) { super(code); }
}

let csrf = '';

export async function api<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  const response = await fetch(`/api/v1${path}`, {
    method,
    credentials: 'same-origin',
    headers: { ...(body ? { 'Content-Type': 'application/json' } : {}), ...(method !== 'GET' ? { 'X-CSRF-Token': csrf } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = response.status === 204 ? null : await response.json();
  if (!response.ok) {
    const detail = data && typeof data.detail === 'object' && data.detail ? data.detail : {};
    throw new ApiError(typeof detail.code === 'string' ? detail.code : 'request_failed', detail);
  }
  if (data && typeof data.csrf_token === 'string') csrf = data.csrf_token;
  return data as T;
}

export async function bootstrap(): Promise<Session> { return api<Session>('/auth/session'); }
export function clearCsrf() { csrf = ''; }
