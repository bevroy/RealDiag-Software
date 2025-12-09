'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import HealthDashboard from '../../components/health-manager/HealthDashboard';
import WearableSync from '../../components/health-manager/WearableSync';
import EHRIntegration from '../../components/health-manager/EHRIntegration';
import HealthMetrics from '../../components/health-manager/HealthMetrics';
import SymptomTracker from '../../components/health-manager/SymptomTracker';
import DiagnosticSearch from '../../components/health-manager/DiagnosticSearch';

export default function HealthManagerPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [userData, setUserData] = useState(null);
  const [wearableData, setWearableData] = useState(null);
  const [ehrData, setEHRData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login?redirect=/health-manager');
      return;
    }

    // Load user data
    loadUserData();
    loadWearableData();
    loadEHRData();
  }, []);

  const loadUserData = async () => {
    try {
      const response = await fetch('/api/users/profile', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setUserData(data);
      }
    } catch (error) {
      console.error('Failed to load user data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadWearableData = async () => {
    try {
      const response = await fetch('/api/health/wearable', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setWearableData(data);
      }
    } catch (error) {
      console.error('Failed to load wearable data:', error);
    }
  };

  const loadEHRData = async () => {
    try {
      const response = await fetch('/api/health/ehr', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setEHRData(data);
      }
    } catch (error) {
      console.error('Failed to load EHR data:', error);
    }
  };

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'metrics', label: 'Health Metrics', icon: '❤️' },
    { id: 'symptoms', label: 'Symptom Tracker', icon: '🩺' },
    { id: 'diagnostics', label: 'Diagnostic Search', icon: '🔍' },
    { id: 'wearable', label: 'Wearable Devices', icon: '⌚' },
    { id: 'ehr', label: 'Medical Records', icon: '📋' }
  ];

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <div style={{ textAlign: 'center', color: 'white' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚕️</div>
          <h2>Loading Health Manager...</h2>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '2rem'
    }}>
      {/* Header */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '1.5rem',
        marginBottom: '2rem',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ margin: 0, color: '#2d3748', fontSize: '2rem' }}>
              🏥 Health Manager
            </h1>
            <p style={{ margin: '0.5rem 0 0 0', color: '#718096' }}>
              Your personal health tracking and diagnostic assistant
            </p>
          </div>
          <button
            onClick={() => router.push('/dashboard')}
            style={{
              padding: '0.75rem 1.5rem',
              background: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '1rem',
        marginBottom: '2rem',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '0.5rem'
        }}>
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '1rem',
                background: activeTab === tab.id ? '#667eea' : 'transparent',
                color: activeTab === tab.id ? 'white' : '#4a5568',
                border: activeTab === tab.id ? 'none' : '2px solid #e2e8f0',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600',
                transition: 'all 0.2s',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.25rem'
              }}
            >
              <span style={{ fontSize: '1.5rem' }}>{tab.icon}</span>
              <span style={{ fontSize: '0.875rem' }}>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '2rem',
        minHeight: '500px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
      }}>
        {activeTab === 'dashboard' && (
          <HealthDashboard
            userData={userData}
            wearableData={wearableData}
            ehrData={ehrData}
            onRefresh={() => {
              loadUserData();
              loadWearableData();
              loadEHRData();
            }}
          />
        )}

        {activeTab === 'metrics' && (
          <HealthMetrics
            wearableData={wearableData}
            ehrData={ehrData}
            onSync={loadWearableData}
          />
        )}

        {activeTab === 'symptoms' && (
          <SymptomTracker
            userData={userData}
            onSave={loadUserData}
          />
        )}

        {activeTab === 'diagnostics' && (
          <DiagnosticSearch
            userData={userData}
            wearableData={wearableData}
            ehrData={ehrData}
          />
        )}

        {activeTab === 'wearable' && (
          <WearableSync
            wearableData={wearableData}
            onSync={loadWearableData}
          />
        )}

        {activeTab === 'ehr' && (
          <EHRIntegration
            ehrData={ehrData}
            onSync={loadEHRData}
          />
        )}
      </div>

      {/* Footer */}
      <div style={{
        textAlign: 'center',
        marginTop: '2rem',
        color: 'white',
        fontSize: '0.875rem',
        opacity: 0.8
      }}>
        <p>
          🔒 Your health data is encrypted and HIPAA-compliant
        </p>
      </div>
    </div>
  );
}
