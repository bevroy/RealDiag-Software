import { useState } from 'react';
import Image from 'next/image';

export default function Home() {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com';
  
  const [symptomInput, setSymptomInput] = useState('');
  const [symptoms, setSymptoms] = useState([]);
  const [age, setAge] = useState('');
  const [sex, setSex] = useState('');
  const [family, setFamily] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);

  const FAMILIES = [
    { id: "", label: "All Specialties" },
    { id: "cardiology", label: "Cardiology" },
    { id: "dermatology", label: "Dermatology" },
    { id: "endocrinology", label: "Endocrinology" },
    { id: "ent", label: "ENT" },
    { id: "gastroenterology", label: "Gastroenterology" },
    { id: "hematology_oncology", label: "Hematology/Oncology" },
    { id: "infectious_disease", label: "Infectious Disease" },
    { id: "nephrology", label: "Nephrology" },
    { id: "neurology", label: "Neurology" },
    { id: "obstetrics_gynecology", label: "OB/GYN" },
    { id: "ophthalmology", label: "Ophthalmology" },
    { id: "orthopedics", label: "Orthopedics" },
    { id: "psychiatry", label: "Psychiatry" },
    { id: "pulmonology", label: "Pulmonology" },
    { id: "rheumatology", label: "Rheumatology" },
    { id: "toxicology", label: "Toxicology" },
    { id: "urology", label: "Urology" },
  ];

  const getFamilyColor = (fam) => {
    const colorMap = {
      neurology: "#3b82f6", cardiology: "#ef4444", endocrinology: "#f97316",
      pulmonology: "#8b5cf6", gastroenterology: "#10b981", infectious_disease: "#f59e0b",
      nephrology: "#06b6d4", rheumatology: "#ec4899", dermatology: "#84cc16",
      psychiatry: "#6366f1", obstetrics_gynecology: "#d946ef",
      hematology_oncology: "#f43f5e", orthopedics: "#14b8a6",
      ophthalmology: "#0ea5e9", ent: "#f472b6", urology: "#22d3ee", toxicology: "#fb923c"
    };
    return colorMap[fam] || "#6b7280";
  };

  const getFamilyLabel = (fam) => {
    const family = FAMILIES.find(f => f.id === fam);
    return family ? family.label : fam;
  };

  const handleAddSymptom = () => {
    const trimmed = symptomInput.trim();
    if (trimmed && !symptoms.includes(trimmed)) {
      setSymptoms([...symptoms, trimmed]);
      setSymptomInput('');
    }
  };

  const handleRemoveSymptom = (symptom) => {
    setSymptoms(symptoms.filter(s => s !== symptom));
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddSymptom();
    }
  };

  const handleSearch = async () => {
    if (symptoms.length === 0) {
      setError('Please enter at least one symptom');
      return;
    }

    setLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const requestBody = {
        symptoms: symptoms,
        ...(age && { age: parseInt(age) }),
        ...(sex && { sex: sex }),
        ...(family && { family: family })
      };

      const response = await fetch(`${apiBase}/search/by-symptoms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data = await response.json();
      setResults(data.results || []);
    } catch (err) {
      setError(err.message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearAll = () => {
    setSymptoms([]);
    setSymptomInput('');
    setAge('');
    setSex('');
    setFamily('');
    setResults([]);
    setHasSearched(false);
    setError(null);
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
      padding: '2rem'
    }}>
      {/* Header */}
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto 2rem',
        textAlign: 'center'
      }}>
        <Image 
          src="/logo.png" 
          alt="RealDiag Logo" 
          width={100} 
          height={100}
          style={{ maxHeight: '100px', width: 'auto', marginBottom: '1rem' }}
        />
        <h1 style={{ margin: 0, fontSize: '3rem', color: '#1a202c', fontWeight: '700' }}>
          RealDiag
        </h1>
        <p style={{ margin: '0.5rem 0 0', color: '#718096', fontSize: '1.25rem' }}>
          AI-Powered Clinical Diagnostic Search Engine
        </p>
        <p style={{ margin: '0.5rem 0 0', color: '#a0aec0', fontSize: '1rem' }}>
          268 diagnoses • 17 specialties • Evidence-based decision support
        </p>
      </div>

      {/* Main Content */}
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* Search Form */}
        <div style={{
          background: 'white',
          padding: '2.5rem',
          borderRadius: '12px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
          marginBottom: '2rem'
        }}>
          <h2 style={{ marginTop: 0, color: '#1a202c', fontSize: '1.5rem', marginBottom: '1.5rem' }}>
            🔍 Search by Symptoms
          </h2>

          {/* Symptom Input */}
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', color: '#374151' }}>
              Enter Patient Symptoms
            </label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                value={symptomInput}
                onChange={(e) => setSymptomInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="e.g., chest pain, shortness of breath, dizziness"
                style={{
                  flex: 1,
                  padding: '1rem',
                  border: '2px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '1.1rem',
                  outline: 'none',
                  transition: 'border-color 0.2s'
                }}
                onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
              />
              <button
                onClick={handleAddSymptom}
                style={{
                  padding: '1rem 2rem',
                  background: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600',
                  fontSize: '1.1rem',
                  whiteSpace: 'nowrap'
                }}
              >
                + Add
              </button>
            </div>
          </div>

          {/* Symptom Tags */}
          {symptoms.length > 0 && (
            <div style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '0.75rem',
              marginBottom: '1.5rem',
              padding: '1.25rem',
              background: '#f0f9ff',
              borderRadius: '8px',
              border: '1px solid #bae6fd'
            }}>
              {symptoms.map((symptom, idx) => (
                <div key={idx} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.6rem 1.2rem',
                  background: '#3b82f6',
                  color: 'white',
                  borderRadius: '25px',
                  fontSize: '1rem',
                  fontWeight: '500'
                }}>
                  <span>{symptom}</span>
                  <button
                    onClick={() => handleRemoveSymptom(symptom)}
                    style={{
                      background: 'rgba(255,255,255,0.2)',
                      border: 'none',
                      color: 'white',
                      cursor: 'pointer',
                      fontSize: '1.3rem',
                      padding: '0 0.4rem',
                      borderRadius: '50%',
                      lineHeight: '1'
                    }}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Filters */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '1rem',
            marginBottom: '1.5rem'
          }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', color: '#374151' }}>
                Age (optional)
              </label>
              <input
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                placeholder="Patient age"
                style={{
                  width: '100%',
                  padding: '0.9rem',
                  border: '2px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '1rem'
                }}
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', color: '#374151' }}>
                Sex (optional)
              </label>
              <select
                value={sex}
                onChange={(e) => setSex(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.9rem',
                  border: '2px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '1rem'
                }}
              >
                <option value="">Any</option>
                <option value="M">Male</option>
                <option value="F">Female</option>
              </select>
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', color: '#374151' }}>
                Specialty Filter (optional)
              </label>
              <select
                value={family}
                onChange={(e) => setFamily(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.9rem',
                  border: '2px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '1rem'
                }}
              >
                {FAMILIES.map(f => (
                  <option key={f.id} value={f.id}>{f.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button
              onClick={handleSearch}
              disabled={symptoms.length === 0 || loading}
              style={{
                flex: 1,
                padding: '1.25rem',
                background: symptoms.length === 0 || loading ? '#9ca3af' : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: symptoms.length === 0 || loading ? 'not-allowed' : 'pointer',
                fontWeight: '700',
                fontSize: '1.2rem',
                boxShadow: symptoms.length === 0 || loading ? 'none' : '0 4px 12px rgba(16, 185, 129, 0.4)'
              }}
            >
              {loading ? '🔄 Searching...' : '🔍 Search Diagnoses'}
            </button>
            <button
              onClick={handleClearAll}
              style={{
                padding: '1.25rem 2.5rem',
                background: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '1.1rem'
              }}
            >
              Clear
            </button>
          </div>

          {error && (
            <div style={{
              marginTop: '1rem',
              padding: '1rem',
              background: '#fee2e2',
              color: '#991b1b',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: '500'
            }}>
              ⚠️ {error}
            </div>
          )}
        </div>

        {/* Results */}
        {hasSearched && (
          <div style={{
            background: 'white',
            padding: '2.5rem',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)'
          }}>
            <h2 style={{ marginTop: 0, color: '#1a202c', fontSize: '1.75rem', marginBottom: '1.5rem' }}>
              📊 Diagnostic Results
              {results.length > 0 && (
                <span style={{ marginLeft: '1rem', color: '#6b7280', fontWeight: 'normal', fontSize: '1.1rem' }}>
                  ({results.length} {results.length === 1 ? 'match' : 'matches'})
                </span>
              )}
            </h2>

            {results.length === 0 ? (
              <div style={{ 
                textAlign: 'center', 
                padding: '3rem',
                color: '#6b7280'
              }}>
                <p style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>
                  🔍 No diagnoses found matching these symptoms
                </p>
                <p style={{ fontSize: '1rem' }}>
                  Try different symptoms, fewer symptoms, or broaden your search
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                {results.map((result, idx) => (
                  <div key={idx} style={{
                    border: '2px solid #e5e7eb',
                    borderRadius: '10px',
                    padding: '1.75rem',
                    background: '#fafafa',
                    transition: 'all 0.2s',
                    cursor: 'default'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#3b82f6';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(59, 130, 246, 0.15)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '#e5e7eb';
                    e.currentTarget.style.boxShadow = 'none';
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1.25rem' }}>
                      <div>
                        <h3 style={{ margin: '0 0 0.75rem', color: '#1a202c', fontSize: '1.3rem', fontWeight: '600' }}>
                          {result.label}
                        </h3>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                          <span style={{
                            padding: '0.4rem 1rem',
                            background: getFamilyColor(result.family),
                            color: 'white',
                            borderRadius: '15px',
                            fontSize: '0.85rem',
                            fontWeight: '600'
                          }}>
                            {getFamilyLabel(result.family)}
                          </span>
                          <span style={{ color: '#9ca3af', fontSize: '0.9rem', fontFamily: 'monospace' }}>
                            {result.rule_id}
                          </span>
                        </div>
                      </div>
                      <div style={{
                        padding: '0.75rem 1.5rem',
                        background: 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)',
                        color: '#166534',
                        borderRadius: '8px',
                        fontWeight: '700',
                        fontSize: '1.1rem',
                        border: '2px solid #86efac'
                      }}>
                        {result.match_score.toFixed(1)} pts
                      </div>
                    </div>

                    <div style={{ marginBottom: '1.25rem' }}>
                      <h4 style={{ margin: '0 0 0.75rem', color: '#059669', fontSize: '1rem', fontWeight: '700' }}>
                        ✓ Matched Presentations:
                      </h4>
                      <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#047857', fontSize: '0.95rem', lineHeight: '1.8' }}>
                        {result.matched_presentations.map((pres, i) => (
                          <li key={i} style={{ marginBottom: '0.3rem' }}>{pres}</li>
                        ))}
                      </ul>
                    </div>

                    <div style={{ marginBottom: '1.25rem' }}>
                      <h4 style={{ margin: '0 0 0.75rem', color: '#374151', fontSize: '0.95rem', fontWeight: '600' }}>
                        All Typical Presentations:
                      </h4>
                      <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#6b7280', fontSize: '0.9rem', lineHeight: '1.7' }}>
                        {result.all_presentations.map((pres, i) => (
                          <li key={i} style={{ marginBottom: '0.3rem' }}>{pres}</li>
                        ))}
                      </ul>
                    </div>

                    <div style={{ 
                      display: 'flex', 
                      gap: '2rem', 
                      fontSize: '0.9rem', 
                      color: '#6b7280',
                      padding: '1rem',
                      background: 'white',
                      borderRadius: '6px'
                    }}>
                      <div>
                        <strong style={{ color: '#374151' }}>ICD-10:</strong> {result.icd10.join(', ') || 'N/A'}
                      </div>
                      <div>
                        <strong style={{ color: '#374151' }}>SNOMED:</strong> {result.snomed.join(', ') || 'N/A'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={{
        maxWidth: '1400px',
        margin: '2rem auto 0',
        textAlign: 'center',
        color: '#9ca3af',
        fontSize: '0.9rem'
      }}>
        <p>RealDiag Clinical Decision Support • Evidence-based diagnostics • For educational purposes</p>
      </div>
    </div>
  );
}

