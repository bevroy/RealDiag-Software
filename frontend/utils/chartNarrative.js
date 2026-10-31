// Readable chart narrative built by templates from facts the encounter
// assessment already returned (chart summary and the rules-based extraction
// from notes). No AI and no server call: given a response, it runs anywhere,
// including offline. Every sentence lists its sources (resource type, date,
// document). Nothing is inferred: a sentence only restates facts.
//
// CommonJS so jest can load it without a Babel config (see __tests__).

const NARRATIVE_LABEL =
  'Narrative built by fixed templates from chart data and text extracted from notes. Not a clinical interpretation.'

function day(value) {
  return value ? String(value).slice(0, 10) : null
}

function list(items) {
  if (items.length <= 1) return items.join('')
  return `${items.slice(0, -1).join(', ')} and ${items[items.length - 1]}`
}

function value(v, unit) {
  return `${v}${unit ? ` ${unit}` : ''}`
}

function noteRef(source) {
  const what = source.document_type || 'Note'
  return source.date ? `The ${what} of ${source.date}` : `A ${what} (undated)`
}

function buildNarrative(assessment) {
  const a = assessment || {}
  const summary = a.summary || {}
  const status = summary.data_status || {}
  const sentences = []
  const add = (text, sources) => sentences.push({ text, sources })

  if (summary.name) {
    const who = summary.age != null ? `${summary.name} is a ${summary.age}-year-old ${summary.gender || 'patient'}.`
      : `${summary.name}, age unknown.`
    add(who, [{ resource_type: 'Patient' }])
  }

  if (status.conditions && status.conditions !== 'retrieved') {
    add('The problem list could not be retrieved.', [{ resource_type: 'Condition' }])
  } else if ((summary.active_problems || []).length) {
    add(`Problem list: ${list(summary.active_problems)}.`, [{ resource_type: 'Condition', note: 'problem list' }])
  }

  if (status.allergies && status.allergies !== 'retrieved') {
    add('Allergies could not be retrieved.', [{ resource_type: 'AllergyIntolerance' }])
  } else if ((summary.allergies || []).length) {
    const items = summary.allergies.map((x) => (x.reaction ? `${x.name} (${x.reaction})` : x.name))
    add(`Recorded allergies: ${list(items)}.`, [{ resource_type: 'AllergyIntolerance' }])
  }

  const vitalsByDate = {}
  for (const v of summary.recent_vitals || []) {
    const d = day(v.date)
    if (!vitalsByDate[d]) vitalsByDate[d] = {}
    if (!vitalsByDate[d][v.name]) vitalsByDate[d][v.name] = v
  }
  const latestVitalDay = Object.keys(vitalsByDate).sort().reverse()[0]
  if (latestVitalDay) {
    const items = Object.values(vitalsByDate[latestVitalDay]).map((v) => `${v.name} ${value(v.value, v.unit)}`)
    add(`Vital signs recorded on ${latestVitalDay}: ${list(items)}.`,
      [{ resource_type: 'Observation', category: 'vital-signs', date: latestVitalDay }])
  }

  for (const lab of summary.abnormal_labs || []) {
    add(`${lab.name} was ${value(lab.value, lab.unit)}${lab.date ? ` on ${day(lab.date)}` : ''}, outside the lab's reference range` +
      `${lab.preliminary ? ' (preliminary result)' : ''}.`,
      [{ resource_type: 'Observation', category: 'laboratory', date: day(lab.date) }])
  }

  // Notes: one sentence per kind of fact per document.
  const byDoc = new Map()
  for (const fact of (a.extracted_summary && a.extracted_summary.facts) || []) {
    const key = fact.source.document_id || `${fact.source.document_type}|${fact.source.date}`
    if (!byDoc.has(key)) byDoc.set(key, { source: fact.source, facts: [] })
    byDoc.get(key).facts.push(fact)
  }
  for (const { source, facts } of byDoc.values()) {
    const ref = { resource_type: 'DocumentReference', document_id: source.document_id,
      document_type: source.document_type, date: source.date }
    const of = (kind) => facts.filter((f) => f.kind === kind)
    const cc = of('chief_complaint')[0]
    if (cc) add(`${noteRef(source)} records the chief complaint "${cc.text}".`, [{ ...ref, section: cc.section }])
    const problems = of('problem')
    if (problems.length) {
      add(`${noteRef(source)} lists these problems: ${list(problems.map((f) => f.text))}.`,
        [...new Set(problems.map((f) => f.section))].map((section) => ({ ...ref, section })))
    }
    const meds = of('medication')
    if (meds.length) add(`${noteRef(source)} lists these medications: ${list(meds.map((f) => f.text))}.`, [{ ...ref, section: 'medications' }])
    const allergies = of('allergy')
    if (allergies.length) add(`${noteRef(source)} lists these allergies: ${list(allergies.map((f) => f.text))}.`, [{ ...ref, section: 'allergies' }])
    const findings = of('finding')
    if (findings.length) {
      add(`${noteRef(source)} records ${list(findings.map((f) => `${f.label} ${value(f.value, f.unit)}`))}.`,
        [...new Set(findings.map((f) => f.section))].map((section) => ({ ...ref, section })))
    }
  }
  return { label: NARRATIVE_LABEL, sentences }
}

function sourceText(source) {
  const parts = [source.resource_type]
  if (source.category) parts.push(source.category)
  if (source.note) parts.push(source.note)
  if (source.document_type) parts.push(source.document_type)
  if (source.document_id) parts.push(`id ${source.document_id}`)
  if (source.section) parts.push(`section: ${source.section.replace(/_/g, ' ')}`)
  if (source.date) parts.push(source.date)
  return parts.join(', ')
}

module.exports = { buildNarrative, sourceText, NARRATIVE_LABEL }
