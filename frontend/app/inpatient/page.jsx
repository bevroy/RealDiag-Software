'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { getApiBase } from '../../utils/auth';

/**
 * Inpatient
 * ---------
 * Consolidated inpatient module: Chart Summary (CDS evaluations, abnormal
 * labs) and Handoff (structured delta + narrative since admission/shift
 * start) as tabs under one shared patient banner. Reached either directly
 * from the EHR launch (/smart/callback redirects here) or, if the
 * clinician also has an active SMART session, from the "Inpatient" link
 * in the main app nav. Authenticated via the realdiag_smart_session
 * cookie only - no RealDiag account/login required, matching how a real
 * EHR-launched SMART app should behave.
 */
export default function InpatientPage() {
  return (
    <Suspense fallback={
      <div style={styles.container}>
        <div style={styles.loadingContainer}>
          <div style={styles.spinner}></div>
          <p style={styles.loadingText}>Loading...</p>
        </div>
      </div>
    }>
      <Inpatient />
    </Suspense>
  );
}

function Inpatient() {
  const searchParams = useSearchParams();
  const patientId = searchParams.get('patient_id');
  const initialTab = searchParams.get('tab') === 'handoff' ? 'handoff' : 'summary';

  const [activeTab, setActiveTab] = useState(initialTab);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [patientData, setPatientData] = useState(null);
  const [evaluations, setEvaluations] = useState([]);

  const [handoffData, setHandoffData] = useState(null);
  const [handoffLoading, setHandoffLoading] = useState(false);
  const [handoffError, setHandoffError] = useState(null);
  const [sinceOverride, setSinceOverride] = useState('');

  useEffect(() => {
    if (!patientId) {
      setError('Missing patient context. This page must be launched from the EHR.');
      setLoading(false);
      return;
    }
    fetchChartSummary(patientId);
  }, [patientId]);

  useEffect(() => {
    if (activeTab === 'handoff' && patientId && !handoffData && !handoffLoading) {
      fetchHandoff(patientId, null);
    }
  }, [activeTab, patientId]);

  const fetchChartSummary = async (pid) => {
    try {
      const apiBase = getApiBase();
      const summaryResponse = await fetch(`${apiBase}/smart/patient/${pid}`, { credentials: 'include' });
      if (!summaryResponse.ok) {
        if (summaryResponse.status === 401) {
          throw new Error('Your session with the EHR has expired. Please relaunch from the EHR.');
        }
        throw new Error('Failed to fetch patient data from the EHR');
      }
      const summary = await summaryResponse.json();
      setPatientData(summary);

      const evalResponse = await fetch(`${apiBase}/smart/evaluate-patient`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient_id: pid, chief_complaint: null, focus_specialties: null })
      });
      if (!evalResponse.ok) {
        throw new Error('Failed to evaluate patient');
      }
      setEvaluations(await evalResponse.json());
      setLoading(false);
    } catch (err) {
      console.error('Error fetching chart summary:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const fetchHandoff = async (pid, since) => {
    setHandoffLoading(true);
    setHandoffError(null);
    try {
      const apiBase = getApiBase();
      const url = new URL(`${apiBase}/smart/patient/${pid}/handoff`);
      if (since) url.searchParams.set('since', since);
      const response = await fetch(url.toString(), { credentials: 'include' });
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Your session with the EHR has expired. Please relaunch from the EHR.');
        }
        throw new Error('Failed to fetch handoff summary');
      }
      setHandoffData(await response.json());
      setHandoffLoading(false);
    } catch (err) {
      console.error('Error fetching handoff summary:', err);
      setHandoffError(err.message);
      setHandoffLoading(false);
    }
  };

  const handleApplySince = () => {
    if (!sinceOverride || !patientId) return;
    const iso = new Date(sinceOverride).toISOString();
    fetchHandoff(patientId, iso);
  };

  const handleResetToAdmission = () => {
    setSinceOverride('');
    if (patientId) fetchHandoff(patientId, null);
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loadingContainer}>
          <div style={styles.spinner}></div>
          <p style={styles.loadingText}>Loading patient data from the EHR...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.errorContainer}>
          <h2 style={styles.errorTitle}>⚠️ Launch Error</h2>
          <p style={styles.errorText}>{error}</p>
          <p style={styles.errorHint}>
            This page must be launched from within the EHR using the SMART on FHIR protocol.
          </p>
          <button style={styles.backButton} onClick={() => window.location.href = '/'}>Return to Home</button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <PatientBanner patient={patientData} />

      <div style={styles.tabBar}>
        <button
          style={{ ...styles.tabButton, ...(activeTab === 'summary' ? styles.tabButtonActive : {}) }}
          onClick={() => setActiveTab('summary')}
        >
          Chart Summary
        </button>
        <button
          style={{ ...styles.tabButton, ...(activeTab === 'handoff' ? styles.tabButtonActive : {}) }}
          onClick={() => setActiveTab('handoff')}
        >
          Handoff
        </button>
      </div>

      <div style={styles.content}>
        {activeTab === 'summary' && (
          <ChartSummaryTab patientData={patientData} evaluations={evaluations} />
        )}
        {activeTab === 'handoff' && (
          <HandoffTab
            loading={handoffLoading}
            error={handoffError}
            data={handoffData}
            sinceOverride={sinceOverride}
            setSinceOverride={setSinceOverride}
            onApplySince={handleApplySince}
            onResetToAdmission={handleResetToAdmission}
          />
        )}
      </div>
    </div>
  );
}

