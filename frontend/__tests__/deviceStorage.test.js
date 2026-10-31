// What the site may keep on the device: no symptom text, no admin token, no
// unprotected copy of the rule library (see the access-lockdown PR).
const fs = require('fs')
const path = require('path')

const read = (...p) => fs.readFileSync(path.join(__dirname, '..', ...p), 'utf8')

test('recent symptom searches are never written to device storage and old copies are removed', () => {
  const page = read('pages', 'symptom-search.js')
  expect(page).not.toMatch(/setItem\('recentSearches'/)
  expect(page).not.toMatch(/getItem\('recentSearches'/)
  expect(page).toMatch(/localStorage\.removeItem\('recentSearches'\)/)
  expect(read('utils', 'clientAuth.js')).toMatch(/clearStoredAuth\(\) \{[\s\S]*?removeItem\('recentSearches'\)/)
})

test('the admin token is kept in memory only and old copies are removed', () => {
  const page = read('pages', 'admin-review.js')
  expect(page).not.toMatch(/setItem\('admin_token'/)
  expect(page).not.toMatch(/getItem\('admin_token'/)
  expect(page).toMatch(/localStorage\.removeItem\('admin_token'\)/)
  expect(read('utils', 'clientAuth.js')).toMatch(/removeItem\('admin_token'\)/)
})

test('"Download All Rules" is gone and its IndexedDB copy is deleted on open and at sign-out', () => {
  const page = read('pages', 'symptom-search.js')
  expect(page).not.toMatch(/Download All Rules|downloadAllRules|getOfflineStats/)
  expect(page).toMatch(/deleteLegacyOfflineDatabase\(\)/)
  const auth = read('utils', 'clientAuth.js')
  expect(auth).toMatch(/clearStoredAuth\(\) \{[\s\S]*?deleteLegacyOfflineDatabase\(\)/)
  expect(auth).toMatch(/indexedDB\.deleteDatabase\(OFFLINE_DB\.name\)/)
  expect(fs.existsSync(path.join(__dirname, '..', 'utils', 'ruleDownload.js'))).toBe(false)
})
