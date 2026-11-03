// Copia della pagina per riaprirla senza rete; quando c'è rete prende sempre la versione nuova.
const CACHE = "diario-2580";
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.add("./"))); self.skipWaiting(); });
self.addEventListener("activate", e => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  e.respondWith(fetch(e.request).then(r => {
    const copia = r.clone();
    caches.open(CACHE).then(c => c.put(e.request, copia));
    return r;
  }).catch(() => caches.match(e.request).then(r => r || caches.match("./"))));
});
