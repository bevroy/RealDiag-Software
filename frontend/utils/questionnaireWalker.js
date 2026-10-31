// Walking a questionnaire tree one question at a time (/diagnose).
//
// The tree comes from GET /diagnostic/trees/{id}/questionnaire: an entry node
// id and nodes keyed by id, each a question ({kind: 'question', text, options:
// [{label, next}]}) or an outcome ({kind: 'outcome', title, ...}). Answers are
// the chosen option index for each question in order. Nothing is ranked or
// rewritten: the walk follows the tree's own options.
//
// CommonJS so jest can load it without a Babel config (see __tests__).

function questionnaireTrees(trees) {
  return (trees || []).filter((t) => t.node_format === 'questionnaire' && t.walk_available !== false)
}

// -> { path: [{ id, question, answer }], current, outcome, endReason }
// endReason: 'question' (waiting for an answer), 'outcome', 'end' (an option
// with no next step), 'missing_node' or 'loop' (tree content problems).
function walkQuestionnaire(questionnaire, answers) {
  const nodes = (questionnaire && questionnaire.nodes) || {}
  const path = []
  const seen = new Set()
  let id = questionnaire ? questionnaire.entry : null
  let i = 0
  while (id) {
    if (seen.has(id)) return { path, current: null, outcome: null, endReason: 'loop', nodeId: id }
    seen.add(id)
    const node = nodes[id]
    if (!node) return { path, current: null, outcome: null, endReason: 'missing_node', nodeId: id }
    if (node.kind === 'outcome') return { path, current: null, outcome: { id, ...node }, endReason: 'outcome' }
    const choice = (answers || [])[i]
    if (choice === undefined || choice === null) {
      return { path, current: { id, ...node }, outcome: null, endReason: 'question' }
    }
    const option = node.options[choice]
    if (!option) return { path, current: { id, ...node }, outcome: null, endReason: 'question' }
    path.push({ id, question: node.text, answer: option.label })
    id = option.next
    i += 1
  }
  return { path, current: null, outcome: null, endReason: 'end' }
}

function walkEndMessage(walk) {
  if (walk.endReason === 'missing_node') {
    return `The tree's next step ("${walk.nodeId}") is missing from the tree content, so the walk stops here. ` +
      'This is a content problem, not a problem with your answers.'
  }
  if (walk.endReason === 'loop') return 'The tree returns to a step already answered, so the walk stops here.'
  if (walk.endReason === 'end') return 'This answer ends the tree without an outcome step.'
  return null
}

module.exports = { questionnaireTrees, walkQuestionnaire, walkEndMessage }
