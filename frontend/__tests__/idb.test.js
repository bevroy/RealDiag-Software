const fs = require('fs')
const path = require('path')
const { requestToPromise, transactionDone } = require('../utils/idb')

// Minimal stand-ins for IDBRequest / IDBTransaction: events fire later, like the real ones.
function fakeRequest(result, error) {
  const req = { result: undefined, error: null }
  setTimeout(() => {
    if (error) { req.error = error; req.onerror && req.onerror() } else { req.result = result; req.onsuccess && req.onsuccess() }
  }, 0)
  return req
}

describe('IndexedDB promise wrappers', () => {
  test('requestToPromise resolves to the request result, not the request', async () => {
    const req = fakeRequest([{ id: 'A' }])
    expect(await requestToPromise(req)).toEqual([{ id: 'A' }])
  })

  test('requestToPromise rejects with the request error', async () => {
    await expect(requestToPromise(fakeRequest(null, new Error('DataError')))).rejects.toThrow('DataError')
  })

  test('awaiting the raw request (the old bug) does not give the result', async () => {
    const req = fakeRequest([{ id: 'A' }])
    const raw = await req
    expect(Array.isArray(raw)).toBe(false)
  })

  test('transactionDone waits for complete, and rejects on error or abort', async () => {
    const tx = {}
    setTimeout(() => tx.oncomplete(), 0)
    await expect(transactionDone(tx)).resolves.toBeUndefined()
    const failed = { error: new Error('QuotaExceededError') }
    setTimeout(() => failed.onerror(), 0)
    await expect(transactionDone(failed)).rejects.toThrow('QuotaExceededError')
    const aborted = { error: null }
    setTimeout(() => aborted.onabort(), 0)
    await expect(transactionDone(aborted)).rejects.toThrow('aborted')
  })

  test('offlineManager never awaits a raw IndexedDB request', () => {
    const src = fs.readFileSync(path.join(__dirname, '..', 'utils', 'offlineManager.js'), 'utf8')
    expect(src).not.toMatch(/await\s+(store|index)\.(get|getAll|put|add|delete|clear)\(/)
    expect(src).not.toMatch(/return\s+await\s+(store|index)\./)
    // Booleans are not valid IndexedDB keys.
    expect(src).not.toMatch(/getAll\(false\)/)
    for (const fn of ['getRule', 'getAllRules', 'getRulesByFamily', 'getAllSearches', 'getAllFavorites', 'getUserData']) {
      const body = src.slice(src.indexOf(`export async function ${fn}(`))
      expect(body.slice(0, body.indexOf('\n}\n'))).toMatch(/requestToPromise\(/)
    }
  })
})
