/* Connected-only service worker: precaches the public shell, never touches /api, auth or personal data. */
const VERSION = new URL(self.location.href).searchParams.get('v') || 'dev';
const CACHE = `mmath-shell-${VERSION}`;
const SHELL = ['/offline.html', '/manifest.webmanifest', '/icons/icon-192.png', '/icons/icon-512.png'];
const PUBLIC_PREFIXES = ['/assets/', '/icons/'];
const PUBLIC_FILES = new Set(['/offline.html', '/manifest.webmanifest']);

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)));
});

self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim()));
});

self.addEventListener('message', event => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});

function cacheable(url) {
  return url.origin === self.location.origin && (PUBLIC_FILES.has(url.pathname) || PUBLIC_PREFIXES.some(prefix => url.pathname.startsWith(prefix)));
}

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.pathname.startsWith('/api/') || url.pathname.startsWith('/health') || url.pathname.startsWith('/internal')) return;
  if (event.request.mode === 'navigate') {
    // Navigations always go to the network; offline launch gets the public connection-required page.
    event.respondWith(fetch(event.request).catch(() => caches.match('/offline.html')));
    return;
  }
  if (!cacheable(url)) return;
  event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request).then(response => {
    if (response.ok) caches.open(CACHE).then(cache => cache.put(event.request, response.clone()));
    return response;
  })));
});
