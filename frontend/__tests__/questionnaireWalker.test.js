const { questionnaireTrees, walkQuestionnaire, walkEndMessage } = require('../utils/questionnaireWalker')

const q = {
  entry: 'duration',
  nodes: {
    duration: { kind: 'question', text: 'Duration of cough?', options: [
      { label: '< 3 weeks', next: 'acute' }, { label: '≥ 3 weeks', next: 'chronic' }, { label: 'Other', next: 'gone' }] },
    acute: { kind: 'question', text: 'Fever?', options: [{ label: 'Yes', next: 'cap' }, { label: 'No', next: 'duration' }] },
    chronic: { kind: 'outcome', title: 'Chronic cough', workup: [], treatment: [], recommendations: [], icd10: [], urgency: null },
    cap: { kind: 'outcome', title: 'Pneumonia', workup: ['CXR'], treatment: [], recommendations: [], icd10: ['J18.9'], urgency: 'high' },
  },
}

describe('walkQuestionnaire', () => {
  test('starts at the entry question', () => {
    const walk = walkQuestionnaire(q, [])
    expect(walk.endReason).toBe('question')
    expect(walk.current.text).toBe('Duration of cough?')
  })

  test('follows the chosen options to an outcome, recording each answer', () => {
    const walk = walkQuestionnaire(q, [0, 0])
    expect(walk.outcome.title).toBe('Pneumonia')
    expect(walk.path).toEqual([
      { id: 'duration', question: 'Duration of cough?', answer: '< 3 weeks' },
      { id: 'acute', question: 'Fever?', answer: 'Yes' }])
  })

  test('content problems stop the walk with a message', () => {
    const missing = walkQuestionnaire(q, [2])
    expect(missing.endReason).toBe('missing_node')
    expect(walkEndMessage(missing)).toMatch(/missing from the tree content/)
    const loop = walkQuestionnaire(q, [0, 1, 0])
    expect(loop.endReason).toBe('loop')
  })

  test('only walkable questionnaire trees are listed', () => {
    expect(questionnaireTrees([
      { id: 'A', node_format: 'questionnaire', walk_available: true },
      { id: 'B', node_format: 'conditional', walk_available: true },
      { id: 'C', node_format: 'questionnaire', walk_available: false }]).map((t) => t.id)).toEqual(['A'])
  })
})
