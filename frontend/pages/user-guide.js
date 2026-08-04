import RoleBasedNavigation from '../components/RoleBasedNavigation'

export default function UserGuidePage() {
  const printedOn = new Date().toLocaleDateString()

  return (
    <div style={styles.pageWrap}>
      <style>{`
        @media print {
          .screen-only { display: none !important; }
          .print-shell {
            box-shadow: none !important;
            border: none !important;
            margin: 0 !important;
            padding: 0 !important;
            max-width: 100% !important;
          }
          .print-page-break {
            page-break-before: always;
            break-before: page;
          }
          @page {
            size: Letter;
            margin: 0.6in;
          }
        }
      `}</style>

      <RoleBasedNavigation />

      <div style={styles.banner} className="screen-only">
        <div style={styles.bannerInner}>
          <img src="/logo.png" alt="RealDiag Logo" style={styles.logo} />
          <div>
            <h1 style={styles.bannerTitle}>User Guide</h1>
            <p style={styles.bannerSubtitle}>Printable quick-start and workflow reference</p>
          </div>
          <button
            onClick={() => window.print()}
            style={styles.printButton}
            aria-label="Print user guide"
          >
            Print Guide
          </button>
        </div>
      </div>

      <main style={styles.container} className="print-shell">
        <header style={styles.header}>
          <h1 style={styles.title}>RealDiag User Guide</h1>
          <p style={styles.subtitle}>Printable quick-start and workflow reference</p>
          <p style={styles.meta}>Version: 1.1 | Printed: {printedOn}</p>
        </header>

        <section style={styles.section}>
          <h2 style={styles.h2}>1. Purpose</h2>
          <p style={styles.p}>
            RealDiag helps clinicians and learners generate evidence-based differential diagnoses,
            review supporting findings, and plan next diagnostic steps.
          </p>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>2. Before You Start</h2>
          <ul style={styles.list}>
            <li>Confirm you are logged in with the appropriate account role.</li>
            <li>If connected to EHR/EMR, verify patient context and encounter selection.</li>
            <li>Collect presenting symptoms, onset timeline, and key red flags.</li>
            <li>Enter vitals when available for improved relevance and safety checks.</li>
          </ul>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>3. Core Workflow: Symptom Search</h2>
          <ol style={styles.list}>
            <li>Open Symptom Search from the home page.</li>
            <li>Enter primary symptoms and optional demographics.</li>
            <li>Add vital signs: HR, BP, temperature, respiratory rate, and oxygen saturation.</li>
            <li>Run search and review ranked results.</li>
            <li>Open each result to review clinical pearls, tests, referrals, and management notes.</li>
          </ol>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>4. Diagnostic Evaluation with History</h2>
          <ul style={styles.list}>
            <li>Use a specific diagnostic tree when a focused evaluation is needed.</li>
            <li>Include encounter symptoms, exam/red-flag findings, and vitals.</li>
            <li>If EHR-connected, include patient ID to pull historical context.</li>
            <li>Review medication-history evidence signals and blocked recommendations.</li>
            <li>Use output as decision support, not as a standalone clinical determination.</li>
          </ul>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>5. How to Read Results</h2>
          <ul style={styles.list}>
            <li><strong>Top matches:</strong> Most relevant differential candidates.</li>
            <li><strong>Matched presentations:</strong> Findings that aligned with your input.</li>
            <li><strong>Tests and referrals:</strong> Suggested workup and specialty escalation.</li>
            <li><strong>Medication safety:</strong> Interaction/contraindication risk summary.</li>
            <li><strong>History signals:</strong> Supportive/conflicting medication-history factors.</li>
          </ul>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>6. Printing Tips</h2>
          <ul style={styles.list}>
            <li>Use the Print Guide button for optimized print layout.</li>
            <li>Recommended paper size: Letter or A4.</li>
            <li>Enable background graphics if your institution requires branded copies.</li>
          </ul>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>7. Troubleshooting</h2>
          <ul style={styles.list}>
            <li>No results: broaden symptom wording and include onset/context clues.</li>
            <li>Unexpected ranking: verify vitals and age/sex filters are correct.</li>
            <li>Missing EHR data: confirm integration token and patient identifier mapping.</li>
            <li>Medication warning mismatch: check generic-vs-brand medication names.</li>
          </ul>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>8. Access and Role Notes</h2>
          <ul style={styles.list}>
            <li>Approved clinical domains can be promoted to provider-level access without relying on stale cached roles.</li>
            <li>The navigation now rechecks backend session state so logged-in users should see the full provider feature set after refresh.</li>
            <li>Admin users can update account roles by email or user ID from the admin review page when onboarding or correcting access.</li>
            <li>If the menu still looks limited, hard refresh once so the newest client bundle and auth cache are loaded.</li>
          </ul>
        </section>

        <section style={styles.section} className="print-page-break">
          <h2 style={styles.h2}>9. Clinical Safety Reminder</h2>
          <p style={styles.p}>
            RealDiag is a clinical decision support aid. It does not replace clinical judgment,
            institution protocols, or emergency pathways. Always validate recommendations against
            the full clinical picture and local standards of care.
          </p>
        </section>

        <footer style={styles.footer}>
          <p style={styles.footerText}>RealDiag User Guide</p>
          <p style={styles.footerText}>For operational use, training, and print reference.</p>
        </footer>
      </main>
    </div>
  )
}

