import Link from 'next/link';

export default function Home() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f0fdfa 0%, #e7f5f3 100%)',
      padding: '2rem'
    }}>
      {/* Header */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto 3rem',
        textAlign: 'center'
      }}>
        <img 
          src="/logo.png" 
          alt="RealDiag Logo" 
          style={{ height: '100px', width: 'auto', marginBottom: '1rem' }}
        />
        <h1 style={{ margin: 0, fontSize: '3.5rem', color: '#0f766e', fontWeight: '700', letterSpacing: '-0.02em' }}>
          RealDiag
        </h1>
        <p style={{ margin: '1rem 0 0.5rem', color: '#64748b', fontSize: '1.4rem', fontWeight: '500' }}>
          AI-Powered Clinical Diagnostic Search
        </p>
        <p style={{ margin: '0', color: '#94a3b8', fontSize: '1rem' }}>
          268 diagnoses • 17 specialties • Evidence-based
        </p>
      </div>

      {/* Main Content */}
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
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

        {/* Features Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1.25rem',
          marginBottom: '3rem'
        }}>
          <div style={{
            background: 'white',
            padding: '1.75rem',
            borderRadius: '12px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            border: '1px solid #e2e8f0'
          }}>
            <div style={{ fontSize: '2.25rem', marginBottom: '0.75rem' }}>🎯</div>
            <h3 style={{ margin: '0 0 0.5rem', color: '#0f766e', fontSize: '1.1rem', fontWeight: '600' }}>
              Evidence-Based
            </h3>
            <p style={{ margin: 0, color: '#64748b', lineHeight: '1.5', fontSize: '0.95rem' }}>
              Differential diagnoses ranked by Bayesian likelihood with sensitivity and specificity data.
            </p>
          </div>

          <div style={{
            background: 'white',
            padding: '1.75rem',
            borderRadius: '12px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            border: '1px solid #e2e8f0'
          }}>
            <div style={{ fontSize: '2.25rem', marginBottom: '0.75rem' }}>📚</div>
            <h3 style={{ margin: '0 0 0.5rem', color: '#0f766e', fontSize: '1.1rem', fontWeight: '600' }}>
              Clinical Pearls
            </h3>
            <p style={{ margin: 0, color: '#64748b', lineHeight: '1.5', fontSize: '0.95rem' }}>
              Detailed clinical pearls, management protocols, and evidence-based guidelines.
            </p>
          </div>

          <div style={{
            background: 'white',
            padding: '1.75rem',
            borderRadius: '12px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            border: '1px solid #e2e8f0'
          }}>
            <div style={{ fontSize: '2.25rem', marginBottom: '0.75rem' }}>🏥</div>
            <h3 style={{ margin: '0 0 0.5rem', color: '#0f766e', fontSize: '1.1rem', fontWeight: '600' }}>
              17 Specialties
            </h3>
            <p style={{ margin: 0, color: '#64748b', lineHeight: '1.5', fontSize: '0.95rem' }}>
              Cardiology, neurology, emergency medicine, and 14 other medical specialties.
            </p>
          </div>

          <div style={{
            background: 'white',
            padding: '1.75rem',
            borderRadius: '12px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            border: '1px solid #e2e8f0'
          }}>
            <div style={{ fontSize: '2.25rem', marginBottom: '0.75rem' }}>🔬</div>
            <h3 style={{ margin: '0 0 0.5rem', color: '#0f766e', fontSize: '1.1rem', fontWeight: '600' }}>
              Test Recommendations
            </h3>
            <p style={{ margin: 0, color: '#64748b', lineHeight: '1.5', fontSize: '0.95rem' }}>
              Suggested diagnostic tests and specialist referrals for each diagnosis.
            </p>
          </div>

          <div style={{
            background: 'white',
            padding: '1.75rem',
            borderRadius: '12px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            border: '1px solid #e2e8f0'
          }}>
            <div style={{ fontSize: '2.25rem', marginBottom: '0.75rem' }}>📖</div>
            <h3 style={{ margin: '0 0 0.5rem', color: '#0f766e', fontSize: '1.1rem', fontWeight: '600' }}>
              Medical Training
            </h3>
            <p style={{ margin: 0, color: '#64748b', lineHeight: '1.5', fontSize: '0.95rem' }}>
              Case library, quizzes, flashcards, and progress tracking for students.
            </p>
          </div>

          <div style={{
            background: 'white',
            padding: '1.75rem',
            borderRadius: '12px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            border: '1px solid #e2e8f0'
          }}>
            <div style={{ fontSize: '2.25rem', marginBottom: '0.75rem' }}>⚡</div>
            <h3 style={{ margin: '0 0 0.5rem', color: '#0f766e', fontSize: '1.1rem', fontWeight: '600' }}>
              Fast & Accurate
            </h3>
            <p style={{ margin: 0, color: '#64748b', lineHeight: '1.5', fontSize: '0.95rem' }}>
              Instant results powered by advanced algorithms and diagnostic rules.
            </p>
          </div>
        </div>

        {/* Quick Links */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '1rem',
          marginBottom: '3rem'
        }}>
          <a href="/rules" style={{
            padding: '1rem',
            background: 'white',
            border: '1px solid #e2e8f0',
            borderRadius: '10px',
            textDecoration: 'none',
            textAlign: 'center',
            color: '#0f766e',
            fontWeight: '600',
            fontSize: '0.95rem',
            transition: 'all 0.2s',
            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
          }}>
            📋 Browse Rules
          </a>
          <a href="/integration" style={{
            padding: '1rem',
            background: 'white',
            border: '1px solid #e2e8f0',
            borderRadius: '10px',
            textDecoration: 'none',
            textAlign: 'center',
            color: '#0f766e',
            fontWeight: '600',
            fontSize: '0.95rem',
            transition: 'all 0.2s',
            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
          }}>
            🔌 API
          </a>
          <a href="/features-demo" style={{
            padding: '1rem',
            background: 'white',
            border: '1px solid #e2e8f0',
            borderRadius: '10px',
            textDecoration: 'none',
            textAlign: 'center',
            color: '#0f766e',
            fontWeight: '600',
            fontSize: '0.95rem',
            transition: 'all 0.2s',
            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
          }}>
            ✨ Features
          </a>
          <a href="/education" style={{
            padding: '1rem',
            background: 'white',
            border: '1px solid #e2e8f0',
            borderRadius: '10px',
            textDecoration: 'none',
            textAlign: 'center',
            color: '#0f766e',
            fontWeight: '600',
            fontSize: '0.95rem',
            transition: 'all 0.2s',
            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
          }}>
            📚 Training
          </a>
          <a href="/sources" style={{
            padding: '1rem',
            background: 'white',
            border: '1px solid #e2e8f0',
            borderRadius: '10px',
            textDecoration: 'none',
            textAlign: 'center',
            color: '#0f766e',
            fontWeight: '600',
            fontSize: '0.95rem',
            transition: 'all 0.2s',
            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
          }}>
            📖 Sources
          </a>
          <a href="/account" style={{
            padding: '1rem',
            background: 'white',
            border: '1px solid #e2e8f0',
            borderRadius: '10px',
            textDecoration: 'none',
            textAlign: 'center',
            color: '#0f766e',
            fontWeight: '600',
            fontSize: '0.95rem',
            transition: 'all 0.2s',
            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
          }}>
            👤 Account
          </a>
        </div>
      </div>

      {/* Banners at Bottom */}
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* NEW UPDATE BANNER */}
        <div style={{
          margin: '0 0 1rem',
          padding: '1rem 1.5rem',
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          borderRadius: '10px',
          color: 'white',
          textAlign: 'center',
          boxShadow: '0 2px 8px rgba(16, 185, 129, 0.2)'
        }}>
          <strong style={{ fontSize: '0.95rem' }}>🎉 NEW: Medical Training Center!</strong>
          <p style={{ margin: '0.5rem 0 0', fontSize: '0.85rem', opacity: 0.95 }}>
            Case library, quiz mode, flashcards, progress tracking. Updated: November 19, 2025
          </p>
        </div>

        {/* MEDICAL DISCLAIMER */}
        <div style={{
          margin: '0 0 2rem',
          padding: '1rem 1.5rem',
          background: 'linear-gradient(135deg, #dc2626 0%, #991b1b 100%)',
          borderRadius: '10px',
          color: 'white',
          textAlign: 'center',
          boxShadow: '0 2px 8px rgba(220, 38, 38, 0.2)',
          border: '1px solid rgba(252, 165, 165, 0.3)'
        }}>
          <strong style={{ fontSize: '0.95rem' }}>⚠️ MEDICAL DISCLAIMER: NOT FOR CLINICAL USE</strong>
          <p style={{ margin: '0.5rem 0 0', fontSize: '0.85rem', opacity: 0.95 }}>
            Educational purposes only. Not FDA-approved. Not a substitute for professional medical judgment.
            See <Link href="/legal-disclaimer" style={{ color: '#fef3c7', textDecoration: 'underline' }}>Legal Disclaimer</Link> for complete terms.
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

