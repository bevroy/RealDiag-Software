'use client';

import { useState, useEffect } from 'react';

export default function HealthDashboard({ userData, wearableData, ehrData, onRefresh }) {
  const [stats, setStats] = useState({
    heartRate: null,
    steps: null,
    sleep: null,
    activeMinutes: null,
    lastSync: null
  });

  useEffect(() => {
    if (wearableData) {
      setStats({
        heartRate: wearableData.heartRate?.current || null,
        steps: wearableData.steps?.today || null,
        sleep: wearableData.sleep?.lastNight || null,
        activeMinutes: wearableData.activity?.today || null,
        lastSync: wearableData.lastSync || null
      });
    }
  }, [wearableData]);

  const recentSymptoms = userData?.symptomHistory?.slice(0, 5) || [];
  const recentDiagnoses = userData?.diagnosisHistory?.slice(0, 5) || [];
  const medications = ehrData?.medications || [];
  const allergies = ehrData?.allergies || [];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2 style={{ margin: 0, color: '#2d3748', fontSize: '1.75rem' }}>
          Welcome back, {userData?.name || 'User'}!
        </h2>
        <button
          onClick={onRefresh}
          style={{
            padding: '0.5rem 1rem',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          🔄 Refresh Data
        </button>
      </div>

      {/* Health Metrics Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        <MetricCard
          icon="❤️"
          label="Heart Rate"
          value={stats.heartRate ? `${stats.heartRate} bpm` : 'No data'}
          status={getHeartRateStatus(stats.heartRate)}
        />
        <MetricCard
          icon="👟"
          label="Steps Today"
          value={stats.steps ? stats.steps.toLocaleString() : 'No data'}
          status={getStepsStatus(stats.steps)}
        />
        <MetricCard
          icon="😴"
          label="Sleep Last Night"
          value={stats.sleep ? `${stats.sleep}h` : 'No data'}
          status={getSleepStatus(stats.sleep)}
        />
        <MetricCard
          icon="🏃"
          label="Active Minutes"
          value={stats.activeMinutes ? `${stats.activeMinutes} min` : 'No data'}
          status={getActivityStatus(stats.activeMinutes)}
        />
      </div>

      {/* Two Column Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Recent Symptoms */}
        <div style={{
          border: '2px solid #e2e8f0',
          borderRadius: '8px',
          padding: '1.5rem'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#2d3748' }}>
            📝 Recent Symptoms
          </h3>
          {recentSymptoms.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {recentSymptoms.map((symptom, idx) => (
                <div key={idx} style={{
                  padding: '0.75rem',
                  background: '#f7fafc',
                  borderRadius: '6px',
                  borderLeft: '4px solid #667eea'
                }}>
                  <div style={{ fontWeight: '600', color: '#2d3748' }}>
                    {symptom.symptoms?.join(', ') || 'Unknown'}
                  </div>
                  <div style={{ fontSize: '0.875rem', color: '#718096', marginTop: '0.25rem' }}>
                    {new Date(symptom.timestamp).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#718096', fontStyle: 'italic' }}>
              No recent symptoms tracked
            </p>
          )}
        </div>

        {/* Recent Diagnoses */}
        <div style={{
          border: '2px solid #e2e8f0',
          borderRadius: '8px',
          padding: '1.5rem'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#2d3748' }}>
            🔍 Recent Diagnoses
          </h3>
          {recentDiagnoses.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {recentDiagnoses.map((diagnosis, idx) => (
                <div key={idx} style={{
                  padding: '0.75rem',
                  background: '#f7fafc',
                  borderRadius: '6px',
                  borderLeft: '4px solid #48bb78'
                }}>
                  <div style={{ fontWeight: '600', color: '#2d3748' }}>
                    {diagnosis.diagnosis || 'Unknown'}
                  </div>
                  <div style={{ fontSize: '0.875rem', color: '#718096', marginTop: '0.25rem' }}>
                    {new Date(diagnosis.timestamp).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#718096', fontStyle: 'italic' }}>
              No recent diagnoses
            </p>
          )}
        </div>
      </div>

      {/* Medications & Allergies */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Current Medications */}
        <div style={{
          border: '2px solid #e2e8f0',
          borderRadius: '8px',
          padding: '1.5rem'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#2d3748' }}>
            💊 Current Medications
          </h3>
          {medications.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {medications.map((med, idx) => (
                <div key={idx} style={{
                  padding: '0.5rem',
                  background: '#f7fafc',
                  borderRadius: '4px',
                  fontSize: '0.875rem'
                }}>
                  <div style={{ fontWeight: '600', color: '#2d3748' }}>
                    {med.name}
                  </div>
                  <div style={{ color: '#718096' }}>
                    {med.dosage} - {med.frequency}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#718096', fontStyle: 'italic' }}>
              No medications on record
            </p>
          )}
        </div>

        {/* Allergies */}
        <div style={{
          border: '2px solid #e2e8f0',
          borderRadius: '8px',
          padding: '1.5rem'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#2d3748' }}>
            ⚠️ Allergies
          </h3>
          {allergies.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {allergies.map((allergy, idx) => (
                <div key={idx} style={{
                  padding: '0.5rem',
                  background: '#fff5f5',
                  borderRadius: '4px',
                  borderLeft: '3px solid #fc8181'
                }}>
                  <div style={{ fontWeight: '600', color: '#c53030' }}>
                    {allergy.allergen}
                  </div>
                  <div style={{ fontSize: '0.875rem', color: '#718096' }}>
                    Reaction: {allergy.reaction}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#718096', fontStyle: 'italic' }}>
              No known allergies
            </p>
          )}
        </div>
      </div>

      {/* Last Sync Info */}
      {stats.lastSync && (
        <div style={{
          marginTop: '2rem',
          padding: '1rem',
          background: '#edf2f7',
          borderRadius: '6px',
          textAlign: 'center',
          fontSize: '0.875rem',
          color: '#4a5568'
        }}>
          Last synced: {new Date(stats.lastSync).toLocaleString()}
        </div>
      )}
    </div>
  );
}

function MetricCard({ icon, label, value, status }) {
  return (
    <div style={{
      padding: '1.5rem',
      border: '2px solid #e2e8f0',
      borderRadius: '8px',
      background: status === 'good' ? '#f0fff4' : status === 'warning' ? '#fffaf0' : 'white'
    }}>
      <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{icon}</div>
      <div style={{ fontSize: '0.875rem', color: '#718096', marginBottom: '0.25rem' }}>
        {label}
      </div>
      <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#2d3748' }}>
        {value}
      </div>
      {status && (
        <div style={{
          marginTop: '0.5rem',
          fontSize: '0.75rem',
          color: status === 'good' ? '#38a169' : status === 'warning' ? '#d69e2e' : '#718096'
        }}>
          {status === 'good' ? '✓ Normal' : status === 'warning' ? '⚠ Monitor' : ''}
        </div>
      )}
    </div>
  );
}

function getHeartRateStatus(hr) {
  if (!hr) return null;
  if (hr >= 60 && hr <= 100) return 'good';
  if ((hr >= 50 && hr < 60) || (hr > 100 && hr <= 120)) return 'warning';
  return 'alert';
}

function getStepsStatus(steps) {
  if (!steps) return null;
  if (steps >= 10000) return 'good';
  if (steps >= 5000) return 'warning';
  return null;
}

function getSleepStatus(hours) {
  if (!hours) return null;
  if (hours >= 7 && hours <= 9) return 'good';
  if ((hours >= 6 && hours < 7) || (hours > 9 && hours <= 10)) return 'warning';
  return 'alert';
}

function getActivityStatus(minutes) {
  if (!minutes) return null;
  if (minutes >= 30) return 'good';
  if (minutes >= 15) return 'warning';
  return null;
}
