// The offline bundle on this device: stored in Cache Storage, refreshed from
// GET /offline/bundle when online and the server's version differs.
//
// The bundle holds the tree library's search fields and the walkable
// questionnaire trees (no patient data). With it, Symptom Search ranks and
// /diagnose walks question-by-question trees without a network. Refreshing
// also fetches the two pages and their scripts so the service worker has
// them for offline use.
//
// CommonJS so jest can load it without a Babel config (see __tests__).

const BUNDLE_CACHE = 'realdiag-offline-bundle'
const BUNDLE_KEY = '/offline-bundle.json'
const OFFLINE_PAGES = ['/symptom-search', '/diagnose']

function cacheStorage() {
  return typeof caches !== 'undefined' ? caches : null
}

async function loadStoredBundle(storage = cacheStorage()) {
  if (!storage) return null
  try {
    const cache = await storage.open(BUNDLE_CACHE)
    const response = await cache.match(BUNDLE_KEY)
    if (!response) return null
    const bundle = await response.json()
    return bundle && bundle.version && bundle.search ? bundle : null
  } catch (err) {
    return null
  }
}

async function storeBundle(bundle, storage = cacheStorage()) {
  const cache = await storage.open(BUNDLE_CACHE)
  await cache.put(BUNDLE_KEY, new Response(JSON.stringify(bundle), {
    headers: { 'Content-Type': 'application/json', 'X-RealDiag-Bundle-Version': bundle.version },
  }))
}

// Script and stylesheet URLs a page's HTML loads from /_next/static/.
function pageAssets(html) {
  const urls = new Set()
  for (const m of String(html).matchAll(/(?:src|href)="(\/_next\/static\/[^"]+)"/g)) urls.add(m[1])
  return [...urls]
}

// Fetch the offline pages and their assets so the service worker caches them.
async function warmPages(fetchFn, pages = OFFLINE_PAGES) {
  for (const page of pages) {
    const response = await fetchFn(page, { credentials: 'same-origin' })
    if (!response.ok) continue
    const assets = pageAssets(await response.text())
    await Promise.all(assets.map((url) => fetchFn(url).catch(() => null)))
  }
}

// -> { status: 'current' | 'updated' | 'failed', version, stored, error }
// apiFetchFn: (path) => Response (credentials included); fetchFn for pages.
async function refreshBundle({ apiFetchFn, fetchFn, storage = cacheStorage() }) {
  const stored = await loadStoredBundle(storage)
  try {
    const versionResponse = await apiFetchFn('/offline/bundle/version')
    if (!versionResponse.ok) throw new Error(`HTTP ${versionResponse.status}`)
    const remote = await versionResponse.json()
    if (stored && stored.version === remote.version) {
      return { status: 'current', version: stored.version, stored }
    }
    const bundleResponse = await apiFetchFn('/offline/bundle')
    if (!bundleResponse.ok) throw new Error(`HTTP ${bundleResponse.status}`)
    const bundle = await bundleResponse.json()
    if (!bundle.version || !bundle.search) throw new Error('The downloaded bundle is incomplete.')
    await storeBundle(bundle, storage)
    if (fetchFn) await warmPages(fetchFn).catch(() => null)
    return { status: 'updated', version: bundle.version, stored: bundle }
  } catch (err) {
    return { status: 'failed', version: stored ? stored.version : null, stored, error: err.message }
  }
}

// Questionnaire trees in the bundle, shaped like GET /diagnostic/trees entries.
function bundleQuestionnaireTrees(bundle) {
  return Object.values((bundle && bundle.questionnaires) || {}).map((q) => ({
    ...q.tree, node_format: 'questionnaire', walk_available: true,
  }))
}

// One questionnaire, shaped like GET /diagnostic/trees/{id}/questionnaire.
function bundleQuestionnaire(bundle, treeId) {
  const q = bundle && bundle.questionnaires && bundle.questionnaires[treeId]
  return q ? { ...q, clinical_review_notice: bundle.clinical_review_notice } : null
}

function bundleSummary(bundle) {
  if (!bundle) return 'No offline library on this device yet. Open this page once while online and signed in.'
  const q = Object.keys(bundle.questionnaires || {}).length
  return `Offline library ${bundle.version}: ${bundle.tree_count} trees for symptom search, ` +
    `${q} question-by-question trees.`
}

module.exports = {
  BUNDLE_CACHE, BUNDLE_KEY, OFFLINE_PAGES, loadStoredBundle, storeBundle, refreshBundle, pageAssets, warmPages,
  bundleSummary, bundleQuestionnaireTrees, bundleQuestionnaire,
}
