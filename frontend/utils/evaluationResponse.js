// Normalizes the /smart/evaluate-patient response.
//
// Current API: { evaluations, data_status, data_warnings, data_notes }.
// Older API (before chart-safety changes): a bare list of evaluations, with no
// information about which chart data was retrieved. The frontend and backend
// can deploy at different times, so both shapes must work - and an older
// response must never be shown as a complete, all-clear review.
//
// CommonJS so it can be unit-tested with Jest without a Babel config.

const UNKNOWN_COMPLETENESS_WARNING =
  'The server did not report which chart data was retrieved; some data may be missing. Do not assume the review is complete.'

function parseEvaluationResponse(body) {
  if (Array.isArray(body)) {
    return {
      evaluations: body,
      dataStatus: {},
      dataWarnings: [UNKNOWN_COMPLETENESS_WARNING],
      dataNotes: [],
      assessmentWarnings: [],
      clinicalReviewNotice: undefined,
    }
  }
  if (!body || typeof body !== 'object' || !Array.isArray(body.evaluations)) {
    return {
      evaluations: [],
      dataStatus: {},
      dataWarnings: ['The evaluation response could not be read; no evaluations are shown.'],
      dataNotes: [],
      assessmentWarnings: [],
      clinicalReviewNotice: undefined,
    }
  }
  return {
    evaluations: body.evaluations,
    dataStatus: body.data_status || {},
    dataWarnings: Array.isArray(body.data_warnings) ? body.data_warnings : [],
    dataNotes: Array.isArray(body.data_notes) ? body.data_notes : [],
    // e.g. "Chronic conditions could not be assessed: lab results could not be retrieved."
    assessmentWarnings: Array.isArray(body.assessment_warnings) ? body.assessment_warnings : [],
    // undefined when the API predates the field (UI then shows the default notice)
    clinicalReviewNotice: body.clinical_review_notice,
  }
}

module.exports = { parseEvaluationResponse, UNKNOWN_COMPLETENESS_WARNING }
