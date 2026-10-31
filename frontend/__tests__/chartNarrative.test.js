const { buildNarrative, sourceText, NARRATIVE_LABEL } = require('../utils/chartNarrative')

const assessment = {
  summary: {
    name: 'Test Patient', age: 62, gender: 'male', active_problems: ['Hypertension', 'Type 2 diabetes'],
    allergies: [{ name: 'Penicillin', reaction: 'Rash' }],
    recent_vitals: [
      { name: 'Heart rate', value: 112, unit: '/min', date: '2026-10-30T08:00:00' },
      { name: 'Heart rate', value: 80, unit: '/min', date: '2026-10-28T08:00:00' }],
    abnormal_labs: [{ name: 'HbA1c', value: 8.2, unit: '%', date: '2026-10-01T00:00:00', preliminary: false }],
    data_status: { conditions: 'retrieved', allergies: 'retrieved' },
  },
  extracted_summary: {
    facts: [
      { kind: 'chief_complaint', text: 'chest pain', section: 'chief_complaint',
        source: { resource_type: 'DocumentReference', document_id: 'doc-1', document_type: 'Progress Note', date: '2026-10-28' } },
      { kind: 'problem', text: 'Chest pain, rule out ACS', section: 'assessment',
        source: { resource_type: 'DocumentReference', document_id: 'doc-1', document_type: 'Progress Note', date: '2026-10-28' } },
      { kind: 'finding', text: 'BP 152/94', label: 'Blood pressure', value: '152/94', unit: 'mmHg', section: 'hpi',
        source: { resource_type: 'DocumentReference', document_id: 'doc-1', document_type: 'Progress Note', date: '2026-10-28' } }],
  },
}

describe('buildNarrative', () => {
  const { label, sentences } = buildNarrative(assessment)
  const texts = sentences.map((s) => s.text)

  test('every sentence restates facts and has at least one source', () => {
    expect(label).toBe(NARRATIVE_LABEL)
    expect(sentences.every((s) => s.sources.length > 0 && s.sources.every((x) => x.resource_type))).toBe(true)
  })

  test('structured chart data', () => {
    expect(texts).toContain('Test Patient is a 62-year-old male.')
    expect(texts).toContain('Problem list: Hypertension and Type 2 diabetes.')
    expect(texts).toContain('Recorded allergies: Penicillin (Rash).')
    expect(texts).toContain('Vital signs recorded on 2026-10-30: Heart rate 112 /min.')
    expect(texts).toContain("HbA1c was 8.2 % on 2026-10-01, outside the lab's reference range.")
  })

  test('note facts cite the document, its date and section', () => {
    expect(texts).toContain('The Progress Note of 2026-10-28 records the chief complaint "chest pain".')
    expect(texts).toContain('The Progress Note of 2026-10-28 lists these problems: Chest pain, rule out ACS.')
    const findings = sentences.find((s) => s.text.startsWith('The Progress Note of 2026-10-28 records Blood pressure'))
    expect(sourceText(findings.sources[0])).toBe('DocumentReference, Progress Note, id doc-1, section: hpi, 2026-10-28')
  })

  test('data that could not be retrieved is said so, never as none', () => {
    const { sentences: s } = buildNarrative({ summary: { name: 'X', age: null, data_status: { conditions: 'failed' } } })
    expect(s.map((x) => x.text)).toContain('The problem list could not be retrieved.')
  })
})
