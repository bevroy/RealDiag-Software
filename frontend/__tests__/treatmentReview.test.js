const { reviewedSections, markStyle, factorLines, MARKS } = require('../utils/treatmentReview')

const treatment = {
  label: 'Treatment information from the decision tree (reference, not an order)',
  sections: [{ title: null, items: ['Saline irrigation', 'amoxicillin 500 mg', 'amlodipine 5 mg'] }],
  review: {
    notice: 'Options are listed in the tree\'s order and are not ranked.',
    patient_factors: { renal: { value: 'stage 4', source: 'Lab: eGFR 25 mL/min/1.73m2 on 2026-10-01' }, hepatic: null,
      pregnancy: { value: true, source: 'Problem list: Pregnancy' } },
    not_checked: [],
    sections: [[
      { text: 'Saline irrigation', mark: 'not_checked', medications: [], reasons: [] },
      { text: 'amoxicillin 500 mg', mark: 'avoid', medications: ['amoxicillin'],
        reasons: [{ medication: 'amoxicillin', mark: 'avoid', reason: 'Possible cross-reactivity.', source: 'Allergies: penicillin' }] },
      { text: 'amlodipine 5 mg', mark: 'appropriate', medications: ['amlodipine'], reasons: [] },
    ]],
  },
}

test('pairs each line with its review and keeps the tree order', () => {
  const [section] = reviewedSections(treatment)
  expect(section.items.map((i) => i.text)).toEqual(treatment.sections[0].items)
  expect(section.items.map((i) => i.mark)).toEqual(['not_checked', 'avoid', 'appropriate'])
  expect(section.items[1].reasons[0].source).toBe('Allergies: penicillin')
})

test('a missing or mismatched review leaves lines unmarked, not appropriate', () => {
  const [plain] = reviewedSections({ sections: treatment.sections })
  expect(plain.items.every((i) => i.mark === null)).toBe(true)
  const shifted = { ...treatment, review: { ...treatment.review, sections: [treatment.review.sections[0].slice(1)] } }
  expect(reviewedSections(shifted)[0].items.every((i) => i.mark === null)).toBe(true)
})

test('mark styles and factor lines', () => {
  expect(markStyle('avoid').label).toBe('Avoid')
  expect(markStyle('appropriate').label).toBe('Appropriate (no conflict found)')
  expect(markStyle(null)).toBeNull()
  expect(Object.keys(MARKS)).toEqual(['appropriate', 'caution', 'avoid', 'not_checked'])
  expect(factorLines(treatment.review)).toEqual([
    'Renal function: stage 4 (Lab: eGFR 25 mL/min/1.73m2 on 2026-10-01)',
    'Pregnancy (Problem list: Pregnancy)',
  ])
})
