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
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Task 6.1: Skip Link */}
      <SkipLink targetId="main-content" />
      
      <header role="banner" style={{ marginBottom: '2rem' }}>
        <h1>RealDiag - New Features Demo</h1>
        <p style={{ color: '#6b7280', fontSize: '1.1rem' }}>
          Accessibility, Tablet Optimization & Advanced Decision Support
        </p>
      </header>
      
      <main id="main-content" role="main">
        {/* Task 6.1: Accessibility Features */}
        <section aria-labelledby="accessibility-heading" style={{ marginBottom: '3rem' }}>
          <h2 id="accessibility-heading">Task 6.1: Accessibility (WCAG 2.1 AA)</h2>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '1.5rem',
            marginTop: '1rem'
          }}>
            <div style={{ padding: '1.5rem', background: '#f3f4f6', borderRadius: '8px' }}>
              <h3>✅ Implemented Features</h3>
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
            
            <div style={{ padding: '1.5rem', background: '#dbeafe', borderRadius: '8px' }}>
              <h3>🔍 Try It Out</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
                <AccessibleButton
                  onClick={() => setShowModal(true)}
                  ariaLabel="Open accessible modal dialog"
                  style={{
                    padding: '1rem',
                    background: '#3b82f6',
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
          <h2 id="tablet-heading">Task 4.3: Tablet Optimization</h2>
          
          <div className="tablet-split-screen" style={{ marginTop: '1rem' }}>
            <div className="tablet-search-panel" style={{ 
              padding: '1.5rem', 
              background: '#fef3c7', 
              borderRadius: '8px' 
            }}>
              <h3>📱 Tablet Features</h3>
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
              {[1, 2, 3].map(i => (
                <div key={i} style={{ 
                  padding: '1rem', 
                  background: '#f9fafb', 
                  border: '2px solid #e5e7eb',
                  borderRadius: '8px' 
                }}>
                  <h4>Result Card {i}</h4>
                  <p>Optimized for tablet viewing</p>
                </div>
              ))}
            </div>
          </div>
        </section>
        
        {/* Task 3.3: Advanced Decision Support */}
        <section aria-labelledby="decision-heading" style={{ marginBottom: '3rem' }}>
          <h2 id="decision-heading">Task 3.3: Advanced Decision Support</h2>
          
          <div style={{ 
            marginTop: '1rem', 
            padding: '2rem', 
            background: 'white', 
            border: '2px solid #e5e7eb',
            borderRadius: '8px'
          }}>
            <h3>🩺 Sample Diagnosis: {sampleResult.label}</h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginTop: '1.5rem' }}>
              {/* Match Score */}
              <div style={{ 
                padding: '1.5rem', 
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: 'white',
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '0.8rem', opacity: 0.9 }}>MATCH SCORE</div>
                <div style={{ fontSize: '2rem', fontWeight: '700', margin: '0.5rem 0' }}>
                  {sampleResult.match_score.toFixed(1)}
                </div>
                <div style={{ fontSize: '0.8rem', opacity: 0.9 }}>out of 10</div>
              </div>
              
              {/* Likelihood Score (NEW) */}
              <div style={{ 
                padding: '1.5rem', 
                background: `linear-gradient(135deg, ${confidenceColor} 0%, ${confidenceColor}dd 100%)`,
                color: 'white',
                borderRadius: '8px',
                textAlign: 'center',
                border: '3px solid ' + confidenceColor
              }}>
                <div style={{ fontSize: '0.8rem', opacity: 0.9 }}>LIKELIHOOD</div>
                <div style={{ fontSize: '2rem', fontWeight: '700', margin: '0.5rem 0' }}>
                  {likelihood ? likelihood.toFixed(0) + '%' : 'N/A'}
                </div>
                <div style={{ fontSize: '0.8rem', opacity: 0.9 }}>{confidenceLevel} Confidence</div>
              </div>
              
              {/* Test Characteristics */}
              <div style={{ padding: '1.5rem', background: '#f3f4f6', borderRadius: '8px' }}>
                <div style={{ marginBottom: '0.75rem' }}>
                  <div style={{ fontSize: '0.8rem', color: '#6b7280', fontWeight: '600' }}>SENSITIVITY</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#10b981' }}>
                    {(sampleResult.sensitivity * 100).toFixed(0)}%
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.8rem', color: '#6b7280', fontWeight: '600' }}>SPECIFICITY</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#3b82f6' }}>
                    {(sampleResult.specificity * 100).toFixed(0)}%
                  </div>
                </div>
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
                borderRadius: '4px'
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
              background: 'linear-gradient(to right, #f3e8ff, #faf5ff)',
              borderLeft: '4px solid #8b5cf6',
              borderRadius: '8px'
            }}>
              <h4 style={{ margin: '0 0 1rem', color: '#5b21b6' }}>
                🔮 What-If Scenario Analysis
              </h4>
              <p style={{ marginBottom: '1rem', color: '#6b21a8' }}>
                Try removing findings to see how likelihood changes:
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {sampleResult.matched_presentations.map((finding, i) => (
                  <button
                    key={i}
                    aria-label={`Toggle ${finding} finding`}
                    style={{
                      padding: '0.5rem 1rem',
                      background: '#8b5cf6',
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
                background: '#fef3c7',
                borderRadius: '6px',
                fontSize: '0.875rem',
                color: '#92400e'
              }}>
                💡 <strong>Interactive Mode:</strong> In the main app, clicking these buttons toggles findings and recalculates likelihood in real-time!
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
  );
}
