'use client';

import { Suspense, useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { getApiBase } from '../../utils/auth';
import { parseEncounterAssessment, evidenceLabel } from '../../utils/encounterAssessment';
import { REVIEW_UNAVAILABLE, reviewedSections, markStyle, factorLines } from '../../utils/treatmentReview';
import { buildNarrative, sourceText } from '../../utils/chartNarrative';
import { ClinicalReviewNotice, ReviewStatusBadge } from '../../components/ClinicalReview';

/**
 * Encounter assessment (SMART on FHIR).
 *
 * One chart pull, shown as: chart summary, today's complaint, diagnoses with
 * their evidence, guidance from each matched tree, red flags, and what could
 * not be assessed. Decision support only; nothing here is an order.
 * Authenticated by the HttpOnly SMART session cookie (credentials: 'include').
 */
export default function EncounterPage() {
  return (
    <Suspense fallback={<p style={styles.loading}>Loading...</p>}>
      <EncounterAssessment />
    </Suspense>
  );
}

function EncounterAssessment() {
  const searchParams = useSearchParams();
  const patientId = searchParams.get('patient_id');
  const [complaintInput, setComplaintInput] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const assess = useCallback(async (complaint) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${getApiBase()}/smart/encounter-assessment`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient_id: patientId, chief_complaint: complaint || null }),
      });
      if (!response.ok) {
        if (response.status === 401) throw new Error('Your session with the EHR has expired. Please relaunch from the EHR.');
        throw new Error('Encounter assessment failed. Please try again or relaunch from the EHR.');
      }
      setResult(parseEncounterAssessment(await response.json()));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [patientId]);

  useEffect(() => {
    if (!patientId) {
      setError('Missing patient context. This page must be launched from the EHR.');
      return;
    }
    assess(null); // first pass uses the EHR visit reason, if any
  }, [patientId, assess]);

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Encounter Assessment</h1>
      <form
        style={styles.complaintForm}
        onSubmit={(e) => { e.preventDefault(); assess(complaintInput.trim()); }}
      >
        <label htmlFor="complaint" style={styles.label}>Today&apos;s complaint</label>
        <input
          id="complaint"
          style={styles.input}
          value={complaintInput}
          onChange={(e) => setComplaintInput(e.target.value)}
          placeholder="e.g. chest pain since this morning, no fever"
        />
        <button type="submit" style={styles.button} disabled={loading || !patientId}>
          {loading ? 'Assessing...' : 'Assess'}
        </button>
      </form>

      {error && <div style={styles.error} role="alert">{error}</div>}
      {loading && !result && <p style={styles.loading}>Loading the chart from the EHR...</p>}
      {result && <AssessmentView result={result} />}
    </div>
  );
}

function AssessmentView({ result }) {
  const { summary, complaint, diagnoses, complaintMatchesNote, guidanceById, redFlags, notAssessed } = result;
  return (
    <>
      <ClinicalReviewNotice notice={result.clinicalReviewNotice} />
      {result.decisionSupportNotice && <p style={styles.notice}>{result.decisionSupportNotice}</p>}

      <Section title="Chart summary">
        {summary ? (
          <>
            <p>{summary.summary_text}</p>
            <DataStatus summary={summary} />
            <WarningList items={[...(summary.data_warnings || []), ...(summary.cut_off_notes || [])]} />
          </>
        ) : <p>Chart summary not available.</p>}
      </Section>

      <ChartNarrative summary={summary} extracted={result.extractedSummary} />

      <Section title="Today's complaint">
        <p>
          {complaint.text ? <strong>{complaint.text}</strong> : <em>None</em>}
          {' '}<span style={styles.muted}>({complaint.source_label})</span>
        </p>
        {complaint.negated_terms && complaint.negated_terms.length > 0 && (
          <p style={styles.muted}>Not searched (negated): {complaint.negated_terms.join(', ')}</p>
        )}
        {complaint.chart_terms && complaint.chart_terms.length > 0 && (
          <div>
            <p><strong>Also searched, from the chart:</strong></p>
            <ul>
              {complaint.chart_terms.map((t, i) => (
                <li key={i}>{t.term} <span style={styles.muted}>({t.source}{t.date ? `, ${t.date}` : ''})</span></li>
              ))}
            </ul>
          </div>
        )}
      </Section>

      <Section title="Diagnoses to consider">
        {complaintMatchesNote && <p style={styles.muted}>{complaintMatchesNote}</p>}
        {diagnoses.length === 0 ? (
          <p>No diagnoses matched the complaint or the chart criteria. See &quot;Could not be assessed&quot; below.</p>
        ) : diagnoses.map((d) => (
          <DiagnosisCard key={d.tree_id} diagnosis={d} guidance={guidanceById[d.tree_id]} />
        ))}
      </Section>

      <Section title="Red flags">
        {redFlags.length === 0 ? <p>No conditions to show red flags for.</p> : redFlags.map((r) => (
          <div key={r.tree_id} style={styles.redFlagBlock}>
            <strong>{r.name}</strong>
            {r.red_flags.length ? (
              <ul>{r.red_flags.map((f, i) => <li key={i}>{f}</li>)}</ul>
            ) : <p style={styles.muted}>{r.note}</p>}
          </div>
        ))}
      </Section>

      <MissedItems missed={result.missedItems} />

      <MedicationReview review={result.medicationReview} />

      <Section title="Could not be assessed">
        {notAssessed.length === 0 ? <p>Everything needed was retrieved.</p> : (
          <ul>{notAssessed.map((item, i) => <li key={i}>{item.text}</li>)}</ul>
        )}
      </Section>
    </>
  );
}

// Compact: grouped by check, one line per item with source and review
// status; evidence, window checked and caveats expand on demand.
function ChartNarrative({ summary, extracted }) {
  const narrative = buildNarrative({ summary, extracted_summary: extracted });
  return (
    <Section title="Chart narrative">
      <p style={styles.muted}>{narrative.label}{extracted.label ? ` ${extracted.label}` : ''}</p>
      {(extracted.not_read || []).map((text, i) => <p key={i} style={styles.notChecked}>Not read: {text}</p>)}
      {narrative.sentences.length === 0 ? <p style={styles.muted}>Nothing to summarize.</p> : (
        <ul>
          {narrative.sentences.map((s, i) => (
            <li key={i}>
              {s.text}{' '}
              <span style={styles.muted}>[{s.sources.map(sourceText).join('; ')}]</span>
            </li>
          ))}
        </ul>
      )}
    </Section>
  );
}

function MissedItems({ missed }) {
  return (
    <Section title={missed.title || 'Possible missed items'}>
      {missed.notice && <p style={styles.muted}>{missed.notice}</p>}
      {missed.checks.map((check) => (
        <div key={check.type} style={styles.missedGroup}>
          <h3 style={styles.missedTitle}>{check.title} ({check.items.length})</h3>
          {check.not_checked.map((text, i) => <p key={i} style={styles.notChecked}>Not checked: {text}</p>)}
          {check.items.length === 0 && check.not_checked.length === 0 && <p style={styles.muted}>None found.</p>}
          {check.items.map((item, i) => <MissedItem key={i} item={item} />)}
          {check.single_results && check.single_results.items.length > 0 && (
            <details style={styles.missedItem}>
              <summary style={styles.missedSummary}>
                {check.single_results.title} ({check.single_results.items.length})
              </summary>
              <div style={{ paddingLeft: 16 }}>
                {check.single_results.items.map((item, i) => <MissedItem key={i} item={item} />)}
              </div>
            </details>
          )}
        </div>
      ))}
    </Section>
  );
}

function MedicationReview({ review }) {
  const history = review.history;
  return (
    <Section title={review.title || 'Medication review'}>
      {review.notice && <p style={styles.muted}>{review.notice}</p>}
      {review.not_checked.map((text, i) => <p key={i} style={styles.notChecked}>Not checked: {text}</p>)}
      {review.medications.length > 0 && (
        <p><strong>Active medications ({review.medications.length}):</strong> {review.medications.join(', ')}</p>
      )}
      {review.alerts.length === 0 && review.medications.length > 0 && (
        <p style={styles.muted}>No alerts from the rules RealDiag has for these medications.</p>
      )}
      {review.alerts.map((alert, i) => (
        <details key={i} style={styles.missedItem}>
          <summary style={styles.missedSummary}>
            <strong>{(alert.severity || '').toUpperCase()}</strong> {alert.description}
          </summary>
          <div style={styles.missedDetails}>
            {alert.clinical_effect && <p><strong>Effect:</strong> {alert.clinical_effect}</p>}
            {alert.recommendation && <p><strong>Reference note:</strong> {alert.recommendation}</p>}
            {alert.monitoring && <p><strong>Monitoring:</strong> {alert.monitoring}</p>}
            <p><strong>From:</strong> {alert.data_sources.join(', ')}</p>
          </div>
        </details>
      ))}
      {history && (
        <div>
          <p><strong>Medication history:</strong> {history.stopped_medications_on_file} stopped medication(s) on file; {history.recent_discontinuations_30d} stopped in the last 30 days.</p>
          {history.prior_adverse_reactions.map((r, i) => (
            <p key={i}>Prior adverse reaction: {r.medication}{r.stopped ? ` (stopped ${r.stopped})` : ''}: {r.reason} <span style={styles.muted}>({r.source})</span></p>
          ))}
        </div>
      )}
    </Section>
  );
}

function MissedItem({ item }) {
  return (
    <details style={styles.missedItem}>
      <summary style={styles.missedSummary}>
        {item.summary}{' '}
        <ReviewStatusBadge status={item.review_status} label={item.review_status_label} />
      </summary>
      <div style={styles.missedDetails}>
        {item.source && <p><strong>Source:</strong> {item.url ? <a href={item.url} target="_blank" rel="noreferrer">{item.source}</a> : item.source}</p>}
        <p><strong>Window checked:</strong> {item.details.window}</p>
        <ul>{item.details.evidence.map((e, j) => <li key={j}>{e}</li>)}</ul>
        {item.details.caveats.length > 0 && (
          <>
            <strong>Caveats</strong>
            <ul>{item.details.caveats.map((c, j) => <li key={j}>{c}</li>)}</ul>
          </>
        )}
      </div>
    </details>
  );
}

function DiagnosisCard({ diagnosis, guidance }) {
  const [open, setOpen] = useState(false);
  const c = diagnosis.criteria;
  const match = diagnosis.complaint_match;
  return (
    <div style={styles.card}>
      <button type="button" style={styles.cardHeader} onClick={() => setOpen(!open)} aria-expanded={open}>
        <span>
          <strong>{diagnosis.name}</strong>{' '}
          <ReviewStatusBadge status={diagnosis.review_status} label={diagnosis.review_status_label} />
          {diagnosis.cant_miss && <span style={styles.cantMiss}>{diagnosis.cant_miss_label || "Can't-miss condition"}</span>}
        </span>
        <span style={styles.evidence}>{evidenceLabel(diagnosis.evidence)}</span>
      </button>
      {c && c.evaluation_status !== 'evaluated' && (
        <p style={styles.statusText}>{c.evaluation_status.toUpperCase()}{c.status_reason ? ` — ${c.status_reason}` : ''}</p>
      )}
      {c && c.recommendations.map((r, i) => <p key={i} style={styles.recommendation}>{r}</p>)}
      {open && (
        <div style={styles.cardBody}>
          {match && (
            <Detail title="Complaint match">
              {[...(match.matched_terms || []), ...(match.matched_presentations || [])].join('; ')}
            </Detail>
          )}
          {c && c.criteria_met.length > 0 && (
            <Detail title="Criteria met">
              <ul>{c.criteria_met.map((m, i) => (
                <li key={i}>{m.criterion}: {m.value}{m.expected ? ` (expected ${m.expected})` : ''}
                  {m.source && <span style={styles.muted}> — {m.source}</span>}</li>
              ))}</ul>
            </Detail>
          )}
          {guidance && <Guidance guidance={guidance} />}
        </div>
      )}
    </div>
  );
}

function Guidance({ guidance }) {
  return (
    <>
      <SectionList title="Workup" sections={guidance.workup} />
      <TreatmentList treatment={guidance.treatment} />
      <SectionList title="Referrals" sections={guidance.referrals} />
      <SectionList title="Disposition" sections={guidance.disposition_guidance} />
      {guidance.sources.length > 0 && (
        <Detail title="Sources"><ul>{guidance.sources.map((s, i) => <li key={i}>{s}</li>)}</ul></Detail>
      )}
    </>
  );
}

function TreatmentList({ treatment }) {
  const sections = reviewedSections(treatment);
  if (!sections.length) return null;
  const review = treatment.review;
  return (
    <Detail title={treatment.label}>
      {review ? (
        <>
          <p style={styles.muted}>{review.notice}</p>
          {factorLines(review).map((line, i) => <p key={i} style={styles.muted}>Chart: {line}</p>)}
          {review.not_checked.map((text, i) => <p key={i} style={styles.notChecked}>Not checked: {text}</p>)}
        </>
      ) : <p style={styles.notChecked}>{REVIEW_UNAVAILABLE}</p>}
      {sections.map((s, i) => (
        <div key={i}>
          {s.title && <em>{s.title}</em>}
          <ul>{s.items.map((line, j) => <TreatmentLine key={j} line={line} />)}</ul>
        </div>
      ))}
    </Detail>
  );
}

function TreatmentLine({ line }) {
  const mark = markStyle(line.mark);
  const badge = mark && (
    <span style={{ ...styles.markBadge, color: mark.color, background: mark.background, borderColor: mark.border }}>
      {mark.label}
    </span>
  );
  if (!line.reasons.length) {
    return (
      <li>
        {badge} {line.text}
        {line.mark === 'appropriate' && <span style={styles.muted}> (checked: {line.medications.join(', ')})</span>}
      </li>
    );
  }
  return (
    <li>
      <details>
        <summary style={styles.missedSummary}>{badge} {line.text}</summary>
        <ul style={styles.missedDetails}>
          {line.reasons.map((r, k) => (
            <li key={k}>
              <strong>{markStyle(r.mark).label}{r.medication ? ` (${r.medication})` : ''}:</strong> {r.reason}{' '}
              <span style={styles.muted}>Source: {r.source}</span>
            </li>
          ))}
        </ul>
      </details>
    </li>
  );
}

function SectionList({ title, sections }) {
  if (!sections || sections.length === 0) return null;
  return (
    <Detail title={title}>
      {sections.map((s, i) => (
        <div key={i}>
          {s.title && <em>{s.title}</em>}
          <ul>{s.items.map((item, j) => <li key={j}>{item}</li>)}</ul>
        </div>
      ))}
    </Detail>
  );
}

function DataStatus({ summary }) {
  const status = summary.data_status || {};
  const labels = summary.data_status_labels || {};
  const entries = Object.entries(status);
  if (!entries.length) return null;
  return (
    <ul style={styles.statusList}>
      {entries.map(([resource, outcome]) => (
        <li key={resource} style={outcome === 'retrieved' ? styles.ok : styles.bad}>
          {labels[resource] || resource}: {outcome}
        </li>
      ))}
    </ul>
  );
}

function WarningList({ items }) {
  if (!items.length) return null;
  return (
    <div style={styles.warning} role="alert">
      <ul style={{ margin: 0, paddingLeft: 20 }}>{items.map((w, i) => <li key={i}>{w}</li>)}</ul>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <section style={styles.section}>
      <h2 style={styles.sectionTitle}>{title}</h2>
      {children}
    </section>
  );
}

function Detail({ title, children }) {
  return (
    <div style={styles.detail}>
      <h4 style={styles.detailTitle}>{title}</h4>
      {children}
    </div>
  );
}

const styles = {
  container: { maxWidth: 960, margin: '0 auto', padding: '24px 16px', fontFamily: 'system-ui, sans-serif', color: '#111827' },
  title: { fontSize: 24, margin: '0 0 16px' },
  complaintForm: { display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center', marginBottom: 16 },
  label: { fontWeight: 600, width: '100%' },
  input: { flex: '1 1 260px', padding: '8px 10px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 15 },
  button: { padding: '8px 16px', background: '#2563eb', color: 'white', border: 'none', borderRadius: 6, cursor: 'pointer' },
  loading: { color: '#6b7280' },
  error: { background: '#fef2f2', border: '1px solid #fca5a5', padding: 12, borderRadius: 6, marginBottom: 16 },
  notice: { fontSize: 14, color: '#374151', margin: '0 0 16px' },
  section: { borderTop: '1px solid #e5e7eb', padding: '16px 0' },
  sectionTitle: { fontSize: 18, margin: '0 0 8px' },
  muted: { color: '#6b7280', fontSize: 14 },
  warning: { background: '#fffbeb', border: '1px solid #f59e0b', padding: 10, borderRadius: 6, marginTop: 8, fontSize: 14 },
  statusList: { listStyle: 'none', padding: 0, display: 'flex', flexWrap: 'wrap', gap: '4px 16px', fontSize: 13 },
  ok: { color: '#166534' },
  bad: { color: '#b91c1c', fontWeight: 600 },
  card: { border: '1px solid #e5e7eb', borderRadius: 8, padding: 12, marginBottom: 10 },
  cardHeader: { display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8, width: '100%',
    background: 'none', border: 'none', padding: 0, textAlign: 'left', cursor: 'pointer', fontSize: 15 },
  evidence: { fontSize: 13, color: '#1d4ed8' },
  cantMiss: { marginLeft: 6, padding: '2px 8px', borderRadius: 999, fontSize: 12, fontWeight: 600,
    background: '#fef2f2', border: '1px solid #ef4444', color: '#991b1b' },
  statusText: { fontSize: 13, color: '#92400e', margin: '6px 0' },
  recommendation: { fontSize: 14, margin: '6px 0' },
  cardBody: { marginTop: 8 },
  detail: { marginTop: 8 },
  detailTitle: { fontSize: 14, margin: '0 0 4px' },
  redFlagBlock: { marginBottom: 8 },
  missedGroup: { marginBottom: 12 },
  missedTitle: { fontSize: 15, margin: '8px 0 4px' },
  notChecked: { fontSize: 13, color: '#92400e', margin: '2px 0' },
  missedItem: { borderBottom: '1px solid #f3f4f6', padding: '4px 0' },
  missedSummary: { cursor: 'pointer', fontSize: 14 },
  missedDetails: { fontSize: 13, padding: '4px 0 4px 16px', color: '#374151' },
  markBadge: { padding: '1px 8px', borderRadius: 999, fontSize: 12, fontWeight: 600, border: '1px solid', whiteSpace: 'nowrap' },
};
