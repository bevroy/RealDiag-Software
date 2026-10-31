const fs = require('fs')
const path = require('path')
const { encounterHref } = require('../utils/encounterLink')

const read = (...p) => fs.readFileSync(path.join(__dirname, '..', ...p), 'utf8')

describe('Encounter Assessment links', () => {
  test('href for the SMART launch patient, encoded; none without a patient', () => {
    expect(encounterHref('abc123')).toBe('/encounter?patient_id=abc123')
    expect(encounterHref('a b/c')).toBe('/encounter?patient_id=a%20b%2Fc')
    expect(encounterHref(null)).toBeNull()
    expect(encounterHref('')).toBeNull()
  })

  test('/inpatient links to it', () => {
    const page = read('app', 'inpatient', 'page.jsx')
    expect(page).toMatch(/encounterHref\(patientId\)/)
    expect(page).toMatch(/Encounter Assessment →/)
  })

  test('the nav shows it only inside the SMART-session block', () => {
    const nav = read('components', 'RoleBasedNavigation.jsx')
    const block = nav.slice(nav.indexOf('if (smartActive) {'))
    const end = block.indexOf('\n  }\n')
    expect(block.slice(0, end)).toMatch(/encounterHref\(smartPatientId\)/)
    expect(nav.indexOf('Encounter Assessment')).toBeGreaterThan(nav.indexOf('if (smartActive) {'))
  })
})