function ChartSummaryTab({ patientData, evaluations }) {
  return (
    <>
      <h2 style={styles.contentTitle}>Clinical Decision Support</h2>
      {evaluations.length === 0 ? (
        <div style={styles.noResults}>
          <p>✓ No significant diagnostic concerns identified.</p>
          <p style={styles.subtext}>Patient data reviewed. All values within normal ranges.</p>
        </div>
      ) : (
        <div style={styles.evaluationsList}>
          {evaluations.map((evaluation, idx) => (
            <DiagnosticCard key={idx} evaluation={evaluation} />
          ))}
        </div>
      )}
      {patientData.abnormal_labs && patientData.abnormal_labs.length > 0 && (
        <LabTable title={`⚠️ Abnormal Lab Values (${patientData.abnormal_labs.length})`} labs={patientData.abnormal_labs} />
      )}
    </>
  );
}

function HandoffTab({ loading, error, data, sinceOverride, setSinceOverride, onApplySince, onResetToAdmission }) {
  if (loading) {
    return <p style={styles.subtext}>Loading handoff summary...</p>;
  }
  if (error) {
    return <p style={{ color: '#ef4444' }}>{error}</p>;
  }
  if (!data) {
    return null;
  }

  const { full_summary, updates, narrative, admission_start, timeframe_source } = data;

  return (
    <>
      <div style={styles.statsRow}>
        <div style={styles.statBox}><strong>{full_summary.lab_count}</strong><span>Labs</span></div>
        <div style={styles.statBox}><strong>{full_summary.vital_count}</strong><span>Vitals</span></div>
        <div style={styles.statBox}><strong>{full_summary.condition_count}</strong><span>Conditions</span></div>
        <div style={styles.statBox}><strong>{full_summary.medication_count}</strong><span>Medications</span></div>
      </div>

      <div style={styles.timeframeHeader}>
        <h2 style={styles.contentTitle}>
          Updates {timeframe_source === 'admission' ? 'Since Admission' : timeframe_source === 'manual' ? 'Since Selected Time' : ''}
        </h2>
        {admission_start && (
          <span style={styles.admissionBadge}>Admission start: {new Date(admission_start).toLocaleString()}</span>
        )}
      </div>

      <div style={styles.sinceControl}>
        <label style={styles.sinceLabel}>
          Use a different shift-change time:
          <input
            type="datetime-local"
            value={sinceOverride}
            onChange={(e) => setSinceOverride(e.target.value)}
            style={styles.sinceInput}
          />
        </label>
        <button style={styles.applyButton} onClick={onApplySince}>Apply</button>
        {timeframe_source === 'manual' && (
          <button style={styles.resetButton} onClick={onResetToAdmission}>Reset to Admission</button>
        )}
      </div>

      <div style={styles.narrativeBox}>
        <p style={styles.narrativeText}>{narrative}</p>
      </div>

      {updates && (
        <>
          {updates.new_abnormal_labs.length > 0 && (
            <LabTable title={`New Abnormal Labs (${updates.new_abnormal_labs.length})`} labs={updates.new_abnormal_labs} />
          )}
          {updates.new_conditions.length > 0 && (
            <SimpleList title={`New Conditions (${updates.new_conditions.length})`} items={updates.new_conditions} />
          )}
          {updates.new_medications.length > 0 && (
            <SimpleList title={`New Medications (${updates.new_medications.length})`} items={updates.new_medications} />
          )}
        </>
      )}
    </>
  );
}

