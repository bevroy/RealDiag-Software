/**
 * Example: Using Accessibility & Decision Support Features
 * Demonstrates Task 6.1, 4.3, and 3.3 implementations
 */

import React, { useState, useRef } from 'react';
import { 
  SkipLink, 
  AccessibleButton, 
  LiveRegion, 
  useKeyboardNavigation,
  useFocusTrap 
} from '../components/AccessibilityHelpers';
import { 
  calculateLikelihood, 
  getConfidenceLevel, 
  getConfidenceColor,
  generateDecisionTrace 
} from '../utils/decisionSupport';

export default function FeaturesDemo() {
  const [showModal, setShowModal] = useState(false);
  const modalRef = useRef(null);
  
  // Task 6.1: Keyboard navigation (Esc to close modal)
  useKeyboardNavigation(() => setShowModal(false), [showModal]);
  
  // Task 6.1: Focus trap in modal
  useFocusTrap(modalRef, showModal);
  
  // Sample diagnostic result for Task 3.3 demo
  const sampleResult = {
    label: "Migraine Headache",
    match_score: 8.5,
    sensitivity: 0.92,
    specificity: 0.88,
    matched_presentations: ["headache", "photophobia", "nausea"],
    family: "neurology"
  };
  
  const likelihood = calculateLikelihood(sampleResult);
  const confidenceLevel = getConfidenceLevel(likelihood);
  const confidenceColor = getConfidenceColor(likelihood);
  const decisionTrace = generateDecisionTrace(sampleResult, likelihood);

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #f0fdfa 0%, #e7f5f3 100%)', padding: '2rem' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Task 6.1: Skip Link */}
        <SkipLink targetId="main-content" />
      
      {/* Navigation Dropdown */}
      <div style={{ marginBottom: '1rem' }}>
        <details style={{
          background: 'white',
          padding: '0.75rem 1.25rem',
          borderRadius: '10px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          border: '1px solid #e2e8f0',
          cursor: 'pointer'
        }}>
          <summary style={{ 
            color: '#0f766e', 
            fontSize: '1rem',
            fontWeight: '600',
            listStyle: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <span>☰ Navigation</span>
          </summary>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
            gap: '0.75rem',
            marginTop: '1rem',
            paddingTop: '1rem',
            borderTop: '1px solid #e2e8f0'
          }}>
            <a href="/" style={{
              padding: '0.75rem',
              background: '#f0fdfa',
              border: '1px solid #ccfbf1',
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: '#0f766e',
              fontWeight: '600',
              fontSize: '0.9rem'
            }}>
              🏠 Home
            </a>
            <a href="/symptom-search" style={{
              padding: '0.75rem',
              background: '#f0fdfa',
              border: '1px solid #ccfbf1',
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: '#0f766e',
              fontWeight: '600',
              fontSize: '0.9rem'
            }}>
              🔬 Symptom Search
            </a>
            <a href="/search" style={{
              padding: '0.75rem',
              background: '#f0fdfa',
              border: '1px solid #ccfbf1',
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: '#0f766e',
              fontWeight: '600',
              fontSize: '0.9rem'
            }}>
              🔍 Diagnosis Search
            </a>
            <a href="/rules" style={{
              padding: '0.75rem',
              background: '#f0fdfa',
              border: '1px solid #ccfbf1',
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: '#0f766e',
              fontWeight: '600',
              fontSize: '0.9rem'
            }}>
              📋 Browse Rules
            </a>
            <a href="/integration" style={{
              padding: '0.75rem',
              background: '#f0fdfa',
              border: '1px solid #ccfbf1',
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: '#0f766e',
              fontWeight: '600',
              fontSize: '0.9rem'
            }}>
              🔌 API
            </a>
            <a href="/features-demo" style={{
              padding: '0.75rem',
              background: '#f0fdfa',
              border: '1px solid #ccfbf1',
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: '#0f766e',
              fontWeight: '600',
              fontSize: '0.9rem'
            }}>
              ✨ Features
            </a>
            <a href="/education" style={{
              padding: '0.75rem',
              background: '#f0fdfa',
              border: '1px solid #ccfbf1',
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: '#0f766e',
              fontWeight: '600',
              fontSize: '0.9rem'
            }}>
              📚 Training
            </a>
            <a href="/sources" style={{
              padding: '0.75rem',
              background: '#f0fdfa',
              border: '1px solid #ccfbf1',
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: '#0f766e',
              fontWeight: '600',
              fontSize: '0.9rem'
            }}>
              📖 Sources
            </a>
            <a href="/patient-history" style={{
              padding: '0.75rem',
              background: '#f0fdfa',
              border: '1px solid #ccfbf1',
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: '#0f766e',
              fontWeight: '600',
              fontSize: '0.9rem'
            }}>
              📋 Patient History
            </a>
            <a href="/account" style={{
              padding: '0.75rem',
              background: '#f0fdfa',
              border: '1px solid #ccfbf1',
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: '#0f766e',
              fontWeight: '600',
              fontSize: '0.9rem'
            }}>
              👤 Account
            </a>
          </div>
        </details>
      </div>

      <header role="banner" style={{ marginBottom: '2rem' }}>
        <div style={{ background: 'white', borderRadius: '12px', padding: '1.5rem', marginBottom: '1rem', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <img src="/logo.png" alt="RealDiag Logo" style={{ height: '50px' }} />
            <h1 style={{ marginBottom: 0, color: '#78350f', fontSize: '1.75rem' }}>RealDiag Features</h1>
          </div>
        </div>
      </header>
      
      <main id="main-content" role="main">
        
        {/* Overview Section */}
        <section style={{ marginBottom: '3rem', background: 'white', padding: '2rem', borderRadius: '12px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h2 style={{ color: '#0f766e', fontSize: '1.75rem', marginBottom: '1rem' }}>Complete Feature List</h2>
          <p style={{ fontSize: '1.1rem', color: '#374151', lineHeight: '1.8' }}>
            RealDiag is a comprehensive clinical decision support system with 100+ features across diagnostic search, 
            patient safety, clinical education, EHR integration, and advanced analytics. All features are HIPAA-compliant 
            and designed for real-world clinical workflows.
          </p>
        </section>

        {/* Core Diagnostic Features */}
        <section aria-labelledby="diagnostic-heading" style={{ marginBottom: '3rem' }}>
          <h2 id="diagnostic-heading" style={{ color: '#0f766e', fontSize: '1.5rem', marginBottom: '1.5rem' }}>🔬 Core Diagnostic Features</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Symptom Search</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Multi-symptom differential diagnosis</li>
                <li>676+ diagnostic trees across 55 specialties</li>
                <li>Real-time likelihood scoring</li>
                <li>Match confidence indicators</li>
                <li>Sensitivity & specificity data</li>
                <li>Free trial: 10 searches/week for anonymous users</li>
              </ul>
            </div>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Diagnosis Search</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Direct diagnosis lookup</li>
                <li>Comprehensive clinical details</li>
                <li>Presentations & red flags</li>
                <li>Workup recommendations</li>
                <li>Treatment protocols</li>
                <li>Clinical pearls & evidence</li>
              </ul>
            </div>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>AI Tree Generation</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>GPT-4 & Claude 3.5 integration</li>
                <li>Automatic gap detection</li>
                <li>Evidence-based tree generation</li>
                <li>Medical review workflow</li>
                <li>Quality control validation</li>
                <li>Admin approval system</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Patient Safety Features */}
        <section aria-labelledby="safety-heading" style={{ marginBottom: '3rem' }}>
          <h2 id="safety-heading" style={{ color: '#0f766e', fontSize: '1.5rem', marginBottom: '1.5rem' }}>🛡️ Patient Safety Features</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Medication Safety</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Drug-drug interaction checking (50+ meds)</li>
                <li>Contraindication detection</li>
                <li>Allergen cross-reactivity alerts</li>
                <li>Duplicate therapy detection</li>
                <li>Beers Criteria for elderly</li>
                <li>Renal/hepatic dose adjustments</li>
                <li>Pregnancy risk warnings</li>
              </ul>
            </div>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Drug Interactions</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Major, moderate, minor severity</li>
                <li>Clinical effect descriptions</li>
                <li>Alternative medication suggestions</li>
                <li>Monitoring recommendations</li>
                <li>Color-coded severity badges</li>
                <li>Automatic extraction from management</li>
              </ul>
            </div>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Clinical Calculators</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Wells Score (DVT & PE)</li>
                <li>HEART Score (chest pain)</li>
                <li>CHA₂DS₂-VASc (AFib stroke risk)</li>
                <li>HAS-BLED (bleeding risk)</li>
                <li>CURB-65 (pneumonia severity)</li>
                <li>Centor Score (strep pharyngitis)</li>
                <li>Ottawa Ankle Rules</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Clinical Decision Support */}
        <section aria-labelledby="decision-support-heading" style={{ marginBottom: '3rem' }}>
          <h2 id="decision-support-heading" style={{ color: '#0f766e', fontSize: '1.5rem', marginBottom: '1.5rem' }}>🧠 Advanced Decision Support</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Likelihood Analysis</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Bayesian probability calculations</li>
                <li>Confidence level indicators</li>
                <li>Decision trace visualization</li>
                <li>What-if scenario analysis</li>
                <li>Test characteristics (sensitivity/specificity)</li>
                <li>Match score explanations</li>
              </ul>
            </div>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Cost-Effectiveness</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Diagnostic pathway analysis</li>
                <li>Cost comparisons ($, $$, $$$)</li>
                <li>Time-to-diagnosis estimates</li>
                <li>Recommended pathway selection</li>
                <li>Coverage for PE, DVT, ACS, stroke</li>
                <li>Value-based decision making</li>
              </ul>
            </div>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Patient History</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Comprehensive HPI documentation</li>
                <li>Structured history capture</li>
                <li>Medication list management</li>
                <li>Allergy tracking</li>
                <li>Social & family history</li>
                <li>Auto-sync with diagnostic searches</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Educational Features */}
        <section aria-labelledby="education-heading" style={{ marginBottom: '3rem' }}>
          <h2 id="education-heading" style={{ color: '#0f766e', fontSize: '1.5rem', marginBottom: '1.5rem' }}>📚 Medical Education & Training</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Case Library</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Searchable clinical scenarios</li>
                <li>Beginner, intermediate, advanced levels</li>
                <li>Multi-specialty coverage</li>
                <li>Complete patient presentations</li>
                <li>Lab & imaging results</li>
                <li>Differential diagnosis teaching</li>
              </ul>
            </div>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Interactive Quizzes</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Timed quiz mode (45-60 sec/question)</li>
                <li>Instant feedback with explanations</li>
                <li>Single & multiple choice questions</li>
                <li>Differential ranking exercises</li>
                <li>Scoring system with points</li>
                <li>Performance tracking</li>
              </ul>
            </div>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Progress Tracking</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Overall accuracy rates</li>
                <li>Cases attempted & completed</li>
                <li>Quiz performance metrics</li>
                <li>Average time per case</li>
                <li>Learning objectives mapping</li>
                <li>USMLE topic correlation</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Integration Features */}
        <section aria-labelledby="integration-heading" style={{ marginBottom: '3rem' }}>
          <h2 id="integration-heading" style={{ color: '#0f766e', fontSize: '1.5rem', marginBottom: '1.5rem' }}>🔌 Integration & Interoperability</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>FHIR/EHR Integration</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>FHIR R4 client</li>
                <li>Epic & Cerner connectivity</li>
                <li>Patient data pull (demographics, meds, labs)</li>
                <li>Multiple auth methods (OAuth, Bearer, Basic)</li>
                <li>Smart on FHIR ready</li>
                <li>HL7 v2 message support</li>
              </ul>
            </div>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Export & Reporting</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>PDF report generation</li>
                <li>Multi-format export (JSON, XML, CSV)</li>
                <li>FHIR resource export</li>
                <li>Custom report templates</li>
                <li>Batch export capabilities</li>
                <li>Branded clinical reports</li>
              </ul>
            </div>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>RESTful API</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Comprehensive REST API</li>
                <li>API key authentication</li>
                <li>Rate limiting & quotas</li>
                <li>Webhook support</li>
                <li>Interactive API docs (Swagger/ReDoc)</li>
                <li>Third-party integration ready</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Mobile & Offline */}
        <section aria-labelledby="mobile-heading" style={{ marginBottom: '3rem' }}>
          <h2 id="mobile-heading" style={{ color: '#0f766e', fontSize: '1.5rem', marginBottom: '1.5rem' }}>📱 Mobile & Offline Capabilities</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Progressive Web App</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Install to home screen</li>
                <li>Full offline functionality</li>
                <li>Service worker caching</li>
                <li>IndexedDB storage</li>
                <li>Background sync</li>
                <li>Push notifications</li>
              </ul>
            </div>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Offline Database</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Download all 676 diagnostic trees</li>
                <li>Progress tracking during download</li>
                <li>Specialty-based organization</li>
                <li>Offline search history</li>
                <li>Automatic sync when online</li>
                <li>Storage statistics dashboard</li>
              </ul>
            </div>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Mobile Optimization</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Touch-optimized interface</li>
                <li>Gesture navigation</li>
                <li>Responsive design (320px-2560px)</li>
                <li>Tablet split-screen layout</li>
                <li>Stylus support (iPad Pencil)</li>
                <li>Low-bandwidth mode</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Security & Compliance */}
        <section aria-labelledby="security-heading" style={{ marginBottom: '3rem' }}>
          <h2 id="security-heading" style={{ color: '#0f766e', fontSize: '1.5rem', marginBottom: '1.5rem' }}>🔒 Security & Compliance</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Data Encryption</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>AES-256-GCM client-side encryption</li>
                <li>Fernet database encryption</li>
                <li>PBKDF2 key derivation (100k iterations)</li>
                <li>16 PHI fields encrypted at rest</li>
                <li>TLS 1.3 in transit</li>
                <li>Session key management</li>
              </ul>
            </div>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Authentication</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Multi-factor authentication (TOTP)</li>
                <li>Backup recovery codes</li>
                <li>Session management</li>
                <li>API key authentication</li>
                <li>OAuth 2.0 support</li>
                <li>Role-based access control</li>
              </ul>
            </div>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Compliance</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>HIPAA-compliant architecture</li>
                <li>Audit logging for PHI access</li>
                <li>Automatic session timeout</li>
                <li>Data retention policies</li>
                <li>BAA-ready infrastructure</li>
                <li>SOC 2 Type II preparation</li>
              </ul>
            </div>
          </div>
        </section>

        {/* User Management */}
        <section aria-labelledby="user-heading" style={{ marginBottom: '3rem' }}>
          <h2 id="user-heading" style={{ color: '#0f766e', fontSize: '1.5rem', marginBottom: '1.5rem' }}>👤 User Management & Personalization</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Account Management</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Free account creation</li>
                <li>Email verification</li>
                <li>Password reset flow</li>
                <li>Profile customization</li>
                <li>Specialty selection</li>
                <li>Notification preferences</li>
              </ul>
            </div>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Personalization</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Search history tracking</li>
                <li>Favorites & bookmarks</li>
                <li>Custom diagnostic lists</li>
                <li>Personalized recommendations</li>
                <li>Recently viewed diagnoses</li>
                <li>Specialty-based ranking</li>
              </ul>
            </div>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>Subscription Plans</h3>
              <ul style={{ lineHeight: '1.8', color: '#374151' }}>
                <li>Free tier with search limits</li>
                <li>Starter ($29/month)</li>
                <li>Professional ($49/month)</li>
                <li>Professional Plus ($69/month)</li>
                <li>Team & enterprise plans</li>
                <li>14-day free trial</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Task 6.1: Accessibility Features */}
        <section aria-labelledby="accessibility-heading" style={{ marginBottom: '3rem' }}>
          <h2 id="accessibility-heading" style={{ color: '#0f766e', fontSize: '1.5rem', marginBottom: '1.5rem' }}>♿ Accessibility (WCAG 2.1 AA)</h2>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '1.5rem',
            marginTop: '1rem'
          }}>
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>✅ Implemented Features</h3>
              <ul style={{ lineHeight: '1.8' }}>
                <li><strong>Skip Links:</strong> Press Tab to see "Skip to main content"</li>
                <li><strong>Keyboard Navigation:</strong> Tab, Enter, Escape keys work</li>
                <li><strong>ARIA Labels:</strong> Screen reader friendly</li>
                <li><strong>Focus Management:</strong> Visible focus indicators</li>
                <li><strong>Touch Targets:</strong> Minimum 44x44px on mobile</li>
                <li><strong>High Contrast:</strong> Respects system preferences</li>
                <li><strong>Reduced Motion:</strong> Animations disabled when requested</li>
              </ul>
            </div>
            
            <div style={{ padding: '1.5rem', background: 'white', borderRadius: '8px', border: '1px solid #d1d5db', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>🔍 Try It Out</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
                <AccessibleButton
                  onClick={() => setShowModal(true)}
                  ariaLabel="Open accessible modal dialog"
                  style={{
                    padding: '1rem',
                    background: '#009688',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontWeight: '600',
                    minHeight: '44px'
                  }}
                >
                  Open Modal (Press Esc to close)
                </AccessibleButton>
                
                <label htmlFor="accessible-input" style={{ fontWeight: '500' }}>
                  Accessible Form Input:
                </label>
                <input
                  id="accessible-input"
                  type="text"
                  placeholder="Tab here to see focus indicator"
                  aria-describedby="input-help"
                  style={{
                    padding: '0.75rem',
                    border: '2px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '1rem'
                  }}
                />
                <span id="input-help" style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                  This input has proper ARIA attributes
                </span>
              </div>
            </div>
          </div>
        </section>
        
        {/* Task 4.3: Tablet Optimization */}
        <section aria-labelledby="tablet-heading" style={{ marginBottom: '3rem' }}>
          <h2 id="tablet-heading" style={{ color: '#0f766e', fontSize: '1.5rem', marginBottom: '1.5rem' }}>Tablet Optimization</h2>
          
          <div className="tablet-split-screen" style={{ marginTop: '1rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            <div className="tablet-search-panel" style={{ 
              padding: '1.5rem', 
              background: 'white', 
              borderRadius: '8px',
              border: '1px solid #d1d5db',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <h3 style={{ color: '#0f766e', fontSize: '1.125rem', marginTop: 0 }}>📱 Tablet Features</h3>
              <ul style={{ lineHeight: '1.8' }}>
                <li><strong>Split-Screen Layout:</strong> Search on left, results on right (768-1024px)</li>
                <li><strong>Sticky Navigation:</strong> Search form stays visible while scrolling</li>
                <li><strong>Multi-Column Grids:</strong> Optimal card layouts for tablets</li>
                <li><strong>Landscape Mode:</strong> Special optimizations for horizontal viewing</li>
                <li><strong>Stylus Support:</strong> Precision interactions for iPad Pencil</li>
              </ul>
              <p style={{ 
                marginTop: '1rem', 
                padding: '1rem', 
                background: '#ffffff', 
                borderRadius: '6px',
                fontSize: '0.875rem'
              }}>
                💡 <strong>Tip:</strong> Resize your browser to 768-1024px width to see tablet layout in action!
              </p>
            </div>
            
            <div className="tablet-results-grid" style={{ display: 'grid', gap: '1rem' }}>
              <div style={{ 
                padding: '1.5rem', 
                background: 'white',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}>
                <h4 style={{ margin: '0 0 0.75rem', color: '#78350f', fontSize: '1rem' }}>Multi-Column Layout</h4>
                <p style={{ color: '#374151', lineHeight: '1.6' }}>Diagnostic results display in a 2-column grid on tablets (768-1024px), maximizing screen real estate while maintaining readability.</p>
              </div>
              <div style={{ 
                padding: '1.5rem', 
                background: 'white',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}>
                <h4 style={{ margin: '0 0 0.75rem', color: '#78350f', fontSize: '1rem' }}>Touch-Optimized Cards</h4>
                <p style={{ color: '#374151', lineHeight: '1.6' }}>All interactive elements meet 44x44px minimum touch target size, with generous spacing for comfortable stylus or finger interaction.</p>
              </div>
              <div style={{ 
                padding: '1.5rem', 
                background: 'white',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}>
                <h4 style={{ margin: '0 0 0.75rem', color: '#78350f', fontSize: '1rem' }}>Landscape Optimization</h4>
                <p style={{ color: '#374151', lineHeight: '1.6' }}>Split-screen layout activates in landscape mode, showing search controls alongside results for efficient clinical workflow.</p>
              </div>
            </div>
          </div>
        </section>
        
        {/* Task 3.3: Advanced Decision Support */}
        <section aria-labelledby="decision-heading" style={{ marginBottom: '3rem' }}>
          <h2 id="decision-heading" style={{ color: '#0f766e', fontSize: '1.5rem', marginBottom: '1.5rem' }}>Advanced Decision Support</h2>
          
          <div style={{ 
            marginTop: '1rem',
            padding: '2rem',
            background: 'white',
            borderRadius: '8px',
            border: '1px solid #d1d5db',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ color: '#78350f', fontSize: '1.25rem', marginTop: 0 }}>🩺 Sample Diagnosis: {sampleResult.label}</h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginTop: '1.5rem' }}>
              <div style={{ color: '#92400e', fontSize: '1.1rem', background: 'none', padding: 0 }}>
                <strong>Advanced Decision Support:</strong> This section provides a sample diagnosis, match score, likelihood, and test characteristics in a clear, text-based format. All information is presented without decorative boxes or clip-art for improved accessibility and consistency.
                <br /><br />
                <span><strong>Sample Diagnosis:</strong> {sampleResult.label}</span><br />
                <span><strong>Match Score:</strong> {sampleResult.match_score.toFixed(1)} / 10</span><br />
                <span><strong>Likelihood:</strong> {likelihood ? likelihood.toFixed(0) + '%' : 'N/A'} ({confidenceLevel} Confidence)</span><br />
                <span><strong>Sensitivity:</strong> {(sampleResult.sensitivity * 100).toFixed(0)}%</span><br />
                <span><strong>Specificity:</strong> {(sampleResult.specificity * 100).toFixed(0)}%</span>
              </div>
            </div>
            
            {/* Decision Trace */}
            <details open style={{ marginTop: '2rem' }}>
              <summary style={{ 
                padding: '1rem', 
                background: '#f9fafb', 
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '1.1rem'
              }}>
                🔍 View Decision Trace
              </summary>
              <div style={{ 
                marginTop: '1rem', 
                padding: '1rem', 
                background: '#fef9e7', 
                borderLeft: '4px solid #f59e0b',
                borderRadius: '4px',
                color: '#92400e' // brown
              }}>
                <ol style={{ lineHeight: '2', paddingLeft: '1.5rem' }}>
                  {decisionTrace.map((step, i) => (
                    <li key={i} style={{ marginBottom: '0.5rem' }}>{step}</li>
                  ))}
                </ol>
              </div>
            </details>
            
            {/* What-If Scenario Demo */}
            <div style={{ 
              marginTop: '2rem', 
              padding: '1.5rem', 
              background: '#f9fafb',
              borderRadius: '8px',
              border: '1px solid #e5e7eb'
            }}>
              <h4 style={{ margin: '0 0 1rem', color: '#0f766e', fontWeight: '600', fontSize: '1.125rem' }}>What-If Scenario Analysis</h4>
              <p style={{ marginBottom: '1rem', color: '#6b21a8' }}>
                <span style={{ color: '#92400e' }}>Try removing findings to see how likelihood changes:</span>
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {sampleResult.matched_presentations.map((finding, i) => (
                  <button
                    key={i}
                    aria-label={`Toggle ${finding} finding`}
                    style={{
                      padding: '0.5rem 1rem',
                      background: '#009688', // teal
                      color: 'white',
                      border: 'none',
                      borderRadius: '20px',
                      cursor: 'pointer',
                      fontSize: '0.9rem',
                      fontWeight: '500'
                    }}
                  >
                    ✓ {finding}
                  </button>
                ))}
              </div>
              <div style={{ 
                marginTop: '1rem', 
                padding: '0.75rem', 
                background: '#e0f2f1', // teal
                borderRadius: '6px',
                fontSize: '0.875rem',
                color: '#92400e' // brown
              }}>
                <strong>Interactive Mode:</strong> In the main app, clicking these buttons toggles findings and recalculates likelihood in real-time!
              </div>
            </div>
          </div>
        </section>
        
        {/* Live Region Demo */}
        <LiveRegion 
          aria-live="polite" 
          aria-atomic="true"
          style={{ 
            padding: '1rem', 
            background: '#dcfce7', 
            borderRadius: '6px',
            textAlign: 'center',
            fontWeight: '500',
            color: '#065f46'
          }}
        >
          ✅ All new features successfully loaded!
        </LiveRegion>
      </main>
      
      {/* Accessible Modal */}
      {showModal && (
        <div 
          role="dialog" 
          aria-modal="true" 
          aria-labelledby="modal-title"
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}
          onClick={() => setShowModal(false)}
        >
          <div 
            ref={modalRef}
            onClick={(e) => e.stopPropagation()}
            style={{
              background: 'white',
              padding: '2rem',
              borderRadius: '12px',
              maxWidth: '500px',
              boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)'
            }}
          >
            <h3 id="modal-title" style={{ marginTop: 0 }}>Accessible Modal</h3>
            <p style={{ lineHeight: '1.6', color: '#6b7280' }}>
              This modal demonstrates:
            </p>
            <ul style={{ lineHeight: '1.8' }}>
              <li><strong>Focus Trap:</strong> Tab key cycles through buttons</li>
              <li><strong>Keyboard Navigation:</strong> Press Escape to close</li>
              <li><strong>ARIA Attributes:</strong> role="dialog", aria-modal="true"</li>
              <li><strong>Click Outside:</strong> Click background to close</li>
            </ul>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
              <button 
                onClick={() => setShowModal(false)}
                style={{
                  flex: 1,
                  padding: '0.75rem',
                  background: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                Close Modal
              </button>
              <button 
                onClick={() => alert('Action button clicked!')}
                style={{
                  flex: 1,
                  padding: '0.75rem',
                  background: '#10b981',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                Action Button
              </button>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
}
