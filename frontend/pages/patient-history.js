import React, { useState, useEffect } from 'react'
import styles from '../styles/PatientHistory.module.css'

export default function PatientHistory() {
  const [apiBase, setApiBase] = useState('')
  const [showNav, setShowNav] = useState(false)
  const [patientData, setPatientData] = useState({
    patient_id: '',
    patient_name: '',
    age: '',
    gender: '',
    visit_notes: [],
    diagnostic_tests: [],
    history_and_physicals: [],
    procedures: [],
    imaging_studies: [],
    active_conditions: [],
    current_medications: [],
    allergies: [],
    family_history: '',
    social_history: ''
  })
  
  const [currentSection, setCurrentSection] = useState('demographics')
  const [savedMessage, setSavedMessage] = useState('')
  const [medicationSafetyResult, setMedicationSafetyResult] = useState(null)
  const [showSafetyModal, setShowSafetyModal] = useState(false)
  const [checkingSafety, setCheckingSafety] = useState(false)

  // Get API base
  useEffect(() => {
    const runtimeConfig = (typeof window !== 'undefined' && window.__RUNTIME_CONFIG) ? window.__RUNTIME_CONFIG : null
    const base = runtimeConfig?.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com'
    setApiBase(base.replace(/\/$/, ''))
  }, [])

  // Dropdown options
  const VISIT_NOTE_TYPES = [
    'Admission Note',
    'Consultation Note',
    'Discharge Summary',
    'Emergency Department Note',
    'Follow-up Note',
    'Procedure Note',
    'Progress Note',
    'Referral Note'
  ]

  const SPECIALTIES = [
    'Cardiology',
    'Critical Care',
    'Emergency Medicine',
    'Endocrinology',
    'Family Medicine',
    'Gastroenterology',
    'Hematology/Oncology',
    'Hospitalist',
    'Infectious Disease',
    'Internal Medicine',
    'Nephrology',
    'Neurology',
    'Pulmonology',
    'Rheumatology'
  ]

  const TEST_TYPES = [
    'Chemistry',
    'Culture',
    'Genetic',
    'Hematology',
    'Laboratory',
    'Microbiology',
    'Pathology',
    'Serology',
    'Toxicology'
  ]

  const COMMON_LAB_TESTS = [
    'Arterial Blood Gas (ABG)',
    'Basic Metabolic Panel (BMP)',
    'Blood Culture',
    'BNP/NT-proBNP',
    'Complete Blood Count (CBC)',
    'Comprehensive Metabolic Panel (CMP)',
    'Creatine Kinase (CK/CK-MB)',
    'C-Reactive Protein (CRP)',
    'D-Dimer',
    'Erythrocyte Sedimentation Rate (ESR)',
    'Hemoglobin A1c',
    'Lipid Panel',
    'Liver Function Tests (LFTs)',
    'Partial Thromboplastin Time (PTT)',
    'Prothrombin Time (PT/INR)',
    'Troponin I/T',
    'TSH (Thyroid)',
    'Urinalysis',
    'Urine Culture',
    'Venous Blood Gas (VBG)'
  ]

  const IMAGING_MODALITIES = [
    'Angiography',
    'CT Scan',
    'DEXA Scan',
    'Echocardiography',
    'Mammography',
    'MRI',
    'Nuclear Medicine',
    'PET Scan',
    'Ultrasound',
    'X-Ray'
  ]

  const BODY_SITES = [
    'Abdomen',
    'Chest',
    'Head/Brain',
    'Heart',
    'Kidneys',
    'Liver',
    'Lower Extremity',
    'Lungs',
    'Neck',
    'Pancreas',
    'Pelvis',
    'Spine',
    'Upper Extremity'
  ]

  const COMMON_CONDITIONS = [
    'Anxiety Disorder',
    'Asthma',
    'Atrial Fibrillation',
    'Cancer (Active)',
    'Cancer (History)',
    'Chronic Kidney Disease',
    'Chronic Pain',
    'COPD',
    'Coronary Artery Disease',
    'Deep Vein Thrombosis (DVT)',
    'Depression',
    'GERD',
    'Heart Failure',
    'Hyperlipidemia',
    'Hypertension',
    'Hyperthyroidism',
    'Hypothyroidism',
    'Osteoarthritis',
    'Pulmonary Embolism (PE)',
    'Rheumatoid Arthritis',
    'Sleep Apnea',
    'Stroke (CVA)',
    'TIA',
    'Type 1 Diabetes Mellitus',
    'Type 2 Diabetes Mellitus'
  ]

  const COMMON_MEDICATIONS = [
    'Albuterol',
    'Amlodipine',
    'Apixaban',
    'Aspirin',
    'Atorvastatin',
    'Clopidogrel',
    'Furosemide',
    'Gabapentin',
    'Hydrochlorothiazide',
    'Insulin (various)',
    'Levothyroxine',
    'Lisinopril',
    'Losartan',
    'Metformin',
    'Metoprolol',
    'Omeprazole',
    'Pantoprazole',
    'Prednisone',
    'Sertraline',
    'Warfarin'
  ]

  const COMMON_ALLERGIES = [
    'Aspirin',
    'Codeine',
    'Contrast dye',
    'Eggs',
    'Iodine',
    'Latex',
    'Milk/Dairy',
    'Morphine',
    'NSAIDs',
    'Peanuts',
    'Penicillin',
    'Shellfish',
    'Soy',
    'Sulfa drugs',
    'Tree nuts',
    'Wheat'
  ]

  const ALLERGY_REACTIONS = [
    'Anaphylaxis',
    'Diarrhea',
    'Difficulty breathing',
    'Hives',
    'Itching',
    'Nausea/Vomiting',
    'Rash',
    'Swelling',
    'Unknown'
  ]

  // Add new visit note
  const addVisitNote = () => {
    const newNote = {
      id: Date.now(),
      date: '',
      type: '',
      author: '',
      specialty: '',
      content: ''
    }
    setPatientData(prev => ({
      ...prev,
      visit_notes: [...prev.visit_notes, newNote]
    }))
  }

  const removeVisitNote = (id) => {
    setPatientData(prev => ({
      ...prev,
      visit_notes: prev.visit_notes.filter(note => note.id !== id)
    }))
  }

  const updateVisitNote = (id, field, value) => {
    setPatientData(prev => ({
      ...prev,
      visit_notes: prev.visit_notes.map(note =>
        note.id === id ? { ...note, [field]: value } : note
      )
    }))
  }

  // Add diagnostic test
  const addDiagnosticTest = () => {
    const newTest = {
      id: Date.now(),
      date: '',
      test_name: '',
      test_type: '',
      result: '',
      abnormal: false,
      critical: false,
      interpretation: ''
    }
    setPatientData(prev => ({
      ...prev,
      diagnostic_tests: [...prev.diagnostic_tests, newTest]
    }))
  }

  const removeDiagnosticTest = (id) => {
    setPatientData(prev => ({
      ...prev,
      diagnostic_tests: prev.diagnostic_tests.filter(test => test.id !== id)
    }))
  }

  const updateDiagnosticTest = (id, field, value) => {
    setPatientData(prev => ({
      ...prev,
      diagnostic_tests: prev.diagnostic_tests.map(test =>
        test.id === id ? { ...test, [field]: value } : test
      )
    }))
  }

  // Add H&P
  const addHP = () => {
    const newHP = {
      id: Date.now(),
      date: '',
      author: '',
      chief_complaint: '',
      history_of_present_illness: '',
      past_medical_history: [],
      past_surgical_history: [],
      medications: [],
      allergies: [],
      family_history: '',
      social_history: '',
      review_of_systems: '',
      physical_exam: '',
      assessment: '',
      plan: ''
    }
    setPatientData(prev => ({
      ...prev,
      history_and_physicals: [...prev.history_and_physicals, newHP]
    }))
  }

  const removeHP = (id) => {
    setPatientData(prev => ({
      ...prev,
      history_and_physicals: prev.history_and_physicals.filter(hp => hp.id !== id)
    }))
  }

  const updateHP = (id, field, value) => {
    setPatientData(prev => ({
      ...prev,
      history_and_physicals: prev.history_and_physicals.map(hp =>
        hp.id === id ? { ...hp, [field]: value } : hp
      )
    }))
  }

  // Add procedure
  const addProcedure = () => {
    const newProc = {
      id: Date.now(),
      date: '',
      procedure_name: '',
      indication: '',
      outcome: '',
      complications: '',
      operator: ''
    }
    setPatientData(prev => ({
      ...prev,
      procedures: [...prev.procedures, newProc]
    }))
  }

  const removeProcedure = (id) => {
    setPatientData(prev => ({
      ...prev,
      procedures: prev.procedures.filter(proc => proc.id !== id)
    }))
  }

  const updateProcedure = (id, field, value) => {
    setPatientData(prev => ({
      ...prev,
      procedures: prev.procedures.map(proc =>
        proc.id === id ? { ...proc, [field]: value } : proc
      )
    }))
  }

  // Add imaging study
  const addImagingStudy = () => {
    const newImaging = {
      id: Date.now(),
      date: '',
      modality: '',
      body_site: '',
      indication: '',
      findings: '',
      impression: '',
      radiologist: ''
    }
    setPatientData(prev => ({
      ...prev,
      imaging_studies: [...prev.imaging_studies, newImaging]
    }))
  }

  const removeImagingStudy = (id) => {
    setPatientData(prev => ({
      ...prev,
      imaging_studies: prev.imaging_studies.filter(img => img.id !== id)
    }))
  }

  const updateImagingStudy = (id, field, value) => {
    setPatientData(prev => ({
      ...prev,
      imaging_studies: prev.imaging_studies.map(img =>
        img.id === id ? { ...img, [field]: value } : img
      )
    }))
  }

  // Add condition
  const addCondition = () => {
    const newCondition = {
      id: Date.now(),
      code: '',
      status: 'active',
      recorded_date: '',
      onset: ''
    }
    setPatientData(prev => ({
      ...prev,
      active_conditions: [...prev.active_conditions, newCondition]
    }))
  }

  const removeCondition = (id) => {
    setPatientData(prev => ({
      ...prev,
      active_conditions: prev.active_conditions.filter(cond => cond.id !== id)
    }))
  }

  const updateCondition = (id, field, value) => {
    setPatientData(prev => ({
      ...prev,
      active_conditions: prev.active_conditions.map(cond =>
        cond.id === id ? { ...cond, [field]: value } : cond
      )
    }))
  }

  // Add medication
  const addMedication = () => {
    const newMed = {
      id: Date.now(),
      name: '',
      status: 'active',
      dosage: '',
      date_prescribed: ''
    }
    setPatientData(prev => ({
      ...prev,
      current_medications: [...prev.current_medications, newMed]
    }))
  }

  const removeMedication = (id) => {
    setPatientData(prev => ({
      ...prev,
      current_medications: prev.current_medications.filter(med => med.id !== id)
    }))
  }

  const updateMedication = (id, field, value) => {
    setPatientData(prev => ({
      ...prev,
      current_medications: prev.current_medications.map(med =>
        med.id === id ? { ...med, [field]: value } : med
      )
    }))
  }

  // Add allergy
  const addAllergy = () => {
    const newAllergy = {
      id: Date.now(),
      allergen: '',
      reaction: ''
    }
    setPatientData(prev => ({
      ...prev,
      allergies: [...prev.allergies, newAllergy]
    }))
  }

  const removeAllergy = (id) => {
    setPatientData(prev => ({
      ...prev,
      allergies: prev.allergies.filter(allergy => allergy.id !== id)
    }))
  }

  const updateAllergy = (id, field, value) => {
    setPatientData(prev => ({
      ...prev,
      allergies: prev.allergies.map(allergy =>
        allergy.id === id ? { ...allergy, [field]: value } : allergy
      )
    }))
  }

  // Check medication safety
  const checkMedicationSafety = async () => {
    setCheckingSafety(true)
    try {
      const activeMeds = patientData.current_medications
        .filter(med => med.status === 'active' && med.name && med.name !== '')
        .map(med => med.name)
      
      if (activeMeds.length === 0) {
        alert('Please add at least one active medication to check safety.')
        setCheckingSafety(false)
        return
      }

      const conditions = patientData.active_conditions
        .filter(cond => cond.condition_name && cond.condition_name !== '')
        .map(cond => cond.condition_name)
      
      const allergies = patientData.allergies
        .filter(allergy => allergy.allergen && allergy.allergen !== '')
        .map(allergy => allergy.allergen)

      const response = await fetch(`${apiBase}/diagnostic/medication-safety-check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_medications: activeMeds,
          conditions: conditions,
          known_allergies: allergies
        })
      })

      if (response.ok) {
        const result = await response.json()
        setMedicationSafetyResult(result)
        setShowSafetyModal(true)
      } else {
        alert('Failed to check medication safety. Please try again.')
      }
    } catch (err) {
      console.error('Medication safety check failed:', err)
      alert('Error checking medication safety. Please check your connection.')
    } finally {
      setCheckingSafety(false)
    }
  }

  // Save data
  const handleSave = async () => {
    try {
      const response = await fetch(`${apiBase}/diagnostic/manual-history`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patientData)
      })
      
      if (response.ok) {
        setSavedMessage('✓ Patient history saved successfully!')
        setTimeout(() => setSavedMessage(''), 3000)
      } else {
        setSavedMessage('✗ Failed to save patient history')
      }
    } catch (err) {
      console.error('Save failed:', err)
      setSavedMessage('✗ Error saving patient history')
    }
  }

  const sections = [
    { id: 'demographics', label: 'Demographics', icon: '👤' },
    { id: 'visit_notes', label: 'Visit Notes', icon: '📋' },
    { id: 'diagnostic_tests', label: 'Diagnostic Tests', icon: '🧪' },
    { id: 'history_physicals', label: 'H&P', icon: '📝' },
    { id: 'procedures', label: 'Procedures', icon: '🔬' },
    { id: 'imaging', label: 'Imaging', icon: '🏥' },
    { id: 'conditions', label: 'Conditions', icon: '📊' },
    { id: 'medications', label: 'Medications', icon: '💊' },
    { id: 'allergies', label: 'Allergies', icon: '⚠️' },
    { id: 'history', label: 'Family/Social History', icon: '👨‍👩‍👧' }
  ]

  return (
    <div className={styles.container}>
      {/* Navigation Dropdown */}
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto 1rem'
      }}>
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
              🔍 Symptom Search
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

      <header className={styles.header}>
        <div className={styles.headerContent} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <img src="/logo.png" alt="RealDiag Logo" style={{ height: '50px' }} />
            <div>
              <h1 style={{ marginBottom: '0.5rem' }}>Manual Patient History Entry</h1>
              <p style={{ margin: 0 }}>For non-EMR instances: Enter comprehensive patient history using dropdown lists</p>
            </div>
          </div>
          <a href="/" style={{
            padding: '8px 16px',
            background: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '6px',
            fontSize: '14px',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            whiteSpace: 'nowrap'
          }}>
            🏠 Home
          </a>
        </div>
      </header>

      <div className={styles.main}>
        {/* Section Navigation */}
        <nav className={styles.sectionNav}>
          {sections.map(section => (
            <button
              key={section.id}
              className={currentSection === section.id ? styles.activeSection : styles.inactiveSection}
              onClick={() => setCurrentSection(section.id)}
            >
              <span className={styles.sectionIcon}>{section.icon}</span>
              <span className={styles.sectionLabel}>{section.label}</span>
            </button>
          ))}
        </nav>

        <div className={styles.content}>
          {/* Demographics Section */}
          {currentSection === 'demographics' && (
            <div className={styles.section}>
              <h2>👤 Patient Demographics</h2>
              <div className={styles.formGrid}>
                <div className={styles.formGroup}>
                  <label>Patient ID / MRN</label>
                  <input
                    type="text"
                    value={patientData.patient_id}
                    onChange={(e) => setPatientData({...patientData, patient_id: e.target.value})}
                    placeholder="Enter patient ID"
                  />
                </div>
                <div className={styles.formGroup}>
                  <label>Patient Name</label>
                  <input
                    type="text"
                    value={patientData.patient_name}
                    onChange={(e) => setPatientData({...patientData, patient_name: e.target.value})}
                    placeholder="Enter patient name"
                  />
                </div>
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
                  <label>Gender</label>
                  <select
                    value={patientData.gender}
                    onChange={(e) => setPatientData({...patientData, gender: e.target.value})}
                  >
                    <option value="">Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                    <option value="unknown">Unknown</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Visit Notes Section */}
          {currentSection === 'visit_notes' && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>📋 Visit Notes</h2>
                <button onClick={addVisitNote} className={styles.addButton}>+ Add Visit Note</button>
              </div>
              
              {patientData.visit_notes.length === 0 && (
                <p className={styles.emptyState}>No visit notes yet. Click "+ Add Visit Note" to begin.</p>
              )}

              {patientData.visit_notes.map(note => (
                <div key={note.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>Visit Note</h3>
                    <button onClick={() => removeVisitNote(note.id)} className={styles.removeButton}>✕</button>
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <label>Date</label>
                      <input
                        type="date"
                        value={note.date}
                        onChange={(e) => updateVisitNote(note.id, 'date', e.target.value)}
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Note Type</label>
                      <select
                        value={note.type}
                        onChange={(e) => updateVisitNote(note.id, 'type', e.target.value)}
                      >
                        <option value="">Select type</option>
                        {VISIT_NOTE_TYPES.map(type => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </select>
                    </div>
                    <div className={styles.formGroup}>
                      <label>Author / Provider</label>
                      <input
                        type="text"
                        value={note.author}
                        onChange={(e) => updateVisitNote(note.id, 'author', e.target.value)}
                        placeholder="Dr. Name"
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Specialty</label>
                      <select
                        value={note.specialty}
                        onChange={(e) => updateVisitNote(note.id, 'specialty', e.target.value)}
                      >
                        <option value="">Select specialty</option>
                        {SPECIALTIES.map(spec => (
                          <option key={spec} value={spec}>{spec}</option>
                        ))}
                      </select>
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Clinical Note Content</label>
                      <textarea
                        value={note.content}
                        onChange={(e) => updateVisitNote(note.id, 'content', e.target.value)}
                        rows={6}
                        placeholder="Enter clinical note..."
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Diagnostic Tests Section */}
          {currentSection === 'diagnostic_tests' && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>🧪 Diagnostic Tests</h2>
                <button onClick={addDiagnosticTest} className={styles.addButton}>+ Add Test</button>
              </div>

              {patientData.diagnostic_tests.length === 0 && (
                <p className={styles.emptyState}>No diagnostic tests yet. Click "+ Add Test" to begin.</p>
              )}

              {patientData.diagnostic_tests.map(test => (
                <div key={test.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>Diagnostic Test</h3>
                    <button onClick={() => removeDiagnosticTest(test.id)} className={styles.removeButton}>✕</button>
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <label>Date</label>
                      <input
                        type="date"
                        value={test.date}
                        onChange={(e) => updateDiagnosticTest(test.id, 'date', e.target.value)}
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Test Name</label>
                      <select
                        value={test.test_name}
                        onChange={(e) => updateDiagnosticTest(test.id, 'test_name', e.target.value)}
                      >
                        <option value="">Select test</option>
                        {COMMON_LAB_TESTS.map(testName => (
                          <option key={testName} value={testName}>{testName}</option>
                        ))}
                        <option value="Other">Other (enter below)</option>
                      </select>
                    </div>
                    {test.test_name === 'Other' && (
                      <div className={styles.formGroup}>
                        <label>Custom Test Name</label>
                        <input
                          type="text"
                          placeholder="Enter test name"
                          onChange={(e) => updateDiagnosticTest(test.id, 'test_name', e.target.value)}
                        />
                      </div>
                    )}
                    <div className={styles.formGroup}>
                      <label>Test Type</label>
                      <select
                        value={test.test_type}
                        onChange={(e) => updateDiagnosticTest(test.id, 'test_type', e.target.value)}
                      >
                        <option value="">Select type</option>
                        {TEST_TYPES.map(type => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </select>
                    </div>
                    <div className={styles.formGroup}>
                      <label>Result</label>
                      <input
                        type="text"
                        value={test.result}
                        onChange={(e) => updateDiagnosticTest(test.id, 'result', e.target.value)}
                        placeholder="Enter result value"
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>
                        <input
                          type="checkbox"
                          checked={test.abnormal}
                          onChange={(e) => updateDiagnosticTest(test.id, 'abnormal', e.target.checked)}
                        />
                        {' '}Abnormal
                      </label>
                      <label>
                        <input
                          type="checkbox"
                          checked={test.critical}
                          onChange={(e) => updateDiagnosticTest(test.id, 'critical', e.target.checked)}
                        />
                        {' '}Critical
                      </label>
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Interpretation</label>
                      <textarea
                        value={test.interpretation}
                        onChange={(e) => updateDiagnosticTest(test.id, 'interpretation', e.target.value)}
                        rows={3}
                        placeholder="Clinical interpretation..."
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* H&P Section */}
          {currentSection === 'history_physicals' && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>📝 History & Physical Examinations</h2>
                <button onClick={addHP} className={styles.addButton}>+ Add H&P</button>
              </div>

              {patientData.history_and_physicals.length === 0 && (
                <p className={styles.emptyState}>No H&P documents yet. Click "+ Add H&P" to begin.</p>
              )}

              {patientData.history_and_physicals.map(hp => (
                <div key={hp.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>History & Physical</h3>
                    <button onClick={() => removeHP(hp.id)} className={styles.removeButton}>✕</button>
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <label>Date</label>
                      <input
                        type="date"
                        value={hp.date}
                        onChange={(e) => updateHP(hp.id, 'date', e.target.value)}
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Author / Provider</label>
                      <input
                        type="text"
                        value={hp.author}
                        onChange={(e) => updateHP(hp.id, 'author', e.target.value)}
                        placeholder="Dr. Name"
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Chief Complaint</label>
                      <input
                        type="text"
                        value={hp.chief_complaint}
                        onChange={(e) => updateHP(hp.id, 'chief_complaint', e.target.value)}
                        placeholder="e.g., Chest pain"
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>History of Present Illness (HPI)</label>
                      <textarea
                        value={hp.history_of_present_illness}
                        onChange={(e) => updateHP(hp.id, 'history_of_present_illness', e.target.value)}
                        rows={4}
                        placeholder="Describe the present illness..."
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Review of Systems (ROS)</label>
                      <textarea
                        value={hp.review_of_systems}
                        onChange={(e) => updateHP(hp.id, 'review_of_systems', e.target.value)}
                        rows={4}
                        placeholder="Systematic review..."
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Physical Exam</label>
                      <textarea
                        value={hp.physical_exam}
                        onChange={(e) => updateHP(hp.id, 'physical_exam', e.target.value)}
                        rows={4}
                        placeholder="Physical examination findings..."
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Assessment</label>
                      <textarea
                        value={hp.assessment}
                        onChange={(e) => updateHP(hp.id, 'assessment', e.target.value)}
                        rows={3}
                        placeholder="Clinical assessment..."
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Plan</label>
                      <textarea
                        value={hp.plan}
                        onChange={(e) => updateHP(hp.id, 'plan', e.target.value)}
                        rows={3}
                        placeholder="Treatment plan..."
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Procedures Section */}
          {currentSection === 'procedures' && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>🔬 Procedures</h2>
                <button onClick={addProcedure} className={styles.addButton}>+ Add Procedure</button>
              </div>

              {patientData.procedures.length === 0 && (
                <p className={styles.emptyState}>No procedures yet. Click "+ Add Procedure" to begin.</p>
              )}

              {patientData.procedures.map(proc => (
                <div key={proc.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>Procedure</h3>
                    <button onClick={() => removeProcedure(proc.id)} className={styles.removeButton}>✕</button>
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <label>Date</label>
                      <input
                        type="date"
                        value={proc.date}
                        onChange={(e) => updateProcedure(proc.id, 'date', e.target.value)}
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Procedure Name</label>
                      <input
                        type="text"
                        value={proc.procedure_name}
                        onChange={(e) => updateProcedure(proc.id, 'procedure_name', e.target.value)}
                        placeholder="e.g., Coronary angiography"
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Operator / Surgeon</label>
                      <input
                        type="text"
                        value={proc.operator}
                        onChange={(e) => updateProcedure(proc.id, 'operator', e.target.value)}
                        placeholder="Dr. Name"
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Indication</label>
                      <textarea
                        value={proc.indication}
                        onChange={(e) => updateProcedure(proc.id, 'indication', e.target.value)}
                        rows={2}
                        placeholder="Reason for procedure..."
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Outcome</label>
                      <textarea
                        value={proc.outcome}
                        onChange={(e) => updateProcedure(proc.id, 'outcome', e.target.value)}
                        rows={3}
                        placeholder="Procedure outcome..."
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Complications (if any)</label>
                      <textarea
                        value={proc.complications}
                        onChange={(e) => updateProcedure(proc.id, 'complications', e.target.value)}
                        rows={2}
                        placeholder="None or describe complications..."
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Imaging Section */}
          {currentSection === 'imaging' && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>🏥 Imaging Studies</h2>
                <button onClick={addImagingStudy} className={styles.addButton}>+ Add Imaging</button>
              </div>

              {patientData.imaging_studies.length === 0 && (
                <p className={styles.emptyState}>No imaging studies yet. Click "+ Add Imaging" to begin.</p>
              )}

              {patientData.imaging_studies.map(img => (
                <div key={img.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>Imaging Study</h3>
                    <button onClick={() => removeImagingStudy(img.id)} className={styles.removeButton}>✕</button>
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <label>Date</label>
                      <input
                        type="date"
                        value={img.date}
                        onChange={(e) => updateImagingStudy(img.id, 'date', e.target.value)}
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Modality</label>
                      <select
                        value={img.modality}
                        onChange={(e) => updateImagingStudy(img.id, 'modality', e.target.value)}
                      >
                        <option value="">Select modality</option>
                        {IMAGING_MODALITIES.map(mod => (
                          <option key={mod} value={mod}>{mod}</option>
                        ))}
                      </select>
                    </div>
                    <div className={styles.formGroup}>
                      <label>Body Site</label>
                      <select
                        value={img.body_site}
                        onChange={(e) => updateImagingStudy(img.id, 'body_site', e.target.value)}
                      >
                        <option value="">Select body site</option>
                        {BODY_SITES.map(site => (
                          <option key={site} value={site}>{site}</option>
                        ))}
                      </select>
                    </div>
                    <div className={styles.formGroup}>
                      <label>Radiologist</label>
                      <input
                        type="text"
                        value={img.radiologist}
                        onChange={(e) => updateImagingStudy(img.id, 'radiologist', e.target.value)}
                        placeholder="Dr. Name"
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Indication</label>
                      <textarea
                        value={img.indication}
                        onChange={(e) => updateImagingStudy(img.id, 'indication', e.target.value)}
                        rows={2}
                        placeholder="Reason for imaging..."
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Findings</label>
                      <textarea
                        value={img.findings}
                        onChange={(e) => updateImagingStudy(img.id, 'findings', e.target.value)}
                        rows={4}
                        placeholder="Detailed imaging findings..."
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Impression</label>
                      <textarea
                        value={img.impression}
                        onChange={(e) => updateImagingStudy(img.id, 'impression', e.target.value)}
                        rows={2}
                        placeholder="Radiologist impression..."
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Conditions Section */}
          {currentSection === 'conditions' && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>📊 Active Medical Conditions</h2>
                <button onClick={addCondition} className={styles.addButton}>+ Add Condition</button>
              </div>

              {patientData.active_conditions.length === 0 && (
                <p className={styles.emptyState}>No conditions yet. Click "+ Add Condition" to begin.</p>
              )}

              {patientData.active_conditions.map(cond => (
                <div key={cond.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>Medical Condition</h3>
                    <button onClick={() => removeCondition(cond.id)} className={styles.removeButton}>✕</button>
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <label>Condition</label>
                      <select
                        value={cond.code}
                        onChange={(e) => updateCondition(cond.id, 'code', e.target.value)}
                      >
                        <option value="">Select condition</option>
                        {COMMON_CONDITIONS.map(condition => (
                          <option key={condition} value={condition}>{condition}</option>
                        ))}
                        <option value="Other">Other (enter custom)</option>
                      </select>
                    </div>
                    {cond.code === 'Other' && (
                      <div className={styles.formGroup}>
                        <label>Custom Condition</label>
                        <input
                          type="text"
                          placeholder="Enter condition name"
                          onChange={(e) => updateCondition(cond.id, 'code', e.target.value)}
                        />
                      </div>
                    )}
                    <div className={styles.formGroup}>
                      <label>Status</label>
                      <select
                        value={cond.status}
                        onChange={(e) => updateCondition(cond.id, 'status', e.target.value)}
                      >
                        <option value="active">Active</option>
                        <option value="resolved">Resolved</option>
                        <option value="inactive">Inactive</option>
                      </select>
                    </div>
                    <div className={styles.formGroup}>
                      <label>Recorded Date</label>
                      <input
                        type="date"
                        value={cond.recorded_date}
                        onChange={(e) => updateCondition(cond.id, 'recorded_date', e.target.value)}
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Onset Date</label>
                      <input
                        type="date"
                        value={cond.onset}
                        onChange={(e) => updateCondition(cond.id, 'onset', e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Medications Section */}
          {currentSection === 'medications' && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>💊 Current Medications</h2>
                <div>
                  <button 
                    onClick={checkMedicationSafety} 
                    className={styles.safetyButton}
                    disabled={checkingSafety}
                    style={{ marginRight: '10px' }}
                  >
                    {checkingSafety ? '⏳ Checking...' : '🛡️ Check Safety'}
                  </button>
                  <button onClick={addMedication} className={styles.addButton}>+ Add Medication</button>
                </div>
              </div>

              {patientData.current_medications.length === 0 && (
                <p className={styles.emptyState}>No medications yet. Click "+ Add Medication" to begin.</p>
              )}

              {patientData.current_medications.map(med => (
                <div key={med.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>Medication</h3>
                    <button onClick={() => removeMedication(med.id)} className={styles.removeButton}>✕</button>
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <label>Medication Name</label>
                      <select
                        value={med.name}
                        onChange={(e) => updateMedication(med.id, 'name', e.target.value)}
                      >
                        <option value="">Select medication</option>
                        {COMMON_MEDICATIONS.map(medication => (
                          <option key={medication} value={medication}>{medication}</option>
                        ))}
                        <option value="Other">Other (enter custom)</option>
                      </select>
                    </div>
                    {med.name === 'Other' && (
                      <div className={styles.formGroup}>
                        <label>Custom Medication</label>
                        <input
                          type="text"
                          placeholder="Enter medication name"
                          onChange={(e) => updateMedication(med.id, 'name', e.target.value)}
                        />
                      </div>
                    )}
                    <div className={styles.formGroup}>
                      <label>Dosage</label>
                      <input
                        type="text"
                        value={med.dosage}
                        onChange={(e) => updateMedication(med.id, 'dosage', e.target.value)}
                        placeholder="e.g., 20mg once daily"
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Status</label>
                      <select
                        value={med.status}
                        onChange={(e) => updateMedication(med.id, 'status', e.target.value)}
                      >
                        <option value="active">Active</option>
                        <option value="stopped">Stopped</option>
                        <option value="completed">Completed</option>
                      </select>
                    </div>
                    <div className={styles.formGroup}>
                      <label>Date Prescribed</label>
                      <input
                        type="date"
                        value={med.date_prescribed}
                        onChange={(e) => updateMedication(med.id, 'date_prescribed', e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Allergies Section */}
          {currentSection === 'allergies' && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>⚠️ Allergies & Intolerances</h2>
                <button onClick={addAllergy} className={styles.addButton}>+ Add Allergy</button>
              </div>

              {patientData.allergies.length === 0 && (
                <p className={styles.emptyState}>No allergies yet. Click "+ Add Allergy" to begin.</p>
              )}

              {patientData.allergies.map(allergy => (
                <div key={allergy.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>Allergy</h3>
                    <button onClick={() => removeAllergy(allergy.id)} className={styles.removeButton}>✕</button>
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <label>Allergen</label>
                      <select
                        value={allergy.allergen}
                        onChange={(e) => updateAllergy(allergy.id, 'allergen', e.target.value)}
                      >
                        <option value="">Select allergen</option>
                        {COMMON_ALLERGIES.map(allergen => (
                          <option key={allergen} value={allergen}>{allergen}</option>
                        ))}
                        <option value="Other">Other (enter custom)</option>
                      </select>
                    </div>
                    {allergy.allergen === 'Other' && (
                      <div className={styles.formGroup}>
                        <label>Custom Allergen</label>
                        <input
                          type="text"
                          placeholder="Enter allergen"
                          onChange={(e) => updateAllergy(allergy.id, 'allergen', e.target.value)}
                        />
                      </div>
                    )}
                    <div className={styles.formGroup}>
                      <label>Reaction</label>
                      <select
                        value={allergy.reaction}
                        onChange={(e) => updateAllergy(allergy.id, 'reaction', e.target.value)}
                      >
                        <option value="">Select reaction</option>
                        {ALLERGY_REACTIONS.map(reaction => (
                          <option key={reaction} value={reaction}>{reaction}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Family/Social History Section */}
          {currentSection === 'history' && (
            <div className={styles.section}>
              <h2>👨‍👩‍👧 Family & Social History</h2>
              <div className={styles.formGrid}>
                <div className={styles.formGroupFull}>
                  <label>Family History</label>
                  <textarea
                    value={patientData.family_history}
                    onChange={(e) => setPatientData({...patientData, family_history: e.target.value})}
                    rows={6}
                    placeholder="e.g., Father: MI at age 62; Mother: Type 2 diabetes, hypertension; Sister: breast cancer at age 50"
                  />
                </div>
                <div className={styles.formGroupFull}>
                  <label>Social History</label>
                  <textarea
                    value={patientData.social_history}
                    onChange={(e) => setPatientData({...patientData, social_history: e.target.value})}
                    rows={6}
                    placeholder="e.g., Former smoker (quit 2020, 20 pack-year history); Occasional alcohol use (2-3 drinks/week); Works as accountant; Married with 2 children"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Save Button */}
        <div className={styles.saveSection}>
          <button onClick={handleSave} className={styles.saveButton}>
            💾 Save Patient History
          </button>
          {savedMessage && (
            <div className={savedMessage.includes('✓') ? styles.successMessage : styles.errorMessage}>
              {savedMessage}
            </div>
          )}
        </div>
      </div>

      {/* Medication Safety Modal */}
      {showSafetyModal && medicationSafetyResult && (
        <div className={styles.modalOverlay} onClick={() => setShowSafetyModal(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>🛡️ Medication Safety Report</h2>
              <button className={styles.closeButton} onClick={() => setShowSafetyModal(false)}>✕</button>
            </div>
            
            <div className={styles.modalBody}>
              {/* Safety Score */}
              <div className={styles.safetyScore}>
                <div className={styles.scoreCircle} style={{
                  borderColor: medicationSafetyResult.safety_score >= 90 ? '#10b981' :
                               medicationSafetyResult.safety_score >= 70 ? '#f59e0b' : '#ef4444'
                }}>
                  <span className={styles.scoreNumber}>{medicationSafetyResult.safety_score}</span>
                  <span className={styles.scoreLabel}>Safety Score</span>
                </div>
                <p className={styles.scoreSummary}>{medicationSafetyResult.summary}</p>
              </div>

              {/* Alerts */}
              {medicationSafetyResult.alerts && medicationSafetyResult.alerts.length > 0 && (
                <div className={styles.alertsSection}>
                  <h3>⚠️ Safety Alerts ({medicationSafetyResult.alerts.length})</h3>
                  {medicationSafetyResult.alerts.map((alert, index) => (
                    <div key={index} className={`${styles.alertCard} ${styles[alert.severity]}`}>
                      <div className={styles.alertHeader}>
                        <span className={styles.alertType}>
                          {alert.alert_type === 'drug_interaction' ? '💊' :
                           alert.alert_type === 'contraindication' ? '🚫' :
                           alert.alert_type === 'allergen_cross_reactivity' ? '⚠️' :
                           alert.alert_type === 'dose_concern' ? '📊' :
                           alert.alert_type === 'pregnancy_risk' ? '🤰' :
                           alert.alert_type === 'renal_adjustment' ? '🩺' :
                           alert.alert_type === 'hepatic_adjustment' ? '🩺' : '⚠️'}
                          {' '}
                          {alert.alert_type.replace(/_/g, ' ').toUpperCase()}
                        </span>
                        <span className={styles.severityBadge}>{alert.severity}</span>
                      </div>
                      
                      <p className={styles.alertMedication}>
                        <strong>Medication:</strong> {alert.medication}
                        {alert.interacting_medication && (
                          <span> + {alert.interacting_medication}</span>
                        )}
                        {alert.condition && (
                          <span> with {alert.condition}</span>
                        )}
                        {alert.allergen && alert.cross_reactive_drug && (
                          <span> ({alert.allergen} → {alert.cross_reactive_drug})</span>
                        )}
                      </p>

                      {alert.clinical_effect && (
                        <p className={styles.alertEffect}>
                          <strong>Clinical Effect:</strong> {alert.clinical_effect}
                        </p>
                      )}

                      {alert.recommendation && (
                        <p className={styles.alertRecommendation}>
                          <strong>Recommendation:</strong> {alert.recommendation}
                        </p>
                      )}

                      {alert.monitoring && (
                        <p className={styles.alertMonitoring}>
                          <strong>Monitoring:</strong> {alert.monitoring}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* No Alerts */}
              {(!medicationSafetyResult.alerts || medicationSafetyResult.alerts.length === 0) && (
                <div className={styles.noAlerts}>
                  <p>✅ No safety concerns detected with current medication regimen.</p>
                </div>
              )}

              {/* Additional Info */}
              {medicationSafetyResult.requires_monitoring && medicationSafetyResult.requires_monitoring.length > 0 && (
                <div className={styles.infoSection}>
                  <h4>📋 Requires Monitoring</h4>
                  <ul>
                    {medicationSafetyResult.requires_monitoring.map((med, index) => (
                      <li key={index}>{med}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className={styles.modalFooter}>
              <button className={styles.primaryButton} onClick={() => setShowSafetyModal(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
