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
          <p style={styles.p}>
            Questionnaire trees (October 2026): GET /diagnostic/trees/{id}/questionnaire returns a questionnaire tree&apos;s questions (options with next steps) and outcome steps, and /diagnose walks it one question at a time (frontend/utils/questionnaireWalker.js). Step-level icd10 and urgency are display only, not mapped to the tree urgency scale or used for ranking.
          </p>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>2. Symptom Search and Ranking</h2>
          <p style={styles.p}>
            Symptom search uses normalized symptom terms, demographic filters, and presentation
            matching to rank likely diagnoses. Matching emphasizes direct phrase overlap and
            clinically relevant word intersections, with optional AI-assisted suggestions when
            confidence is low. Each tree&apos;s chief complaint is matched along with its presentations,
            and a short list of lay and clinical synonyms (for example shortness of breath and
            dyspnea) is searched together. Negated parts of the input (&quot;no chest pain&quot;) are dropped
            before ranking in symptom search, the ambulatory differential and the encounter assessment. Emergent trees that match are always returned and labelled
            &quot;Can&apos;t-miss condition&quot;, whatever their score or the result cap.
          </p>
          <p style={styles.p}>
            AI features are off unless ENABLE_AI_GENERATION or ENABLE_AI_ENRICHMENT is set to
            &quot;true&quot;, and anything AI-generated is labelled &quot;AI-generated; not clinically
            validated.&quot; Chart-driven requests (encounter assessment, ambulatory differential,
            symptom search with an EHR patient) never use AI: EHR data is never sent to an AI provider.
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
          <p style={styles.p}>
            The encounter assessment pulls the chart once (no data type is requested twice) and
            reports every data type that could not be retrieved or was cut off at the page limit.
            Today&apos;s complaint comes from the clinician&apos;s text, otherwise the EHR visit reason.
            Acute chart cards (ACS, sepsis, DKA) appear when a criterion is met or the complaint
            matches the tree&apos;s reviewed complaint terms.
          </p>
          <p style={styles.p}>
            Possible missed items are rule-based (no AI): chronic-condition criteria met without a
            matching problem-list entry; problem-list conditions with no supporting result or related
            medication in the lookback; and USPSTF grade A/B screening rules evaluated against age, sex,
            BMI, smoking status, procedures, imaging and results over 10 years. Data RealDiag cannot see
            (such as pack-years) is reported as unavailable, never assumed.
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
            Content still under clinical review (trees, urgency, treatment, thresholds and screening
            rules) carries a review notice and per-tree status in every page, API response, export
            (FHIR, HL7, JSON, XML, CSV) and PDF report.
            RealDiag is a decision-support system, not an autonomous diagnostic authority. It must
            be used with clinician oversight, institutional protocols, and full patient context.
            Urgent or emergent care decisions should always follow local emergency standards.
          </p>
          <p style={styles.p}>
            Offline (October 2026): GET /offline/bundle (login required) serves a versioned bundle (content hash) of
            every tree&apos;s ranking fields, the ranking settings (synonyms, negation cues) and the walkable
            questionnaire trees; about 0.5 MB, no patient data. The browser keeps it in Cache Storage and refetches it
            only when GET /offline/bundle/version changes. frontend/utils/offlineSearch.js ports the tree-library
            ranking of /search/by-symptoms; a shared fixture checks the server and the port give the same results.
            Offline search has no AI suggestions, vital-sign terms or chart history; branching-tree evaluation, chart
            and EHR features stay online-only.
          </p>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>8. Recent Platform Updates</h2>
          <ul style={styles.list}>
            <li>Security maintenance (eMudhra certificate compromise and Node.js security release, October 2026): Node.js is pinned to 22.23.4 for Netlify builds, CI and the frontend images (Node 20 and earlier receive no fix); certifi is pinned to 2026.10.19 or later; and the Python and Node images upgrade the system ca-certificates package when they are built. Running services pick this up only after a rebuild and redeploy.</li>
            <li>Security maintenance (Next.js advisories, October 2026): the frontend moves from Next.js 16.3.4 to 16.4.3, which fixes three critical and one high-severity published advisory. Production on Netlify is a static export with no Next.js server, so exposure there was low; the frontend Docker image runs a Next.js server and is the main beneficiary.</li>
            <li>Correctness fixes (October 2026), each with tests; no threshold, urgency or tree status changed except where marked pending clinical review:
              (1) Vital signs: one shared mapper (backend/services/vitals_terms.py) for symptom search and tree evaluation; temperature is converted from its recorded unit (°F if none) before the °F thresholds; where the two old copies differed the stricter rule is kept (diastolic &gt;= 90 is hypertension; heart rate &gt;= 130 and SpO2 &lt; 90 add red flags).
              (2) The /search urgency badge shows emergent in red.
              (3) Possible missed items: a tree&apos;s criteria.suppressed_by names other trees whose problem-list codes suppress its finding; prediabetes is suppressed by diabetes (pending clinical review).
              (4) Prediabetes ranges are [5.7, 6.5) % and [100, 126) mg/dL (new operator at_least_below), meeting the diabetes thresholds with no gap (pending clinical review).
              (5) EHR medication history reads R4 stop dates (dosage boundsPeriod.end, else dispense validityPeriod.end) and statusReason, instead of the R5-only statusChanged.
              (6) FHIR requests time out after 30 seconds and are reported as failed.
              (7) The handoff &quot;since&quot; search keeps the full timestamp when it has a timezone.
              (8) The encounter summary counts abnormal results from the last 30 days only and says so.
              (9) A lab and its reference range in different units are converted before the result is flagged abnormal.</li>
            <li>Rate limits use the real client address (backend/services/client_ip.py): behind Render&apos;s proxy, CF-Connecting-IP / True-Client-IP or the right-most untrusted X-Forwarded-For entry, trusted only when the connection comes from a private proxy address. Signed-in requests are limited per account, not per IP, so a class on one campus network does not share one limit. Sign-in (150 per 15 minutes per IP) and registration (60 per hour per IP) are sized for a class; repeated wrong passwords lock that account for 15 minutes after 5 attempts, stored on the user record so it holds across workers. Admins can check what the server sees at GET /admin/client-ip.</li>
            <li>Email failures are reported, not silent: forgot-password returns 503 when email is not configured and 502 when sending fails; registration, verification and resend responses say when an email could not be sent. SMTP connections time out after 15 seconds, and reset/verification links are no longer written to the server log.</li>
            <li>Admin account tools: POST /admin/users/reset-password, /admin/users/deactivate and /admin/users/reactivate (admin token plus a signed-in session). Deactivated accounts are refused at sign-in and on every authenticated request.</li>
            <li>Misleading-behavior fixes (October 2026), each with tests:
              (1) GET /rules/all returns the whole rule library with a content version, and &quot;Download All Rules&quot; reports real success or failure.
              (2) Offline IndexedDB reads and writes are wrapped in promises (frontend/utils/idb.js), so offline storage returns its data.
              (3) Pages and the service worker share one database name, version and schema (public/offline-db-schema.js).
              (4) Background sync is removed: its endpoints never existed and the data it would sync is never stored.
              (5) Offline POSTs get HTTP 503 with X-RealDiag-Offline: 1 instead of a fake success, and Symptom Search shows an offline message.
              (6) offline.html lists only what works offline.
              (7) Guideline names stored as origin evidence_level are shown as sources, not as evidence levels.
              (8) /search shows the remedies stored in trees (homeopathy.remedies) with &quot;This content has not been clinically validated.&quot;
              (9) Approving an AI-generated tree is described accurately: it is not added to the clinical library.
              (10) POST /analyze is removed (unused; its outputs never matched the schema).
              (11) /inpatient and the nav link to Encounter Assessment during a SMART session.</li>
            <li>The tree validator rejects any branch or questionnaire option that points to a node the tree does not contain. Two trees are explicit known exceptions pending clinical review (ID-FEVER, PSYCH-PSYCHOSIS; see docs/CLINICAL_CONTENT_REVIEW.md section 13): /diagnostic/trees marks them walk_available false and /diagnose does not offer them.</li>
            <li>Every page calls the API through one client (frontend/utils/apiClient.js) that always sends the sign-in cookie; previously /diagnose, the tree counts, Patient History save and medication check, Diagnosis Search and Training sent no credentials and got 401. Login, registration, email verification and password reset now use the configured API address and stay on the same site afterwards.</li>
            <li>Decision tree engine: every predicate key used by the conditional trees is evaluated (exam_findings_any, exam_findings, symptoms_contains_all, symptoms, patient_characteristics_any, no_red_flags, age comparators, and named findings such as rapid_strep: positive, matched exactly). Unrecognised keys used to be ignored, so those branches matched every patient; unrecognised predicate shapes now fail closed. Walk results report end_reason (end_node, no_matching_branch, missing_node, loop) and trace each branch taken. Tree content is unchanged.</li>
            <li>GET /diagnostic/trees/&#123;id&#125;/inputs returns the answer choices a conditional tree&apos;s own branches test for; /diagnostic/trees lists each tree&apos;s node_format. /diagnose offers only the 17 conditional trees, and tests confirm every end node of each is reachable from those choices.</li>
            <li>All pages use the configured API address (api.realdiag.com in production); the retired realdiag-software.onrender.com address has been removed from the app, scripts and docs.</li>
            <li>The /diagnostic page and its CI check now use the production API (api.realdiag.com) via the site&apos;s runtime configuration; CI checks app.realdiag.com after each push to main and retries while Netlify publishes.</li>
            <li>All decision trees now share one standard template: codes (ICD-10, SNOMED CT, ICPC-2) are grouped together, guideline sources are consolidated, and every tree carries a version, review status, and change log.</li>
            <li>Tree urgency uses three standard levels (emergent, urgent, routine); every tree has a level, and levels proposed during standardization are marked in each tree's change log pending clinician confirmation.</li>
            <li>Authentication now revalidates cookie-based sessions against the backend before restricting access.</li>
            <li>Navigation normalizes legacy roles so approved clinical accounts are shown provider-level tools consistently.</li>
            <li>Admin role-management endpoints support updates by email or user ID for onboarding and access corrections.</li>
            <li>Client cache invalidation was added so stale bundles do not preserve older limited-navigation behavior after deploys.</li>
            <li>Integration and security hardening (October 2026), each with tests:
              (1) SMART on FHIR access and refresh tokens are encrypted at rest (Fernet; key SMART_TOKEN_ENCRYPTION_KEY or derived from JWT_SECRET_KEY).
              (2) Only EHR vendors with a configuration are offered (MEDITECH removed); others get a clear 503.
              (3) Cerner requests a read scope for every resource the chart pull queries (adds ImagingStudy and FamilyMemberHistory); GET /smart/config reports the active vendor&apos;s scopes.
              (4) The patient history service follows FHIR next links up to HISTORY_MAX_PAGES (default 5) and reports searches cut off at the cap.
              (5) The patient-facing symptom search refuses emr_patient_id (400).
              (6) Tree walks keep tests, diagnoses and referrals in path order with the step that produced each.
              (7) Steps whose own condition is not met are marked in the trace (walk unchanged).
              (8) Medication outcome feedback is stored in the database (medication_outcomes).</li>
          </ul>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>9. Related In-App Guides</h2>
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
