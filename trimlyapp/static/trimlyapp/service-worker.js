const CACHE_NAME = 'trimly-cache-v1';
const urlsToCache = [
  '/',
  '/barber_reservations/',
  '/static/trimlyapp/style.css',
  '/static/trimlyapp/icon-192.png',
  '/static/trimlyapp/icon-512.png',
  '/static/trimlyapp/manifest.json',
  // Agrega aquí otros archivos estáticos necesarios
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

// Cache First Strategy: busca en caché y si no está, lo descarga y lo guarda
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      if (response) {
        return response;
      }
      // Si no está en caché, lo descarga y lo guarda para la próxima vez
      return fetch(event.request).then(fetchResponse => {
        // Solo cachea GET requests y páginas principales
        if (
          event.request.method === 'GET' &&
          (event.request.url.includes('/barber_reservations/') ||
           event.request.url.includes('/static/'))
        ) {
          return caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, fetchResponse.clone());
            return fetchResponse;
          });
        } else {
          return fetchResponse;
        }
      }).catch(() => {
        // Opcional: muestra una página offline personalizada si lo deseas
        // return caches.match('/offline.html');
      });
    })
  );
});