const styles = {
  pageWrap: {
    minHeight: '100vh',
    background: 'linear-gradient(160deg, #f4f7fb 0%, #eef6f2 60%, #f8fafc 100%)',
    color: '#0f172a',
    fontFamily: "'Poppins', system-ui, -apple-system, sans-serif",
  },
  banner: {
    padding: '0.5rem 1rem 0.25rem',
  },
  bannerInner: {
    maxWidth: '960px',
    margin: '0 auto 0.5rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '1rem',
    padding: '1rem 1.1rem',
    background: '#ffffff',
    border: '1px solid #dbe4ea',
    borderRadius: '18px',
    boxShadow: '0 10px 28px rgba(15, 23, 42, 0.08)',
  },
  logo: {
    maxHeight: '56px',
    width: 'auto',
    objectFit: 'contain',
    flexShrink: 0,
  },
  bannerTitle: {
    margin: '0 0 0.25rem',
    fontSize: '1.5rem',
    lineHeight: 1.2,
    color: '#0f172a',
  },
  bannerSubtitle: {
    margin: 0,
    color: '#0f766e',
    fontWeight: 600,
    fontSize: '0.95rem',
  },
  printButton: {
    border: 'none',
    borderRadius: '999px',
    padding: '0.65rem 1rem',
    background: 'linear-gradient(135deg, #0f172a 0%, #0f766e 100%)',
    color: '#fff',
    fontWeight: 600,
    cursor: 'pointer',
  },
  container: {
    maxWidth: '960px',
    margin: '1.25rem auto 2rem',
    background: '#fff',
    border: '1px solid #dbe4ea',
    borderRadius: '20px',
    boxShadow: '0 14px 32px rgba(15, 23, 42, 0.08)',
    padding: '2rem',
  },
  header: {
    borderBottom: '2px solid #e2e8f0',
    paddingBottom: '1rem',
    marginBottom: '1rem',
  },
  title: {
    margin: '0 0 0.35rem',
    fontSize: '2rem',
    lineHeight: 1.2,
    color: '#0f172a',
  },
  subtitle: {
    margin: '0 0 0.35rem',
    color: '#0f766e',
    fontWeight: 600,
  },
  meta: {
    margin: 0,
    color: '#64748b',
    fontSize: '0.9rem',
  },
  section: {
    margin: '1rem 0',
  },
  h2: {
    fontSize: '1.15rem',
    margin: '0 0 0.5rem',
    color: '#0f172a',
  },
  p: {
    margin: 0,
    lineHeight: 1.7,
    color: '#334155',
  },
  list: {
    margin: '0.25rem 0 0',
    paddingLeft: '1.25rem',
    lineHeight: 1.7,
    color: '#334155',
  },
  footer: {
    marginTop: '1.5rem',
    borderTop: '1px solid #e2e8f0',
    paddingTop: '0.75rem',
  },
  footerText: {
    margin: 0,
    color: '#64748b',
    fontSize: '0.85rem',
  },
}
