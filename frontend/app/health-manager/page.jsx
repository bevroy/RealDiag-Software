'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function HealthManagerPage() {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication - use cookie-based auth
    const checkAuth = async () => {
      try {
        const response = await fetch('https://realdiag-software.onrender.com/users/me', {
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
          const data = await response.json();
          setUserData(data);
          setLoading(false);
        } else {
          // Not authenticated, redirect to login
          window.location.href = '/app/login';
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
        setLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: 'linear-gradient(135deg, #f0fdfa 0%, #e7f5f3 100%)'
      }}>
        <div style={{
          fontSize: '1.5rem',
          color: '#0f766e'
        }}>
          Loading...
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f0fdfa 0%, #e7f5f3 100%)',
      padding: '2rem'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        {/* Header */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '2rem',
          marginBottom: '2rem',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div>
            <h1 style={{
              margin: '0 0 0.5rem 0',
              color: '#0f766e',
              fontSize: '2rem'
            }}>
              🏥 Health Manager
            </h1>
            <p style={{
              margin: 0,
              color: '#64748b',
              fontSize: '1rem'
            }}>
              Welcome back, {userData?.full_name || 'Patient'}
            </p>
          </div>
          <Link href="/" style={{
            padding: '0.75rem 1.5rem',
            background: '#0f766e',
            color: 'white',
            borderRadius: '8px',
            textDecoration: 'none',
            fontWeight: '600'
          }}>
            ← Back to Home
          </Link>
        </div>

        {/* Quick Actions */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2rem'
        }}>
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '1.5rem',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            border: '2px solid #ccfbf1'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔬</div>
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#0f766e' }}>
              Symptom Search
            </h3>
            <p style={{ margin: '0 0 1rem 0', color: '#64748b', fontSize: '0.875rem' }}>
              Check symptoms and get diagnostic suggestions
            </p>
            <Link href="/symptom-search" style={{
              padding: '0.5rem 1rem',
              background: '#0f766e',
              color: 'white',
              borderRadius: '6px',
              textDecoration: 'none',
              fontSize: '0.875rem',
              display: 'inline-block'
            }}>
              Start Search →
            </Link>
          </div>

          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '1.5rem',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            border: '2px solid #ccfbf1'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📋</div>
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#0f766e' }}>
              Medical Records (Coming Soon)
            </h3>
            <p style={{ margin: '0', color: '#64748b', fontSize: '0.875rem' }}>
              Connect to your EHR and view health records, medications, and lab results
            </p>
          </div>

          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '1.5rem',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            border: '2px solid #ccfbf1'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>⌚</div>
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#0f766e' }}>
              Wearable Devices (Coming Soon)
            </h3>
            <p style={{ margin: '0', color: '#64748b', fontSize: '0.875rem' }}>
              Sync data from Apple Watch, Fitbit, and other health trackers
            </p>
          </div>
        </div>

        {/* Information Section */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '2rem',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ margin: '0 0 1rem 0', color: '#0f766e' }}>
            📊 Patient Health Dashboard
          </h2>
          <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>
            The Health Manager is your personal health hub for managing medical records, tracking symptoms, and accessing diagnostic tools.
          </p>
          
          <div style={{
            background: '#f0fdfa',
            border: '1px solid #ccfbf1',
            borderRadius: '8px',
            padding: '1.5rem',
            marginTop: '1rem'
          }}>
            <h3 style={{ margin: '0 0 1rem 0', color: '#0f766e' }}>
              🚀 Coming Soon Features:
            </h3>
            <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#64748b' }}>
              <li style={{ marginBottom: '0.5rem' }}>EHR Integration with Epic, Cerner, and other major systems</li>
              <li style={{ marginBottom: '0.5rem' }}>Personal Health Records (PHR) management</li>
              <li style={{ marginBottom: '0.5rem' }}>Medication tracking and reminders</li>
              <li style={{ marginBottom: '0.5rem' }}>Lab results and imaging reports</li>
              <li style={{ marginBottom: '0.5rem' }}>Wearable device integration (Apple Health, Fitbit, etc.)</li>
              <li style={{ marginBottom: '0.5rem' }}>Symptom diary and health journal</li>
              <li style={{ marginBottom: '0.5rem' }}>Appointment scheduling and reminders</li>
              <li>Health metrics visualization and trends</li>
            </ul>
          </div>

          <div style={{
            marginTop: '1.5rem',
            padding: '1rem',
            background: '#fef3c7',
            border: '1px solid #fde047',
            borderRadius: '8px'
          }}>
            <p style={{ margin: 0, color: '#78350f', fontSize: '0.875rem' }}>
              <strong>🔒 Privacy & Security:</strong> All health data is encrypted end-to-end and complies with HIPAA regulations. 
              You have full control over who can access your health information.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div style={{
          textAlign: 'center',
          marginTop: '2rem',
          color: '#64748b',
          fontSize: '0.875rem'
        }}>
          <p>Need help? <a href="/account" style={{ color: '#0f766e' }}>Contact Support</a></p>
        </div>
      </div>
    </div>
  );
}
