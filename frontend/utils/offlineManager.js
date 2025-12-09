/**
 * Offline Data Manager
 * Handles downloading and managing offline rule database
 * NOW WITH ENCRYPTION: All sensitive data encrypted using Web Crypto API
 */

import { 
  encryptData, 
  decryptData, 
  getEncryptionKey, 
  isCryptoAvailable 
} from './crypto.js';

// IndexedDB configuration
const DB_NAME = 'RealDiagOfflineDB';
const DB_VERSION = 4; // Incremented for encryption migration
const STORES = {
  RULES: 'rules',
  SEARCHES: 'searches',
  FAVORITES: 'favorites',
  SYNC_QUEUE: 'syncQueue',
  USER_DATA: 'userData'
};

// Encryption settings
const ENCRYPT_SEARCHES = true; // Searches may contain PHI
const ENCRYPT_USER_DATA = true; // User data may contain sensitive info
const ENCRYPT_RULES = false; // Rules are public medical knowledge

// Open IndexedDB connection
export async function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      
      // Create stores if they don't exist
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

// Save rule to offline storage
export async function saveRule(rule) {
  const db = await openDB();
  const transaction = db.transaction([STORES.RULES], 'readwrite');
  const store = transaction.objectStore(STORES.RULES);
  
  const ruleWithMeta = {
    ...rule,
    id: rule.rule_id || rule.id,
    lastUpdated: Date.now(),
    downloadedAt: Date.now()
  };
  
  await store.put(ruleWithMeta);
  return ruleWithMeta;
}

// Get rule from offline storage
export async function getRule(ruleId) {
  const db = await openDB();
  const transaction = db.transaction([STORES.RULES], 'readonly');
  const store = transaction.objectStore(STORES.RULES);
  return await store.get(ruleId);
}

// Get all rules from offline storage
export async function getAllRules() {
  const db = await openDB();
  const transaction = db.transaction([STORES.RULES], 'readonly');
  const store = transaction.objectStore(STORES.RULES);
  const rules = await store.getAll();
  if (!Array.isArray(rules)) {
    return [];
  }
  return rules;
}

// Get rules by family
export async function getRulesByFamily(family) {
  const db = await openDB();
  const transaction = db.transaction([STORES.RULES], 'readonly');
  const store = transaction.objectStore(STORES.RULES);
  const index = store.index('family');
  return await index.getAll(family);
}

// Save search to offline storage (ENCRYPTED)
export async function saveSearch(search) {
  const db = await openDB();
  const transaction = db.transaction([STORES.SEARCHES], 'readwrite');
  const store = transaction.objectStore(STORES.SEARCHES);
  
  const searchWithMeta = {
    ...search,
    timestamp: Date.now(),
    synced: false
  };
  
  // Encrypt if encryption is enabled and key is available
  let dataToStore = searchWithMeta;
  if (ENCRYPT_SEARCHES && isCryptoAvailable()) {
    const encKey = getEncryptionKey();
    if (encKey) {
      try {
        const { encrypted, salt, iv } = await encryptData(searchWithMeta, encKey);
        dataToStore = {
          _encrypted: true,
          data: encrypted,
          salt,
          iv,
          timestamp: searchWithMeta.timestamp,
          synced: searchWithMeta.synced
        };
      } catch (error) {
        console.warn('[OfflineManager] Encryption failed, storing unencrypted:', error);
      }
    }
  }
  
  const request = await store.add(dataToStore);
  return request;
}

// Get all searches (DECRYPT if encrypted)
export async function getAllSearches() {
  const db = await openDB();
  const transaction = db.transaction([STORES.SEARCHES], 'readonly');
  const store = transaction.objectStore(STORES.SEARCHES);
  const searches = await store.getAll();
  
  // Ensure searches is an array
  if (!Array.isArray(searches)) {
    return [];
  }
  
  // Decrypt encrypted searches
  const decrypted = [];
  const encKey = getEncryptionKey();
  
  for (const search of searches) {
    if (search._encrypted && encKey) {
      try {
        const decryptedData = await decryptData(search.data, search.salt, search.iv, encKey);
        decrypted.push(decryptedData);
      } catch (error) {
        console.error('[OfflineManager] Failed to decrypt search:', error);
        // Skip corrupted/undecryptable searches
      }
    } else {
      decrypted.push(search);
    }
  }
  
  return decrypted.sort((a, b) => b.timestamp - a.timestamp);
}

// Get unsynced searches
export async function getUnsyncedSearches() {
  const db = await openDB();
  const transaction = db.transaction([STORES.SEARCHES], 'readonly');
  const store = transaction.objectStore(STORES.SEARCHES);
  const index = store.index('synced');
  return await index.getAll(false);
}

