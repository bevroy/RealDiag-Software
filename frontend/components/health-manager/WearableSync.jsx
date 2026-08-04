'use client';

import { useState, useEffect } from 'react';
import { authenticatedFetch } from '../../utils/auth';

export default function WearableSync({ wearableData, onSync }) {
  const [syncing, setSyncing] = useState(false);
  const [connectedDevices, setConnectedDevices] = useState([]);
  const [showConnectModal, setShowConnectModal] = useState(false);

  useEffect(() => {
    if (wearableData?.devices) {
      setConnectedDevices(wearableData.devices);
    }
  }, [wearableData]);

  const handleSync = async (deviceId) => {
    setSyncing(true);
    try {
      const response = await authenticatedFetch('/api/health/wearable/sync', {
        method: 'POST',
        body: JSON.stringify({ deviceId })
      });

      if (response.ok) {
        await onSync();
        alert('✓ Device synced successfully!');
      } else {
        alert('Failed to sync device. Please try again.');
      }
    } catch (error) {
      console.error('Sync error:', error);
      alert('Failed to sync device. Please try again.');
    } finally {
      setSyncing(false);
    }
  };

  const handleConnect = async (deviceType) => {
    try {
      const response = await authenticatedFetch('/api/health/wearable/connect', {
        method: 'POST',
        body: JSON.stringify({ deviceType })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.authUrl) {
          // Redirect to OAuth authorization
          window.location.href = data.authUrl;
        }
      } else {
        alert('Failed to initiate connection. Please try again.');
      }
    } catch (error) {
      console.error('Connection error:', error);
      alert('Failed to initiate connection. Please try again.');
    }
  };

  const handleDisconnect = async (deviceId) => {
    if (!confirm('Are you sure you want to disconnect this device?')) return;

    try {
      const response = await authenticatedFetch(`/api/health/wearable/${deviceId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        await onSync();
        alert('✓ Device disconnected successfully!');
      } else {
        alert('Failed to disconnect device. Please try again.');
      }
    } catch (error) {
      console.error('Disconnect error:', error);
      alert('Failed to disconnect device. Please try again.');
    }
  };

  const supportedDevices = [
    {
      id: 'apple-watch',
      name: 'Apple Watch',
      icon: '⌚',
      description: 'Connect your Apple Watch via Apple Health',
      capabilities: ['Heart Rate', 'Steps', 'Sleep', 'Activity', 'Workouts', 'ECG']
    },
    {
      id: 'fitbit',
      name: 'Fitbit',
      icon: '📱',
      description: 'Connect your Fitbit device',
      capabilities: ['Heart Rate', 'Steps', 'Sleep', 'Activity', 'SpO2']
    },
    {
      id: 'garmin',
      name: 'Garmin',
      icon: '⌚',
      description: 'Connect your Garmin device',
      capabilities: ['Heart Rate', 'Steps', 'Sleep', 'Activity', 'Stress', 'Body Battery']
    },
    {
      id: 'samsung-health',
      name: 'Samsung Health',
      icon: '📱',
      description: 'Connect Samsung Health app',
      capabilities: ['Heart Rate', 'Steps', 'Sleep', 'Activity', 'Blood Pressure']
    },
    {
      id: 'google-fit',
      name: 'Google Fit',
      icon: '💪',
      description: 'Connect Google Fit',
      capabilities: ['Heart Rate', 'Steps', 'Activity', 'Weight']
    },
    {
      id: 'whoop',
      name: 'WHOOP',
      icon: '🏃',
      description: 'Connect your WHOOP strap',
      capabilities: ['Heart Rate', 'HRV', 'Sleep', 'Strain', 'Recovery']
    }
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2 style={{ margin: 0, color: '#2d3748', fontSize: '1.75rem' }}>
            ⌚ Wearable Devices
          </h2>
          <p style={{ margin: '0.5rem 0 0 0', color: '#718096' }}>
            Connect your fitness trackers and smartwatches
          </p>
        </div>
        <button
          onClick={() => setShowConnectModal(true)}
          style={{
            padding: '0.75rem 1.5rem',
            background: '#48bb78',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          ➕ Connect Device
        </button>
      </div>

      {/* Connected Devices */}
      {connectedDevices.length > 0 && (
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ color: '#2d3748', marginBottom: '1rem' }}>
            Connected Devices ({connectedDevices.length})
          </h3>
          <div style={{ display: 'grid', gap: '1rem' }}>
            {connectedDevices.map((device) => (
              <div key={device.id} style={{
                border: '2px solid #e2e8f0',
                borderRadius: '8px',
                padding: '1.5rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '2rem' }}>
                      {supportedDevices.find(d => d.id === device.type)?.icon || '⌚'}
                    </span>
                    <div>
                      <h4 style={{ margin: 0, color: '#2d3748' }}>
                        {device.name}
                      </h4>
                      <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#718096' }}>
                        Last synced: {device.lastSync ? new Date(device.lastSync).toLocaleString() : 'Never'}
                      </p>
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.75rem' }}>
                    {device.capabilities?.map((cap, idx) => (
                      <span key={idx} style={{
                        padding: '0.25rem 0.75rem',
                        background: '#edf2f7',
                        borderRadius: '12px',
                        fontSize: '0.75rem',
                        color: '#4a5568'
                      }}>
                        {cap}
                      </span>
                    ))}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    onClick={() => handleSync(device.id)}
                    disabled={syncing}
                    style={{
                      padding: '0.5rem 1rem',
                      background: syncing ? '#cbd5e0' : '#667eea',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: syncing ? 'not-allowed' : 'pointer',
                      fontWeight: '600'
                    }}
                  >
                    {syncing ? '⏳ Syncing...' : '🔄 Sync'}
                  </button>
                  <button
                    onClick={() => handleDisconnect(device.id)}
                    style={{
                      padding: '0.5rem 1rem',
                      background: 'white',
                      color: '#e53e3e',
                      border: '2px solid #e53e3e',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontWeight: '600'
                    }}
                  >
                    Disconnect
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Available Devices */}
      <div>
        <h3 style={{ color: '#2d3748', marginBottom: '1rem' }}>
          Supported Devices
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
          {supportedDevices.map((device) => {
            const isConnected = connectedDevices.some(d => d.type === device.id);
            return (
              <div key={device.id} style={{
                border: '2px solid #e2e8f0',
                borderRadius: '8px',
                padding: '1.5rem',
                opacity: isConnected ? 0.5 : 1
              }}>
                <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>
                  {device.icon}
                </div>
                <h4 style={{ margin: '0 0 0.5rem 0', color: '#2d3748' }}>
                  {device.name}
                </h4>
                <p style={{ margin: '0 0 1rem 0', fontSize: '0.875rem', color: '#718096' }}>
                  {device.description}
                </p>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
                  {device.capabilities.map((cap, idx) => (
                    <span key={idx} style={{
                      padding: '0.25rem 0.5rem',
                      background: '#edf2f7',
                      borderRadius: '10px',
                      fontSize: '0.75rem',
                      color: '#4a5568'
                    }}>
                      {cap}
                    </span>
                  ))}
                </div>
                {isConnected ? (
                  <div style={{
                    padding: '0.5rem',
                    background: '#c6f6d5',
                    color: '#22543d',
                    borderRadius: '6px',
                    textAlign: 'center',
                    fontSize: '0.875rem',
                    fontWeight: '600'
                  }}>
                    ✓ Connected
                  </div>
                ) : (
                  <button
                    onClick={() => handleConnect(device.id)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      background: '#667eea',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontWeight: '600'
                    }}
                  >
                    Connect
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Info Box */}
      <div style={{
        marginTop: '2rem',
        padding: '1.5rem',
        background: '#ebf8ff',
        border: '2px solid #90cdf4',
        borderRadius: '8px'
      }}>
        <h4 style={{ margin: '0 0 0.5rem 0', color: '#2c5282' }}>
          ℹ️ About Wearable Integration
        </h4>
        <p style={{ margin: 0, fontSize: '0.875rem', color: '#2d3748', lineHeight: '1.6' }}>
          Your wearable data is securely synced and encrypted. We use official APIs from device manufacturers 
          to access your health metrics. You can disconnect any device at any time, and your data will be 
          permanently deleted from our servers.
        </p>
      </div>
    </div>
  );
}
