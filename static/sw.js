/* gen-pdf service worker: offline shell + API GET cache.
   Mutations go straight through; the offline outbox lives in app.js
   (workers have no localStorage). Version the cache on every release. */
const VERSION = 'gen-pdf-v1';
const SHELL = ['/', '/index.html', '/styles.css', '/app.js', '/manifest.json'];
const OUTBOX_KEY = 'genpdf.outbox.v1';

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;
  if (e.request.method === 'GET') {
    if (url.pathname.startsWith('/api/')) {
      e.respondWith(fetch(e.request).then((r) => {
        const copy = r.clone();
        caches.open(VERSION).then((c) => c.put(e.request, copy));
        return r;
      }).catch(() => caches.match(e.request)));
    } else {
      e.respondWith(caches.match(e.request).then((hit) => hit || fetch(e.request).then((r) => {
        const copy = r.clone();
        caches.open(VERSION).then((c) => c.put(e.request, copy));
        return r;
      })));
    }
    return;
  }
  // Mutations go straight through; failures are queued client-side (see app.js).
  e.respondWith(fetch(e.request));
});
