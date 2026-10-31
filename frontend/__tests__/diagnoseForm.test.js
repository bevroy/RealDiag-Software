const fs = require('fs')
const path = require('path')
const {
  NOT_ASSESSED,
  walkableTrees,
  unavailableTrees,
  displayLabel,
  emptyAnswers,
  buildSteps,
  toggle,
  findingOptionKey,
  findingFromOptionKey,
  buildPatientBody,
  endReasonMessage,
} = require('../utils/diagnoseForm')

// Shape of GET /diagnostic/trees/ENT-SORE-THROAT/inputs
const soreThroatInputs = {
  symptoms: ['stridor', 'unable_to_swallow'],
  exam: ['trismus', 'tonsillar_exudates'],
  red_flags: [],
  patient_characteristics: [],
  no_red_flags: [],
  findings: { rapid_strep: ['positive'], centor_score: ['2-3', '>=4'], recent_attempt: [true, false] },
  uses_age: false,
  uses_onset_hours: false,
  uses_diagnosis: false,
}

test('only conditional trees are offered for walking', () => {
  const trees = [
    { id: 'ENT-SORE-THROAT', node_format: 'conditional' },
    { id: 'PULM-COUGH', node_format: 'questionnaire' },
    { id: 'GEN-MED-OBESITY', node_format: 'content' },
    { id: 'CARD-ACS', node_format: 'none' },
  ]
  expect(walkableTrees(trees).map((t) => t.id)).toEqual(['ENT-SORE-THROAT'])
  expect(walkableTrees(undefined)).toEqual([])
})

test('trees pending content review are held back and listed for the note', () => {
  const trees = [
    { id: 'ENT-SORE-THROAT', node_format: 'conditional', walk_available: true },
    { id: 'ID-FEVER', title: 'Fever Workup', node_format: 'conditional', walk_available: false },
    { id: 'PSYCH-PSYCHOSIS', title: 'Psychosis', node_format: 'conditional', walk_available: false },
    { id: 'PULM-COUGH', node_format: 'questionnaire', walk_available: false },
  ]
  expect(walkableTrees(trees).map((t) => t.id)).toEqual(['ENT-SORE-THROAT'])
  expect(unavailableTrees(trees).map((t) => t.id)).toEqual(['ID-FEVER', 'PSYCH-PSYCHOSIS'])
  // An older API without walk_available still offers conditional trees.
  expect(walkableTrees([{ id: 'X', node_format: 'conditional' }])).toHaveLength(1)
})

test('steps skip sections the tree does not use', () => {
  expect(buildSteps(soreThroatInputs)).toEqual(['symptoms', 'exam', 'findings', 'medications'])
  expect(buildSteps({ ...soreThroatInputs, uses_age: true, red_flags: ['hypotension'] }))
    .toEqual(['patient', 'symptoms', 'exam', 'red_flags', 'findings', 'medications'])
  expect(buildSteps({ ...emptyAnswers(), findings: {}, no_red_flags: ['no LOC'] })).toEqual(['findings', 'medications'])
  expect(buildSteps(null)).toEqual([])
})

test('tree tokens are shown with spaces and booleans as Yes/No', () => {
  expect(displayLabel('unable_to_swallow')).toBe('unable to swallow')
  expect(displayLabel('>=4')).toBe('>=4')
  expect(displayLabel(true)).toBe('Yes')
  expect(displayLabel(false)).toBe('No')
})

test('finding select values round-trip to the tree value', () => {
  for (const value of ['positive', '>=4', true, false]) {
    expect(findingFromOptionKey(findingOptionKey(value))).toBe(value)
  }
  expect(findingFromOptionKey(NOT_ASSESSED)).toBeUndefined()
})

test('patient body sends only what was answered', () => {
  const answers = emptyAnswers()
  answers.symptoms = toggle(answers.symptoms, 'stridor')
  answers.exam = toggle(toggle(answers.exam, 'trismus'), 'trismus')
  answers.findings = { rapid_strep: 'positive', centor_score: undefined, recent_attempt: false }
  answers.age = '17'
  answers.onset_hours = ''
  answers.diagnosis = '  '
  expect(buildPatientBody(answers)).toEqual({
    symptoms: ['stridor'],
    exam: [],
    red_flags: [],
    patient_characteristics: [],
    no_red_flags: [],
    findings: { rapid_strep: 'positive', recent_attempt: false },
    age: 17,
  })
})