function PatientBanner({ patient }) {
  return (
    <div style={styles.banner}>
      <div style={styles.bannerLeft}>
        <strong style={styles.patientName}>{patient.name}</strong>
        <span style={styles.patientInfo}>{patient.age} yo {patient.gender}</span>
        {patient.date_of_birth && <span style={styles.patientInfo}>DOB: {patient.date_of_birth}</span>}
      </div>
      <div style={styles.bannerRight}>
        <span style={styles.mrn}>MRN: {patient.patient_id}</span>
        <span style={styles.stats}>{patient.lab_count} labs • {patient.vital_count} vitals</span>
      </div>
    </div>
  );
}

function DiagnosticCard({ evaluation }) {
  const [expanded, setExpanded] = useState(false);

  const getSeverityColor = (severity) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL': return '#ef4444';
      case 'HIGH': return '#f97316';
      case 'MODERATE': return '#eab308';
      case 'LOW': return '#22c55e';
      default: return '#6b7280';
    }
  };
  const getSeverityEmoji = (severity) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL': return '🔴';
      case 'HIGH': return '🟠';
      case 'MODERATE': return '🟡';
      case 'LOW': return '🟢';
      default: return '⚪';
    }
  };

  return (
    <div style={styles.card}>
      <div style={styles.cardHeader} onClick={() => setExpanded(!expanded)}>
        <div style={styles.cardHeaderLeft}>
          <span style={styles.severityEmoji}>{getSeverityEmoji(evaluation.severity)}</span>
          <div>
            <h3 style={styles.diagnosisLabel}>{evaluation.diagnosis_label}</h3>
            <p style={styles.diagnosisFamily}>{evaluation.diagnosis_family}</p>
          </div>
        </div>
        <div style={styles.cardHeaderRight}>
          <div style={{ ...styles.probabilityBadge, backgroundColor: getSeverityColor(evaluation.severity) }}>
            {(evaluation.probability * 100).toFixed(0)}%
          </div>
          <span style={styles.expandIcon}>{expanded ? '▼' : '▶'}</span>
        </div>
      </div>
      {expanded && (
        <div style={styles.cardBody}>
          {evaluation.criteria_met && evaluation.criteria_met.length > 0 && (
            <div style={styles.criteriaSection}>
              <h4 style={styles.criteriaTitle}>✓ Criteria Met</h4>
              <ul style={styles.criteriaList}>
                {evaluation.criteria_met.map((criterion, idx) => (
                  <li key={idx} style={styles.criterionMet}>
                    <strong>{criterion.criterion}:</strong> {criterion.value}
                    {criterion.expected && <span style={styles.reference}> (expected: {criterion.expected})</span>}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {evaluation.missing_tests && evaluation.missing_tests.length > 0 && (
            <div style={styles.criteriaSection}>
              <h4 style={styles.criteriaTitle}>⚠️ Missing Tests</h4>
              <ul style={styles.criteriaList}>
                {evaluation.missing_tests.map((test, idx) => (
                  <li key={idx} style={styles.missingTest}>{test}</li>
                ))}
              </ul>
            </div>
          )}
          {evaluation.recommendations && evaluation.recommendations.length > 0 && (
            <div style={styles.recommendationsSection}>
              <h4 style={styles.criteriaTitle}>💡 Recommendations</h4>
              <ul style={styles.recommendationsList}>
                {evaluation.recommendations.map((rec, idx) => (
                  <li key={idx} style={styles.recommendation}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function LabTable({ title, labs }) {
  return (
    <div style={styles.tableContainer}>
      <h3 style={styles.tableTitle}>{title}</h3>
      <table style={styles.labTable}>
        <thead>
          <tr>
            <th style={styles.tableHeader}>Test</th>
            <th style={styles.tableHeader}>Value</th>
            <th style={styles.tableHeader}>Reference Range</th>
            <th style={styles.tableHeader}>Date</th>
          </tr>
        </thead>
        <tbody>
          {labs.map((lab, idx) => (
            <tr key={idx} style={idx % 2 === 0 ? styles.tableRowEven : styles.tableRowOdd}>
              <td style={styles.tableCell}>{lab.name}</td>
              <td style={{ ...styles.tableCell, ...styles.abnormalValue }}>{lab.value} {lab.unit}</td>
              <td style={styles.tableCell}>{lab.reference_range || 'N/A'}</td>
              <td style={styles.tableCell}>{lab.date ? new Date(lab.date).toLocaleDateString() : 'N/A'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SimpleList({ title, items }) {
  return (
    <div style={styles.tableContainer}>
      <h3 style={styles.tableTitle}>{title}</h3>
      <ul style={styles.simpleList}>
        {items.map((item, idx) => (
          <li key={idx} style={styles.simpleListItem}>
            <strong>{item.name}</strong>
            {item.date && <span style={styles.simpleListDate}> — {new Date(item.date).toLocaleDateString()}</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}

const styles = {
  container: { minHeight: '100vh', backgroundColor: '#f3f4f6' },
  loadingContainer: { display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' },
  spinner: { width: '50px', height: '50px', border: '4px solid #e5e7eb', borderTop: '4px solid #667eea', borderRadius: '50%', animation: 'spin 1s linear infinite' },
  loadingText: { marginTop: '20px', fontSize: '18px', color: '#6b7280' },
  errorContainer: { maxWidth: '600px', margin: '100px auto', padding: '40px', backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', textAlign: 'center' },
  errorTitle: { color: '#ef4444', marginBottom: '16px' },
  errorText: { color: '#374151', marginBottom: '8px', fontSize: '16px' },
  errorHint: { color: '#6b7280', fontSize: '14px', marginBottom: '24px' },
  backButton: { padding: '12px 24px', backgroundColor: '#667eea', color: 'white', border: 'none', borderRadius: '6px', fontSize: '16px', cursor: 'pointer' },
  banner: { backgroundColor: '#667eea', color: 'white', padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' },
  bannerLeft: { display: 'flex', alignItems: 'center', gap: '16px' },
  bannerRight: { display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' },
  patientName: { fontSize: '20px', fontWeight: 'bold' },
  patientInfo: { fontSize: '16px', opacity: 0.9 },
  mrn: { fontSize: '14px', fontFamily: 'monospace' },
  stats: { fontSize: '12px', opacity: 0.8 },
  tabBar: { display: 'flex', gap: '4px', maxWidth: '1200px', margin: '16px auto 0', padding: '0 24px' },
  tabButton: { padding: '10px 20px', backgroundColor: '#e5e7eb', color: '#374151', border: 'none', borderRadius: '6px 6px 0 0', fontSize: '14px', fontWeight: 600, cursor: 'pointer' },
  tabButtonActive: { backgroundColor: 'white', color: '#667eea', boxShadow: '0 -2px 4px rgba(0,0,0,0.05)' },
  content: { maxWidth: '1200px', margin: '0 auto', padding: '24px', backgroundColor: 'white', borderRadius: '0 8px 8px 8px' },
  contentTitle: { fontSize: '22px', fontWeight: 'bold', color: '#1f2937', margin: '0 0 16px' },
  noResults: { backgroundColor: '#f9fafb', padding: '40px', borderRadius: '8px', textAlign: 'center', color: '#22c55e', fontSize: '18px' },
  subtext: { color: '#6b7280', fontSize: '14px', marginTop: '8px' },
  evaluationsList: { display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '32px' },
  card: { backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflow: 'hidden', border: '1px solid #e5e7eb' },
  cardHeader: { padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', borderBottom: '1px solid #e5e7eb' },
  cardHeaderLeft: { display: 'flex', alignItems: 'center', gap: '12px' },
  cardHeaderRight: { display: 'flex', alignItems: 'center', gap: '16px' },
  severityEmoji: { fontSize: '24px' },
  diagnosisLabel: { fontSize: '18px', fontWeight: 'bold', color: '#1f2937', margin: 0 },
  diagnosisFamily: { fontSize: '14px', color: '#6b7280', margin: '4px 0 0 0' },
  probabilityBadge: { padding: '6px 12px', borderRadius: '12px', color: 'white', fontWeight: 'bold', fontSize: '14px' },
  expandIcon: { color: '#9ca3af', fontSize: '14px' },
  cardBody: { padding: '20px', backgroundColor: '#f9fafb' },
  criteriaSection: { marginBottom: '16px' },
  criteriaTitle: { fontSize: '14px', fontWeight: 'bold', color: '#374151', marginBottom: '8px' },
  criteriaList: { listStyle: 'none', padding: 0, margin: 0 },
  criterionMet: { padding: '8px 12px', backgroundColor: '#d1fae5', border: '1px solid #10b981', borderRadius: '4px', marginBottom: '8px', color: '#065f46', fontSize: '14px' },
  missingTest: { padding: '8px 12px', backgroundColor: '#fef3c7', border: '1px solid #eab308', borderRadius: '4px', marginBottom: '8px', color: '#854d0e', fontSize: '14px' },
  reference: { fontSize: '12px', color: '#6b7280' },
  recommendationsSection: { marginTop: '16px', padding: '16px', backgroundColor: 'white', borderRadius: '6px', border: '1px solid #e5e7eb' },
  recommendationsList: { listStyle: 'disc', paddingLeft: '20px', margin: 0 },
  recommendation: { color: '#374151', fontSize: '14px', marginBottom: '8px' },
  statsRow: { display: 'flex', gap: '16px', margin: '0 0 24px' },
  statBox: { display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '12px 20px', backgroundColor: '#f9fafb', borderRadius: '6px', minWidth: '80px' },
  timeframeHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' },
  admissionBadge: { fontSize: '13px', color: '#6b7280', backgroundColor: '#f3f4f6', padding: '4px 10px', borderRadius: '12px' },
  sinceControl: { display: 'flex', alignItems: 'center', gap: '12px', margin: '16px 0', flexWrap: 'wrap' },
  sinceLabel: { display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: '#374151' },
  sinceInput: { padding: '6px 10px', borderRadius: '4px', border: '1px solid #d1d5db' },
  applyButton: { padding: '8px 16px', backgroundColor: '#667eea', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px' },
  resetButton: { padding: '8px 16px', backgroundColor: '#e5e7eb', color: '#374151', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px' },
  narrativeBox: { backgroundColor: '#eef2ff', border: '1px solid #c7d2fe', borderRadius: '6px', padding: '16px', margin: '16px 0' },
  narrativeText: { margin: 0, fontSize: '15px', color: '#312e81', lineHeight: 1.6 },
  tableContainer: { marginTop: '20px' },
  tableTitle: { fontSize: '16px', fontWeight: 'bold', color: '#374151', marginBottom: '8px' },
  labTable: { width: '100%', borderCollapse: 'collapse' },
  tableHeader: { textAlign: 'left', padding: '12px', backgroundColor: '#f3f4f6', color: '#374151', fontWeight: 'bold', fontSize: '14px', borderBottom: '2px solid #e5e7eb' },
  tableRowEven: { backgroundColor: 'white' },
  tableRowOdd: { backgroundColor: '#f9fafb' },
  tableCell: { padding: '12px', borderBottom: '1px solid #e5e7eb', fontSize: '14px', color: '#374151' },
  abnormalValue: { fontWeight: 'bold', color: '#ef4444' },
  simpleList: { listStyle: 'none', padding: 0, margin: 0 },
  simpleListItem: { padding: '10px 12px', backgroundColor: '#f9fafb', borderRadius: '4px', marginBottom: '6px', fontSize: '14px', color: '#374151' },
  simpleListDate: { color: '#6b7280', fontSize: '13px' },
};
