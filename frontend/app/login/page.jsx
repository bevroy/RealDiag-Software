'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

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
      const response = await fetch('https://realdiag-backend.onrender.com/users/login', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      // Login successful - store user data and token
      if (data.csrf_token) {
        sessionStorage.setItem('csrf_token', data.csrf_token);
      }
      
      // Store user data for cross-domain authentication
      if (data.user) {
        localStorage.setItem('realdiag_user', JSON.stringify(data.user));
        localStorage.setItem('realdiag_authenticated', 'true');
      }

      // Show success message
      alert(`Welcome back, ${data.user?.full_name || data.user?.email}!`);
      
      // Redirect to main site
      window.location.href = 'https://realdiag.netlify.app/';
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

        <p style={{ textAlign: 'center', marginTop: '1rem' }}>
          <Link href="/forgot-password" style={styles.link}>
            Forgot your password?
          </Link>
        </p>

        <p style={styles.footer}>
          Don't have an account?{' '}
          <Link href="/register" style={styles.link}>
            Create one
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
