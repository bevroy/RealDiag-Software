const { refreshBundle, loadStoredBundle, pageAssets, bundleSummary, bundleQuestionnaireTrees, bundleQuestionnaire,
  BUNDLE_CACHE, BUNDLE_KEY } =
  require('../utils/offlineBundle')

// Minimal Cache Storage and Response stand-ins (jest's node environment has neither).
class FakeResponse {
  constructor(body, init = {}) { this.body = body; this.status = init.status || 200; this.ok = this.status < 400 }
  async json() { return JSON.parse(this.body) }
  async text() { return this.body }
}
global.Response = FakeResponse

function fakeStorage() {
  const caches = {}
  return {
    caches,
    async open(name) {
      caches[name] = caches[name] || {}
      const store = caches[name]
      return { async match(key) { return store[key] }, async put(key, response) { store[key] = response } }
    },
  }
}

const bundle = (version) => ({ version, tree_count: 2, search: { rules: [] }, questionnaires: { Q1: {} } })
const json = (body, status = 200) => new FakeResponse(JSON.stringify(body), { status })

test('downloads and stores the bundle when there is none', async () => {
  const storage = fakeStorage()
  const calls = []
  const apiFetchFn = async (path) => {
    calls.push(path)
    return path === '/offline/bundle/version' ? json({ version: 'v1' }) : json(bundle('v1'))
  }
  const out = await refreshBundle({ apiFetchFn, storage })
  expect(out.status).toBe('updated')
  expect(calls).toEqual(['/offline/bundle/version', '/offline/bundle'])
  expect(storage.caches[BUNDLE_CACHE][BUNDLE_KEY]).toBeTruthy()
  expect((await loadStoredBundle(storage)).version).toBe('v1')
})

test('skips the download when the stored version is current, refreshes when it changed', async () => {
  const storage = fakeStorage()
  await refreshBundle({ apiFetchFn: async (p) => (p.endsWith('version') ? json({ version: 'v1' }) : json(bundle('v1'))), storage })
  const calls = []
  const same = await refreshBundle({ apiFetchFn: async (p) => { calls.push(p); return json({ version: 'v1' }) }, storage })
  expect(same.status).toBe('current')
  expect(calls).toEqual(['/offline/bundle/version'])
  const changed = await refreshBundle({ apiFetchFn: async (p) => (p.endsWith('version') ? json({ version: 'v2' }) : json(bundle('v2'))), storage })
  expect(changed.status).toBe('updated')
  expect((await loadStoredBundle(storage)).version).toBe('v2')
})

test('a failed refresh keeps the stored bundle and says so', async () => {
  const storage = fakeStorage()
  await refreshBundle({ apiFetchFn: async (p) => (p.endsWith('version') ? json({ version: 'v1' }) : json(bundle('v1'))), storage })
  const out = await refreshBundle({ apiFetchFn: async () => { throw new TypeError('Failed to fetch') }, storage })
  expect(out).toMatchObject({ status: 'failed', version: 'v1', error: 'Failed to fetch' })
  const unauth = await refreshBundle({ apiFetchFn: async () => json({ detail: 'Not authenticated' }, 401), storage: fakeStorage() })
  expect(unauth).toMatchObject({ status: 'failed', version: null, error: 'HTTP 401' })
})

test('page warm-up finds the page scripts and styles', () => {
  const html = '<script src="/_next/static/chunks/a.js"></script><link href="/_next/static/css/b.css" rel="stylesheet">' +
    '<script src="https://other/x.js"></script><script src="/_next/static/chunks/a.js"></script>'
  expect(pageAssets(html)).toEqual(['/_next/static/chunks/a.js', '/_next/static/css/b.css'])
})

test('summary says what is on the device', () => {
  expect(bundleSummary(null)).toMatch(/No offline library on this device/)
  expect(bundleSummary(bundle('abc'))).toBe('Offline library abc: 2 trees for symptom search, 1 question-by-question trees.')
})

test('questionnaires from the bundle have the online shapes', () => {
  const b = { version: 'v1', clinical_review_notice: 'Draft content.', questionnaires: {
    Q1: { tree: { id: 'Q1', title: 'Cough', review_status_label: 'Draft' }, node_format: 'questionnaire', entry: 'a', nodes: {} },
  } }
  expect(bundleQuestionnaireTrees(b)).toEqual([
    { id: 'Q1', title: 'Cough', review_status_label: 'Draft', node_format: 'questionnaire', walk_available: true }])
  expect(bundleQuestionnaire(b, 'Q1')).toMatchObject({ entry: 'a', clinical_review_notice: 'Draft content.' })
  expect(bundleQuestionnaire(b, 'nope')).toBeNull()
  expect(bundleQuestionnaireTrees(null)).toEqual([])
})

test('the service worker keeps the offline library cache when it updates', () => {
  const sw = require('fs').readFileSync(require('path').join(__dirname, '..', 'public', 'sw.js'), 'utf8')
  expect(sw).toContain(`const OFFLINE_BUNDLE_CACHE = '${BUNDLE_CACHE}'`)
  expect(sw).toMatch(/name !== OFFLINE_BUNDLE_CACHE/)
})
