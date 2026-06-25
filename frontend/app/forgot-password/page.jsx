'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);

    try {
      const response = await fetch(
        'https://realdiag-backend.onrender.com/users/forgot-password',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to send reset email.');
      }

      setMessage(
        data.message ||
          'If an account exists for that email, a password reset link has been sent.'
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Forgot your password?</h1>
        <p style={styles.subtitle}>
          Enter the email address associated with your RealDiag account and
          we'll send you a link to reset your password.
        </p>

        {message && <div style={styles.success}>{message}</div>}
        {error && <div style={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div style={styles.formGroup}>
            <label style={styles.label}>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={styles.input}
              placeholder="your.email@hospital.com"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{ ...styles.button, ...(loading ? styles.buttonDisabled : {}) }}
          >
            {loading ? 'Sending...' : 'Send reset link'}
          </button>
        </form>

        <p style={styles.footer}>
          Remembered your password?{' '}
          <Link href="/login" style={styles.link}>
            Back to sign in
          </Link>
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
    background: 'linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%)',
    padding: '2rem',
  },
  card: {
    background: '#fff',
    padding: '2.5rem',
    borderRadius: '12px',
    boxShadow: '0 10px 30px rgba(15, 118, 110, 0.15)',
    maxWidth: '440px',
    width: '100%',
  },
  title: { color: '#0f766e', marginBottom: '0.5rem', fontSize: '1.75rem' },
  subtitle: { color: '#475569', marginBottom: '1.5rem', fontSize: '0.95rem', lineHeight: 1.5 },
  formGroup: { marginBottom: '1.25rem' },
  label: { display: 'block', marginBottom: '0.5rem', color: '#0f766e', fontWeight: 600 },
  input: {
    width: '100%',
    padding: '0.75rem 1rem',
    border: '2px solid #ccfbf1',
    borderRadius: '8px',
    fontSize: '1rem',
    boxSizing: 'border-box',
    outline: 'none',
  },
  button: {
    width: '100%',
    padding: '0.875rem',
    background: '#0f766e',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: 600,
    cursor: 'pointer',
  },
  buttonDisabled: { background: '#94a3b8', cursor: 'not-allowed' },
  footer: { textAlign: 'center', marginTop: '1.5rem', color: '#475569' },
  link: { color: '#0f766e', textDecoration: 'none', fontWeight: 600 },
  success: {
    background: '#ecfdf5',
    color: '#065f46',
    border: '1px solid #a7f3d0',
    padding: '0.75rem 1rem',
    borderRadius: '8px',
    marginBottom: '1rem',
    fontSize: '0.9rem',
  },
  error: {
    background: '#fef2f2',
    color: '#991b1b',
    border: '1px solid #fecaca',
    padding: '0.75rem 1rem',
    borderRadius: '8px',
    marginBottom: '1rem',
    fontSize: '0.9rem',
  },
};
