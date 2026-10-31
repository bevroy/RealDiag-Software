// Background sync was removed: its server endpoints (/api/searches/sync,
// /api/favorites/sync) never existed, the stores it synced were never written,
// and its tags never matched. Nothing should claim or attempt it.
const fs = require('fs')
const path = require('path')

const read = (...p) => fs.readFileSync(path.join(__dirname, '..', ...p), 'utf8')

describe('no background sync', () => {
  test('the service worker has no sync handlers or sync endpoints', () => {
    const sw = read('public', 'sw.js')
    expect(sw).not.toMatch(/addEventListener\('sync'/)
    expect(sw).not.toMatch(/addEventListener\('periodicsync'/)
    expect(sw).not.toMatch(/\/api\/searches\/sync|\/api\/favorites\/sync/)
  })

  test('pages and offlineManager do not request background sync', () => {
    for (const file of [['utils', 'offlineManager.js'], ['pages', 'symptom-search.js']]) {
      const src = read(...file)
      expect(src).not.toMatch(/requestBackgroundSync|listenForSyncMessages|registration\.sync/)
      expect(src).not.toMatch(/search-sync|favorites-sync|sync-searches|sync-favorites/)
    }
  })
})
