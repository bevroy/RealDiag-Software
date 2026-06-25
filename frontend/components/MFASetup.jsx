import { useState } from 'react';
import { getCSRFToken } from '../utils/auth';

/**
 * MFA Setup Component
 * 
 * Allows users to enroll in two-factor authentication using TOTP.
 * Compatible with Google Authenticator, Authy, Microsoft Authenticator, etc.
 */
export default function MFASetup({ apiBase, onComplete }) {
  const [step, setStep] = useState('initial'); // initial, enrolled, verify, complete
  const [secret, setSecret] = useState('');
  const [qrCode, setQrCode] = useState('');
  const [backupCodes, setBackupCodes] = useState([]);
  const [token, setToken] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const enrollMFA = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${apiBase}/mfa/enroll`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': getCSRFToken()
        }
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to enroll in MFA');
      }

      const data = await response.json();
      setSecret(data.secret);
      setQrCode(data.qr_code);
      setBackupCodes(data.backup_codes);
      setStep('enrolled');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

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
        setStep('complete');
        if (onComplete) onComplete();
      } else {
        setError('Invalid token. Please try again.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadBackupCodes = () => {
    const text = `RealDiag MFA Backup Codes
Generated: ${new Date().toLocaleString()}

IMPORTANT: Save these codes in a secure location.
Each code can only be used once for account recovery.

${backupCodes.join('\n')}

Do not share these codes with anyone.
`;

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'realdiag-backup-codes.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{
      maxWidth: '600px',
      margin: '0 auto',
      padding: '2rem',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <h2 style={{ marginBottom: '1.5rem' }}>Two-Factor Authentication Setup</h2>

      {error && (
        <div style={{
          padding: '1rem',
          marginBottom: '1rem',
          background: '#fee',
          border: '1px solid #fcc',
          borderRadius: '4px',
          color: '#c00'
        }}>
          {error}
        </div>
      )}

      {/* Initial Step */}
      {step === 'initial' && (
        <div>
          <p style={{ marginBottom: '1.5rem', lineHeight: '1.6' }}>
            Enable two-factor authentication to add an extra layer of security to your account.
            You'll need an authenticator app like:
          </p>
          <ul style={{ marginBottom: '1.5rem', lineHeight: '1.8' }}>
            <li>Google Authenticator</li>
            <li>Microsoft Authenticator</li>
            <li>Authy</li>
            <li>1Password</li>
          </ul>
          <button
            onClick={enrollMFA}
            disabled={loading}
            style={{
              padding: '0.75rem 1.5rem',
              background: '#0f766e',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.6 : 1
            }}
          >
            {loading ? 'Setting up...' : 'Begin Setup'}
          </button>
        </div>
      )}

      {/* Enrolled - Scan QR Code */}
      {step === 'enrolled' && (
        <div>
          <h3 style={{ marginBottom: '1rem' }}>Step 1: Scan QR Code</h3>
          <p style={{ marginBottom: '1rem', lineHeight: '1.6' }}>
            Open your authenticator app and scan this QR code:
          </p>
          
          <div style={{
            textAlign: 'center',
            marginBottom: '1.5rem',
            padding: '1rem',
            background: 'white',
            border: '1px solid #ddd',
            borderRadius: '8px'
          }}>
            <img src={qrCode} alt="MFA QR Code" style={{ maxWidth: '300px' }} />
          </div>

          <div style={{
            padding: '1rem',
            background: '#f0f9ff',
            border: '1px solid #bae6fd',
            borderRadius: '6px',
            marginBottom: '1.5rem'
          }}>
            <p style={{ margin: 0, fontSize: '0.9rem', lineHeight: '1.6' }}>
              <strong>Can't scan?</strong> Manually enter this secret key:<br/>
              <code style={{
                display: 'inline-block',
                marginTop: '0.5rem',
                padding: '0.5rem',
                background: 'white',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '0.9rem',
                wordBreak: 'break-all'
              }}>
                {secret}
              </code>
            </p>
          </div>

          <h3 style={{ marginBottom: '1rem' }}>Step 2: Save Backup Codes</h3>
          <p style={{ marginBottom: '1rem', lineHeight: '1.6' }}>
            Save these backup codes in a secure location. You'll need them if you lose access to your authenticator app.
          </p>

          <div style={{
            padding: '1rem',
            background: '#fef3c7',
            border: '2px solid #f59e0b',
            borderRadius: '6px',
            marginBottom: '1rem'
          }}>
            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '0.5rem',
              fontFamily: 'monospace',
              fontSize: '0.9rem'
            }}>
              {backupCodes.map((code, i) => (
                <div key={i}>{code}</div>
              ))}
            </div>
          </div>

          <button
            onClick={downloadBackupCodes}
            style={{
              padding: '0.5rem 1rem',
              background: 'white',
              border: '1px solid #ddd',
              borderRadius: '4px',
              marginBottom: '1.5rem',
              cursor: 'pointer'
            }}
          >
            📥 Download Backup Codes
          </button>

          <h3 style={{ marginBottom: '1rem' }}>Step 3: Verify Setup</h3>
          <p style={{ marginBottom: '1rem', lineHeight: '1.6' }}>
            Enter the 6-digit code from your authenticator app to verify setup:
          </p>

          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
            <input
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              maxLength={6}
              value={token}
              onChange={(e) => setToken(e.target.value.replace(/\D/g, ''))}
              placeholder="000000"
              style={{
                flex: 1,
                padding: '0.75rem',
                fontSize: '1.5rem',
                letterSpacing: '0.5rem',
                textAlign: 'center',
                border: '2px solid #ddd',
                borderRadius: '6px',
                fontFamily: 'monospace'
              }}
            />
            <button
              onClick={verifyToken}
              disabled={loading || token.length !== 6}
              style={{
                padding: '0.75rem 1.5rem',
                background: '#0f766e',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: (loading || token.length !== 6) ? 'not-allowed' : 'pointer',
                opacity: (loading || token.length !== 6) ? 0.6 : 1
              }}
            >
              Verify
            </button>
          </div>
        </div>
      )}

      {/* Complete */}
      {step === 'complete' && (
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '80px',
            height: '80px',
            margin: '0 auto 1rem',
            background: '#d1fae5',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '3rem'
          }}>
            ✓
          </div>
          <h3 style={{ color: '#059669', marginBottom: '0.5rem' }}>MFA Enabled!</h3>
          <p style={{ color: '#666', marginBottom: '2rem' }}>
            Two-factor authentication is now active on your account.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '0.75rem 1.5rem',
              background: '#0f766e',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            Done
          </button>
        </div>
      )}
    </div>
  );
}
