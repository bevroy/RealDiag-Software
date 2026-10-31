// Enhanced Service Worker for RealDiag PWA - Field-Ready Offline Mode
const CACHE_VERSION = '4.1.0';
const CACHE_NAME = `realdiag-v${CACHE_VERSION}`;
const RUNTIME_CACHE = `realdiag-runtime-v${CACHE_VERSION}`;
const RULES_CACHE = `realdiag-rules-v${CACHE_VERSION}`;
const API_CACHE = `realdiag-api-v${CACHE_VERSION}`;
const IMAGES_CACHE = `realdiag-images-v${CACHE_VERSION}`;
// The offline library (utils/offlineBundle.js) has its own cache, versioned by
// its content; it is kept across service worker updates.
const OFFLINE_BUNDLE_CACHE = 'realdiag-offline-bundle';

// IndexedDB for offline data: the same name, version and stores as the pages
// (one definition in offline-db-schema.js).
importScripts('/offline-db-schema.js');
const OFFLINE_DB = self.REALDIAG_OFFLINE_DB;
const DB_NAME = OFFLINE_DB.name;
const DB_VERSION = OFFLINE_DB.version;
const STORES = OFFLINE_DB.STORES;

// Assets to cache on install
const PRECACHE_URLS = [
  '/',
  '/symptom-search',
  '/diagnose',
  '/rules',
  '/features-demo',
  '/integration',
  '/account',
  '/logo.png',
  '/runtime-config.js',
  '/offline.html'
];

// IndexedDB requests are not promises; wrap them so reads return results.
function requestToPromise(request) {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

// Initialize IndexedDB
async function initDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    request.onupgradeneeded = (event) => OFFLINE_DB.upgrade(event.target.result);
  });
}

// Save to IndexedDB
async function saveToStore(storeName, data) {
  try {
    const db = await initDB();
    const transaction = db.transaction([storeName], 'readwrite');
    await requestToPromise(transaction.objectStore(storeName).put(data));
    return true;
  } catch (error) {
    console.error(`Error saving to ${storeName}:`, error);
    return false;
  }
}

// Get from IndexedDB
async function getFromStore(storeName, key) {
  try {
    const db = await initDB();
    const transaction = db.transaction([storeName], 'readonly');
    return await requestToPromise(transaction.objectStore(storeName).get(key));
  } catch (error) {
    console.error(`Error getting from ${storeName}:`, error);
    return null;
  }
}

// Get all from IndexedDB store
async function getAllFromStore(storeName) {
  try {
    const db = await initDB();
    const transaction = db.transaction([storeName], 'readonly');
    return await requestToPromise(transaction.objectStore(storeName).getAll());
  } catch (error) {
    console.error(`Error getting all from ${storeName}:`, error);
    return [];
  }
}

// Install event - cache core assets and initialize DB
self.addEventListener('install', (event) => {
  console.log('[SW] Installing enhanced service worker v' + CACHE_VERSION);
  event.waitUntil(
    Promise.all([
      caches.open(CACHE_NAME).then((cache) => {
        console.log('[SW] Precaching core assets');
        return cache.addAll(PRECACHE_URLS);
      }),
      initDB().then(() => {
        console.log('[SW] IndexedDB initialized');
      })
    ])
  );
  // Don't auto-skipWaiting; let the page decide so it can reload cleanly.
});

// Allow the page to trigger activation of a newly-installed SW.
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// Activate event - clean up old caches and claim clients
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating enhanced service worker');
  event.waitUntil(
    Promise.all([
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => 
              name.startsWith('realdiag-') && 
              name !== CACHE_NAME && 
              name !== RUNTIME_CACHE &&
              name !== RULES_CACHE &&
              name !== API_CACHE &&
              name !== IMAGES_CACHE &&
              name !== OFFLINE_BUNDLE_CACHE
            )
            .map((name) => {
              console.log('[SW] Deleting old cache:', name);
              return caches.delete(name);
            })
        );
      }),
      self.clients.claim()
    ])
  );
});

