// Normalizes the /smart/encounter-assessment response for the encounter page.
//
// Missing sections become empty lists so the page always renders every
// heading; a missing "could not be assessed" list is never shown as "nothing
// missing" - it gets an explicit warning instead.
//
// CommonJS so it can be unit-tested with Jest without a Babel config.

const MISSING_SECTION_WARNING =
  'The server did not report what could not be assessed; do not assume the assessment is complete.'

const EVIDENCE_LABELS = {
  'complaint and criteria': "Matches today's complaint and chart criteria",
  criteria: 'Chart criteria',
  complaint: "Matches today's complaint",
}

function evidenceLabel(evidence) {
  return EVIDENCE_LABELS[evidence] || evidence || ''
}

function parseEncounterAssessment(body) {
  const b = body || {}
  const diagnoses = b.diagnoses || {}
  const notAssessed = Array.isArray(b.not_assessed)
    ? b.not_assessed
    : [{ category: 'data', text: MISSING_SECTION_WARNING }]
  const guidanceById = {}
  for (const g of b.guidance || []) guidanceById[g.tree_id] = g
  const redFlagsById = {}
  for (const r of b.red_flags || []) redFlagsById[r.tree_id] = r
  return {
    summary: b.summary || null,
    complaint: b.complaint || { text: null, source: 'none', source_label: 'No complaint entered or found' },
    diagnoses: diagnoses.items || [],
    complaintMatchesNote: diagnoses.complaint_matches_note || null,
    guidanceById,
    redFlags: b.red_flags || [],
    redFlagsById,
    notAssessed,
    decisionSupportNotice: b.decision_support_notice || null,
    clinicalReviewNotice: b.clinical_review_notice,
  }
}

module.exports = { parseEncounterAssessment, evidenceLabel, MISSING_SECTION_WARNING }
