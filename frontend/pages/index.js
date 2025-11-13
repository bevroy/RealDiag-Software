import Link from 'next/link'

export default function Home(){
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '3rem',
        maxWidth: '600px',
        textAlign: 'center',
        boxShadow: '0 20px 40px rgba(0,0,0,0.2)'
      }}>
        <h1 style={{fontSize: '2.5rem', color: '#2d3748', marginBottom: '1rem'}}>
          🩺 RealDiag
        </h1>
        <p style={{color: '#718096', fontSize: '1.1rem', marginBottom: '2rem'}}>
          Clinical Decision Support System
        </p>
        
        <div style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
          <Link href="/diagnose" style={{
            padding: '1.25rem',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            borderRadius: '8px',
            textDecoration: 'none',
            fontSize: '1.1rem',
            fontWeight: '600',
            boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
            transition: 'transform 0.2s'
          }}>
            🩺 Interactive Diagnosis Tool
          </Link>
          
          <Link href="/rules" style={{
            padding: '1.25rem',
            background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
            color: 'white',
            borderRadius: '8px',
            textDecoration: 'none',
            fontSize: '1.1rem',
            fontWeight: '600',
            boxShadow: '0 4px 12px rgba(72, 187, 120, 0.4)',
            transition: 'transform 0.2s'
          }}>
            📚 Clinical Rules Reference
          </Link>
          
          <Link href="/diagnostic" style={{
            padding: '1.25rem',
            background: 'white',
            color: '#4a5568',
            border: '2px solid #e2e8f0',
            borderRadius: '8px',
            textDecoration: 'none',
            fontSize: '1.1rem',
            fontWeight: '600',
            transition: 'transform 0.2s'
          }}>
            🔧 System Diagnostic
          </Link>
        </div>
      </div>
    </div>
  )
}

