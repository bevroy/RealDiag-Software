const fs = require('fs')
const path = require('path')
const { URGENCY_COLORS, urgencyBadgeColor } = require('../utils/urgencyBadge')

describe('urgencyBadgeColor', () => {
  test('emergent is red, urgent amber, routine green', () => {
    expect(urgencyBadgeColor('emergent')).toBe('#dc2626')
    expect(urgencyBadgeColor('urgent')).toBe('#f59e0b')
    expect(urgencyBadgeColor('routine')).toBe('#10b981')
  })

  test('emergent is not shown in the routine color', () => {
    expect(urgencyBadgeColor('emergent')).not.toBe(URGENCY_COLORS.routine)
  })

  test('case and whitespace do not matter; critical stays red', () => {
    expect(urgencyBadgeColor(' Emergent ')).toBe('#dc2626')
    expect(urgencyBadgeColor('critical')).toBe('#dc2626')
  })

  test('every urgency used by the trees has its own color', () => {
    const dir = path.join(__dirname, '..', '..', 'backend', 'trees')
    const used = new Set()
    for (const f of fs.readdirSync(dir).filter((n) => n.endsWith('.yml'))) {
      const m = fs.readFileSync(path.join(dir, f), 'utf8').match(/^urgency:\s*['"]?([a-z]+)/m)
      if (m) used.add(m[1])
    }
    expect([...used].sort()).toEqual(['emergent', 'routine', 'urgent'])
    for (const u of used) expect(Object.keys(URGENCY_COLORS)).toContain(u)
  })

  test('/search uses the helper instead of checking for "critical"', () => {
    const page = fs.readFileSync(path.join(__dirname, '..', 'pages', 'search.js'), 'utf8')
    expect(page).toMatch(/urgencyBadgeColor\(result\.urgency\)/)
    expect(page).not.toMatch(/result\.urgency === 'critical'/)
  })
})
