'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { storeAuthData } from '../../utils/clientAuth';
import { apiFetch } from '../../utils/apiClient';
import { loginNextStep, mfaVerifyBody } from '../../utils/loginFlow';
import MFASetup from '../../components/MFASetup';

export default function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  // Two-factor step after the password: 'password' | 'code' | 'setup'.
  const [stage, setStage] = useState('password');
  const [mfaToken, setMfaToken] = useState('');
  const [code, setCode] = useState('');
  const [useBackupCode, setUseBackupCode] = useState(false);

  // Signed in with MFA: store the user and go to the app.
  const finish = (user, csrfToken) => {
    if (csrfToken) sessionStorage.setItem('csrf_token', csrfToken);
    if (user) storeAuthData(user, csrfToken || null);
    alert(`Welcome back, ${user?.full_name || user?.email}!`);
    // Stay on this site: the login cookie and stored user belong to this origin
    window.location.href = '/';
  };

  const finishFromSession = async () => {
    const me = await apiFetch('/users/me');
    if (!me.ok) throw new Error('Signed in, but your profile could not be loaded. Please sign in again.');
    finish(await me.json(), null);
  };

  const handleCode = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await apiFetch('/mfa/login-verify', {
        method: 'POST',
        body: JSON.stringify(mfaVerifyBody(mfaToken, code, useBackupCode)),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Code not accepted');
      await finishFromSession();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError(''); // Clear error when user types
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await apiFetch('/users/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      // Password accepted; two-factor authentication comes next.
      const next = loginNextStep(data);
      if (next === 'code') {
        setMfaToken(data.mfa_token);
        setStage('code');
      } else if (next === 'setup') {
        setStage('setup');
      } else {
        finish(data.user, data.csrf_token);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        {/* Logo and Branding */}
        <div style={styles.header}>
          <img 
            src="/logo.png" 
            alt="RealDiag Logo" 
            style={styles.logo}
          />
          <h1 style={styles.title}>RealDiag, LLC</h1>
          <p style={styles.tagline}>
            <em>AI-Powered</em><br />Real-Time Diagnostic Assistant
          </p>
        </div>

        <div style={styles.divider}></div>

        <h2 style={styles.welcomeTitle}>Welcome Back</h2>
        <p style={styles.subtitle}>Sign in to your account</p>

        {error && (
          <div style={styles.error}>
            {error}
          </div>
        )}

        {stage === 'code' && (
          <form onSubmit={handleCode} style={styles.form}>
            <div style={styles.formGroup}>
              <label style={styles.label}>{useBackupCode ? 'Backup code' : 'Code from your authenticator app'}</label>
              <input
                name="code"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                required
                autoFocus
                autoComplete="one-time-code"
                inputMode={useBackupCode ? 'text' : 'numeric'}
                style={styles.input}
                placeholder={useBackupCode ? 'Backup code' : '6-digit code'}
              />
            </div>
            <button type="submit" disabled={loading} style={{ ...styles.button, ...(loading ? styles.buttonDisabled : {}) }}>
              {loading ? 'Checking...' : 'Verify'}
            </button>
            <p style={{ textAlign: 'center', marginTop: '1rem' }}>
              <button type="button" style={{ ...styles.link, background: 'none', border: 'none', cursor: 'pointer' }}
                onClick={() => { setUseBackupCode(!useBackupCode); setCode(''); }}>
                {useBackupCode ? 'Use a code from the app instead' : 'Use a backup code instead'}
              </button>
            </p>
          </form>
        )}

        {stage === 'setup' && (
          <div>
            <p style={styles.subtitle}>
              Two-factor authentication is required for every RealDiag account. Set it up with an authenticator app
              to continue.
            </p>
            <MFASetup onComplete={() => finishFromSession().catch((err) => setError(err.message))} />
          </div>
        )}

        {stage === 'password' && (
        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.formGroup}>
            <label style={styles.label}>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              style={styles.input}
              placeholder="your.email@hospital.com"
              onFocus={(e) => e.target.style.borderColor = '#0f766e'}
              onBlur={(e) => e.target.style.borderColor = '#ccfbf1'}
            />
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              style={styles.input}
              placeholder="Enter your password"
              onFocus={(e) => e.target.style.borderColor = '#0f766e'}
              onBlur={(e) => e.target.style.borderColor = '#ccfbf1'}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              ...styles.button,
              ...(loading ? styles.buttonDisabled : {})
            }}
            onMouseEnter={(e) => !loading && (e.target.style.background = '#115e59')}
            onMouseLeave={(e) => !loading && (e.target.style.background = '#0f766e')}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        )}

        <p style={{ textAlign: 'center', marginTop: '1rem' }}>
          <Link href="/forgot-password" style={styles.link}>
            Forgot your password?
          </Link>
        </p>

        <p style={styles.footer}>
          Accounts are by invitation. Ask your RealDiag administrator for an invite.
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #f0fdfa 0%, #e7f5f3 100%)',
    padding: '20px'
  },
  card: {
    background: 'white',
    borderRadius: '16px',
    padding: '40px',
    maxWidth: '480px',
    width: '100%',
    boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
    border: '1px solid #ccfbf1'
  },
  header: {
    textAlign: 'center',
    marginBottom: '24px'
  },
  logo: {
    height: '100px',
    width: 'auto',
    marginBottom: '16px'
  },
  title: {
    fontSize: '2rem',
    fontWeight: '700',
    color: '#78350f',
    margin: '0 0 8px 0',
    letterSpacing: '-0.02em'
  },
  tagline: {
    color: '#64748b',
    fontSize: '1rem',
    fontWeight: '500',
    lineHeight: '1.6',
    margin: '0'
  },
  divider: {
    height: '1px',
    background: 'linear-gradient(to right, transparent, #ccfbf1, transparent)',
    margin: '24px 0'
  },
  welcomeTitle: {
    fontSize: '24px',
    fontWeight: '700',
    color: '#0f766e',
    marginBottom: '8px',
    textAlign: 'center'
  },
  subtitle: {
    color: '#64748b',
    textAlign: 'center',
    marginBottom: '32px',
    fontSize: '14px'
  },
  error: {
    background: '#fee2e2',
    color: '#991b1b',
    padding: '12px',
    borderRadius: '8px',
    marginBottom: '20px',
    fontSize: '14px',
    border: '1px solid #fecaca'
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px'
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  label: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#0f766e'
  },
  input: {
    padding: '12px',
    fontSize: '16px',
    border: '2px solid #ccfbf1',
    borderRadius: '8px',
    outline: 'none',
    transition: 'border-color 0.2s',
    fontFamily: 'inherit',
    backgroundColor: '#f0fdfa'
  },
  button: {
    padding: '14px',
    fontSize: '16px',
    fontWeight: '600',
    color: 'white',
    background: '#0f766e',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    marginTop: '8px',
    transition: 'all 0.2s',
    boxShadow: '0 2px 8px rgba(15, 118, 110, 0.3)'
  },
  buttonDisabled: {
    opacity: 0.6,
    cursor: 'not-allowed'
  },
  footer: {
    textAlign: 'center',
    marginTop: '24px',
    color: '#64748b',
    fontSize: '14px'
  },
  link: {
    color: '#0f766e',
    fontWeight: '600',
    textDecoration: 'none'
  }
};
