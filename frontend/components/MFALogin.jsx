import { useState } from 'react';
import { getCSRFToken } from '../utils/auth';

/**
 * MFA Login Component
 * 
 * Prompts for TOTP token after successful password authentication.
 * Supports both TOTP tokens and backup codes.
 */
export default function MFALogin({ apiBase, onSuccess, onCancel }) {
  const [token, setToken] = useState('');
  const [useBackupCode, setUseBackupCode] = useState(false);
  const [backupCode, setBackupCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const verifyToken = async () => {
    if (token.length !== 6) {
      setError('Token must be 6 digits');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${apiBase}/mfa/verify`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': getCSRFToken()
        },
        body: JSON.stringify({ token })
      });

      const data = await response.json();

      if (data.valid) {
        if (onSuccess) onSuccess();
      } else {
        setError('Invalid token. Please try again.');
      }
    } catch (err) {
      setError(err.message || 'Failed to verify token');
    } finally {
      setLoading(false);
    }
  };

  const verifyBackupCode = async () => {
    if (backupCode.length < 8) {
      setError('Backup code must be at least 8 characters');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${apiBase}/mfa/verify-backup`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': getCSRFToken()
        },
        body: JSON.stringify({ backup_code: backupCode })
      });

      const data = await response.json();

      if (data.valid) {
        if (onSuccess) onSuccess();
      } else {
        setError('Invalid backup code. Please try again.');
      }
    } catch (err) {
      setError(err.message || 'Failed to verify backup code');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      if (useBackupCode) {
        verifyBackupCode();
      } else {
        verifyToken();
      }
    }
  };

  return (
    <div style={{
      maxWidth: '400px',
      margin: '0 auto',
      padding: '2rem',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <h2 style={{ marginBottom: '0.5rem' }}>Two-Factor Authentication</h2>
      <p style={{ color: '#666', marginBottom: '2rem', fontSize: '0.9rem' }}>
        Enter the code from your authenticator app
      </p>

      {error && (
        <div style={{
          padding: '1rem',
          marginBottom: '1rem',
          background: '#fee',
          border: '1px solid #fcc',
          borderRadius: '4px',
          color: '#c00',
          fontSize: '0.9rem'
        }}>
          {error}
        </div>
      )}

      {!useBackupCode ? (
        <>
          <input
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={6}
            value={token}
            onChange={(e) => setToken(e.target.value.replace(/\D/g, ''))}
            onKeyPress={handleKeyPress}
            placeholder="000000"
            autoFocus
            style={{
              width: '100%',
              padding: '1rem',
              fontSize: '2rem',
              letterSpacing: '0.8rem',
              textAlign: 'center',
              border: '2px solid #ddd',
              borderRadius: '8px',
              marginBottom: '1rem',
              fontFamily: 'monospace',
              boxSizing: 'border-box'
            }}
          />

          <button
            onClick={verifyToken}
            disabled={loading || token.length !== 6}
            style={{
              width: '100%',
              padding: '1rem',
              background: '#0f766e',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: (loading || token.length !== 6) ? 'not-allowed' : 'pointer',
              opacity: (loading || token.length !== 6) ? 0.6 : 1,
              marginBottom: '1rem'
            }}
          >
            {loading ? 'Verifying...' : 'Verify'}
          </button>
        </>
      ) : (
        <>
          <input
            type="text"
            value={backupCode}
            onChange={(e) => setBackupCode(e.target.value.toUpperCase())}
            onKeyPress={handleKeyPress}
            placeholder="XXXX-XXXX"
            autoFocus
            style={{
              width: '100%',
              padding: '1rem',
              fontSize: '1.2rem',
              letterSpacing: '0.1rem',
              textAlign: 'center',
              border: '2px solid #ddd',
              borderRadius: '8px',
              marginBottom: '1rem',
              fontFamily: 'monospace',
              boxSizing: 'border-box'
            }}
          />

          <button
            onClick={verifyBackupCode}
            disabled={loading || backupCode.length < 8}
            style={{
              width: '100%',
              padding: '1rem',
              background: '#0f766e',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: (loading || backupCode.length < 8) ? 'not-allowed' : 'pointer',
              opacity: (loading || backupCode.length < 8) ? 0.6 : 1,
              marginBottom: '1rem'
            }}
          >
            {loading ? 'Verifying...' : 'Verify Backup Code'}
          </button>
        </>
      )}

      <div style={{ textAlign: 'center' }}>
        <button
          onClick={() => {
            setUseBackupCode(!useBackupCode);
            setToken('');
            setBackupCode('');
            setError('');
          }}
          style={{
            background: 'none',
            border: 'none',
            color: '#0f766e',
            fontSize: '0.9rem',
            cursor: 'pointer',
            textDecoration: 'underline',
            marginBottom: '0.5rem'
          }}
        >
          {useBackupCode ? 'Use authenticator code' : 'Use backup code'}
        </button>
      </div>

      {onCancel && (
        <div style={{ textAlign: 'center' }}>
          <button
            onClick={onCancel}
            style={{
              background: 'none',
              border: 'none',
              color: '#999',
              fontSize: '0.9rem',
              cursor: 'pointer',
              textDecoration: 'underline'
            }}
          >
            Cancel
          </button>
        </div>
      )}

      <div style={{
        marginTop: '2rem',
        padding: '1rem',
        background: '#f0f9ff',
        border: '1px solid #bae6fd',
        borderRadius: '6px',
        fontSize: '0.85rem',
        color: '#0c4a6e'
      }}>
        <strong>Lost your device?</strong><br/>
        Use a backup code to access your account. If you've lost both your device and backup codes, contact support.
      </div>
    </div>
  );
}
