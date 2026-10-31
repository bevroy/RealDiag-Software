// Recognising "you're offline" for requests that need the server.
//
// When the browser is offline, the service worker (public/sw.js) answers a
// POST with HTTP 503, the header X-RealDiag-Offline: 1 and a JSON body
// { offline: true, ... } instead of a fake success, so pages can say the
// user is offline rather than showing "no results".
//
// CommonJS so jest can load it without a Babel config (see __tests__).

const OFFLINE_HEADER = 'X-RealDiag-Offline'
const OFFLINE_SEARCH_MESSAGE =
  "You're offline. Symptom search needs a connection to the RealDiag server; try again when you're back online."

function isOfflineResponse(response) {
  return Boolean(response && response.status === 503 && response.headers &&
    typeof response.headers.get === 'function' && response.headers.get(OFFLINE_HEADER) === '1')
}

// True when a fetch failed because there is no connection (no service worker
// response at all, e.g. before it is installed).
function isOfflineError(error, navigatorLike) {
  const nav = navigatorLike || (typeof navigator !== 'undefined' ? navigator : null)
  return Boolean(error && error.name === 'TypeError' && nav && nav.onLine === false)
}

module.exports = { OFFLINE_HEADER, OFFLINE_SEARCH_MESSAGE, isOfflineResponse, isOfflineError }
