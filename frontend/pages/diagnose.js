import React, { useState, useEffect } from 'react'
import styles from '../styles/Diagnose.module.css'

export default function Diagnose() {
  const [trees, setTrees] = useState([])
  const [selectedTree, setSelectedTree] = useState('')
  const [currentStep, setCurrentStep] = useState(1) // Track wizard step
  const [patientData, setPatientData] = useState({
    diagnosis: '',
    symptoms: [],
    exam: [],
    red_flags: [],
    age: '',
    onset_hours: ''
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [apiBase, setApiBase] = useState('')
  const [showWizardMode, setShowWizardMode] = useState(true) // Toggle between wizard and traditional

  // Get API base from runtime config or environment
  useEffect(() => {
    const runtimeConfig = (typeof window !== 'undefined' && window.__RUNTIME_CONFIG) ? window.__RUNTIME_CONFIG : null
    const base = runtimeConfig?.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com'
    setApiBase(base.replace(/\/$/, ''))
  }, [])

  // Fetch available diagnostic trees
  useEffect(() => {
    if (!apiBase) return
    fetch(`${apiBase}/diagnostic/trees`)
      .then(res => res.json())
      .then(data => setTrees(data.trees || []))
      .catch(err => console.error('Failed to load trees:', err))
  }, [apiBase])

  const handleSymptomToggle = (symptom) => {
    setPatientData(prev => ({
      ...prev,
      symptoms: prev.symptoms.includes(symptom)
        ? prev.symptoms.filter(s => s !== symptom)
        : [...prev.symptoms, symptom]
    }))
  }

  const handleExamToggle = (finding) => {
    setPatientData(prev => ({
      ...prev,
      exam: prev.exam.includes(finding)
        ? prev.exam.filter(e => e !== finding)
        : [...prev.exam, finding]
    }))
  }

  const handleRedFlagToggle = (flag) => {
    setPatientData(prev => ({
      ...prev,
      red_flags: prev.red_flags.includes(flag)
        ? prev.red_flags.filter(f => f !== flag)
        : [...prev.red_flags, flag]
    }))
  }

  const handleEvaluate = async () => {
    if (!selectedTree) {
      alert('Please select a diagnostic tree')
      return
    }

    setLoading(true)
    setResult(null)

    try {
      const response = await fetch(`${apiBase}/diagnostic/evaluate/${selectedTree}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patientData)
      })
      const data = await response.json()
      setResult(data.tree_result)
    } catch (err) {
      console.error('Evaluation failed:', err)
      alert('Failed to evaluate. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setPatientData({
      diagnosis: '',
      symptoms: [],
      exam: [],
      red_flags: [],
      age: '',
      onset_hours: ''
    })
    setResult(null)
    setCurrentStep(1)
  }

  const getTotalSteps = () => {
    if (!selectedTree) return 4
    return 5 // Tree selection + symptoms + exam + red flags + evaluate
  }

  const getStepTitle = (step) => {
    const titles = [
      'Select Diagnostic Tree',
      'Patient Demographics',
      'Clinical Symptoms',
      'Physical Examination',
      'Red Flags & Risk Factors'
    ]
    return titles[step - 1] || 'Unknown Step'
  }

  const canProceedToNextStep = () => {
    if (currentStep === 1) return selectedTree !== ''
    if (currentStep === 2) return patientData.age !== ''
    if (currentStep === 3) return patientData.symptoms.length > 0
    return true
  }

  const nextStep = () => {
    if (canProceedToNextStep() && currentStep < getTotalSteps()) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  // Symptom options based on tree type
  const getSymptomOptions = () => {
    if (selectedTree === 'NEU-HEADACHE') {
      return ['headache', 'nausea', 'vomiting', 'photophobia', 'phonophobia', 'aura', 'pulsatile tinnitus']
    } else if (selectedTree === 'NEU-VERTIGO') {
      return ['vertigo', 'dizziness', 'nausea', 'vomiting', 'hearing loss', 'tinnitus', 'imbalance']
    }
    return []
  }

  const getExamOptions = () => {
    if (selectedTree === 'NEU-HEADACHE') {
      return ['papilledema', 'focal neuro deficit', 'altered mental status', 'fever', 'neck stiffness']
    } else if (selectedTree === 'NEU-VERTIGO') {
      return ['nystagmus', 'hearing loss', 'focal neuro deficit', 'ataxia', 'head impulse test abnormal']
    }
    return []
  }

  const getRedFlagOptions = () => {
    if (selectedTree === 'NEU-HEADACHE') {
      return ['thunderclap', 'worst headache of life', 'new onset > 50 years', 'immunocompromised', 'cancer history']
    } else if (selectedTree === 'NEU-VERTIGO') {
      return ['sudden onset', 'severe headache', 'focal neuro signs', 'chest pain', 'dyspnea']
    }
    return []
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div style={{background: 'white', borderRadius: '12px', padding: '2rem', maxWidth: '800px', margin: '0 auto 2rem', boxShadow: '0 4px 6px rgba(0,0,0,0.1)'}}>
          <img src="/logo.png" alt="RealDiag Logo" style={{maxHeight: '80px', marginBottom: '1rem'}} />
          <h1>RealDiag - Clinical Decision Support</h1>
          <p style={{color: '#4a5568', marginTop: '0.5rem'}}>Interactive diagnostic decision trees for clinical evaluation</p>
        </div>
      </header>

      <div className={styles.main}>
        {/* Wizard Mode Toggle */}
        <div style={{maxWidth: '800px', margin: '0 auto 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <button
            onClick={() => setShowWizardMode(!showWizardMode)}
            style={{
              padding: '0.5rem 1rem',
              background: showWizardMode ? '#3b82f6' : '#e5e7eb',
              color: showWizardMode ? 'white' : '#374151',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.9rem',
              fontWeight: '500'
            }}
          >
            {showWizardMode ? '✓ Wizard Mode' : 'Traditional Mode'}
          </button>
          {result && (
            <button
              onClick={handleReset}
              style={{
                padding: '0.5rem 1rem',
                background: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.9rem',
                fontWeight: '500'
              }}
            >
              🔄 Start Over
            </button>
          )}
        </div>

        {/* Progress Indicator (Wizard Mode Only) */}
        {showWizardMode && selectedTree && !result && (
          <div style={{maxWidth: '800px', margin: '0 auto 2rem', background: 'white', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 2px 4px rgba(0,0,0,0.1)'}}>
            <div style={{marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
              <span style={{fontSize: '0.9rem', fontWeight: '600', color: '#374151'}}>
                Step {currentStep} of {getTotalSteps()}: {getStepTitle(currentStep)}
              </span>
              <span style={{fontSize: '0.85rem', color: '#6b7280'}}>
                {Math.round((currentStep / getTotalSteps()) * 100)}% Complete
              </span>
            </div>
            {/* Progress Bar */}
            <div style={{width: '100%', height: '8px', background: '#e5e7eb', borderRadius: '4px', overflow: 'hidden'}}>
              <div style={{
                width: `${(currentStep / getTotalSteps()) * 100}%`,
                height: '100%',
                background: 'linear-gradient(90deg, #3b82f6 0%, #2563eb 100%)',
                transition: 'width 0.3s ease'
              }} />
            </div>
            {/* Step Indicators */}
            <div style={{display: 'flex', justifyContent: 'space-between', marginTop: '1rem', gap: '0.5rem'}}>
              {Array.from({length: getTotalSteps()}, (_, i) => i + 1).map(step => (
                <div
                  key={step}
                  style={{
                    flex: 1,
                    textAlign: 'center',
                    padding: '0.5rem',
                    borderRadius: '4px',
                    background: step === currentStep ? '#dbeafe' : (step < currentStep ? '#dcfce7' : '#f3f4f6'),
                    border: step === currentStep ? '2px solid #3b82f6' : 'none',
                    fontSize: '0.75rem',
                    fontWeight: '500',
                    color: step <= currentStep ? '#374151' : '#9ca3af',
                    transition: 'all 0.3s ease'
                  }}
                >
                  {step === currentStep ? '▶' : (step < currentStep ? '✓' : step)}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tree Selection */}
        <section className={styles.section} style={{display: (!showWizardMode || currentStep === 1) ? 'block' : 'none'}}>
          <h2>1. Select Diagnostic Tree</h2>
          <div className={styles.treeSelection}>
            {trees.map(tree => (
              <button
                key={tree.id}
                className={`${styles.treeButton} ${selectedTree === tree.id ? styles.active : ''}`}
                onClick={() => {
                  setSelectedTree(tree.id)
                  handleReset()
                }}
              >
                {tree.title}
              </button>
            ))}
          </div>
        </section>

        {selectedTree && (
          <>
            {/* Patient Demographics */}
            <section className={styles.section} style={{display: (!showWizardMode || currentStep === 2) ? 'block' : 'none'}}>
              <h2>2. Patient Information</h2>
              <div className={styles.formGrid}>
                <div className={styles.formGroup}>
                  <label>Age</label>
                  <input
                    type="number"
                    value={patientData.age}
                    onChange={(e) => setPatientData({...patientData, age: e.target.value})}
                    placeholder="Patient age"
                  />
                </div>
                <div className={styles.formGroup}>
                  <label>Onset (hours ago)</label>
                  <input
                    type="number"
                    value={patientData.onset_hours}
                    onChange={(e) => setPatientData({...patientData, onset_hours: e.target.value})}
                    placeholder="Hours since onset"
                  />
                </div>
                <div className={styles.formGroup}>
                  <label>Working Diagnosis</label>
                  <input
                    type="text"
                    value={patientData.diagnosis}
                    onChange={(e) => setPatientData({...patientData, diagnosis: e.target.value})}
                    placeholder="Optional"
                  />
                </div>
              </div>
            </section>

            {/* Symptoms */}
            <section className={styles.section} style={{display: (!showWizardMode || currentStep === 3) ? 'block' : 'none'}}>
              <h2>3. Symptoms</h2>
              <div className={styles.checkboxGrid}>
                {getSymptomOptions().map(symptom => (
                  <label key={symptom} className={styles.checkbox}>
                    <input
                      type="checkbox"
                      checked={patientData.symptoms.includes(symptom)}
                      onChange={() => handleSymptomToggle(symptom)}
                    />
                    <span>{symptom}</span>
                  </label>
                ))}
              </div>
            </section>

            {/* Physical Exam */}
            <section className={styles.section} style={{display: (!showWizardMode || currentStep === 4) ? 'block' : 'none'}}>
              <h2>4. Physical Exam Findings</h2>
              <div className={styles.checkboxGrid}>
                {getExamOptions().map(finding => (
                  <label key={finding} className={styles.checkbox}>
                    <input
                      type="checkbox"
                      checked={patientData.exam.includes(finding)}
                      onChange={() => handleExamToggle(finding)}
                    />
                    <span>{finding}</span>
                  </label>
                ))}
              </div>
            </section>

            {/* Red Flags */}
            <section className={`${styles.section} ${styles.redFlags}`} style={{display: (!showWizardMode || currentStep === 5) ? 'block' : 'none'}}>
              <h2>5. Red Flags ⚠️</h2>
              <div className={styles.checkboxGrid}>
                {getRedFlagOptions().map(flag => (
                  <label key={flag} className={styles.checkbox}>
                    <input
                      type="checkbox"
                      checked={patientData.red_flags.includes(flag)}
                      onChange={() => handleRedFlagToggle(flag)}
                    />
                    <span>{flag}</span>
                  </label>
                ))}
              </div>
            </section>

            {/* Actions / Wizard Navigation */}
            <section className={styles.actions}>
              {showWizardMode ? (
                <div style={{display: 'flex', gap: '1rem', justifyContent: 'space-between'}}>
                  <button
                    onClick={prevStep}
                    disabled={currentStep === 1}
                    style={{
                      flex: 1,
                      padding: '1rem 2rem',
                      background: currentStep === 1 ? '#e5e7eb' : '#6b7280',
                      color: currentStep === 1 ? '#9ca3af' : 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: currentStep === 1 ? 'not-allowed' : 'pointer',
                      fontSize: '1rem',
                      fontWeight: '600'
                    }}
                  >
                    ← Previous
                  </button>
                  {currentStep < getTotalSteps() ? (
                    <button
                      onClick={nextStep}
                      disabled={!canProceedToNextStep()}
                      style={{
                        flex: 2,
                        padding: '1rem 2rem',
                        background: canProceedToNextStep() ? '#3b82f6' : '#9ca3af',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: canProceedToNextStep() ? 'pointer' : 'not-allowed',
                        fontSize: '1rem',
                        fontWeight: '600'
                      }}
                    >
                      Continue →
                    </button>
                  ) : (
                    <button
                      onClick={handleEvaluate}
                      disabled={loading}
                      style={{
                        flex: 2,
                        padding: '1rem 2rem',
                        background: loading ? '#9ca3af' : '#10b981',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        fontSize: '1rem',
                        fontWeight: '600'
                      }}
                    >
                      {loading ? '🔄 Evaluating...' : '🩺 Complete Evaluation'}
                    </button>
                  )}
                </div>
              ) : (
                <>
                  <button
                    className={styles.evaluateButton}
                    onClick={handleEvaluate}
                    disabled={loading}
                  >
                    {loading ? '🔄 Evaluating...' : '🩺 Evaluate Diagnosis'}
                  </button>
                  <button
                    className={styles.resetButton}
                    onClick={handleReset}
                  >
                    🔄 Reset
                  </button>
                </>
              )}
            </section>

            {/* Results */}
            {result && (
              <section className={`${styles.section} ${styles.results}`}>
                <h2>📋 Clinical Decision Support Results</h2>
                
                {result.path && result.path.length > 0 && (
                  <div className={styles.resultCard}>
                    <h3>✓ Decision Path: {result.path.join(' → ')}</h3>
                    
                    {result.provisional_dx && result.provisional_dx.length > 0 && (
                      <div className={styles.resultSection}>
                        <h4>🎯 Suggested Diagnoses:</h4>
                        <ul>
                          {result.provisional_dx.map((dx, i) => (
                            <li key={i}>{dx}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {result.tests && result.tests.length > 0 && (
                      <div className={styles.resultSection}>
                        <h4>🔬 Recommended Tests:</h4>
                        <ul>
                          {result.tests.map((test, i) => (
                            <li key={i}>{test}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {result.referrals && result.referrals.length > 0 && (
                      <div className={styles.resultSection}>
                        <h4>👨‍⚕️ Specialist Referrals:</h4>
                        <ul>
                          {result.referrals.map((referral, i) => (
                            <li key={i}>{referral}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {result.trace && result.trace.length > 0 && (
                      <details className={styles.trace}>
                        <summary>View Decision Trace</summary>
                        <ul>
                          {result.trace.map((step, i) => (
                            <li key={i}>{step}</li>
                          ))}
                        </ul>
                      </details>
                    )}
                  </div>
                )}

                {(!result.path || result.path.length === 0) && (
                  <div className={styles.noMatch}>
                    <p>No matching diagnostic pathway found with current inputs.</p>
                  </div>
                )}
              </section>
            )}
          </>
        )}

        {!selectedTree && (
          <div className={styles.emptyState}>
            <p>👆 Select a diagnostic tree above to begin clinical evaluation</p>
          </div>
        )}
      </div>
    </div>
  )
}
