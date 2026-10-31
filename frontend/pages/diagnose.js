import React, { useState, useEffect } from 'react'
import styles from '../styles/Diagnose.module.css'
import RoleBasedNavigation from '../components/RoleBasedNavigation'
import PatientContext from '../components/PatientContext'
import ContextResults from '../components/ContextResults'
import PageHeader from '../components/PageHeader'
import { ClinicalReviewNotice, ReviewStatusBadge } from '../components/ClinicalReview'
import { apiFetch, getApiBase } from '../utils/apiClient'
import QuestionnaireWalk from '../components/QuestionnaireWalk'
import { questionnaireTrees } from '../utils/questionnaireWalker'
import {
  NOT_ASSESSED,
  STEP_TITLES,
  walkableTrees,
  unavailableTrees,
  displayLabel,
  itemsWithSource,
  emptyAnswers,
  buildSteps,
  toggle,
  findingOptionKey,
  findingFromOptionKey,
  buildPatientBody,
  endReasonMessage,
} from '../utils/diagnoseForm'

const navButton = (enabled, color) => ({
  padding: '1rem 2rem',
  background: enabled ? color : '#e5e7eb',
  color: enabled ? 'white' : '#9ca3af',
  border: 'none',
  borderRadius: '6px',
  cursor: enabled ? 'pointer' : 'not-allowed',
  fontSize: '1rem',
  fontWeight: '600'
})

function CheckboxGroup({ options, selected, onToggle }) {
  return (
    <div className={styles.checkboxGrid}>
      {options.map(option => (
        <label key={option} className={styles.checkbox}>
          <input
            type="checkbox"
            checked={selected.includes(option)}
            onChange={() => onToggle(option)}
          />
          <span>{displayLabel(option)}</span>
        </label>
      ))}
    </div>
  )
}

