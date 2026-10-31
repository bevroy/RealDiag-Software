const {
  parseEncounterAssessment,
  evidenceLabel,
  MISSING_SECTION_WARNING,
  MISSED_ITEMS_UNAVAILABLE,
} = require('../utils/encounterAssessment')

const body = {
  summary: { name: 'A', summary_text: 'A is a 62-year-old male.', data_warnings: [], cut_off_notes: [] },
  complaint: { text: 'chest pain', source: 'entered', source_label: 'Entered by clinician' },
  diagnoses: {
    items: [{ tree_id: 'CARD-ACUTE-CORONARY-SYNDROME', evidence: 'complaint and criteria' }],
    complaint_matches_total: 22,
    complaint_matches_shown: 15,
    complaint_matches_note: 'Showing 15 of 22 complaint matches.',
  },
  guidance: [{ tree_id: 'CARD-ACUTE-CORONARY-SYNDROME', treatment: { label: 'L', sections: [] } }],
  red_flags: [{ tree_id: 'CARD-ACUTE-CORONARY-SYNDROME', red_flags: [], note: 'No red flags listed for this condition.' }],
  not_assessed: [{ category: 'data', text: 'Lab results could not be retrieved; do not assume none.' }],
  decision_support_notice: 'Decision support only.',
  clinical_review_notice: 'Clinical content is under review.',
}

test('sections are passed through and indexed by tree', () => {
  const parsed = parseEncounterAssessment(body)
  expect(parsed.diagnoses).toHaveLength(1)
  expect(parsed.complaintMatchesNote).toBe('Showing 15 of 22 complaint matches.')
  expect(parsed.guidanceById['CARD-ACUTE-CORONARY-SYNDROME'].treatment.label).toBe('L')
  expect(parsed.redFlagsById['CARD-ACUTE-CORONARY-SYNDROME'].note).toBe('No red flags listed for this condition.')
  expect(parsed.notAssessed[0].text).toMatch(/could not be retrieved/)
  expect(parsed.complaint.source_label).toBe('Entered by clinician')
})

test('missing not-assessed section is never shown as complete', () => {
  const parsed = parseEncounterAssessment({ ...body, not_assessed: undefined })
  expect(parsed.notAssessed).toEqual([{ category: 'data', text: MISSING_SECTION_WARNING }])
})

test('empty response renders safely', () => {
  const parsed = parseEncounterAssessment(null)
  expect(parsed.diagnoses).toEqual([])
  expect(parsed.complaint.source).toBe('none')
  expect(parsed.notAssessed[0].text).toBe(MISSING_SECTION_WARNING)
})

test('missed items pass through, and a missing section says the check did not run', () => {
  const missed = { title: 'Possible missed items', notice: 'n', item_count: 1,
    checks: [{ type: 'overdue_screening', title: 'Screenings that may be due', not_checked: [], items: [{ summary: 's' }] }] }
  expect(parseEncounterAssessment({ ...body, missed_items: missed }).missedItems).toEqual(missed)
  const absent = parseEncounterAssessment(body).missedItems
  expect(absent.checks).toEqual([])
  expect(absent.notice).toBe(MISSED_ITEMS_UNAVAILABLE)
})

test('evidence labels', () => {
  expect(evidenceLabel('complaint and criteria')).toBe("Matches today's complaint and chart criteria")
  expect(evidenceLabel('criteria')).toBe('Chart criteria')
  expect(evidenceLabel('complaint')).toBe("Matches today's complaint")
})

describe('medication review', () => {
  const { parseEncounterAssessment, MEDICATION_REVIEW_UNAVAILABLE } = require('../utils/encounterAssessment')

  test('passes the section through', () => {
    const review = { title: 'Medication review', notice: 'n', medications: ['Warfarin 5 mg'], alerts: [{ type: 'drug_interaction' }], history: null, not_checked: [] }
    expect(parseEncounterAssessment({ medication_review: review }).medicationReview).toBe(review)
  })

  test('a missing section is reported as not reviewed, never as no alerts', () => {
    const review = parseEncounterAssessment({}).medicationReview
    expect(review.alerts).toEqual([])
    expect(review.not_checked).toEqual([MEDICATION_REVIEW_UNAVAILABLE])
  })
})