// Mark search as synced
export async function markSearchSynced(searchId) {
  const db = await openDB();
  const transaction = db.transaction([STORES.SEARCHES], 'readwrite');
  const store = transaction.objectStore(STORES.SEARCHES);
  const search = await store.get(searchId);
  if (search) {
    search.synced = true;
    await store.put(search);
  }
}

// Save favorite
export async function saveFavorite(favorite) {
  const db = await openDB();
  const transaction = db.transaction([STORES.FAVORITES], 'readwrite');
  const store = transaction.objectStore(STORES.FAVORITES);
  
  const favoriteData = {
    ...favorite,
    addedAt: Date.now()
  };
  
  // Encrypt if encryption is available (favorites may contain patient context)
  const encKey = getEncryptionKey();
  if (encKey && isCryptoAvailable()) {
    try {
      const { encrypted, salt, iv } = await encryptData(favoriteData, encKey);
      return await store.add({
        _encrypted: true,
        data: encrypted,
        salt,
        iv,
        addedAt: favoriteData.addedAt
      });
    } catch (error) {
      console.error('[OfflineManager] Favorite encryption failed, storing unencrypted:', error);
    }
  }
  
  // Fallback to unencrypted
  return await store.add(favoriteData);
}

// Get all favorites
export async function getAllFavorites() {
  const db = await openDB();
  const transaction = db.transaction([STORES.FAVORITES], 'readonly');
  const store = transaction.objectStore(STORES.FAVORITES);
  const favorites = await store.getAll();
  
  if (!Array.isArray(favorites)) {
    return [];
  }
  
  // Decrypt encrypted favorites
  const decrypted = [];
  const encKey = getEncryptionKey();
  
  for (const favorite of favorites) {
    if (favorite._encrypted && encKey) {
      try {
        const decryptedData = await decryptData(favorite.data, favorite.salt, favorite.iv, encKey);
        decrypted.push(decryptedData);
      } catch (error) {
        console.error('[OfflineManager] Failed to decrypt favorite:', error);
        // Skip corrupted/undecryptable favorites
      }
    } else {
      decrypted.push(favorite);
    }
  }
  
  return decrypted;
}

// Delete favorite
export async function deleteFavorite(favoriteId) {
  const db = await openDB();
  const transaction = db.transaction([STORES.FAVORITES], 'readwrite');
  const store = transaction.objectStore(STORES.FAVORITES);
  await store.delete(favoriteId);
}

// Download all rules from API
export async function downloadAllRules(apiBase, onProgress) {
  try {
    // Get list of all available rules
    const response = await fetch(`${apiBase}/rules/list`);
    if (!response.ok) throw new Error('Failed to fetch rules list');
    
    const rulesList = await response.json();
    const total = rulesList.length;
    let downloaded = 0;
    
    // Download each rule
    for (const ruleInfo of rulesList) {
      try {
        const ruleResponse = await fetch(`${apiBase}/rules/${ruleInfo.id}`);
        if (ruleResponse.ok) {
          const rule = await ruleResponse.json();
          await saveRule(rule);
          downloaded++;
          
          if (onProgress) {
            onProgress({
              downloaded,
              total,
              current: ruleInfo.id,
              percentage: Math.round((downloaded / total) * 100)
            });
          }
        }
      } catch (error) {
        console.error(`Failed to download rule ${ruleInfo.id}:`, error);
      }
    }
    
    return { success: true, downloaded, total };
  } catch (error) {
    console.error('Error downloading rules:', error);
    return { success: false, error: error.message };
  }
}

// Get offline data statistics
export async function getOfflineStats() {
  try {
    const [rules, searches, favorites] = await Promise.all([
      getAllRules(),
      getAllSearches(),
      getAllFavorites()
    ]);
    
    // Ensure all are arrays
    const safeRules = Array.isArray(rules) ? rules : [];
    const safeSearches = Array.isArray(searches) ? searches : [];
    const safeFavorites = Array.isArray(favorites) ? favorites : [];
    
    const unsyncedSearches = safeSearches.filter(s => !s.synced);
    
    // Calculate storage size estimate
    const rulesSize = JSON.stringify(safeRules).length;
    const searchesSize = JSON.stringify(safeSearches).length;
    const favoritesSize = JSON.stringify(safeFavorites).length;
    const totalSize = rulesSize + searchesSize + favoritesSize;
    
    // Group rules by family
    const rulesByFamily = safeRules.reduce((acc, rule) => {
      const family = rule.family || 'Unknown';
      acc[family] = (acc[family] || 0) + 1;
      return acc;
    }, {});
    
    const lastUpdated = safeRules.length > 0 
      ? Math.max(...safeRules.map(r => r.lastUpdated || 0))
      : 0;
    
    return {
      rules: {
        count: safeRules.length,
        byFamily: rulesByFamily,
        size: rulesSize,
        lastUpdated: lastUpdated
      },
      searches: {
        count: safeSearches.length,
        unsynced: unsyncedSearches.length,
        size: searchesSize
      },
      favorites: {
        count: safeFavorites.length,
        size: favoritesSize
      },
      totalSize: totalSize,
      totalSizeMB: (totalSize / 1024 / 1024).toFixed(2)
    };
  } catch (error) {
    console.error('Error getting offline stats:', error);
    return null;
  }
}