test('stop reasons are explained; a normal end node needs no message', () => {
  expect(endReasonMessage({ evaluated: true, path: ['a', 'end_node'], end_reason: 'end_node' })).toBeNull()
  expect(endReasonMessage({ evaluated: true, path: ['ruq_pain'], end_reason: 'no_matching_branch' }))
    .toMatch(/None of the next steps after "ruq pain" matched/)
  expect(endReasonMessage({
    evaluated: true, path: ['initial_assessment'], end_reason: 'missing_node', missing_node: 'localized_infection',
  })).toMatch(/"localized infection"\) is missing from the tree content/)
  expect(endReasonMessage({ evaluated: false, warning: 'x' })).toBeNull()
  expect(endReasonMessage(null)).toBeNull()
})

test('/diagnose has no hard-coded symptom lists for trees that do not exist', () => {
  const src = fs.readFileSync(path.join(__dirname, '..', 'pages', 'diagnose.js'), 'utf8')
  expect(src).not.toMatch(/NEU-HEADACHE|NEU-VERTIGO/)
  expect(src).toMatch(/\/diagnostic\/trees\/\$\{encodeURIComponent\(treeId\)\}\/inputs/)
})

test('/diagnose notes trees that are temporarily unavailable', () => {
  const src = fs.readFileSync(path.join(__dirname, '..', 'pages', 'diagnose.js'), 'utf8')
  expect(src).toMatch(/temporarily unavailable pending\s+content review/)
})

test('/diagnose shows the clinical review notice and review status', () => {
  const src = fs.readFileSync(path.join(__dirname, '..', 'pages', 'diagnose.js'), 'utf8')
  expect((src.match(/<ClinicalReviewNotice/g) || []).length).toBeGreaterThanOrEqual(3)
  expect((src.match(/<ReviewStatusBadge/g) || []).length).toBeGreaterThanOrEqual(2)
})

test('the menu links to /diagnose', () => {
  const src = fs.readFileSync(path.join(__dirname, '..', 'components', 'RoleBasedNavigation.jsx'), 'utf8')
  expect(src).toMatch(/href: '\/diagnose', label: '[^']*Step-by-Step Decision Trees', roles: \['all'\]/)
})

describe('itemsWithSource', () => {
  const { itemsWithSource } = require('../utils/diagnoseForm')

  test('uses the per-node lists, in path order, with their steps', () => {
    const result = {
      tests: ['CBC', 'BMP'],
      tests_by_node: [{ text: 'CBC', nodes: ['start', 'end'] }, { text: 'BMP', nodes: ['middle'] }],
    }
    expect(itemsWithSource(result, 'tests')).toEqual(result.tests_by_node)
  })

  test('falls back to the plain list without steps', () => {
    expect(itemsWithSource({ referrals: ['ENT'] }, 'referrals')).toEqual([{ text: 'ENT', nodes: [] }])
    expect(itemsWithSource({}, 'provisional_dx')).toEqual([])
  })
})

describe('medications and allergies', () => {
  const { buildPatientBody, emptyAnswers, splitList } = require('../utils/diagnoseForm')

  test('typed lists become current_medications and allergies', () => {
    expect(splitList('warfarin 5 mg, aspirin 81 mg\nmetoprolol;')).toEqual(['warfarin 5 mg', 'aspirin 81 mg', 'metoprolol'])
    const body = buildPatientBody({ ...emptyAnswers(), medications: 'warfarin 5 mg, aspirin 81 mg', allergies: 'penicillin' })
    expect(body.current_medications).toEqual(['warfarin 5 mg', 'aspirin 81 mg'])
    expect(body.allergies).toEqual(['penicillin'])
  })

  test('nothing typed sends nothing', () => {
    const body = buildPatientBody(emptyAnswers())
    expect(body.current_medications).toBeUndefined()
    expect(body.allergies).toBeUndefined()
  })
})
