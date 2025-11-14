import { useState, useMemo, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';

export default function SymptomSearch() {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
  
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
    { id: "", label: "All Families" },
    { id: "neurology", label: "Neurology" },
    { id: "cardiology", label: "Cardiology" },
    { id: "endocrinology", label: "Endocrinology" },
    { id: "pulmonology", label: "Pulmonology" },
    { id: "gastroenterology", label: "Gastroenterology" },
    { id: "infectious_disease", label: "Infectious Disease" },
    { id: "nephrology", label: "Nephrology" },
    { id: "rheumatology", label: "Rheumatology" },
    { id: "dermatology", label: "Dermatology" },
    { id: "psychiatry", label: "Psychiatry" },
    { id: "obstetrics_gynecology", label: "OB/GYN" },
    { id: "hematology_oncology", label: "Hematology/Oncology" },
    { id: "orthopedics", label: "Orthopedics" },
  ];

  const getFamilyColor = (fam) => {
    const colorMap = {
      neurology: "#3b82f6", cardiology: "#ef4444", endocrinology: "#f97316",
      pulmonology: "#8b5cf6", gastroenterology: "#10b981", infectious_disease: "#f59e0b",
      nephrology: "#06b6d4", rheumatology: "#ec4899", dermatology: "#84cc16",
      psychiatry: "#6366f1", obstetrics_gynecology: "#d946ef",
      hematology_oncology: "#f43f5e", orthopedics: "#14b8a6"
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
        maxWidth: '1200px',
        margin: '0 auto 2rem',
        background: 'white',
        padding: '1.5rem',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Image 
            src="/logo.png" 
            alt="RealDiag Logo" 
            width={60} 
            height={60}
            style={{ maxHeight: '60px', width: 'auto' }}
          />
          <div>
            <h1 style={{ margin: 0, fontSize: '1.75rem', color: '#1a202c' }}>
              Symptom-Based Search
            </h1>
            <p style={{ margin: '0.25rem 0 0', color: '#718096', fontSize: '0.9rem' }}>
              Enter symptoms to find possible diagnoses
            </p>
          </div>
        </div>
        <Link href="/" style={{
          padding: '0.5rem 1rem',
          background: '#3b82f6',
          color: 'white',
          borderRadius: '6px',
          textDecoration: 'none',
          fontSize: '0.9rem',
          fontWeight: '500'
        }}>
          ← Back to Home
        </Link>
      </div>

      {/* Main Content */}
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Search Form */}
        <div style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          marginBottom: '2rem'
        }}>
          <h2 style={{ marginTop: 0, color: '#1a202c', fontSize: '1.25rem' }}>
            Enter Patient Symptoms
          </h2>

          {/* Symptom Input */}
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#374151' }}>
              Add Symptoms
            </label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                value={symptomInput}
                onChange={(e) => setSymptomInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="e.g., chest pain, shortness of breath, fever"
                style={{
                  flex: 1,
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '1rem'
                }}
              />
              <button
                onClick={handleAddSymptom}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: '500',
                  fontSize: '1rem'
                }}
              >
                Add
              </button>
            </div>
          </div>

          {/* Symptom Tags */}
          {symptoms.length > 0 && (
            <div style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '0.5rem',
              marginBottom: '1.5rem',
              padding: '1rem',
              background: '#f9fafb',
              borderRadius: '6px'
            }}>
              {symptoms.map((symptom, idx) => (
                <div key={idx} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.5rem 1rem',
                  background: '#3b82f6',
                  color: 'white',
                  borderRadius: '20px',
                  fontSize: '0.9rem'
                }}>
                  <span>{symptom}</span>
                  <button
                    onClick={() => handleRemoveSymptom(symptom)}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: 'white',
                      cursor: 'pointer',
                      fontSize: '1.2rem',
                      padding: '0',
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
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem',
            marginBottom: '1.5rem'
          }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#374151' }}>
                Age (optional)
              </label>
              <input
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                placeholder="Patient age"
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '1rem'
                }}
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#374151' }}>
                Sex (optional)
              </label>
              <select
                value={sex}
                onChange={(e) => setSex(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '1rem'
                }}
              >
                <option value="">Any</option>
                <option value="M">Male</option>
                <option value="F">Female</option>
              </select>
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#374151' }}>
                Family (optional)
              </label>
              <select
                value={family}
                onChange={(e) => setFamily(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
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
                padding: '1rem',
                background: symptoms.length === 0 || loading ? '#9ca3af' : '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: symptoms.length === 0 || loading ? 'not-allowed' : 'pointer',
                fontWeight: '600',
                fontSize: '1rem'
              }}
            >
              {loading ? 'Searching...' : 'Search Diagnoses'}
            </button>
            <button
              onClick={handleClearAll}
              style={{
                padding: '1rem 2rem',
                background: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '1rem'
              }}
            >
              Clear All
            </button>
          </div>

          {error && (
            <div style={{
              marginTop: '1rem',
              padding: '1rem',
              background: '#fee2e2',
              color: '#991b1b',
              borderRadius: '6px',
              fontSize: '0.9rem'
            }}>
              {error}
            </div>
          )}
        </div>

        {/* Results */}
        {hasSearched && (
          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <h2 style={{ marginTop: 0, color: '#1a202c', fontSize: '1.25rem' }}>
              Search Results
              {results.length > 0 && (
                <span style={{ marginLeft: '1rem', color: '#6b7280', fontWeight: 'normal', fontSize: '1rem' }}>
                  ({results.length} {results.length === 1 ? 'match' : 'matches'})
                </span>
              )}
            </h2>

            {results.length === 0 ? (
              <p style={{ color: '#6b7280', textAlign: 'center', padding: '2rem' }}>
                No diagnoses found matching these symptoms. Try different or fewer symptoms.
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {results.map((result, idx) => (
                  <div key={idx} style={{
                    border: '1px solid #e5e7eb',
                    borderRadius: '6px',
                    padding: '1.5rem',
                    background: '#fafafa'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                      <div>
                        <h3 style={{ margin: '0 0 0.5rem', color: '#1a202c', fontSize: '1.1rem' }}>
                          {result.label}
                        </h3>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                          <span style={{
                            padding: '0.25rem 0.75rem',
                            background: getFamilyColor(result.family),
                            color: 'white',
                            borderRadius: '12px',
                            fontSize: '0.75rem',
                            fontWeight: '500'
                          }}>
                            {getFamilyLabel(result.family)}
                          </span>
                          <span style={{ color: '#6b7280', fontSize: '0.85rem' }}>
                            {result.rule_id}
                          </span>
                        </div>
                      </div>
                      <div style={{
                        padding: '0.5rem 1rem',
                        background: '#dcfce7',
                        color: '#166534',
                        borderRadius: '6px',
                        fontWeight: '600',
                        fontSize: '0.9rem'
                      }}>
                        Match: {result.match_score.toFixed(1)}
                      </div>
                    </div>

                    <div style={{ marginBottom: '1rem' }}>
                      <h4 style={{ margin: '0 0 0.5rem', color: '#374151', fontSize: '0.9rem', fontWeight: '600' }}>
                        Matched Presentations:
                      </h4>
                      <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#059669' }}>
                        {result.matched_presentations.map((pres, i) => (
                          <li key={i} style={{ marginBottom: '0.25rem' }}>{pres}</li>
                        ))}
                      </ul>
                    </div>

                    <div style={{ marginBottom: '1rem' }}>
                      <h4 style={{ margin: '0 0 0.5rem', color: '#374151', fontSize: '0.9rem', fontWeight: '600' }}>
                        All Typical Presentations:
                      </h4>
                      <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#6b7280', fontSize: '0.85rem' }}>
                        {result.all_presentations.map((pres, i) => (
                          <li key={i} style={{ marginBottom: '0.25rem' }}>{pres}</li>
                        ))}
                      </ul>
                    </div>

                    <div style={{ display: 'flex', gap: '2rem', fontSize: '0.85rem', color: '#6b7280' }}>
                      <div>
                        <strong>ICD-10:</strong> {result.icd10.join(', ') || 'N/A'}
                      </div>
                      <div>
                        <strong>SNOMED:</strong> {result.snomed.join(', ') || 'N/A'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
