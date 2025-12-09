'use client';

import { useState } from 'react';

export default function SymptomTracker({ userData, onSave }) {
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [customSymptom, setCustomSymptom] = useState('');
  const [severity, setSeverity] = useState('moderate');
  const [duration, setDuration] = useState('');
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);

  const commonSymptoms = [
    { category: 'General', symptoms: ['Fever', 'Fatigue', 'Weakness', 'Chills', 'Night sweats', 'Weight loss', 'Weight gain'] },
    { category: 'Head', symptoms: ['Headache', 'Dizziness', 'Lightheadedness', 'Confusion', 'Memory problems'] },
    { category: 'Respiratory', symptoms: ['Cough', 'Shortness of breath', 'Wheezing', 'Chest pain', 'Sore throat', 'Runny nose', 'Congestion'] },
    { category: 'Gastrointestinal', symptoms: ['Nausea', 'Vomiting', 'Diarrhea', 'Constipation', 'Abdominal pain', 'Bloating', 'Heartburn'] },
    { category: 'Musculoskeletal', symptoms: ['Joint pain', 'Muscle pain', 'Back pain', 'Neck pain', 'Stiffness', 'Swelling'] },
    { category: 'Cardiovascular', symptoms: ['Chest pain', 'Palpitations', 'Irregular heartbeat', 'Leg swelling', 'Shortness of breath'] },
    { category: 'Neurological', symptoms: ['Numbness', 'Tingling', 'Vision changes', 'Hearing loss', 'Seizures', 'Tremors'] },
    { category: 'Skin', symptoms: ['Rash', 'Itching', 'Hives', 'Bruising', 'Hair loss', 'Nail changes'] },
    { category: 'Mental Health', symptoms: ['Anxiety', 'Depression', 'Insomnia', 'Mood changes', 'Irritability'] }
  ];

  const handleSymptomToggle = (symptom) => {
    if (selectedSymptoms.includes(symptom)) {
      setSelectedSymptoms(selectedSymptoms.filter(s => s !== symptom));
    } else {
      setSelectedSymptoms([...selectedSymptoms, symptom]);
    }
  };

  const handleAddCustomSymptom = () => {
    if (customSymptom.trim() && !selectedSymptoms.includes(customSymptom.trim())) {
      setSelectedSymptoms([...selectedSymptoms, customSymptom.trim()]);
      setCustomSymptom('');
    }
  };

  const handleSave = async () => {
    if (selectedSymptoms.length === 0) {
      alert('Please select at least one symptom');
      return;
    }

    setSaving(true);
    try {
      const response = await fetch('/api/health/symptoms', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          symptoms: selectedSymptoms,
          severity,
          duration,
          notes,
          timestamp: new Date().toISOString()
        })
      });

      if (response.ok) {
        alert('✓ Symptoms saved successfully!');
        setSelectedSymptoms([]);
        setSeverity('moderate');
        setDuration('');
        setNotes('');
        if (onSave) onSave();
      } else {
        alert('Failed to save symptoms. Please try again.');
      }
    } catch (error) {
      console.error('Save error:', error);
      alert('Failed to save symptoms. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ margin: 0, color: '#2d3748', fontSize: '1.75rem' }}>
          🩺 Symptom Tracker
        </h2>
        <p style={{ margin: '0.5rem 0 0 0', color: '#718096' }}>
          Log your symptoms for accurate diagnostic assistance
        </p>
      </div>

      {/* Selected Symptoms Display */}
      {selectedSymptoms.length > 0 && (
        <div style={{
          padding: '1.5rem',
          background: '#f0fff4',
          border: '2px solid #9ae6b4',
          borderRadius: '8px',
          marginBottom: '2rem'
        }}>
          <h4 style={{ margin: '0 0 1rem 0', color: '#22543d' }}>
            Selected Symptoms ({selectedSymptoms.length})
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {selectedSymptoms.map(symptom => (
              <span key={symptom} style={{
                padding: '0.5rem 1rem',
                background: '#48bb78',
                color: 'white',
                borderRadius: '20px',
                fontSize: '0.875rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                {symptom}
                <button
                  onClick={() => handleSymptomToggle(symptom)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: 'white',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    padding: 0
                  }}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Symptom Selection by Category */}
      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ color: '#2d3748', marginBottom: '1rem' }}>
          Select Symptoms
        </h3>
        {commonSymptoms.map(category => (
          <div key={category.category} style={{
            marginBottom: '1.5rem',
            border: '2px solid #e2e8f0',
            borderRadius: '8px',
            padding: '1rem'
          }}>
            <h4 style={{ margin: '0 0 0.75rem 0', color: '#4a5568', fontSize: '1rem' }}>
              {category.category}
            </h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {category.symptoms.map(symptom => (
                <button
                  key={symptom}
                  onClick={() => handleSymptomToggle(symptom)}
                  style={{
                    padding: '0.5rem 1rem',
                    background: selectedSymptoms.includes(symptom) ? '#667eea' : 'white',
                    color: selectedSymptoms.includes(symptom) ? 'white' : '#4a5568',
                    border: selectedSymptoms.includes(symptom) ? 'none' : '2px solid #e2e8f0',
                    borderRadius: '20px',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    transition: 'all 0.2s'
                  }}
                >
                  {symptom}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Custom Symptom Input */}
      <div style={{
        marginBottom: '2rem',
        border: '2px solid #e2e8f0',
        borderRadius: '8px',
        padding: '1.5rem'
      }}>
        <h4 style={{ margin: '0 0 1rem 0', color: '#2d3748' }}>
          Add Custom Symptom
        </h4>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="text"
            value={customSymptom}
            onChange={(e) => setCustomSymptom(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddCustomSymptom()}
            placeholder="Enter a symptom not listed above"
            style={{
              flex: 1,
              padding: '0.75rem',
              border: '2px solid #e2e8f0',
              borderRadius: '6px',
              fontSize: '1rem'
            }}
          />
          <button
            onClick={handleAddCustomSymptom}
            style={{
              padding: '0.75rem 1.5rem',
              background: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            Add
          </button>
        </div>
      </div>

      {/* Additional Information */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Severity */}
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', color: '#2d3748', fontWeight: '600' }}>
            Severity
          </label>
          <select
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '2px solid #e2e8f0',
              borderRadius: '6px',
              fontSize: '1rem'
            }}
          >
            <option value="mild">Mild - Minor discomfort</option>
            <option value="moderate">Moderate - Noticeable impact</option>
            <option value="severe">Severe - Significant impact</option>
            <option value="critical">Critical - Seek immediate care</option>
          </select>
        </div>

        {/* Duration */}
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', color: '#2d3748', fontWeight: '600' }}>
            Duration
          </label>
          <select
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '2px solid #e2e8f0',
              borderRadius: '6px',
              fontSize: '1rem'
            }}
          >
            <option value="">Select duration</option>
            <option value="<1hour">Less than 1 hour</option>
            <option value="1-6hours">1-6 hours</option>
            <option value="6-24hours">6-24 hours</option>
            <option value="1-3days">1-3 days</option>
            <option value="3-7days">3-7 days</option>
            <option value=">1week">More than 1 week</option>
            <option value=">1month">More than 1 month</option>
          </select>
        </div>
      </div>

      {/* Notes */}
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', marginBottom: '0.5rem', color: '#2d3748', fontWeight: '600' }}>
          Additional Notes (Optional)
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Describe any additional details, triggers, or patterns you've noticed..."
          rows={4}
          style={{
            width: '100%',
            padding: '0.75rem',
            border: '2px solid #e2e8f0',
            borderRadius: '6px',
            fontSize: '1rem',
            fontFamily: 'inherit',
            resize: 'vertical'
          }}
        />
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
        <button
          onClick={() => {
            setSelectedSymptoms([]);
            setSeverity('moderate');
            setDuration('');
            setNotes('');
          }}
          style={{
            padding: '0.75rem 1.5rem',
            background: 'white',
            color: '#4a5568',
            border: '2px solid #e2e8f0',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: '600'
          }}
        >
          Clear All
        </button>
        <button
          onClick={handleSave}
          disabled={saving || selectedSymptoms.length === 0}
          style={{
            padding: '0.75rem 2rem',
            background: saving || selectedSymptoms.length === 0 ? '#cbd5e0' : '#48bb78',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: saving || selectedSymptoms.length === 0 ? 'not-allowed' : 'pointer',
            fontWeight: '600'
          }}
        >
          {saving ? 'Saving...' : '💾 Save Symptoms'}
        </button>
      </div>

      {/* Info Box */}
      <div style={{
        marginTop: '2rem',
        padding: '1.5rem',
        background: '#ebf8ff',
        border: '2px solid #90cdf4',
        borderRadius: '8px'
      }}>
        <h4 style={{ margin: '0 0 0.5rem 0', color: '#2c5282' }}>
          💡 Why Track Symptoms?
        </h4>
        <p style={{ margin: 0, fontSize: '0.875rem', color: '#2d3748', lineHeight: '1.6' }}>
          Tracking your symptoms helps identify patterns and provides valuable information for diagnostic analysis. 
          Your symptom history can be used with the Diagnostic Search feature to get personalized health insights.
        </p>
      </div>
    </div>
  );
}
