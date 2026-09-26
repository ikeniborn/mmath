/** Service worker registration and a waiting-update handshake that only reloads at a safe screen. */
export type UpdateListener = (waiting: boolean) => void;

const listeners = new Set<UpdateListener>();
let waitingWorker: ServiceWorker | null = null;

export function onUpdate(listener: UpdateListener): () => void {
  listeners.add(listener);
  listener(waitingWorker !== null);
  return () => { listeners.delete(listener); };
}

function announce(worker: ServiceWorker | null) {
  waitingWorker = worker;
  for (const listener of listeners) listener(worker !== null);
}

export function registerServiceWorker(buildId: string): void {
  if (!('serviceWorker' in navigator)) return;
  if (!(import.meta.env.PROD || import.meta.env.VITE_ENABLE_SW)) return;
  navigator.serviceWorker.register(`/sw.js?v=${encodeURIComponent(buildId)}`).then(registration => {
    if (registration.waiting && navigator.serviceWorker.controller) announce(registration.waiting);
    registration.addEventListener('updatefound', () => {
      const installing = registration.installing;
      installing?.addEventListener('statechange', () => {
        if (installing.state === 'installed' && navigator.serviceWorker.controller) announce(registration.waiting);
      });
    });
  }).catch(() => { /* registration failure never blocks the web app */ });
  let reloading = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (waitingWorker && !reloading) { reloading = true; window.location.reload(); }
  });
}

/** Called only from a safe screen after the user accepted the update. */
export function applyUpdate(): void {
  waitingWorker?.postMessage('SKIP_WAITING');
}
