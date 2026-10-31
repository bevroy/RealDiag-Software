// Badge color for a tree's urgency on /search.
//
// Trees use emergent / urgent / routine (backend/trees/*.yml `urgency`).
// "critical" is kept as red for any other source that still sends it.
//
// CommonJS so jest can load it without a Babel config (see __tests__).

const URGENCY_COLORS = {
  emergent: '#dc2626', // red
  critical: '#dc2626', // red
  urgent: '#f59e0b', // amber
  routine: '#10b981', // green
}

function urgencyBadgeColor(urgency) {
  const key = String(urgency || '').trim().toLowerCase()
  return URGENCY_COLORS[key] || URGENCY_COLORS.routine
}

module.exports = { URGENCY_COLORS, urgencyBadgeColor }
