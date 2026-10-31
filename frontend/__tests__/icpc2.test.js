const { icpc2Label } = require('../utils/icpc2')

test('pending status is shown when there are no codes', () => {
  expect(icpc2Label({ icpc2: [], icpc2_status: 'pending licensed mapping and review' }))
    .toBe('ICPC-2: pending licensed mapping and review')
})

test('codes are shown once a reviewed mapping exists', () => {
  expect(icpc2Label({ icpc2: ['R05', 'R78'], icpc2_status: 'reviewed' })).toBe('ICPC-2: R05, R78')
})

test('nothing for responses without ICPC-2 fields', () => {
  expect(icpc2Label({ icd10: 'J18.9' })).toBeNull()
})
