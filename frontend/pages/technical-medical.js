import Link from 'next/link'
import RoleBasedNavigation from '../components/RoleBasedNavigation'

export default function TechnicalMedicalPage() {
  return (
    <div style={styles.page}>
      <RoleBasedNavigation />

      <div style={styles.bannerWrap}>
        <div style={styles.bannerInner}>
          <img src="/logo.png" alt="RealDiag Logo" style={styles.logo} />
          <div style={{ flex: 1 }}>
            <h1 style={styles.title}>Technical and Medical Overview</h1>
            <p style={styles.subtitle}>
              How RealDiag combines medical reasoning, safety checks, and data integration
            </p>
          </div>
        </div>
      </div>

      <main style={styles.main}>
        <section style={styles.section}>
          <h2 style={styles.h2}>1. Diagnostic Core</h2>
          <p style={styles.p}>
            RealDiag evaluates symptom and context inputs against structured decision trees and
            rule-based criteria. Each tree contains clinical paths, matched findings, and
            suggested workup actions. This creates transparent, auditable logic rather than
            black-box-only output.
          </p>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>2. Symptom Search and Ranking</h2>
          <p style={styles.p}>
            Symptom search uses normalized symptom terms, demographic filters, and presentation
            matching to rank likely diagnoses. Matching emphasizes direct phrase overlap and
            clinically relevant word intersections, with optional AI-assisted suggestions when
            confidence is low.
          </p>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>3. Clinical Pearls and Management Notes</h2>
          <p style={styles.p}>
            Many diagnoses include clinical pearls to help interpretation at the bedside:
            distinguishing features, cautionary flags, and practical next steps. Management and
            test recommendations are intended to support workflow planning and prioritization.
          </p>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>4. Medication Intelligence</h2>
          <p style={styles.p}>
            RealDiag includes medication safety analysis and medication-history context. Current
            and historical medication patterns can influence recommendations through:
          </p>
          <ul style={styles.list}>
            <li>Drug interaction and contraindication checks</li>
            <li>Class-based historical failure signals</li>
            <li>Recency-weighted interpretation of discontinued therapies</li>
            <li>Adverse-history blocks for high-risk repeat recommendations</li>
            <li>Explainability outputs for supported and conflicting medication signals</li>
          </ul>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>5. EHR and EMR Context Integration</h2>
          <p style={styles.p}>
            When configured for SMART on FHIR or direct FHIR access, RealDiag can ingest clinical
            context including current vitals, active conditions, medication lists, allergies, and
            selected historical records. This enables diagnosis support that reflects encounter and
            longitudinal context rather than symptom-only snapshots.
          </p>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>6. Explainability and Traceability</h2>
          <p style={styles.p}>
            Outputs are designed for inspection. Decision paths, matched criteria, safety alerts,
            and history-derived signals can be surfaced so clinicians can understand why a
            suggestion appeared and where risk adjustments were applied.
          </p>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>7. Safety Boundaries</h2>
          <p style={styles.p}>
            RealDiag is a decision-support system, not an autonomous diagnostic authority. It must
            be used with clinician oversight, institutional protocols, and full patient context.
            Urgent or emergent care decisions should always follow local emergency standards.
          </p>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>8. Related In-App Guides</h2>
          <ul style={styles.list}>
            <li>
              <Link href="/user-guide">
                <a style={styles.inlineLink}>User Guide</a>
              </Link>
              : operational steps and printable workflow reference.
            </li>
            <li>
              <Link href="/legal-disclaimer">
                <a style={styles.inlineLink}>Legal Disclaimer</a>
              </Link>
              : intended use, liability limits, and safety constraints.
            </li>
          </ul>
        </section>
      </main>
    </div>
  )
}

const styles = {
  page: {
    minHeight: '100vh',
    background: 'linear-gradient(160deg, #f6fbf8 0%, #eef7fb 55%, #f8fafc 100%)',
    color: '#0f172a',
    fontFamily: "'Poppins', system-ui, -apple-system, sans-serif",
  },
  bannerWrap: {
    padding: '0.5rem 1rem 0.25rem',
  },
  bannerInner: {
    maxWidth: '980px',
    margin: '0 auto 0.5rem',
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    padding: '1rem 1.1rem',
    border: '1px solid #d7e3ee',
    borderRadius: '18px',
    background: '#ffffff',
    boxShadow: '0 12px 28px rgba(15, 23, 42, 0.07)',
  },
  logo: {
    maxHeight: '56px',
    width: 'auto',
    objectFit: 'contain',
    flexShrink: 0,
  },
  backLink: {
    display: 'inline-block',
    color: '#0f766e',
    textDecoration: 'none',
    fontWeight: 600,
    whiteSpace: 'nowrap',
  },
  title: {
    margin: '0 0 0.4rem',
    fontSize: '2rem',
    lineHeight: 1.2,
    color: '#0f172a',
  },
  subtitle: {
    margin: 0,
    color: '#334155',
    fontSize: '1rem',
  },
  main: {
    maxWidth: '980px',
    margin: '1.25rem auto 2rem',
    background: '#ffffff',
    border: '1px solid #dbe5ef',
    borderRadius: '18px',
    boxShadow: '0 12px 28px rgba(15, 23, 42, 0.07)',
    padding: '1.5rem 1.5rem 1.25rem',
  },
  section: {
    marginBottom: '1rem',
    paddingBottom: '0.75rem',
    borderBottom: '1px solid #edf2f7',
  },
  h2: {
    margin: '0 0 0.45rem',
    fontSize: '1.15rem',
    color: '#0f172a',
  },
  p: {
    margin: 0,
    lineHeight: 1.7,
    color: '#334155',
  },
  list: {
    margin: '0.45rem 0 0',
    paddingLeft: '1.2rem',
    lineHeight: 1.7,
    color: '#334155',
  },
  inlineLink: {
    color: '#0f766e',
    textDecoration: 'underline',
    fontWeight: 600,
  },
}
