import Link from 'next/link';

export default function Home() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f0fdfa 0%, #e7f5f3 100%)',
      padding: '2rem'
    }}>
      {/* NEW UPDATE BANNER */}
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto 1rem',
        padding: '1rem 1.5rem',
        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        borderRadius: '12px',
        color: 'white',
        textAlign: 'center',
        boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)'
      }}>
        <strong>🎉 NEW: User Accounts & Comprehensive Clinical Guidelines!</strong>
        <p style={{ margin: '0.5rem 0 0', fontSize: '0.9rem', opacity: 0.95 }}>
          Create an account to save your search history, favorite diagnoses, and create custom differential lists! 140+ rules now include detailed clinical pearls, management protocols, tests, and referrals.
          Updated: November 17, 2025
        </p>
      </div>

      {/* Header */}
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto 2rem',
        textAlign: 'center',
        position: 'relative'
      }}>
        <div style={{ position: 'absolute', top: 0, right: 0 }}>
          <a href="/account" style={{
            display: 'inline-block',
            padding: '0.75rem 1.5rem',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            borderRadius: '8px',
            textDecoration: 'none',
            fontWeight: '600',
            boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)'
          }}>
            👤 Account
          </a>
        </div>
        <img 
          src="/logo.png" 
          alt="RealDiag Logo" 
          style={{ height: '120px', width: 'auto', marginBottom: '1rem' }}
        />
        <h1 style={{ margin: 0, fontSize: '3rem', color: '#0f766e', fontWeight: '700' }}>
          RealDiag
        </h1>
        <p style={{ margin: '0.5rem 0 0', color: '#78716c', fontSize: '1.25rem' }}>
          AI-Powered Clinical Diagnostic Search Engine
        </p>
        <p style={{ margin: '0.5rem 0 0', color: '#a8a29e', fontSize: '1rem' }}>
          268 diagnoses • 17 specialties • Evidence-based decision support
        </p>
      </div>

      {/* Main Content */}
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* Call to Action */}
        <div style={{
          background: 'white',
          padding: '3rem',
          borderRadius: '12px',
          boxShadow: '0 4px 20px rgba(20, 184, 166, 0.15)',
          marginBottom: '2rem',
          textAlign: 'center'
        }}>
          <h2 style={{ 
            margin: '0 0 1rem', 
            fontSize: '2rem', 
            color: '#0f766e',
            fontWeight: '600'
          }}>
            Start Your Diagnostic Search
          </h2>
          <p style={{ 
            margin: '0 0 2rem', 
            fontSize: '1.1rem', 
            color: '#78716c',
            maxWidth: '600px',
            marginLeft: 'auto',
            marginRight: 'auto'
          }}>
            Enter patient symptoms and get evidence-based diagnostic suggestions with clinical pearls, recommended tests, and management protocols.
          </p>
          <Link href="/symptom-search">
            <a style={{
              display: 'inline-block',
              padding: '1.25rem 3rem',
              background: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
              color: 'white',
              borderRadius: '12px',
              textDecoration: 'none',
              fontSize: '1.25rem',
              fontWeight: '700',
              boxShadow: '0 8px 24px rgba(20, 184, 166, 0.4)',
              transition: 'all 0.3s'
            }}>
              🔍 Search by Symptoms
            </a>
          </Link>
        </div>

        {/* Features Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2rem'
        }}>
          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '12px',
            boxShadow: '0 2px 12px rgba(0, 0, 0, 0.08)'
          }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🎯</div>
            <h3 style={{ margin: '0 0 0.75rem', color: '#0f766e', fontSize: '1.3rem' }}>
              Evidence-Based Results
            </h3>
            <p style={{ margin: 0, color: '#78716c', lineHeight: '1.6' }}>
              Get differential diagnoses ranked by Bayesian likelihood using sensitivity and specificity data.
            </p>
          </div>

          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '12px',
            boxShadow: '0 2px 12px rgba(0, 0, 0, 0.08)'
          }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>📚</div>
            <h3 style={{ margin: '0 0 0.75rem', color: '#0f766e', fontSize: '1.3rem' }}>
              Clinical Pearls
            </h3>
            <p style={{ margin: 0, color: '#78716c', lineHeight: '1.6' }}>
              Access detailed clinical pearls, management protocols, and evidence-based guidelines.
            </p>
          </div>

          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '12px',
            boxShadow: '0 2px 12px rgba(0, 0, 0, 0.08)'
          }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>💾</div>
            <h3 style={{ margin: '0 0 0.75rem', color: '#0f766e', fontSize: '1.3rem' }}>
              Save & Track
            </h3>
            <p style={{ margin: 0, color: '#78716c', lineHeight: '1.6' }}>
              Create an account to save your searches, favorite diagnoses, and build custom differential lists.
            </p>
          </div>

          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '12px',
            boxShadow: '0 2px 12px rgba(0, 0, 0, 0.08)'
          }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🏥</div>
            <h3 style={{ margin: '0 0 0.75rem', color: '#0f766e', fontSize: '1.3rem' }}>
              17 Specialties
            </h3>
            <p style={{ margin: 0, color: '#78716c', lineHeight: '1.6' }}>
              Coverage across cardiology, neurology, emergency medicine, and 14 other medical specialties.
            </p>
          </div>

          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '12px',
            boxShadow: '0 2px 12px rgba(0, 0, 0, 0.08)'
          }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🔬</div>
            <h3 style={{ margin: '0 0 0.75rem', color: '#0f766e', fontSize: '1.3rem' }}>
              Test Recommendations
            </h3>
            <p style={{ margin: 0, color: '#78716c', lineHeight: '1.6' }}>
              Get suggested diagnostic tests and specialist referrals for each potential diagnosis.
            </p>
          </div>

          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '12px',
            boxShadow: '0 2px 12px rgba(0, 0, 0, 0.08)'
          }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>⚡</div>
            <h3 style={{ margin: '0 0 0.75rem', color: '#0f766e', fontSize: '1.3rem' }}>
              Fast & Accurate
            </h3>
            <p style={{ margin: 0, color: '#78716c', lineHeight: '1.6' }}>
              Instant results powered by advanced algorithms and comprehensive diagnostic rules.
            </p>
          </div>
        </div>

        {/* Quick Links */}
        <div style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '12px',
          boxShadow: '0 2px 12px rgba(0, 0, 0, 0.08)',
          marginBottom: '2rem'
        }}>
          <h3 style={{ 
            margin: '0 0 1.5rem', 
            color: '#0f766e', 
            fontSize: '1.5rem',
            textAlign: 'center'
          }}>
            Explore More
          </h3>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem'
          }}>
            <a href="/rules" style={{
              padding: '1rem',
              background: 'linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%)',
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: '#0f766e',
              fontWeight: '600',
              transition: 'all 0.2s'
            }}>
              📋 Browse All Rules
            </a>
            <a href="/integration" style={{
              padding: '1rem',
              background: 'linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%)',
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: '#0f766e',
              fontWeight: '600',
              transition: 'all 0.2s'
            }}>
              🔌 API Integration
            </a>
            <a href="/features-demo" style={{
              padding: '1rem',
              background: 'linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%)',
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: '#0f766e',
              fontWeight: '600',
              transition: 'all 0.2s'
            }}>
              ✨ Features Demo
            </a>
            <a href="/account" style={{
              padding: '1rem',
              background: 'linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%)',
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: '#0f766e',
              fontWeight: '600',
              transition: 'all 0.2s'
            }}>
              👤 My Account
            </a>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div style={{
        maxWidth: '1400px',
        margin: '2rem auto 0',
        textAlign: 'center',
        color: '#a8a29e',
        fontSize: '0.9rem'
      }}>
        <p>RealDiag Clinical Decision Support • Evidence-based diagnostics • For educational purposes</p>
      </div>
    </div>
  );
}

