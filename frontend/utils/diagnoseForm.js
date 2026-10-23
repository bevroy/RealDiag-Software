// Form logic for /diagnose (walking a conditional decision tree).
//
// The answer choices come from GET /diagnostic/trees/{id}/inputs, which reads
// them from the tree's own branches, so every choice can change the walk and
// the wording is the tree's. Nothing here adds, ranks or rewrites content.
//
// CommonJS so jest can load it without a Babel config (see __tests__).

const LIST_FIELDS = ['symptoms', 'exam', 'red_flags', 'patient_characteristics', 'no_red_flags']
const NOT_ASSESSED = ''

// Only trees the engine walks automatically. Questionnaire and content-only
// trees are listed with node_format and are not offered on /diagnose; a
// conditional tree with walk_available false (a branch to a missing step,
// pending content review) is held back too.
function walkableTrees(trees) {
  return (trees || []).filter((t) => t.node_format === 'conditional' && t.walk_available !== false)
}

// Conditional trees held back, for the note on /diagnose.
function unavailableTrees(trees) {
  return (trees || []).filter((t) => t.node_format === 'conditional' && t.walk_available === false)
}

// Tree tokens are snake_case ids ("unable_to_swallow"); show them with spaces.
function displayLabel(value) {
  if (value === true) return 'Yes'
  if (value === false) return 'No'
  return String(value).replace(/_/g, ' ')
}

function emptyAnswers() {
  return {
    age: '', onset_hours: '', diagnosis: '',
    symptoms: [], exam: [], red_flags: [], patient_characteristics: [], no_red_flags: [],
    findings: {},
  }
}

// Steps after tree selection, skipping any the tree has nothing for.
function buildSteps(inputs) {
  if (!inputs) return []
  const steps = []
  if (inputs.uses_age || inputs.uses_onset_hours || inputs.uses_diagnosis) steps.push('patient')
  if (inputs.symptoms && inputs.symptoms.length) steps.push('symptoms')
  if (inputs.exam && inputs.exam.length) steps.push('exam')
  if (inputs.red_flags && inputs.red_flags.length) steps.push('red_flags')
  const hasFindings = inputs.findings && Object.keys(inputs.findings).length > 0
  if (hasFindings || (inputs.patient_characteristics || []).length || (inputs.no_red_flags || []).length) {
    steps.push('findings')
  }
  return steps
}

const STEP_TITLES = {
  tree: 'Select Decision Tree',
  patient: 'Patient Information',
  symptoms: 'Symptoms',
  exam: 'Examination Findings',
  red_flags: 'Red Flags',
  findings: 'Other Findings',
}

function toggle(list, value) {
  return list.includes(value) ? list.filter((v) => v !== value) : [...list, value]
}

// Select values are strings; map them back to the tree's own value (true,
// false, or the string) so the engine's exact match works.
function findingOptionKey(value) {
  return JSON.stringify(value)
}

function findingFromOptionKey(key) {
  if (key === NOT_ASSESSED) return undefined
  return JSON.parse(key)
}

function toNumber(text) {
  if (text === '' || text === null || text === undefined) return undefined
  const n = Number(text)
  return Number.isFinite(n) ? n : undefined
}

// Body for POST /diagnostic/evaluate/{id}. Only answers the student gave are
// sent; anything left blank is "not assessed" and matches no branch.
function buildPatientBody(answers) {
  const body = {}
  for (const field of LIST_FIELDS) body[field] = [...(answers[field] || [])]
  const findings = {}
  for (const [name, value] of Object.entries(answers.findings || {})) {
    if (value !== undefined) findings[name] = value
  }
  body.findings = findings
  const age = toNumber(answers.age)
  if (age !== undefined) body.age = age
  const onset = toNumber(answers.onset_hours)
  if (onset !== undefined) body.onset_hours = onset
  if (answers.diagnosis && answers.diagnosis.trim()) body.diagnosis = answers.diagnosis.trim()
  return body
}

// Why the walk stopped, in plain words, or null for a normal end node.
function endReasonMessage(result) {
  if (!result || result.evaluated === false) return null
  const last = result.path && result.path.length ? displayLabel(result.path[result.path.length - 1]) : null
  if (result.end_reason === 'no_matching_branch') {
    return `None of the next steps after "${last}" matched your answers, so the walk stops there. ` +
      'Go back and add findings to continue.'
  }
  if (result.end_reason === 'missing_node') {
    return `The tree's next step ("${displayLabel(result.missing_node)}") is missing from the tree content, ` +
      `so the walk stops at "${last}". This is a content problem, not a problem with your answers.`
  }
  if (result.end_reason === 'loop') {
    return 'The tree content loops back on itself here, so the walk was stopped.'
  }
  return null
}

module.exports = {
  LIST_FIELDS,
  NOT_ASSESSED,
  STEP_TITLES,
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
}
