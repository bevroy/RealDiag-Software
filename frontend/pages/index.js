import Link from 'next/link';
import { useEffect, useState } from 'react';
import RoleBasedNavigation from '../components/RoleBasedNavigation';

export default function Home() {
  const [treeCount, setTreeCount] = useState(null);

  useEffect(() => {
    async function loadTreeCount() {
      try {
        const runtimeConfig = (typeof window !== 'undefined' && window.__RUNTIME_CONFIG) ? window.__RUNTIME_CONFIG : null;
        const apiBase = runtimeConfig?.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com';
        
        const treesRes = await fetch(`${apiBase}/diagnostic/trees`);
        if (treesRes.ok) {
          const treesData = await treesRes.json();
          if (treesData.trees) {
            setTreeCount(treesData.trees.length);
          }
        }
      } catch (err) {
        console.error('Failed to load tree count:', err);
      }
    }
    loadTreeCount();
    
    // Also try to load user data if not in localStorage
    const userStr = localStorage.getItem('realdiag_user');
    if (!userStr) {
      console.log('⚠️ Index: No localStorage user, will be fetched by RoleBasedNavigation component');
    } else {
      console.log('✅ Index: User in localStorage:', JSON.parse(userStr));
    }
  }, []);

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f0fdfa 0%, #e7f5f3 100%)',
      padding: '2rem'
    }}>
      {/* Navigation Dropdown */}
      <RoleBasedNavigation />

      {/* Main Content */}
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Demo Section */}
        <div style={{
          background: 'white',
          padding: '3rem 2rem',
          borderRadius: '16px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          marginBottom: '3rem',
          border: '1px solid rgba(20, 184, 166, 0.1)',
          textAlign: 'center'
        }}>
          <h2 style={{
            margin: '0 0 1rem',
            fontSize: '1.75rem',
            color: '#0f766e',
            fontWeight: '600'
          }}>
            🎬 See RealDiag in Action
          </h2>
          <p style={{
            margin: '0 0 2rem',
            color: '#64748b',
            fontSize: '1.05rem',
            maxWidth: '600px',
            marginLeft: 'auto',
            marginRight: 'auto',
            lineHeight: '1.6'
          }}>
            Walk through an interactive clinical scenario showing how RealDiag generates a ranked differential, recommends workup, and flags red flags in real time.
          </p>
          <Link href="/demo">
            <a style={{
              display: 'inline-block',
              padding: '1rem 2.5rem',
              background: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
              color: 'white',
              borderRadius: '10px',
              textDecoration: 'none',
              fontSize: '1.1rem',
              fontWeight: '600',
              boxShadow: '0 4px 12px rgba(20, 184, 166, 0.25)',
              transition: 'all 0.3s'
            }}>
              ▶ Launch Interactive Demo
            </a>
          </Link>
        </div>

        {/* Call to Action */}
        <div style={{
          background: 'white',
          padding: '3rem 2rem',
          borderRadius: '16px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          marginBottom: '3rem',
          textAlign: 'center',
          border: '1px solid rgba(20, 184, 166, 0.1)'
        }}>
          <h2 style={{ 
            margin: '0 0 1rem', 
            fontSize: '1.75rem', 
            color: '#0f766e',
            fontWeight: '600'
          }}>
            Start Diagnostic Search
          </h2>
          <p style={{ 
            margin: '0 0 2rem', 
            fontSize: '1.05rem', 
            color: '#64748b',
            maxWidth: '550px',
            marginLeft: 'auto',
            marginRight: 'auto',
            lineHeight: '1.6'
          }}>
            Enter symptoms to get evidence-based diagnostic suggestions with clinical pearls and management protocols.
          </p>
          <Link href="/symptom-search">
            <a style={{
              display: 'inline-block',
              padding: '1rem 2.5rem',
              background: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
              color: 'white',
              borderRadius: '10px',
              textDecoration: 'none',
              fontSize: '1.1rem',
              fontWeight: '600',
              boxShadow: '0 4px 12px rgba(20, 184, 166, 0.25)',
              transition: 'all 0.3s'
            }}>
              🔍 Search Symptoms
            </a>
          </Link>
        </div>

        {/* Features List */}
        <div style={{
          background: 'white',
          padding: '2rem 2.5rem',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          border: '1px solid #e2e8f0',
          marginBottom: '3rem'
        }}>
          <h3 style={{ 
            margin: '0 0 1.5rem', 
            color: '#0f766e', 
            fontSize: '1.3rem',
            fontWeight: '600',
            textAlign: 'center'
          }}>
            Key Features
          </h3>
          <ul style={{
            listStyle: 'none',
            padding: 0,
            margin: 0,
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '1rem',
            color: '#64748b',
            fontSize: '1rem',
            lineHeight: '1.6'
          }}>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
              <span style={{ fontSize: '1.5rem', flexShrink: 0 }}>🎯</span>
              <span><strong style={{ color: '#0f766e' }}>Evidence-Based:</strong> Differential diagnoses ranked by Bayesian likelihood with sensitivity and specificity data</span>
            </li>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
              <span style={{ fontSize: '1.5rem', flexShrink: 0 }}>📚</span>
              <span><strong style={{ color: '#0f766e' }}>Clinical Pearls:</strong> Detailed clinical pearls, management protocols, and evidence-based guidelines</span>
            </li>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
              <span style={{ fontSize: '1.5rem', flexShrink: 0 }}>🏥</span>
              <span><strong style={{ color: '#0f766e' }}>24+ Specialties:</strong> Cardiology, neurology, emergency medicine, orthopedics, pediatrics, and many more medical specialties</span>
            </li>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
              <span style={{ fontSize: '1.5rem', flexShrink: 0 }}>🔬</span>
              <span><strong style={{ color: '#0f766e' }}>Test Recommendations:</strong> Suggested diagnostic tests and specialist referrals for each diagnosis</span>
            </li>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
              <span style={{ fontSize: '1.5rem', flexShrink: 0 }}>📖</span>
              <span><strong style={{ color: '#0f766e' }}>Medical Training:</strong> Case library, quizzes, flashcards, and progress tracking for students</span>
            </li>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
              <span style={{ fontSize: '1.5rem', flexShrink: 0 }}>⚡</span>
              <span><strong style={{ color: '#0f766e' }}>Fast & Accurate:</strong> Instant results powered by advanced algorithms and diagnostic rules</span>
            </li>
          </ul>
        </div>

      </div>

      {/* Medical Disclaimer at Bottom */}
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{
          margin: '0 0 2rem',
          padding: '1rem 1.5rem',
          background: 'linear-gradient(135deg, #0f766e 0%, #0d9488 100%)',
          borderRadius: '10px',
          color: 'white',
          textAlign: 'center',
          boxShadow: '0 2px 8px rgba(15, 118, 110, 0.2)',
          border: '1px solid rgba(204, 251, 241, 0.3)'
        }}>
          <strong style={{ fontSize: '0.95rem' }}>⚠️ MEDICAL DISCLAIMER: NOT FOR CLINICAL USE</strong>
          <p style={{ margin: '0.5rem 0 0', fontSize: '0.85rem', opacity: 0.95 }}>
            Educational purposes only. Not FDA-approved. Not a substitute for professional medical judgment.
            See <Link href="/legal-disclaimer" style={{ color: '#ccfbf1', textDecoration: 'underline' }}>Legal Disclaimer</Link> for complete terms.
          </p>
        </div>
      </div>

      {/* Footer */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        textAlign: 'center',
        color: '#94a3b8',
        fontSize: '0.85rem',
        paddingBottom: '2rem'
      }}>
        <p style={{ margin: 0 }}>RealDiag Clinical Decision Support • Evidence-based diagnostics • For educational purposes</p>
      </div>
    </div>
  );
}

