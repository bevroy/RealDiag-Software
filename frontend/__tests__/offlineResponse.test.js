const fs = require('fs')
const path = require('path')
const { OFFLINE_HEADER, OFFLINE_SEARCH_MESSAGE, isOfflineResponse, isOfflineError } = require('../utils/offlineResponse')

const headers = (h) => ({ get: (k) => h[k] })
const read = (...p) => fs.readFileSync(path.join(__dirname, '..', ...p), 'utf8')

describe('offline responses', () => {
  test('the service worker offline 503 is recognised', () => {
    expect(isOfflineResponse({ status: 503, headers: headers({ [OFFLINE_HEADER]: '1' }) })).toBe(true)
  })

  test('a real server 503, or a 200, is not "offline"', () => {
    expect(isOfflineResponse({ status: 503, headers: headers({}) })).toBe(false)
    expect(isOfflineResponse({ status: 200, headers: headers({ [OFFLINE_HEADER]: '1' }) })).toBe(false)
  })

  test('a failed fetch while the browser is offline is an offline error', () => {
    const err = new TypeError('Failed to fetch')
    expect(isOfflineError(err, { onLine: false })).toBe(true)
    expect(isOfflineError(err, { onLine: true })).toBe(false)
    expect(isOfflineError(new Error('boom'), { onLine: false })).toBe(false)
  })

  test('the service worker no longer fakes success or queues offline POSTs', () => {
    const sw = read('public', 'sw.js')
    expect(sw).not.toMatch(/queued:\s*true/)
    expect(sw).not.toMatch(/saveToStore\(STORES\.SYNC_QUEUE/)
    expect(sw).toMatch(/status: 503,\s*\n\s*headers: \{ 'Content-Type': 'application\/json', 'X-RealDiag-Offline': '1' \}/)
  })

  test('Symptom Search ranks offline from the offline library, or says it has none, instead of "no results"', () => {
    const page = read('pages', 'symptom-search.js')
    expect(page).toMatch(/isOfflineResponse\(response\)\) \{\s*await runOfflineSearch\(\)/)
    expect(page).toMatch(/if \(!bundle\) \{\s*setError\(OFFLINE_SEARCH_MESSAGE\)/)
    expect(page).not.toMatch(/Cached data is available/)
    expect(OFFLINE_SEARCH_MESSAGE).toMatch(/^You're offline, and this device has no offline library yet\./)
  })
})
