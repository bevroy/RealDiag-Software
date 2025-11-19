import Link from 'next/link';

export default function LegalDisclaimer() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
      padding: '2rem'
    }}>
      {/* Header */}
      <div style={{
        maxWidth: '900px',
        margin: '0 auto 2rem',
        textAlign: 'center'
      }}>
        <Link href="/" style={{
          display: 'inline-block',
          marginBottom: '1rem',
          color: '#14b8a6',
          textDecoration: 'none',
          fontSize: '0.9rem'
        }}>
          ← Back to Home
        </Link>
        <h1 style={{
          margin: '0 0 0.5rem',
          fontSize: '2.5rem',
          background: 'linear-gradient(135deg, #dc2626 0%, #991b1b 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          ⚖️ Legal Disclaimer & Terms of Use
        </h1>
        <p style={{
          fontSize: '1.1rem',
          color: '#6b7280',
          margin: 0
        }}>
          IMPORTANT: Please read carefully before using this software
        </p>
      </div>

      {/* Critical Warning */}
      <div style={{
        maxWidth: '900px',
        margin: '0 auto 2rem',
        padding: '1.5rem',
        background: '#fee2e2',
        border: '3px solid #dc2626',
        borderRadius: '12px'
      }}>
        <h2 style={{
          margin: '0 0 1rem',
          color: '#991b1b',
          fontSize: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          🚨 CRITICAL MEDICAL DISCLAIMER
        </h2>
        <div style={{ fontSize: '1rem', color: '#7f1d1d', lineHeight: '1.6' }}>
          <p style={{ margin: '0 0 0.5rem', fontWeight: '600' }}>
            RealDiag-Software is provided for <strong>EDUCATIONAL AND INFORMATIONAL PURPOSES ONLY</strong>.
          </p>
          <p style={{ margin: '0 0 0.5rem' }}>This software:</p>
          <ul style={{ margin: '0.5rem 0', paddingLeft: '1.5rem' }}>
            <li>❌ <strong>Is NOT FDA-approved</strong> for medical use</li>
            <li>❌ <strong>Is NOT a medical device</strong></li>
            <li>❌ <strong>Is NOT intended for diagnosis or treatment</strong></li>
            <li>❌ <strong>Is NOT a substitute for professional medical advice</strong></li>
            <li>❌ <strong>Should NOT be used for clinical decisions</strong> without physician oversight</li>
          </ul>
          <p style={{ margin: '1rem 0 0', fontWeight: '600', fontSize: '1.1rem' }}>
            ⚠️ Always consult a qualified healthcare provider for medical concerns
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div style={{
        maxWidth: '900px',
        margin: '0 auto',
        background: 'white',
        padding: '2rem',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
      }}>
        {/* Section 1 */}
        <section style={{ marginBottom: '2rem' }}>
          <h2 style={{ color: '#1a202c', fontSize: '1.5rem', marginBottom: '1rem' }}>
            📋 For Healthcare Professionals
          </h2>
          <div style={{ fontSize: '1rem', color: '#4b5563', lineHeight: '1.6' }}>
            <h3 style={{ color: '#14b8a6', fontSize: '1.2rem', marginTop: '1rem' }}>Acceptable Use:</h3>
            <ul style={{ paddingLeft: '1.5rem' }}>
              <li>✅ Educational reference</li>
              <li>✅ Quick clinical pearls lookup</li>
              <li>✅ Differential diagnosis brainstorming</li>
              <li>✅ Teaching tool for medical students</li>
              <li>✅ Personal learning aid</li>
            </ul>

            <h3 style={{ color: '#ef4444', fontSize: '1.2rem', marginTop: '1rem' }}>Prohibited Use:</h3>
            <ul style={{ paddingLeft: '1.5rem' }}>
              <li>❌ Sole basis for clinical decisions</li>
              <li>❌ Replacement for clinical judgment</li>
              <li>❌ Documentation in medical records</li>
              <li>❌ Billing based on software recommendations</li>
              <li>❌ Use in emergency situations without verification</li>
            </ul>

            <p style={{ marginTop: '1rem', padding: '1rem', background: '#fef3c7', borderLeft: '4px solid #f59e0b', borderRadius: '4px' }}>
              <strong>Professional Responsibility:</strong> You assume full responsibility for any clinical decisions made, 
              whether or not informed by this software. This tool provides suggestions only—always apply your professional 
              judgment and verify against current medical literature.
            </p>
          </div>
        </section>

        {/* Section 2 */}
        <section style={{ marginBottom: '2rem' }}>
          <h2 style={{ color: '#1a202c', fontSize: '1.5rem', marginBottom: '1rem' }}>
            🏥 For Patients
          </h2>
          <div style={{ fontSize: '1rem', color: '#4b5563', lineHeight: '1.6' }}>
            <p style={{ fontWeight: '600', color: '#dc2626' }}>
              This software is NOT intended for patient self-diagnosis.
            </p>
            <p>If you are a patient or non-healthcare professional:</p>
            <ul style={{ paddingLeft: '1.5rem' }}>
              <li><strong>Always consult a qualified healthcare provider</strong> for medical concerns</li>
              <li><strong>Call 911</strong> or go to the emergency room for urgent medical issues</li>
              <li><strong>Do not delay seeking medical care</strong> based on information from this software</li>
              <li>This software <strong>cannot provide personalized medical advice</strong></li>
            </ul>

            <div style={{ marginTop: '1rem', padding: '1rem', background: '#dbeafe', border: '2px solid #3b82f6', borderRadius: '8px' }}>
              <p style={{ margin: '0 0 0.5rem', fontWeight: '600', color: '#1e40af' }}>Emergency Resources:</p>
              <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                <li><strong>Emergency Services:</strong> 911 (US)</li>
                <li><strong>Suicide Prevention Lifeline:</strong> 988</li>
                <li><strong>Crisis Text Line:</strong> Text HOME to 741741</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Section 3 */}
        <section style={{ marginBottom: '2rem' }}>
          <h2 style={{ color: '#1a202c', fontSize: '1.5rem', marginBottom: '1rem' }}>
            🔒 HIPAA & Privacy
          </h2>
          <div style={{ fontSize: '1rem', color: '#4b5563', lineHeight: '1.6' }}>
            <div style={{ padding: '1rem', background: '#fee2e2', border: '2px solid #dc2626', borderRadius: '8px', marginBottom: '1rem' }}>
              <p style={{ margin: 0, fontWeight: '600', color: '#991b1b' }}>
                ⚠️ <strong>This software is currently NOT HIPAA compliant.</strong>
              </p>
            </div>
            <p>Do not use in production healthcare environments without implementing:</p>
            <ul style={{ paddingLeft: '1.5rem' }}>
              <li>Encryption at rest and in transit</li>
              <li>Access controls and audit logs</li>
              <li>Business Associate Agreements (BAAs)</li>
              <li>Patient consent mechanisms</li>
              <li>Data retention and destruction policies</li>
            </ul>
            <p style={{ marginTop: '1rem' }}>
              See <Link href="/security" style={{ color: '#14b8a6', textDecoration: 'underline' }}>SECURITY.md</Link> for complete security information.
            </p>
          </div>
        </section>

        {/* Section 4 */}
        <section style={{ marginBottom: '2rem' }}>
          <h2 style={{ color: '#1a202c', fontSize: '1.5rem', marginBottom: '1rem' }}>
            ⚖️ Limitation of Liability
          </h2>
          <div style={{ fontSize: '1rem', color: '#4b5563', lineHeight: '1.6' }}>
            <p><strong>THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND.</strong></p>
            <p>The authors and contributors shall NOT be liable for:</p>
            <ul style={{ paddingLeft: '1.5rem' }}>
              <li>Direct, indirect, incidental, or consequential damages</li>
              <li>Personal injury or death</li>
              <li>Medical malpractice claims</li>
              <li>Errors in diagnosis or treatment</li>
              <li>Any damages arising from use of the software</li>
            </ul>
            <p style={{ marginTop: '1rem', fontStyle: 'italic' }}>
              By using this software, you agree to indemnify and hold harmless the authors from any claims 
              arising from your use.
            </p>
          </div>
        </section>

        {/* Section 5 */}
        <section style={{ marginBottom: '2rem' }}>
          <h2 style={{ color: '#1a202c', fontSize: '1.5rem', marginBottom: '1rem' }}>
            📜 Copyright & Licensing
          </h2>
          <div style={{ fontSize: '1rem', color: '#4b5563', lineHeight: '1.6' }}>
            <p><strong>MIT License</strong></p>
            <p>Copyright (c) 2025 RealDiag-Software Contributors</p>
            <p style={{ fontSize: '0.9rem', fontStyle: 'italic', marginTop: '1rem' }}>
              The diagnostic rules and clinical guidelines are compiled from public medical literature, 
              evidence-based guidelines, and educational resources. Medical knowledge changes rapidly; 
              always refer to primary sources.
            </p>
          </div>
        </section>

        {/* Section 6 */}
        <section>
          <h2 style={{ color: '#1a202c', fontSize: '1.5rem', marginBottom: '1rem' }}>
            ✅ Acknowledgment
          </h2>
          <div style={{ fontSize: '1rem', color: '#4b5563', lineHeight: '1.6', padding: '1rem', background: '#f3f4f6', borderRadius: '8px' }}>
            <p style={{ fontWeight: '600', marginBottom: '0.5rem' }}>BY USING THIS SOFTWARE, YOU ACKNOWLEDGE THAT:</p>
            <ul style={{ paddingLeft: '1.5rem', marginBottom: '1rem' }}>
              <li>✅ You have read and understood this disclaimer</li>
              <li>✅ You agree to all terms and conditions</li>
              <li>✅ You understand this is not medical advice</li>
              <li>✅ You will not use this for clinical decisions without independent verification</li>
              <li>✅ You assume all responsibility for any use of the software</li>
              <li>✅ You understand the limitations and risks</li>
            </ul>
            <p style={{ fontWeight: '600', color: '#dc2626', margin: 0 }}>
              IF YOU DO NOT AGREE, DO NOT USE THIS SOFTWARE.
            </p>
          </div>
        </section>

        {/* Footer */}
        <div style={{ marginTop: '2rem', paddingTop: '2rem', borderTop: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '0.9rem', color: '#9ca3af', margin: '0 0 1rem' }}>
            For complete terms, see:{' '}
            <a href="https://github.com/bevroy/RealDiag-Software/blob/main/LEGAL_DISCLAIMER.md" 
               target="_blank" 
               rel="noopener noreferrer"
               style={{ color: '#14b8a6', textDecoration: 'underline' }}>
              LEGAL_DISCLAIMER.md
            </a>
          </p>
          <p style={{ fontSize: '0.9rem', color: '#9ca3af', margin: 0 }}>
            Last Updated: November 19, 2025 | Version 1.0.0
          </p>
        </div>
      </div>
    </div>
  );
}
