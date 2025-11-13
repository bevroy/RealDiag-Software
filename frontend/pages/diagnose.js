import React, { useState, useEffect } from 'react'
import styles from '../styles/Diagnose.module.css'

export default function Diagnose() {
  const [trees, setTrees] = useState([])
  const [selectedTree, setSelectedTree] = useState('')
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
        <h1>🩺 RealDiag - Clinical Decision Support</h1>
        <p>Interactive diagnostic decision trees for clinical evaluation</p>
      </header>

      <div className={styles.main}>
        {/* Tree Selection */}
        <section className={styles.section}>
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
            <section className={styles.section}>
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
            <section className={styles.section}>
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
            <section className={styles.section}>
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
            <section className={`${styles.section} ${styles.redFlags}`}>
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

            {/* Actions */}
            <section className={styles.actions}>
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
