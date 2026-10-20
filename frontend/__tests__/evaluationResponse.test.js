const {
  parseEvaluationResponse,
  UNKNOWN_COMPLETENESS_WARNING,
} = require('../utils/evaluationResponse')

const evaluation = { diagnosis_id: 'CARD-ACS', diagnosis_label: 'Acute Coronary Syndrome' }

test('current object response is passed through', () => {
  const parsed = parseEvaluationResponse({
    evaluations: [evaluation],
    data_status: { allergies: 'failed' },
    data_warnings: ['Allergies could not be retrieved; do not assume none.'],
    data_notes: ['Potassium: result has no value; skipped.'],
  })
  expect(parsed.evaluations).toEqual([evaluation])
  expect(parsed.dataStatus).toEqual({ allergies: 'failed' })
  expect(parsed.dataWarnings).toEqual(['Allergies could not be retrieved; do not assume none.'])
  expect(parsed.dataNotes).toHaveLength(1)
})

test('object response with complete data has no warnings', () => {
  const parsed = parseEvaluationResponse({ evaluations: [], data_status: {}, data_warnings: [] })
  expect(parsed.evaluations).toEqual([])
  expect(parsed.dataWarnings).toEqual([])
})

test('older list response keeps evaluations but is never treated as complete', () => {
  const parsed = parseEvaluationResponse([evaluation])
  expect(parsed.evaluations).toEqual([evaluation])
  expect(parsed.dataWarnings).toEqual([UNKNOWN_COMPLETENESS_WARNING])
})

test('older empty list response is not an all-clear', () => {
  const parsed = parseEvaluationResponse([])
  expect(parsed.evaluations).toEqual([])
  expect(parsed.dataWarnings).toHaveLength(1)
})

test.each([null, undefined, 'error', { detail: 'Evaluation failed' }])(
  'unreadable response %p shows a warning instead of an empty review',
  (body) => {
    const parsed = parseEvaluationResponse(body)
    expect(parsed.evaluations).toEqual([])
    expect(parsed.dataWarnings[0]).toMatch(/could not be read/)
  }
)

test('assessment warnings are passed through', () => {
  const warning = 'Chronic conditions could not be assessed: lab results could not be retrieved.'
  expect(parseEvaluationResponse({ evaluations: [], assessment_warnings: [warning] }).assessmentWarnings).toEqual([warning])
  expect(parseEvaluationResponse([]).assessmentWarnings).toEqual([])
})

test('clinical review notice is passed through, including null once reviewed', () => {
  const notice = 'Clinical content is under review.'
  expect(parseEvaluationResponse({ evaluations: [], clinical_review_notice: notice }).clinicalReviewNotice).toBe(notice)
  expect(parseEvaluationResponse({ evaluations: [], clinical_review_notice: null }).clinicalReviewNotice).toBeNull()
  expect(parseEvaluationResponse([]).clinicalReviewNotice).toBeUndefined()
})