// Clear all offline data
export async function clearAllOfflineData() {
  try {
    const db = await openDB();
    const transaction = db.transaction(Object.values(STORES), 'readwrite');
    
    for (const storeName of Object.values(STORES)) {
      const store = transaction.objectStore(storeName);
      await store.clear();
    }
    
    return { success: true };
  } catch (error) {
    console.error('Error clearing offline data:', error);
    return { success: false, error: error.message };
  }
}

// Check if service worker is registered
export function isServiceWorkerSupported() {
  return 'serviceWorker' in navigator;
}

// Get service worker status
export async function getServiceWorkerStatus() {
  if (!isServiceWorkerSupported()) {
    return { supported: false };
  }
  
  const registration = await navigator.serviceWorker.getRegistration();
  return {
    supported: true,
    registered: !!registration,
    active: !!registration?.active,
    waiting: !!registration?.waiting,
    installing: !!registration?.installing
  };
}

// Request background sync
export async function requestBackgroundSync(tag = 'sync-searches') {
  if (!isServiceWorkerSupported()) return false;
  
  const registration = await navigator.serviceWorker.ready;
  if ('sync' in registration) {
    try {
      await registration.sync.register(tag);
      return true;
    } catch (error) {
      console.error('Background sync registration failed:', error);
      return false;
    }
  }
  return false;
}

// Listen for sync messages from service worker
export function listenForSyncMessages(callback) {
  if (!isServiceWorkerSupported()) return;
  
  navigator.serviceWorker.addEventListener('message', (event) => {
    if (event.data.type && event.data.type.endsWith('_SYNCED')) {
      callback(event.data);
    }
  });
}

// Save user data with encryption
export async function saveUserData(key, value) {
  const db = await openDB();
  const transaction = db.transaction([STORES.USER_DATA], 'readwrite');
  const store = transaction.objectStore(STORES.USER_DATA);
  
  const userData = {
    key,
    value,
    updatedAt: Date.now()
  };
  
  // Encrypt if enabled
  const encKey = getEncryptionKey();
  if (ENCRYPT_USER_DATA && encKey && isCryptoAvailable()) {
    try {
      const { encrypted, salt, iv } = await encryptData(userData, encKey);
      return await store.put({
        key, // Keep key unencrypted for lookup
        _encrypted: true,
        data: encrypted,
        salt,
        iv,
        updatedAt: userData.updatedAt
      });
    } catch (error) {
      console.error('[OfflineManager] User data encryption failed, storing unencrypted:', error);
    }
  }
  
  // Fallback to unencrypted
  return await store.put(userData);
}

// Get user data with decryption
export async function getUserData(key) {
  const db = await openDB();
  const transaction = db.transaction([STORES.USER_DATA], 'readonly');
  const store = transaction.objectStore(STORES.USER_DATA);
  const userData = await store.get(key);
  
  if (!userData) return null;
  
  // Decrypt if encrypted
  if (userData._encrypted) {
    const encKey = getEncryptionKey();
    if (encKey) {
      try {
        return await decryptData(userData.data, userData.salt, userData.iv, encKey);
      } catch (error) {
        console.error('[OfflineManager] Failed to decrypt user data:', error);
        return null;
      }
    } else {
      console.warn('[OfflineManager] User data is encrypted but no key available');
      return null;
    }
  }
  
  return userData;
}

// Delete user data
export async function deleteUserData(key) {
  const db = await openDB();
  const transaction = db.transaction([STORES.USER_DATA], 'readwrite');
  const store = transaction.objectStore(STORES.USER_DATA);
  await store.delete(key);
}

// Get online status
export function isOnline() {
  return navigator.onLine;
}

// Listen for online/offline events
export function onConnectionChange(callback) {
  window.addEventListener('online', () => callback(true));
  window.addEventListener('offline', () => callback(false));
}

export default {
  openDB,
  saveRule,
  getRule,
  getAllRules,
  getRulesByFamily,
  saveSearch,
  getAllSearches,
  getUnsyncedSearches,
  markSearchSynced,
  saveFavorite,
  getAllFavorites,
  deleteFavorite,
  saveUserData,
  getUserData,
  deleteUserData,
  downloadAllRules,
  getOfflineStats,
  clearAllOfflineData,
  isServiceWorkerSupported,
  getServiceWorkerStatus,
  requestBackgroundSync,
  listenForSyncMessages,
  isOnline,
  onConnectionChange
};
