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
