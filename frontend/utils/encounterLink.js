// Link to the Encounter Assessment page (/encounter) for the SMART launch
// patient. Only meaningful during an active SMART on FHIR session, which the
// page needs to read the chart; returns null without a patient.
//
// CommonJS so jest can load it without a Babel config (see __tests__).

function encounterHref(patientId) {
  if (!patientId) return null
  return `/encounter?patient_id=${encodeURIComponent(patientId)}`
}

module.exports = { encounterHref }