export default function Diagnose() {
  const [trees, setTrees] = useState([])
  const [heldBack, setHeldBack] = useState([])
  const [treesNotice, setTreesNotice] = useState(undefined)
  const [treesError, setTreesError] = useState('')
  const [selectedTree, setSelectedTree] = useState('')
  const [qTrees, setQTrees] = useState([])
  const [questionnaire, setQuestionnaire] = useState(null)
  const [treeInfo, setTreeInfo] = useState(null) // { tree, inputs, clinical_review_notice }
  const [inputsError, setInputsError] = useState('')
  const [answers, setAnswers] = useState(emptyAnswers())
  const [patientContext, setPatientContext] = useState({})
  const [currentStep, setCurrentStep] = useState(0) // index into ['tree', ...buildSteps()]
  const [showWizardMode, setShowWizardMode] = useState(true)
  const [result, setResult] = useState(null)
  const [evaluateError, setEvaluateError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    apiFetch('/diagnostic/trees')
      .then(res => {
        if (!res.ok) throw new Error(`Could not load decision trees (HTTP ${res.status}).`)
        return res.json()
      })
      .then(data => {
        setTrees(walkableTrees(data.trees))
        setHeldBack(unavailableTrees(data.trees))
        setQTrees(questionnaireTrees(data.trees))
        setTreesNotice(data.clinical_review_notice)
      })
      .catch(err => setTreesError(err.message))
  }, [])

  const selectQuestionnaire = async (treeId) => {
    setSelectedTree('')
    setTreeInfo(null)
    setResult(null)
    setInputsError('')
    try {
      const res = await apiFetch(`/diagnostic/trees/${encodeURIComponent(treeId)}/questionnaire`)
      if (!res.ok) throw new Error(`Could not load this tree's questions (HTTP ${res.status}).`)
      setQuestionnaire(await res.json())
    } catch (err) {
      setInputsError(err.message)
    }
  }

  const selectTree = async (treeId) => {
    setQuestionnaire(null)
    setSelectedTree(treeId)
    setTreeInfo(null)
    setInputsError('')
    setAnswers(emptyAnswers())
    setPatientContext({})
    setResult(null)
    setEvaluateError('')
    setCurrentStep(0)
    try {
      const res = await apiFetch(`/diagnostic/trees/${encodeURIComponent(treeId)}/inputs`)
      if (!res.ok) throw new Error(`Could not load this tree's questions (HTTP ${res.status}).`)
      setTreeInfo(await res.json())
    } catch (err) {
      setInputsError(err.message)
    }
  }

  const inputs = treeInfo ? treeInfo.inputs : null
  const steps = ['tree', ...buildSteps(inputs)]
  const stepKey = steps[currentStep]
  const visible = (key) => !showWizardMode || stepKey === key

  const setList = (field) => (value) => setAnswers(prev => ({ ...prev, [field]: toggle(prev[field], value) }))
  const setFinding = (name, optionKey) => setAnswers(prev => ({
    ...prev,
    findings: { ...prev.findings, [name]: findingFromOptionKey(optionKey) }
  }))

  const handleEvaluate = async () => {
    setLoading(true)
    setResult(null)
    setEvaluateError('')
    try {
      const response = await apiFetch(`/diagnostic/evaluate/${encodeURIComponent(selectedTree)}`, {
        method: 'POST',
        body: JSON.stringify({
          ...buildPatientBody(answers),
          patient_context: Object.keys(patientContext).length > 0 ? patientContext : undefined
        })
      })
      if (!response.ok) throw new Error(`Evaluation failed (HTTP ${response.status}).`)
      const data = await response.json()
      setResult({ ...data.tree_result, context: data.context })
    } catch (err) {
      setEvaluateError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleStartOver = () => {
    setAnswers(emptyAnswers())
    setPatientContext({})
    setResult(null)
    setEvaluateError('')
    setCurrentStep(0)
  }

  const reviewHeader = treeInfo && (
    <p style={{ margin: '0 0 0.75rem', display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
      <strong>{treeInfo.tree.title || treeInfo.tree.id}</strong>
      <ReviewStatusBadge status={treeInfo.tree.review_status} label={treeInfo.tree.review_status_label} />
    </p>
  )
  const stopMessage = endReasonMessage(result)
  const isLastStep = currentStep === steps.length - 1

  return (
    <div className={styles.container}>
      <RoleBasedNavigation />
      <header className={styles.header}>
        <PageHeader
          title="Decision Tree Walk"
          subtitle="Walk a diagnostic decision tree step by step, using the tree's own branch criteria"
        />
      </header>

      <div className={styles.main}>
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
            {showWizardMode ? '✓ One step at a time' : 'All steps on one page'}
          </button>
          {selectedTree && (
            <button
              onClick={handleStartOver}
              style={{ padding: '0.5rem 1rem', background: '#ef4444', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.9rem', fontWeight: '500' }}
            >
              🔄 Start Over
            </button>
          )}
        </div>

        {/* Progress (one-step-at-a-time mode) */}
        {showWizardMode && treeInfo && !result && (
          <div style={{maxWidth: '800px', margin: '0 auto 2rem', background: 'white', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 2px 4px rgba(0,0,0,0.1)'}}>
            <div style={{marginBottom: '1rem', fontSize: '0.9rem', fontWeight: '600', color: '#374151'}}>
              Step {currentStep + 1} of {steps.length}: {STEP_TITLES[stepKey]}
            </div>
            <div style={{width: '100%', height: '8px', background: '#e5e7eb', borderRadius: '4px', overflow: 'hidden'}}>
              <div style={{ width: `${((currentStep + 1) / steps.length) * 100}%`, height: '100%', background: 'linear-gradient(90deg, #3b82f6 0%, #2563eb 100%)', transition: 'width 0.3s ease' }} />
            </div>
          </div>
        )}

        {/* Tree selection */}
        {questionnaire && <QuestionnaireWalk key={questionnaire.tree.id} questionnaire={questionnaire} onClose={() => setQuestionnaire(null)} />}

        <section className={styles.section} style={{display: visible('tree') && !result && !questionnaire ? 'block' : 'none'}}>
          <h2>Select a decision tree</h2>
          <ClinicalReviewNotice notice={treesNotice} />
          <p style={{ margin: '0 0 1rem', color: '#4b5563', fontSize: '0.9rem' }}>
            These {trees.length || ''} trees have branching decision steps. Each later step shows only the
            findings this tree&apos;s branches check, in the tree&apos;s own words. Leave anything you did not
            assess unticked.
          </p>
          {heldBack.length > 0 && (
            <div role="note" style={{ padding: '0.6rem 0.9rem', margin: '0 0 1rem', background: '#f3f4f6', border: '1px solid #d1d5db', borderRadius: '8px', color: '#374151', fontSize: '0.875rem' }}>
              {heldBack.length === 1 ? 'One tree is' : `${heldBack.length} trees are`} temporarily unavailable pending
              content review: {heldBack.map(t => t.title || t.id).join(', ')}.
            </div>
          )}
          {treesError && <div role="alert" style={{ color: '#b91c1c' }}>{treesError}</div>}
          <div className={styles.treeSelection}>
            {trees.map(tree => (
              <button
                key={tree.id}
                className={`${styles.treeButton} ${selectedTree === tree.id ? styles.active : ''}`}
                onClick={() => selectTree(tree.id)}
              >
                {tree.title}
                {tree.review_status_label && (
                  <span style={{ display: 'block', fontSize: '0.7rem', fontWeight: 500, opacity: 0.8 }}>
                    {tree.review_status_label}
                  </span>
                )}
              </button>
            ))}
          </div>
          {qTrees.length > 0 && (
            <>
              <h3 style={{ marginTop: '1.5rem' }}>Question-by-question trees</h3>
              <p style={{ margin: '0 0 1rem', color: '#4b5563', fontSize: '0.9rem' }}>
                These {qTrees.length} trees ask one question at a time and end at an outcome step, in the tree&apos;s own words.
              </p>
              <div className={styles.treeSelection}>
                {qTrees.map(tree => (
                  <button key={tree.id} className={styles.treeButton} onClick={() => selectQuestionnaire(tree.id)}>
                    {tree.title}
                    {tree.review_status_label && (
                      <span style={{ display: 'block', fontSize: '0.7rem', fontWeight: 500, opacity: 0.8 }}>
                        {tree.review_status_label}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </>
          )}
          {inputsError && <div role="alert" style={{ color: '#b91c1c', marginTop: '1rem' }}>{inputsError}</div>}
        </section>

        {treeInfo && !result && (
          <>
            {(stepKey !== 'tree' || !showWizardMode) && (
              <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                {reviewHeader}
                <ClinicalReviewNotice notice={treeInfo.clinical_review_notice} />
              </div>
            )}

            {inputs.uses_age || inputs.uses_onset_hours || inputs.uses_diagnosis ? (
              <section className={styles.section} style={{display: visible('patient') ? 'block' : 'none'}}>
                <h2>Patient information</h2>
                <div className={styles.formGrid}>
                  {inputs.uses_age && (
                    <div className={styles.formGroup}>
                      <label htmlFor="diagnose-age">Age (years)</label>
                      <input id="diagnose-age" type="number" value={answers.age} onChange={(e) => setAnswers({...answers, age: e.target.value})} placeholder="Not assessed" />
                    </div>
                  )}
                  {inputs.uses_onset_hours && (
                    <div className={styles.formGroup}>
                      <label htmlFor="diagnose-onset">Onset (hours ago)</label>
                      <input id="diagnose-onset" type="number" value={answers.onset_hours} onChange={(e) => setAnswers({...answers, onset_hours: e.target.value})} placeholder="Not assessed" />
                    </div>
                  )}
                  {inputs.uses_diagnosis && (
                    <div className={styles.formGroup}>
                      <label htmlFor="diagnose-diagnosis">Working diagnosis</label>
                      <input id="diagnose-diagnosis" type="text" value={answers.diagnosis} onChange={(e) => setAnswers({...answers, diagnosis: e.target.value})} placeholder="Optional" />
                    </div>
                  )}
                </div>
              </section>
            ) : null}

            {inputs.symptoms.length > 0 && (
              <section className={styles.section} style={{display: visible('symptoms') ? 'block' : 'none'}}>
                <h2>Symptoms</h2>
                <CheckboxGroup options={inputs.symptoms} selected={answers.symptoms} onToggle={setList('symptoms')} />
              </section>
            )}

            {inputs.exam.length > 0 && (
              <section className={styles.section} style={{display: visible('exam') ? 'block' : 'none'}}>
                <h2>Examination findings</h2>
                <CheckboxGroup options={inputs.exam} selected={answers.exam} onToggle={setList('exam')} />
              </section>
            )}

            {inputs.red_flags.length > 0 && (
              <section className={`${styles.section} ${styles.redFlags}`} style={{display: visible('red_flags') ? 'block' : 'none'}}>
                <h2>Red flags ⚠️</h2>
                <CheckboxGroup options={inputs.red_flags} selected={answers.red_flags} onToggle={setList('red_flags')} />
              </section>
            )}

            {steps.includes('findings') && (
              <section className={styles.section} style={{display: visible('findings') ? 'block' : 'none'}}>
                <h2>Other findings</h2>
                {Object.keys(inputs.findings).length > 0 && (
                  <div className={styles.formGrid}>
                    {Object.entries(inputs.findings).map(([name, values]) => (
                      <div key={name} className={styles.formGroup}>
                        <label htmlFor={`finding-${name}`}>{displayLabel(name)}</label>
                        <select
                          id={`finding-${name}`}
                          value={answers.findings[name] === undefined ? NOT_ASSESSED : findingOptionKey(answers.findings[name])}
                          onChange={(e) => setFinding(name, e.target.value)}
                        >
                          <option value={NOT_ASSESSED}>Not assessed</option>
                          {values.map(value => (
                            <option key={findingOptionKey(value)} value={findingOptionKey(value)}>{displayLabel(value)}</option>
                          ))}
                        </select>
                      </div>
                    ))}
                  </div>
                )}
                {inputs.patient_characteristics.length > 0 && (
                  <>
                    <h3>Patient characteristics</h3>
                    <CheckboxGroup options={inputs.patient_characteristics} selected={answers.patient_characteristics} onToggle={setList('patient_characteristics')} />
                  </>
                )}
                {inputs.no_red_flags.length > 0 && (
                  <>
                    <h3>Confirmed on assessment</h3>
                    <CheckboxGroup options={inputs.no_red_flags} selected={answers.no_red_flags} onToggle={setList('no_red_flags')} />
                  </>
                )}
              </section>
            )}

            {/* Patient context modifiers (last step) */}
            <section className={styles.section} style={{display: !showWizardMode || isLastStep ? 'block' : 'none'}}>
              <PatientContext value={patientContext} onChange={setPatientContext} apiBase={getApiBase()} />
            </section>

            <section className={styles.actions}>
              {showWizardMode && (
                <button onClick={() => setCurrentStep(currentStep - 1)} disabled={currentStep === 0} style={{ ...navButton(currentStep > 0, '#6b7280'), flex: 1 }}>
                  ← Previous
                </button>
              )}
              {showWizardMode && !isLastStep ? (
                <button onClick={() => setCurrentStep(currentStep + 1)} style={{ ...navButton(true, '#3b82f6'), flex: 2 }}>
                  Continue →
                </button>
              ) : (
                <button onClick={handleEvaluate} disabled={loading} style={{ ...navButton(!loading, '#10b981'), flex: 2 }}>
                  {loading ? '🔄 Walking the tree...' : '🩺 Walk the tree'}
                </button>
              )}
            </section>
            {evaluateError && <div role="alert" style={{ color: '#b91c1c', textAlign: 'center' }}>{evaluateError}</div>}
          </>
        )}

        {/* Results */}
        {result && (
          <section className={`${styles.section} ${styles.results}`}>
            <h2>📋 Decision tree walk</h2>
            {result.tree && (
              <p style={{ margin: '0 0 0.75rem', display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
                <strong>{result.tree.title || result.tree.id}</strong>
                <ReviewStatusBadge status={result.tree.review_status} label={result.tree.review_status_label} />
              </p>
            )}
            <ClinicalReviewNotice notice={result.error ? undefined : result.clinical_review_notice} />
            {result.error && (
              <div role="alert" style={{ padding: '0.75rem 1rem', margin: '0 0 1rem', background: '#fef2f2', border: '1px solid #ef4444', borderRadius: '8px', color: '#7f1d1d' }}>
                <strong>This tree could not be walked.</strong> {result.error}
              </div>
            )}
            {result.warning && (
              <div role="alert" style={{ padding: '0.75rem 1rem', margin: '0 0 1rem', background: '#fffbeb', border: '1px solid #f59e0b', borderRadius: '8px', color: '#78350f' }}>
                <strong>{result.evaluated === false ? 'Not evaluated automatically.' : 'Note:'}</strong> {result.warning}
              </div>
            )}
            {stopMessage && (
              <div role="status" style={{ padding: '0.75rem 1rem', margin: '0 0 1rem', background: '#eff6ff', border: '1px solid #3b82f6', borderRadius: '8px', color: '#1e3a8a' }}>
                {stopMessage}
              </div>
            )}

            {result.path && result.path.length > 0 && (
              <div className={styles.resultCard}>
                <h3>✓ Path: {result.path.map(displayLabel).join(' → ')}</h3>

                {result.provisional_dx && result.provisional_dx.length > 0 && (
                  <div className={styles.resultSection}>
                    <h4>🎯 Diagnoses to consider (from the tree):</h4>
                    <ul>{itemsWithSource(result, 'provisional_dx').map((item, i) => <li key={i}>{item.text}{item.nodes.length > 0 && <span style={{ color: '#6b7280', fontSize: '0.85rem' }}> (from: {item.nodes.map(displayLabel).join(', ')})</span>}</li>)}</ul>
                    {result.tree && result.tree.icd10 && result.tree.icd10.length > 0 && (
                      <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: '#f9fafb', borderRadius: '6px', borderLeft: '3px solid #0f766e' }}>
                        <strong style={{color: '#0f766e'}}>📋 ICD-10:</strong>{' '}
                        <span style={{fontFamily: 'monospace', fontSize: '0.9rem'}}>{result.tree.icd10.join(', ')}</span>
                      </div>
                    )}
                  </div>
                )}

                {result.tests && result.tests.length > 0 && (
                  <div className={styles.resultSection}>
                    <h4>🔬 Tests listed on this path:</h4>
                    <ul>{itemsWithSource(result, 'tests').map((item, i) => <li key={i}>{item.text}{item.nodes.length > 0 && <span style={{ color: '#6b7280', fontSize: '0.85rem' }}> (from: {item.nodes.map(displayLabel).join(', ')})</span>}</li>)}</ul>
                  </div>
                )}

                {result.referrals && result.referrals.length > 0 && (
                  <div className={styles.resultSection}>
                    <h4>👨‍⚕️ Referrals listed on this path:</h4>
                    <ul>{itemsWithSource(result, 'referrals').map((item, i) => <li key={i}>{item.text}{item.nodes.length > 0 && <span style={{ color: '#6b7280', fontSize: '0.85rem' }}> (from: {item.nodes.map(displayLabel).join(', ')})</span>}</li>)}</ul>
                  </div>
                )}

                {result.trace && result.trace.length > 0 && (
                  <details className={styles.trace}>
                    <summary>Why the walk went this way</summary>
                    <ul>{result.trace.map((step, i) => <li key={i}>{step}</li>)}</ul>
                  </details>
                )}
              </div>
            )}
            {result.context && <ContextResults contextData={result.context} />}
            {(!result.path || result.path.length === 0) && !result.error && (
              <div className={styles.noMatch}>
                <p>No decision path was produced for these answers.</p>
              </div>
            )}
            <div className={styles.actions}>
              <button className={styles.resetButton} onClick={() => setResult(null)}>← Change answers</button>
            </div>
          </section>
        )}

        {!selectedTree && !questionnaire && (
          <div className={styles.emptyState}>
            <p>👆 Select a decision tree above to begin</p>
          </div>
        )}
      </div>
    </div>
  )
}
