'use client';

import { useState, useEffect } from 'react';
import { authenticatedFetch } from '../../utils/auth';

export default function EHRIntegration({ ehrData, onSync }) {
  const [connecting, setConnecting] = useState(false);
  const [connectedEHR, setConnectedEHR] = useState(null);

  useEffect(() => {
    if (ehrData?.connected) {
      setConnectedEHR(ehrData);
    }
  }, [ehrData]);

  const handleConnect = async (ehrSystem) => {
    setConnecting(true);
    try {
      const response = await authenticatedFetch('/api/health/ehr/connect', {
        method: 'POST',
        body: JSON.stringify({ ehrSystem })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.authUrl) {
          // Redirect to EHR OAuth authorization
          window.location.href = data.authUrl;
        }
      } else {
        alert('Failed to initiate EHR connection. Please try again.');
      }
    } catch (error) {
      console.error('Connection error:', error);
      alert('Failed to initiate EHR connection. Please try again.');
    } finally {
      setConnecting(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm('Are you sure you want to disconnect your EHR? This will remove access to your medical records.')) return;

    try {
      const response = await authenticatedFetch('/api/health/ehr/disconnect', {
        method: 'DELETE'
      });

      if (response.ok) {
        setConnectedEHR(null);
        await onSync();
        alert('✓ EHR disconnected successfully!');
      } else {
        alert('Failed to disconnect EHR. Please try again.');
      }
    } catch (error) {
      console.error('Disconnect error:', error);
      alert('Failed to disconnect EHR. Please try again.');
    }
  };

  const handleSync = async () => {
    try {
      const response = await authenticatedFetch('/api/health/ehr/sync', {
        method: 'POST'
      });

      if (response.ok) {
        await onSync();
        alert('✓ EHR data synced successfully!');
      } else {
        alert('Failed to sync EHR data. Please try again.');
      }
    } catch (error) {
      console.error('Sync error:', error);
      alert('Failed to sync EHR data. Please try again.');
    }
  };

  const ehrSystems = [
    {
      id: 'mychart-epic',
      name: 'MyChart (Epic)',
      icon: '🏥',
      description: 'Connect to Epic MyChart - used by most major health systems',
      providers: ['Mayo Clinic', 'Cleveland Clinic', 'Johns Hopkins', 'Stanford Health'],
      fhir: true
    },
    {
      id: 'cerner',
      name: 'Cerner Health',
      icon: '📋',
      description: 'Connect to Cerner patient portal',
      providers: ['Veterans Affairs', 'Community Health Systems'],
      fhir: true
    },
    {
      id: 'allscripts',
      name: 'Allscripts',
      icon: '📄',
      description: 'Connect to Allscripts FollowMyHealth',
      providers: ['Various community hospitals'],
      fhir: true
    },
    {
      id: 'athenahealth',
      name: 'athenahealth',
      icon: '⚕️',
      description: 'Connect to athenahealth patient portal',
      providers: ['Many independent practices'],
      fhir: true
    },
    {
      id: 'apple-health',
      name: 'Apple Health Records',
      icon: '🍎',
      description: 'Import from Apple Health Records (iPhone)',
      providers: ['500+ participating health systems'],
      fhir: true
    }
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2 style={{ margin: 0, color: '#2d3748', fontSize: '1.75rem' }}>
            📋 Electronic Health Records
          </h2>
          <p style={{ margin: '0.5rem 0 0 0', color: '#718096' }}>
            Connect to your EHR system to import medical records
          </p>
        </div>
      </div>

      {/* Connected EHR */}
      {connectedEHR && (
        <div style={{
          border: '2px solid #48bb78',
          background: '#f0fff4',
          borderRadius: '12px',
          padding: '2rem',
          marginBottom: '2rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                <span style={{ fontSize: '3rem' }}>
                  {ehrSystems.find(s => s.id === connectedEHR.system)?.icon || '🏥'}
                </span>
                <div>
                  <h3 style={{ margin: 0, color: '#2d3748' }}>
                    Connected to {connectedEHR.systemName}
                  </h3>
                  <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#718096' }}>
                    Last synced: {connectedEHR.lastSync ? new Date(connectedEHR.lastSync).toLocaleString() : 'Never'}
                  </p>
                </div>
              </div>

              {/* EHR Data Summary */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '1rem',
                marginTop: '1.5rem'
              }}>
                <DataSummaryCard
                  label="Conditions"
                  count={connectedEHR.conditions?.length || 0}
                  icon="🩺"
                />
                <DataSummaryCard
                  label="Medications"
                  count={connectedEHR.medications?.length || 0}
                  icon="💊"
                />
                <DataSummaryCard
                  label="Allergies"
                  count={connectedEHR.allergies?.length || 0}
                  icon="⚠️"
                />
                <DataSummaryCard
                  label="Lab Results"
                  count={connectedEHR.labResults?.length || 0}
                  icon="🧪"
                />
                <DataSummaryCard
                  label="Immunizations"
                  count={connectedEHR.immunizations?.length || 0}
                  icon="💉"
                />
                <DataSummaryCard
                  label="Procedures"
                  count={connectedEHR.procedures?.length || 0}
                  icon="🏥"
                />
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginLeft: '1rem' }}>
              <button
                onClick={handleSync}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600',
                  whiteSpace: 'nowrap'
                }}
              >
                🔄 Sync Now
              </button>
              <button
                onClick={handleDisconnect}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: 'white',
                  color: '#e53e3e',
                  border: '2px solid #e53e3e',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600',
                  whiteSpace: 'nowrap'
                }}
              >
                Disconnect
              </button>
            </div>
          </div>

          {/* Detailed Records */}
          {connectedEHR.conditions && connectedEHR.conditions.length > 0 && (
            <div style={{ marginTop: '2rem', borderTop: '2px solid #c6f6d5', paddingTop: '1.5rem' }}>
              <h4 style={{ margin: '0 0 1rem 0', color: '#2d3748' }}>Active Conditions</h4>
              <div style={{ display: 'grid', gap: '0.5rem' }}>
                {connectedEHR.conditions.slice(0, 5).map((condition, idx) => (
                  <div key={idx} style={{
                    padding: '0.75rem',
                    background: 'white',
                    borderRadius: '6px',
                    borderLeft: '4px solid #667eea'
                  }}>
                    <div style={{ fontWeight: '600', color: '#2d3748' }}>
                      {condition.name}
                    </div>
                    {condition.onsetDate && (
                      <div style={{ fontSize: '0.75rem', color: '#718096', marginTop: '0.25rem' }}>
                        Since: {new Date(condition.onsetDate).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Available EHR Systems */}
      {!connectedEHR && (
        <div>
          <h3 style={{ color: '#2d3748', marginBottom: '1rem' }}>
            Connect Your EHR System
          </h3>
          <div style={{ display: 'grid', gap: '1rem' }}>
            {ehrSystems.map((system) => (
              <div key={system.id} style={{
                border: '2px solid #e2e8f0',
                borderRadius: '8px',
                padding: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                gap: '1.5rem'
              }}>
                <div style={{ fontSize: '3rem' }}>{system.icon}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <h4 style={{ margin: 0, color: '#2d3748' }}>
                      {system.name}
                    </h4>
                    {system.fhir && (
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        background: '#c6f6d5',
                        color: '#22543d',
                        borderRadius: '10px',
                        fontSize: '0.75rem',
                        fontWeight: '600'
                      }}>
                        FHIR Compatible
                      </span>
                    )}
                  </div>
                  <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.875rem', color: '#718096' }}>
                    {system.description}
                  </p>
                  <div style={{ fontSize: '0.75rem', color: '#4a5568' }}>
                    <strong>Participating providers:</strong> {system.providers.join(', ')}
                  </div>
                </div>
                <button
                  onClick={() => handleConnect(system.id)}
                  disabled={connecting}
                  style={{
                    padding: '0.75rem 1.5rem',
                    background: connecting ? '#cbd5e0' : '#48bb78',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: connecting ? 'not-allowed' : 'pointer',
                    fontWeight: '600',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {connecting ? 'Connecting...' : 'Connect'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info Boxes */}
      <div style={{ display: 'grid', gap: '1rem', marginTop: '2rem' }}>
        <div style={{
          padding: '1.5rem',
          background: '#ebf8ff',
          border: '2px solid #90cdf4',
          borderRadius: '8px'
        }}>
          <h4 style={{ margin: '0 0 0.5rem 0', color: '#2c5282' }}>
            🔒 HIPAA-Compliant & Secure
          </h4>
          <p style={{ margin: 0, fontSize: '0.875rem', color: '#2d3748', lineHeight: '1.6' }}>
            We use industry-standard FHIR (Fast Healthcare Interoperability Resources) APIs to securely 
            access your medical records. Your data is encrypted in transit and at rest. We never share 
            your medical information with third parties.
          </p>
        </div>

        <div style={{
          padding: '1.5rem',
          background: '#fffaf0',
          border: '2px solid #fbd38d',
          borderRadius: '8px'
        }}>
          <h4 style={{ margin: '0 0 0.5rem 0', color: '#744210' }}>
            ℹ️ What Data Is Imported?
          </h4>
          <ul style={{ margin: '0.5rem 0 0 0', paddingLeft: '1.5rem', fontSize: '0.875rem', color: '#2d3748', lineHeight: '1.8' }}>
            <li>Medical conditions and diagnoses</li>
            <li>Current and past medications</li>
            <li>Known allergies and adverse reactions</li>
            <li>Lab results and vital signs</li>
            <li>Immunization history</li>
            <li>Surgical procedures and hospitalizations</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

function DataSummaryCard({ label, count, icon }) {
  return (
    <div style={{
      padding: '1rem',
      background: 'white',
      borderRadius: '8px',
      border: '2px solid #e2e8f0',
      textAlign: 'center'
    }}>
      <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{icon}</div>
      <div style={{ fontSize: '1.75rem', fontWeight: '700', color: '#2d3748', marginBottom: '0.25rem' }}>
        {count}
      </div>
      <div style={{ fontSize: '0.875rem', color: '#718096' }}>
        {label}
      </div>
    </div>
  );
}
