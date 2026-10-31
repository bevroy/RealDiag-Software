'use client';

import Link from 'next/link';

// Accounts are invite-only (backend/services/access_policy.py): POST
// /users/register is refused, so this page explains how to get access.
export default function RegisterPage() {
  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Accounts are by invitation</h1>
        <p style={styles.text}>
          RealDiag accounts are created by an administrator. If you were invited, open the setup link in your
          invitation email to choose a password. Otherwise, ask your RealDiag administrator for an invite.
        </p>
        <p style={styles.text}>
          <Link href="/login" style={styles.link}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)', padding: '1rem' },
  card: { background: 'white', borderRadius: '12px', padding: '2rem', maxWidth: '480px', width: '100%', boxShadow: '0 10px 25px rgba(0,0,0,0.1)' },
  title: { margin: '0 0 1rem', color: '#0f766e', fontSize: '1.5rem' },
  text: { color: '#374151', lineHeight: 1.6 },
  link: { color: '#0d9488', fontWeight: 600 },
};