// Enhanced fetch event with multiple caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    // Offline: answer with a clear "offline" response (503, header
    // X-RealDiag-Offline: 1) instead of a fake success. Nothing is queued:
    // a search or save replayed later would reach no one.
    if (!navigator.onLine) {
      event.respondWith(new Response(JSON.stringify({
        offline: true,
        error: 'offline',
        message: "You're offline. This action needs a connection to the RealDiag server."
      }), {
        status: 503,
        headers: { 'Content-Type': 'application/json', 'X-RealDiag-Offline': '1' }
      }));
    }
    return;
  }

  // API calls - Network first with cache fallback and offline queue
  if (url.hostname.includes('onrender.com') || url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(API_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(async () => {
          // Try cache
          const cached = await caches.match(request);
          if (cached) {
            console.log('[SW] Serving API from cache (offline):', url.pathname);
            return cached;
          }
          // Return offline indicator
          return new Response(JSON.stringify({ 
            error: 'Offline', 
            message: 'No cached data available',
            offline: true 
          }), {
            status: 503,
            headers: { 'Content-Type': 'application/json', 'X-RealDiag-Offline': '1' }
          });
        })
    );
    return;
  }

  // Skip cross-origin requests (except APIs handled above)
  if (url.origin !== location.origin) {
    return;
  }

  // Always-fresh small files: runtime config + manifest must never be stale.
  if (url.pathname === '/runtime-config.js' || url.pathname === '/manifest.json') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(RUNTIME_CACHE).then((cache) => cache.put(request, responseClone));
          }
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // Navigation requests - Network first with offline fallback
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(RUNTIME_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(async () => {
          const cached = await caches.match(request);
          if (cached) {
            console.log('[SW] Serving page from cache (offline):', url.pathname);
            return cached;
          }
          // Fallback to offline page
          const offlinePage = await caches.match('/offline.html');
          if (offlinePage) return offlinePage;
          // Last resort: homepage
          return caches.match('/');
        })
    );
    return;
  }

  // Hash-busted Next.js bundles - safe to cache-first (filename changes on update).
  if (url.pathname.startsWith('/_next/static/')) {
    event.respondWith(
      caches.match(request).then((cached) => {
        if (cached) return cached;
        return fetch(request).then((response) => {
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        });
      })
    );
    return;
  }

  // Non-hashed scripts, styles, fonts - stale-while-revalidate so a new
  // version replaces the cache on the very next load (no manual refresh).
  if (url.pathname.match(/\.(js|css|woff|woff2|ttf|otf)$/)) {
    event.respondWith(
      caches.match(request).then((cached) => {
        const fetchPromise = fetch(request).then((response) => {
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, responseClone));
          }
          return response;
        }).catch(() => cached);
        return cached || fetchPromise;
      })
    );
    return;
  }

  // Images - stale-while-revalidate
  if (url.pathname.match(/\.(png|jpg|jpeg|svg|gif|webp|ico)$/)) {
    event.respondWith(
      caches.match(request).then((cached) => {
        const fetchPromise = fetch(request).then((response) => {
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(IMAGES_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        }).catch(() => cached);
        return cached || fetchPromise;
      })
    );
    return;
  }

  // Everything else - Network first with cache fallback
  event.respondWith(
    fetch(request)
      .then((response) => {
        if (response.ok) {
          const responseClone = response.clone();
          caches.open(RUNTIME_CACHE).then((cache) => {
            cache.put(request, responseClone);
          });
        }
        return response;
      })
      .catch(() => caches.match(request))
  );
});

// Message handler for client communication
self.addEventListener('message', (event) => {
  console.log('[SW] Message received:', event.data);
  
  if (event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  } else if (event.data.type === 'SAVE_RULE') {
    saveToStore(STORES.RULES, event.data.rule).then(() => {
      event.ports[0].postMessage({ success: true });
    });
  } else if (event.data.type === 'SAVE_SEARCH') {
    saveToStore(STORES.SEARCHES, {
      ...event.data.search,
      timestamp: Date.now(),
      synced: false
    }).then(() => {
      event.ports[0].postMessage({ success: true });
    });
  } else if (event.data.type === 'GET_OFFLINE_STATUS') {
    Promise.all([
      getAllFromStore(STORES.RULES),
      getAllFromStore(STORES.SEARCHES),
      getAllFromStore(STORES.FAVORITES)
    ]).then(([rules, searches, favorites]) => {
      event.ports[0].postMessage({
        rulesCount: rules.length,
        searchesCount: searches.length,
        favoritesCount: favorites.length,
        cacheVersion: CACHE_VERSION
      });
    });
  } else if (event.data.type === 'CLEAR_OFFLINE_DATA') {
    Promise.all([
      initDB().then(db => {
        const transaction = db.transaction(Object.values(STORES), 'readwrite');
        Object.values(STORES).forEach(storeName => {
          transaction.objectStore(storeName).clear();
        });
        return transaction.complete;
      }),
      caches.keys().then(keys => 
        Promise.all(
          keys.filter(key => key.startsWith('realdiag-')).map(key => caches.delete(key))
        )
      )
    ]).then(() => {
      event.ports[0].postMessage({ success: true });
    });
  }
});

console.log('[SW] Enhanced service worker loaded - v' + CACHE_VERSION);