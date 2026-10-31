// offline.html must describe only what works offline (see the Phase 2 fixes).
const fs = require('fs')
const path = require('path')

const html = fs.readFileSync(path.join(__dirname, '..', 'public', 'offline.html'), 'utf8')

describe('offline.html', () => {
  test('makes no claims for things that do not work offline', () => {
    for (const claim of ['Access cached diagnostic rules', 'View previous search results', 'Browse saved favorites',
      'Use clinical calculators', 'Auto-sync when back online', 'still available in offline mode']) {
      expect(html).not.toContain(claim)
    }
  })

  test('says what does and does not work', () => {
    expect(html).toContain('may still open from this device')
    expect(html).toContain('ranks from the offline library on this device')
    expect(html).toContain('question-by-question trees run from the offline library')
    expect(html).toContain('evaluate entered findings need a connection')
    expect(html).toContain('need a connection')
    expect(html).toContain('Nothing you do offline is saved for later or sent when you reconnect.')
  })
})
