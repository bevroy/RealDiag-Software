const fs = require('fs')
const path = require('path')
const vm = require('vm')
const schema = require('../public/offline-db-schema')

const read = (...p) => fs.readFileSync(path.join(__dirname, '..', ...p), 'utf8')

function fakeDb() {
  const stores = {}
  return {
    stores,
    objectStoreNames: { contains: (n) => n in stores },
    createObjectStore(name, options) {
      const indexes = []
      stores[name] = { options, indexes }
      return { createIndex: (n, key) => indexes.push([n, key]) }
    },
  }
}

describe('shared offline database schema', () => {
  test('one name, one version, and the stores both sides use', () => {
    expect(schema.name).toBe('RealDiagOfflineDB')
    expect(schema.version).toBe(4)
    const db = fakeDb()
    schema.upgrade(db)
    expect(Object.keys(db.stores).sort()).toEqual(['favorites', 'rules', 'searches', 'syncQueue', 'userData'])
    schema.upgrade(db) // idempotent: an existing store is not recreated
    expect(Object.keys(db.stores)).toHaveLength(5)
  })

  test('the service worker loads the same schema (as self.REALDIAG_OFFLINE_DB)', () => {
    const sandbox = { self: {} }
    vm.runInNewContext(read('public', 'offline-db-schema.js'), sandbox)
    expect(sandbox.self.REALDIAG_OFFLINE_DB.version).toBe(schema.version)
    const sw = read('public', 'sw.js')
    expect(sw).toMatch(/importScripts\('\/offline-db-schema\.js'\)/)
    expect(sw).toMatch(/const DB_VERSION = OFFLINE_DB\.version;/)
    expect(sw).not.toMatch(/const DB_VERSION = \d/)
  })

  test('the pages use the same schema, with no version of their own', () => {
    const manager = read('utils', 'offlineManager.js')
    expect(manager).toMatch(/import OFFLINE_DB from '\.\.\/public\/offline-db-schema'/)
    expect(manager).toMatch(/const DB_VERSION = OFFLINE_DB\.version;/)
    expect(manager).not.toMatch(/const DB_VERSION = \d/)
  })
})
