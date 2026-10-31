// Display helpers for the patient-aware treatment review that the encounter
// assessment attaches to each tree's treatment (guidance.treatment.review).
// Lines keep the tree's order; nothing here ranks or picks an option.
//
// CommonJS so jest can load it without a Babel config (see __tests__).

const MARKS = {
  appropriate: { label: 'Appropriate (no conflict found)', color: '#065f46', background: '#ecfdf5', border: '#10b981' },
  caution: { label: 'Use with caution', color: '#92400e', background: '#fffbeb', border: '#f59e0b' },
  avoid: { label: 'Avoid', color: '#991b1b', background: '#fef2f2', border: '#ef4444' },
  not_checked: { label: 'Not checked', color: '#374151', background: '#f3f4f6', border: '#d1d5db' },
}

const REVIEW_UNAVAILABLE = 'Treatment lines were not checked against the chart (no review in the response).'

// Pair each treatment section's items with their review, by position.
function reviewedSections(treatment) {
  const sections = (treatment && treatment.sections) || []
  const review = treatment && treatment.review
  return sections.map((section, i) => ({
    title: section.title,
    items: section.items.map((text, j) => {
      const line = review && review.sections && review.sections[i] && review.sections[i][j]
      return line && line.text === text ? line : { text, mark: null, reasons: [], medications: [] }
    }),
  }))
}

function markStyle(mark) {
  return MARKS[mark] || null
}

// "Renal: stage 4 (Lab: eGFR 25 ... on 2026-10-01)" etc., for the factors found.
function factorLines(review) {
  const f = (review && review.patient_factors) || {}
  const out = []
  if (f.renal) out.push(`Renal function: ${f.renal.value} (${f.renal.source})`)
  if (f.hepatic) out.push(`Hepatic function: ${f.hepatic.value} (${f.hepatic.source})`)
  if (f.pregnancy) out.push(`Pregnancy (${f.pregnancy.source})`)
  return out
}

module.exports = { MARKS, REVIEW_UNAVAILABLE, reviewedSections, markStyle, factorLines }
