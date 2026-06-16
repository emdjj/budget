const CACHE = 'quiz-v2';
const FILES = [
  '/quiz/',
  '/quiz/index.html',
  '/quiz/manifest.json',
  '/quiz/icon-192.png',
  '/quiz/icon-512.png'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request).then(res => {
      if (res.ok && res.type === 'basic') {
        const c = res.clone();
        caches.open(CACHE).then(cache => cache.put(e.request, c));
      }
      return res;
    }).catch(() => caches.match('/quiz/index.html')))
  );
});
