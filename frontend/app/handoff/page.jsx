'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { getApiBase } from '../../utils/auth';

/**
 * Shift-Handoff Summary
 *
 * Full chart summary followed by what's changed since a timeframe
 * boundary - the current admission's start by default, or a manually
 * entered shift-change time. Authenticated via the same SMART session
 * cookie as /smart-launch (credentials: 'include'), no token in the URL.
 */
export default function HandoffPage() {
  return (
    <Suspense fallback={
      <div style={styles.container}>
        <div style={styles.loadingContainer}>
          <div style={styles.spinner}></div>
          <p style={styles.loadingText}>Loading...</p>
        </div>
      </div>
    }>
      <Handoff />
    </Suspense>
  );
}

function Handoff() {
  const searchParams = useSearchParams();
  const patientId = searchParams.get('patient_id');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const [sinceOverride, setSinceOverride] = useState('');

  useEffect(() => {
    if (!patientId) {
      setError('Missing patient context. This page must be launched from the EHR.');
      setLoading(false);
      return;
    }
    fetchHandoff(patientId, null);
  }, [patientId]);

  const fetchHandoff = async (pid, since) => {
    setLoading(true);
    setError(null);
    try {
      const apiBase = getApiBase();
      const url = new URL(`${apiBase}/smart/patient/${pid}/handoff`);
      if (since) {
        url.searchParams.set('since', since);
      }

      const response = await fetch(url.toString(), { credentials: 'include' });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Your session with the EHR has expired. Please relaunch from the EHR.');
        }
        throw new Error('Failed to fetch handoff summary');
      }

      const result = await response.json();
      setData(result);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching handoff summary:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const handleApplySince = () => {
    if (!sinceOverride) return;
    // datetime-local gives "YYYY-MM-DDTHH:mm" with no timezone - treat as
    // local time and let the browser's Date -> toISOString add the offset.
    const iso = new Date(sinceOverride).toISOString();
    fetchHandoff(patientId, iso);
  };

  const handleResetToAdmission = () => {
    setSinceOverride('');
    fetchHandoff(patientId, null);
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loadingContainer}>
          <div style={styles.spinner}></div>
          <p style={styles.loadingText}>Loading handoff summary...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.errorContainer}>
          <h2 style={styles.errorTitle}>⚠️ Unable to Load Handoff Summary</h2>
          <p style={styles.errorText}>{error}</p>
          <button style={styles.backButton} onClick={() => window.location.href = '/'}>
            Return to Home
          </button>
        </div>
      </div>
    );
  }

  const { full_summary, updates, narrative, admission_start, timeframe_source } = data;

  return (
    <div style={styles.container}>
      <div style={styles.banner}>
        <div style={styles.bannerLeft}>
          <strong style={styles.patientName}>{full_summary.name}</strong>
          <span style={styles.patientInfo}>{full_summary.age} yo {full_summary.gender}</span>
        </div>
        <div style={styles.bannerRight}>
          <span style={styles.mrn}>MRN: {full_summary.patient_id}</span>
          <a href={`/smart-launch?patient_id=${full_summary.patient_id}`} style={styles.bannerLink}>
            View Full Chart Summary & CDS →
          </a>
        </div>
      </div>

      <div style={styles.content}>
        {/* Full summary section - shown first, per handoff convention */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Full Chart Summary</h2>
          <div style={styles.statsRow}>
            <div style={styles.statBox}><strong>{full_summary.lab_count}</strong><span>Labs</span></div>
            <div style={styles.statBox}><strong>{full_summary.vital_count}</strong><span>Vitals</span></div>
            <div style={styles.statBox}><strong>{full_summary.condition_count}</strong><span>Conditions</span></div>
            <div style={styles.statBox}><strong>{full_summary.medication_count}</strong><span>Medications</span></div>
          </div>

          {full_summary.abnormal_labs && full_summary.abnormal_labs.length > 0 && (
            <UpdatesTable title={`⚠️ Abnormal Labs (${full_summary.abnormal_labs.length})`} labs={full_summary.abnormal_labs} highlight />
          )}
        </section>

        {/* Updates since timeframe */}
        <section style={styles.section}>
          <div style={styles.timeframeHeader}>
            <h2 style={styles.sectionTitle}>
              Updates {timeframe_source === 'admission' ? 'Since Admission' : timeframe_source === 'manual' ? 'Since Selected Time' : ''}
            </h2>
            {admission_start && (
              <span style={styles.admissionBadge}>
                Admission start: {new Date(admission_start).toLocaleString()}
              </span>
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
            <button style={styles.applyButton} onClick={handleApplySince}>Apply</button>
            {timeframe_source === 'manual' && (
              <button style={styles.resetButton} onClick={handleResetToAdmission}>Reset to Admission</button>
            )}
          </div>

          <div style={styles.narrativeBox}>
            <p style={styles.narrativeText}>{narrative}</p>
          </div>

          {updates && (
            <>
              {updates.new_abnormal_labs.length > 0 && (
                <UpdatesTable title={`New Abnormal Labs (${updates.new_abnormal_labs.length})`} labs={updates.new_abnormal_labs} highlight />
              )}

              {updates.new_conditions.length > 0 && (
                <SimpleList title={`New Conditions (${updates.new_conditions.length})`} items={updates.new_conditions} />
              )}

              {updates.new_medications.length > 0 && (
                <SimpleList title={`New Medications (${updates.new_medications.length})`} items={updates.new_medications} />
              )}
            </>
          )}
        </section>
      </div>
    </div>
  );
}

function UpdatesTable({ title, labs, highlight }) {
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
              <td style={{ ...styles.tableCell, ...(highlight ? styles.abnormalValue : {}) }}>
                {lab.value} {lab.unit}
              </td>
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
  errorText: { color: '#374151', marginBottom: '24px', fontSize: '16px' },
  backButton: { padding: '12px 24px', backgroundColor: '#667eea', color: 'white', border: 'none', borderRadius: '6px', fontSize: '16px', cursor: 'pointer' },
  banner: { backgroundColor: '#667eea', color: 'white', padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' },
  bannerLeft: { display: 'flex', alignItems: 'center', gap: '16px' },
  bannerRight: { display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' },
  patientName: { fontSize: '20px', fontWeight: 'bold' },
  patientInfo: { fontSize: '16px', opacity: 0.9 },
  mrn: { fontSize: '14px', fontFamily: 'monospace' },
  bannerLink: { fontSize: '13px', color: 'white', textDecoration: 'underline' },
  content: { maxWidth: '1200px', margin: '0 auto', padding: '24px' },
  section: { backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', padding: '24px', marginBottom: '24px' },
  sectionTitle: { fontSize: '22px', fontWeight: 'bold', color: '#1f2937', margin: 0 },
  statsRow: { display: 'flex', gap: '16px', margin: '16px 0' },
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
