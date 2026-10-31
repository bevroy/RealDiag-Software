const fs = require('fs')
const path = require('path')
const { downloadRules, downloadMessage } = require('../utils/ruleDownload')

const ok = (body) => ({ ok: true, status: 200, json: async () => body })

describe('downloadRules', () => {
  test('saves every rule from /rules/all and reports success', async () => {
    const saved = []
    const progress = []
    const result = await downloadRules({
      fetchRules: async () => ok({ version: 'abc', rules: [{ id: 'A' }, { id: 'B' }] }),
      saveRule: async (r) => saved.push(r.id),
      onProgress: (p) => progress.push(p.percentage),
    })
    expect(saved).toEqual(['A', 'B'])
    expect(result).toMatchObject({ success: true, downloaded: 2, total: 2, version: 'abc', error: null })
    expect(progress).toEqual([50, 100])
    expect(downloadMessage(result)).toBe('Downloaded 2 rules (library version abc).')
  })

  test('an HTTP error is a failure, not success', async () => {
    const result = await downloadRules({ fetchRules: async () => ({ ok: false, status: 404 }), saveRule: async () => {} })
    expect(result.success).toBe(false)
    expect(downloadMessage(result)).toBe('Rule download failed (HTTP 404).')
  })

  test('a network error is a failure', async () => {
    const result = await downloadRules({ fetchRules: async () => { throw new Error('offline') }, saveRule: async () => {} })
    expect(result).toMatchObject({ success: false, error: 'Rule download failed: offline' })
  })

  test('rules that cannot be saved make it a failure with a count', async () => {
    const result = await downloadRules({
      fetchRules: async () => ok({ rules: [{ id: 'A' }, { id: 'B' }, { id: 'C' }] }),
      saveRule: async (r) => { if (r.id === 'B') throw new Error('quota') },
    })
    expect(result).toMatchObject({ success: false, downloaded: 2, total: 3 })
    expect(downloadMessage(result)).toBe('1 of 3 rules could not be saved on this device.')
  })

  test('an empty library is a failure', async () => {
    const result = await downloadRules({ fetchRules: async () => ok({ rules: [] }), saveRule: async () => {} })
    expect(result.success).toBe(false)
  })

  test('offlineManager uses the real endpoint, not /rules/list', () => {
    const src = fs.readFileSync(path.join(__dirname, '..', 'utils', 'offlineManager.js'), 'utf8')
    expect(src).toMatch(/apiFetch\('\/rules\/all'\)/)
    expect(src).not.toMatch(/\/rules\/list/)
  })
})
