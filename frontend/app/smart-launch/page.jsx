'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { getApiBase } from '../../utils/auth';

/**
 * SmartLaunch Component
 *
 * Displays the chart summary and clinical decision support view after a
 * SMART on FHIR launch from Epic/Cerner/etc.
 *
 * Usage:
 * 1. EHR launches -> /smart/launch -> EHR auth -> /smart/callback
 * 2. /smart/callback exchanges the code for a token, stores it server-side,
 *    and redirects here as /smart-launch?patient_id=xxx with an HttpOnly
 *    session cookie set (realdiag_smart_session) - never a token in the URL.
 * 3. This page reads patient_id from the URL and calls the backend with
 *    credentials: 'include' so the session cookie authenticates the calls.
 */
export default function SmartLaunchPage() {
  return (
    <Suspense fallback={
      <div style={styles.container}>
        <div style={styles.loadingContainer}>
          <div style={styles.spinner}></div>
          <p style={styles.loadingText}>Loading...</p>
        </div>
      </div>
    }>
      <SmartLaunch />
    </Suspense>
  );
}

function SmartLaunch() {
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [patientData, setPatientData] = useState(null);
  const [evaluations, setEvaluations] = useState([]);

  useEffect(() => {
    const patientId = searchParams.get('patient_id');

    if (!patientId) {
      setError('Missing patient context. This page must be launched from the EHR.');
      setLoading(false);
      return;
    }

    fetchPatientData(patientId);
  }, [searchParams]);

  const fetchPatientData = async (patientId) => {
    try {
      const apiBase = getApiBase();

      // The SMART session cookie set by /smart/callback authenticates this
      // request - credentials: 'include' sends it cross-subdomain to the API.
      const summaryResponse = await fetch(
        `${apiBase}/smart/patient/${patientId}`,
        { credentials: 'include' }
      );

      if (!summaryResponse.ok) {
        if (summaryResponse.status === 401) {
          throw new Error('Your session with the EHR has expired. Please relaunch from the EHR.');
        }
        throw new Error('Failed to fetch patient data from the EHR');
      }

      const summary = await summaryResponse.json();
      setPatientData(summary);

      // Same cookie-based session - no access token in the request body.
      const evalResponse = await fetch(`${apiBase}/smart/evaluate-patient`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          patient_id: patientId,
          chief_complaint: null, // Auto-detect from symptoms
          focus_specialties: null // Evaluate all relevant
        })
      });

      if (!evalResponse.ok) {
        throw new Error('Failed to evaluate patient');
      }

      const evals = await evalResponse.json();
      setEvaluations(evals);
      setLoading(false);

    } catch (err) {
      console.error('Error fetching patient data:', err);
      setError(err.message);
      setLoading(false);
    }
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
            This application must be launched from within the EHR using the SMART on FHIR protocol.
          </p>
          <button
            style={styles.backButton}
            onClick={() => window.location.href = '/'}
          >
            Return to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {/* Patient Banner */}
      <PatientBanner patient={patientData} />

      {/* Diagnostic Evaluations */}
      <div style={styles.content}>
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

        {/* Abnormal Labs Section */}
        {patientData.abnormal_labs && patientData.abnormal_labs.length > 0 && (
          <AbnormalLabsSection labs={patientData.abnormal_labs} />
        )}
      </div>
    </div>
  );
}

// Patient Banner Component
function PatientBanner({ patient }) {
  return (
    <div style={styles.banner}>
      <div style={styles.bannerLeft}>
        <strong style={styles.patientName}>{patient.name}</strong>
        <span style={styles.patientInfo}>
          {patient.age} yo {patient.gender}
        </span>
        {patient.date_of_birth && (
          <span style={styles.patientInfo}>DOB: {patient.date_of_birth}</span>
        )}
      </div>
      <div style={styles.bannerRight}>
        <span style={styles.mrn}>MRN: {patient.patient_id}</span>
        <span style={styles.stats}>
          {patient.lab_count} labs • {patient.vital_count} vitals
        </span>
        <a
          href={`/handoff?patient_id=${patient.patient_id}`}
          style={{ fontSize: '13px', color: 'white', textDecoration: 'underline' }}
        >
          View Shift Handoff Summary →
        </a>
      </div>
    </div>
  );
}

