// The one definition of RealDiag's offline IndexedDB database, shared by the
// pages (frontend/utils/offlineManager.js, via require) and the service worker
// (public/sw.js, via importScripts). Both must open the same name and version
// with the same stores; a version mismatch makes the lower-version open fail.
//
// Bump `version` whenever `upgrade` changes, in this file only.
(function (root) {
  var STORES = {
    RULES: 'rules',
    SEARCHES: 'searches',
    FAVORITES: 'favorites',
    SYNC_QUEUE: 'syncQueue',
    USER_DATA: 'userData'
  };

  function upgrade(db) {
    if (!db.objectStoreNames.contains(STORES.RULES)) {
      var rulesStore = db.createObjectStore(STORES.RULES, { keyPath: 'id' });
      rulesStore.createIndex('family', 'family', { unique: false });
      rulesStore.createIndex('lastUpdated', 'lastUpdated', { unique: false });
    }
    if (!db.objectStoreNames.contains(STORES.SEARCHES)) {
      var searchesStore = db.createObjectStore(STORES.SEARCHES, { keyPath: 'id', autoIncrement: true });
      searchesStore.createIndex('timestamp', 'timestamp', { unique: false });
      searchesStore.createIndex('synced', 'synced', { unique: false });
    }
    if (!db.objectStoreNames.contains(STORES.FAVORITES)) {
      db.createObjectStore(STORES.FAVORITES, { keyPath: 'id', autoIncrement: true });
    }
    if (!db.objectStoreNames.contains(STORES.SYNC_QUEUE)) {
      var syncStore = db.createObjectStore(STORES.SYNC_QUEUE, { keyPath: 'id', autoIncrement: true });
      syncStore.createIndex('timestamp', 'timestamp', { unique: false });
    }
    if (!db.objectStoreNames.contains(STORES.USER_DATA)) {
      db.createObjectStore(STORES.USER_DATA, { keyPath: 'key' });
    }
  }

  var schema = { name: 'RealDiagOfflineDB', version: 4, STORES: STORES, upgrade: upgrade };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = schema;
  } else {
    root.REALDIAG_OFFLINE_DB = schema;
  }
})(typeof self !== 'undefined' ? self : this);
