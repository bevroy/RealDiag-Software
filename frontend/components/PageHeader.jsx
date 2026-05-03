/**
 * PageHeader
 * ----------
 * Shared header card used on every inner page (Symptom Search, Diagnosis Search,
 * Browse Rules, Sources, Patient History, Account, Features, Training,
 * EHR Integration, Health Manager, etc.).
 *
 * Renders a white card with the RealDiag logo on the left and a title /
 * optional subtitle on the right. Use this on every page so the header box
 * has the same height, padding, and logo size throughout the app.
 */
export default function PageHeader({ title, subtitle, color = '#78350f' }) {
  return (
    <div
      style={{
        background: 'white',
        borderRadius: '12px',
        padding: '1.5rem',
        marginBottom: '1rem',
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
        minHeight: '90px',
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
      }}
    >
      <img
        src="/logo.png"
        alt="RealDiag Logo"
        style={{ height: '50px', width: 'auto', flexShrink: 0 }}
      />
      <div style={{ minWidth: 0 }}>
        <h1
          style={{
            margin: 0,
            color,
            fontSize: '1.75rem',
            fontWeight: 700,
            lineHeight: 1.2,
          }}
        >
          {title}
        </h1>
        {subtitle && (
          <p
            style={{
              margin: '0.25rem 0 0',
              color: '#6b7280',
              fontSize: '0.95rem',
            }}
          >
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
}