// Diagnostic Card Component
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
      <div
        style={styles.cardHeader}
        onClick={() => setExpanded(!expanded)}
      >
        <div style={styles.cardHeaderLeft}>
          <span style={styles.severityEmoji}>
            {getSeverityEmoji(evaluation.severity)}
          </span>
          <div>
            <h3 style={styles.diagnosisLabel}>{evaluation.diagnosis_label}</h3>
            <p style={styles.diagnosisFamily}>{evaluation.diagnosis_family}</p>
          </div>
        </div>
        <div style={styles.cardHeaderRight}>
          <div
            style={{
              ...styles.probabilityBadge,
              backgroundColor: getSeverityColor(evaluation.severity)
            }}
          >
            {(evaluation.probability * 100).toFixed(0)}%
          </div>
          <span style={styles.expandIcon}>{expanded ? '▼' : '▶'}</span>
        </div>
      </div>

      {expanded && (
        <div style={styles.cardBody}>
          {/* Criteria Met */}
          {evaluation.criteria_met && evaluation.criteria_met.length > 0 && (
            <div style={styles.criteriaSection}>
              <h4 style={styles.criteriaTitle}>✓ Criteria Met</h4>
              <ul style={styles.criteriaList}>
                {evaluation.criteria_met.map((criterion, idx) => (
                  <li key={idx} style={styles.criterionMet}>
                    <strong>{criterion.criterion}:</strong> {criterion.value}
                    {criterion.reference && (
                      <span style={styles.reference}> (expected: {criterion.reference})</span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Criteria Not Met */}
          {evaluation.criteria_not_met && evaluation.criteria_not_met.length > 0 && (
            <div style={styles.criteriaSection}>
              <h4 style={styles.criteriaTitle}>✗ Criteria Not Met</h4>
              <ul style={styles.criteriaList}>
                {evaluation.criteria_not_met.map((criterion, idx) => (
                  <li key={idx} style={styles.criterionNotMet}>
                    {criterion}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Missing Tests */}
          {evaluation.missing_tests && evaluation.missing_tests.length > 0 && (
            <div style={styles.criteriaSection}>
              <h4 style={styles.criteriaTitle}>⚠️ Missing Tests</h4>
              <ul style={styles.criteriaList}>
                {evaluation.missing_tests.map((test, idx) => (
                  <li key={idx} style={styles.missingTest}>
                    {test}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {evaluation.recommendations && evaluation.recommendations.length > 0 && (
            <div style={styles.recommendationsSection}>
              <h4 style={styles.criteriaTitle}>💡 Recommendations</h4>
              <ul style={styles.recommendationsList}>
                {evaluation.recommendations.map((rec, idx) => (
                  <li key={idx} style={styles.recommendation}>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Abnormal Labs Section
function AbnormalLabsSection({ labs }) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div style={styles.abnormalLabsContainer}>
      <div
        style={styles.abnormalLabsHeader}
        onClick={() => setExpanded(!expanded)}
      >
        <h3 style={styles.abnormalLabsTitle}>⚠️ Abnormal Lab Values ({labs.length})</h3>
        <span style={styles.expandIcon}>{expanded ? '▼' : '▶'}</span>
      </div>

      {expanded && (
        <div style={styles.abnormalLabsBody}>
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
                  <td style={{...styles.tableCell, ...styles.abnormalValue}}>
                    {lab.value} {lab.unit}
                  </td>
                  <td style={styles.tableCell}>
                    {lab.reference_range || 'N/A'}
                  </td>
                  <td style={styles.tableCell}>
                    {new Date(lab.date).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// Styles
const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f3f4f6',
  },
  loadingContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
  },
  spinner: {
    width: '50px',
    height: '50px',
    border: '4px solid #e5e7eb',
    borderTop: '4px solid #667eea',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  loadingText: {
    marginTop: '20px',
    fontSize: '18px',
    color: '#6b7280',
  },
  errorContainer: {
    maxWidth: '600px',
    margin: '100px auto',
    padding: '40px',
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
    textAlign: 'center',
  },
  errorTitle: {
    color: '#ef4444',
    marginBottom: '16px',
  },
  errorText: {
    color: '#374151',
    marginBottom: '8px',
    fontSize: '16px',
  },
  errorHint: {
    color: '#6b7280',
    fontSize: '14px',
    marginBottom: '24px',
  },
  backButton: {
    padding: '12px 24px',
    backgroundColor: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '16px',
    cursor: 'pointer',
  },
  banner: {
    backgroundColor: '#667eea',
    color: 'white',
    padding: '16px 24px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  bannerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  bannerRight: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-end',
    gap: '4px',
  },
  patientName: {
    fontSize: '20px',
    fontWeight: 'bold',
  },
  patientInfo: {
    fontSize: '16px',
    opacity: 0.9,
  },
  mrn: {
    fontSize: '14px',
    fontFamily: 'monospace',
  },
  stats: {
    fontSize: '12px',
    opacity: 0.8,
  },
  content: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '24px',
  },
  contentTitle: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: '24px',
  },
  noResults: {
    backgroundColor: 'white',
    padding: '40px',
    borderRadius: '8px',
    textAlign: 'center',
    color: '#22c55e',
    fontSize: '18px',
  },
  subtext: {
    color: '#6b7280',
    fontSize: '14px',
    marginTop: '8px',
  },
  evaluationsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
    marginBottom: '32px',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    overflow: 'hidden',
  },
  cardHeader: {
    padding: '16px 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    cursor: 'pointer',
    borderBottom: '1px solid #e5e7eb',
  },
  cardHeaderLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  cardHeaderRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  severityEmoji: {
    fontSize: '24px',
  },
  diagnosisLabel: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#1f2937',
    margin: 0,
  },
  diagnosisFamily: {
    fontSize: '14px',
    color: '#6b7280',
    margin: '4px 0 0 0',
  },
  probabilityBadge: {
    padding: '6px 12px',
    borderRadius: '12px',
    color: 'white',
    fontWeight: 'bold',
    fontSize: '14px',
  },
  expandIcon: {
    color: '#9ca3af',
    fontSize: '14px',
  },
  cardBody: {
    padding: '20px',
    backgroundColor: '#f9fafb',
  },
  criteriaSection: {
    marginBottom: '16px',
  },
  criteriaTitle: {
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: '8px',
  },
  criteriaList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
  },
  criterionMet: {
    padding: '8px 12px',
    backgroundColor: '#d1fae5',
    border: '1px solid #10b981',
    borderRadius: '4px',
    marginBottom: '8px',
    color: '#065f46',
    fontSize: '14px',
  },
  criterionNotMet: {
    padding: '8px 12px',
    backgroundColor: '#fee2e2',
    border: '1px solid #ef4444',
    borderRadius: '4px',
    marginBottom: '8px',
    color: '#991b1b',
    fontSize: '14px',
  },
  missingTest: {
    padding: '8px 12px',
    backgroundColor: '#fef3c7',
    border: '1px solid #eab308',
    borderRadius: '4px',
    marginBottom: '8px',
    color: '#854d0e',
    fontSize: '14px',
  },
  reference: {
    fontSize: '12px',
    color: '#6b7280',
  },
  recommendationsSection: {
    marginTop: '16px',
    padding: '16px',
    backgroundColor: 'white',
    borderRadius: '6px',
    border: '1px solid #e5e7eb',
  },
  recommendationsList: {
    listStyle: 'disc',
    paddingLeft: '20px',
    margin: 0,
  },
  recommendation: {
    color: '#374151',
    fontSize: '14px',
    marginBottom: '8px',
  },
  abnormalLabsContainer: {
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    overflow: 'hidden',
  },
  abnormalLabsHeader: {
    padding: '16px 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    cursor: 'pointer',
    backgroundColor: '#fef3c7',
    borderBottom: '1px solid #eab308',
  },
  abnormalLabsTitle: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#854d0e',
    margin: 0,
  },
  abnormalLabsBody: {
    padding: '20px',
    overflowX: 'auto',
  },
  labTable: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  tableHeader: {
    textAlign: 'left',
    padding: '12px',
    backgroundColor: '#f3f4f6',
    color: '#374151',
    fontWeight: 'bold',
    fontSize: '14px',
    borderBottom: '2px solid #e5e7eb',
  },
  tableRowEven: {
    backgroundColor: 'white',
  },
  tableRowOdd: {
    backgroundColor: '#f9fafb',
  },
  tableCell: {
    padding: '12px',
    borderBottom: '1px solid #e5e7eb',
    fontSize: '14px',
    color: '#374151',
  },
  abnormalValue: {
    fontWeight: 'bold',
    color: '#ef4444',
  },
};
