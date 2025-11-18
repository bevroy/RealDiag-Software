// Enhanced Service Worker for RealDiag PWA - Field-Ready Offline Mode
const CACHE_VERSION = '3.0.0';
const CACHE_NAME = `realdiag-v${CACHE_VERSION}-2025-11-18`;
const RUNTIME_CACHE = `realdiag-runtime-v${CACHE_VERSION}`;
const RULES_CACHE = `realdiag-rules-v${CACHE_VERSION}`;
const API_CACHE = `realdiag-api-v${CACHE_VERSION}`;
const IMAGES_CACHE = `realdiag-images-v${CACHE_VERSION}`;

// IndexedDB for offline data
const DB_NAME = 'RealDiagOfflineDB';
const DB_VERSION = 3;
const STORES = {
  RULES: 'rules',
  SEARCHES: 'searches',
  FAVORITES: 'favorites',
  SYNC_QUEUE: 'syncQueue',
  USER_DATA: 'userData'
};

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

// Initialize IndexedDB
async function initDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      
      // Create object stores if they don't exist
      if (!db.objectStoreNames.contains(STORES.RULES)) {
        const rulesStore = db.createObjectStore(STORES.RULES, { keyPath: 'id' });
        rulesStore.createIndex('family', 'family', { unique: false });
        rulesStore.createIndex('lastUpdated', 'lastUpdated', { unique: false });
      }
      
      if (!db.objectStoreNames.contains(STORES.SEARCHES)) {
        const searchesStore = db.createObjectStore(STORES.SEARCHES, { keyPath: 'id', autoIncrement: true });
        searchesStore.createIndex('timestamp', 'timestamp', { unique: false });
        searchesStore.createIndex('synced', 'synced', { unique: false });
      }
      
      if (!db.objectStoreNames.contains(STORES.FAVORITES)) {
        db.createObjectStore(STORES.FAVORITES, { keyPath: 'id', autoIncrement: true });
      }
      
      if (!db.objectStoreNames.contains(STORES.SYNC_QUEUE)) {
        const syncStore = db.createObjectStore(STORES.SYNC_QUEUE, { keyPath: 'id', autoIncrement: true });
        syncStore.createIndex('timestamp', 'timestamp', { unique: false });
      }
      
      if (!db.objectStoreNames.contains(STORES.USER_DATA)) {
        db.createObjectStore(STORES.USER_DATA, { keyPath: 'key' });
      }
    };
  });
}

// Save to IndexedDB
async function saveToStore(storeName, data) {
  try {
    const db = await initDB();
    const transaction = db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);
    await store.put(data);
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
    const store = transaction.objectStore(storeName);
    return await store.get(key);
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
    const store = transaction.objectStore(storeName);
    return await store.getAll();
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
  self.skipWaiting();
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
              name !== IMAGES_CACHE
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
    // For POST/PUT/DELETE when offline, queue for sync
    if (!navigator.onLine) {
      event.respondWith(
        (async () => {
          await saveToStore(STORES.SYNC_QUEUE, {
            url: request.url,
            method: request.method,
            headers: [...request.headers],
            body: await request.text(),
            timestamp: Date.now()
          });
          return new Response(JSON.stringify({ queued: true, offline: true }), {
            headers: { 'Content-Type': 'application/json' }
          });
        })()
      );
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
            headers: { 'Content-Type': 'application/json' }
          });
        })
    );
    return;
  }

  // Skip cross-origin requests (except APIs handled above)
  if (url.origin !== location.origin) {
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

  // Static assets - Cache first with network fallback
  if (url.pathname.startsWith('/_next/static/') || 
      url.pathname.match(/\.(js|css|woff|woff2|ttf|otf)$/)) {
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

  // Images - Cache first with stale-while-revalidate
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
        });
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

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync event:', event.tag);
  
  if (event.tag === 'sync-searches') {
    event.waitUntil(syncSearches());
  } else if (event.tag === 'sync-favorites') {
    event.waitUntil(syncFavorites());
  } else if (event.tag === 'sync-queue') {
    event.waitUntil(syncQueuedRequests());
  }
});

// Sync offline searches
async function syncSearches() {
  try {
    console.log('[SW] Syncing offline searches...');
    const searches = await getAllFromStore(STORES.SEARCHES);
    const unsyncedSearches = searches.filter(s => !s.synced);
    
    if (unsyncedSearches.length === 0) {
      console.log('[SW] No searches to sync');
      return;
    }
    
    // Try to sync each search
    for (const search of unsyncedSearches) {
      try {
        const response = await fetch('/api/searches/sync', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(search)
        });
        
        if (response.ok) {
          search.synced = true;
          await saveToStore(STORES.SEARCHES, search);
          console.log('[SW] Synced search:', search.id);
        }
      } catch (error) {
        console.error('[SW] Failed to sync search:', error);
      }
    }
    
    // Notify clients
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
      client.postMessage({
        type: 'SEARCHES_SYNCED',
        count: unsyncedSearches.length
      });
    });
    
    console.log('[SW] Search sync complete');
  } catch (error) {
    console.error('[SW] Error syncing searches:', error);
  }
}

// Sync favorites
async function syncFavorites() {
  try {
    console.log('[SW] Syncing favorites...');
    const favorites = await getAllFromStore(STORES.FAVORITES);
    
    const response = await fetch('/api/favorites/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ favorites })
    });
    
    if (response.ok) {
      console.log('[SW] Favorites synced successfully');
      
      // Notify clients
      const clients = await self.clients.matchAll();
      clients.forEach(client => {
        client.postMessage({
          type: 'FAVORITES_SYNCED',
          count: favorites.length
        });
      });
    }
  } catch (error) {
    console.error('[SW] Error syncing favorites:', error);
  }
}

// Sync queued requests
async function syncQueuedRequests() {
  try {
    console.log('[SW] Syncing queued requests...');
    const queue = await getAllFromStore(STORES.SYNC_QUEUE);
    
    if (queue.length === 0) {
      console.log('[SW] No queued requests');
      return;
    }
    
    let successCount = 0;
    for (const item of queue) {
      try {
        const response = await fetch(item.url, {
          method: item.method,
          headers: new Headers(item.headers),
          body: item.body
        });
        
        if (response.ok) {
          // Remove from queue
          const db = await initDB();
          const transaction = db.transaction([STORES.SYNC_QUEUE], 'readwrite');
          const store = transaction.objectStore(STORES.SYNC_QUEUE);
          await store.delete(item.id);
          successCount++;
        }
      } catch (error) {
        console.error('[SW] Failed to sync request:', error);
      }
    }
    
    // Notify clients
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
      client.postMessage({
        type: 'QUEUE_SYNCED',
        count: successCount,
        remaining: queue.length - successCount
      });
    });
    
    console.log('[SW] Synced', successCount, 'of', queue.length, 'queued requests');
  } catch (error) {
    console.error('[SW] Error syncing queue:', error);
  }
}

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

// Periodic background sync (if supported)
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'sync-data') {
    event.waitUntil(
      Promise.all([
        syncSearches(),
        syncFavorites(),
        syncQueuedRequests()
      ])
    );
  }
});

console.log('[SW] Enhanced service worker loaded - v' + CACHE_VERSION);