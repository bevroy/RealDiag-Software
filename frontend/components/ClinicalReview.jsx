// Clinical review notice and per-tree review status, shown wherever
// decision-tree content, urgency levels, treatment information or severity
// ratings appear. The backend sends `clinical_review_notice` (null once all
// content is reviewed) and `review_status` / `review_status_label` per tree.

export const DEFAULT_CLINICAL_REVIEW_NOTICE =
  'Clinical content is under review. Urgency levels, treatment information, and severity thresholds are proposed and have not completed clinical review. Verify against current guidelines before acting.'

// notice: string -> show it; null -> content reviewed, show nothing;
// undefined -> the response predates the field (older API), so show the default.
export function ClinicalReviewNotice({ notice, style }) {
  const text = notice === undefined ? DEFAULT_CLINICAL_REVIEW_NOTICE : notice
  if (!text) return null
  return (
    <div
      role="note"
      aria-label="Clinical review notice"
      style={{
        display: 'flex',
        gap: '0.6rem',
        alignItems: 'flex-start',
        padding: '0.75rem 1rem',
        margin: '0 0 1rem',
        background: '#fffbeb',
        border: '1px solid #f59e0b',
        borderLeft: '5px solid #d97706',
        borderRadius: '8px',
        color: '#78350f',
        fontSize: '0.875rem',
        lineHeight: 1.5,
        ...style,
      }}
    >
      <span aria-hidden="true">⚠️</span>
      <span><strong>Under clinical review.</strong> {text}</span>
    </div>
  )
}

const BADGE_COLORS = {
  draft: { background: '#fef3c7', color: '#92400e', border: '#f59e0b' },
  review: { background: '#fef3c7', color: '#92400e', border: '#f59e0b' },
  approved: { background: '#dcfce7', color: '#166534', border: '#22c55e' },
  retired: { background: '#f3f4f6', color: '#4b5563', border: '#9ca3af' },
}

// Per-tree status, e.g. "Draft - under clinical review."
export function ReviewStatusBadge({ status, label, style }) {
  if (!label && !status) return null
  const colors = BADGE_COLORS[(status || '').toLowerCase()] || BADGE_COLORS.draft
  return (
    <span
      title="Clinical review status of this content"
      style={{
        display: 'inline-block',
        padding: '0.15rem 0.55rem',
        borderRadius: '999px',
        fontSize: '0.72rem',
        fontWeight: 600,
        background: colors.background,
        color: colors.color,
        border: `1px solid ${colors.border}`,
        whiteSpace: 'nowrap',
        ...style,
      }}
    >
      {label || `Status: ${status}`}
    </span>
  )
}
