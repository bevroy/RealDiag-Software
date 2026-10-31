// Promise wrappers for IndexedDB.
//
// IndexedDB requests (store.get, store.getAll, store.put, ...) are not
// promises: `await store.getAll()` resolves immediately to the IDBRequest
// itself, not its result. Wrap every request with requestToPromise, and wait
// for writes with transactionDone so they have committed.
//
// CommonJS so jest can load it without a Babel config (see __tests__).

function requestToPromise(request) {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

function transactionDone(transaction) {
  return new Promise((resolve, reject) => {
    transaction.oncomplete = () => resolve()
    transaction.onerror = () => reject(transaction.error)
    transaction.onabort = () => reject(transaction.error || new Error('IndexedDB transaction aborted'))
  })
}

module.exports = { requestToPromise, transactionDone }
