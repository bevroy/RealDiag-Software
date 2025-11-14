import { useState, useMemo, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';

export default function SymptomSearch() {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
  
  const [symptomInput, setSymptomInput] = useState('');
  const [symptoms, setSymptoms] = useState([]);
  const [age, setAge] = useState('');
  const [ageRange, setAgeRange] = useState('');
  const [sex, setSex] = useState('');
  const [family, setFamily] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [viewMode, setViewMode] = useState('card'); // 'card' or 'compact'
  const [sortBy, setSortBy] = useState('score'); // 'score', 'alpha', 'family'
  const [expandedCards, setExpandedCards] = useState({});

  const FAMILIES = [
    { id: "", label: "All Specialties" },
    { id: "cardiology", label: "Cardiology" },
    { id: "dermatology", label: "Dermatology" },
    { id: "emergency_medicine", label: "Emergency Medicine" },
    { id: "endocrinology", label: "Endocrinology" },
    { id: "ent", label: "ENT" },
    { id: "gastroenterology", label: "Gastroenterology" },
    { id: "geriatrics", label: "Geriatrics" },
    { id: "hematology_oncology", label: "Hematology/Oncology" },
    { id: "infectious_disease", label: "Infectious Disease" },
    { id: "nephrology", label: "Nephrology" },
    { id: "neurology", label: "Neurology" },
    { id: "obstetrics_gynecology", label: "OB/GYN" },
    { id: "ophthalmology", label: "Ophthalmology" },
    { id: "orthopedics", label: "Orthopedics" },
    { id: "pediatrics", label: "Pediatrics" },
    { id: "psychiatry", label: "Psychiatry" },
    { id: "pulmonology", label: "Pulmonology" },
    { id: "rheumatology", label: "Rheumatology" },
    { id: "surgery", label: "Surgery" },
    { id: "toxicology", label: "Toxicology" },
    { id: "urology", label: "Urology" },
  ];

  const AGE_RANGES = [
    { id: "", label: "All Ages" },
    { id: "neonate", label: "Neonate (0-1 month)", min: 0, max: 0.08 },
    { id: "infant", label: "Infant (1-12 months)", min: 0.08, max: 1 },
    { id: "toddler", label: "Toddler (1-3 years)", min: 1, max: 3 },
    { id: "child", label: "Child (3-12 years)", min: 3, max: 12 },
    { id: "adolescent", label: "Adolescent (12-18 years)", min: 12, max: 18 },
    { id: "adult", label: "Adult (18-65 years)", min: 18, max: 65 },
    { id: "elderly", label: "Elderly (65+ years)", min: 65, max: 120 },
  ];

  const getFamilyColor = (fam) => {
    const colorMap = {
      neurology: "#3b82f6", cardiology: "#ef4444", endocrinology: "#f97316",
      pulmonology: "#8b5cf6", gastroenterology: "#10b981", infectious_disease: "#f59e0b",
      nephrology: "#06b6d4", rheumatology: "#ec4899", dermatology: "#84cc16",
      psychiatry: "#6366f1", obstetrics_gynecology: "#d946ef",
      hematology_oncology: "#f43f5e", orthopedics: "#14b8a6",
      pediatrics: "#10b981", geriatrics: "#8b5cf6", emergency_medicine: "#ef4444",
      surgery: "#0891b2", ent: "#f97316", ophthalmology: "#06b6d4",
      toxicology: "#dc2626", urology: "#0891b2"
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

  const toggleCardExpand = (idx) => {
    setExpandedCards(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }));
  };

  const getSortedResults = () => {
    const sorted = [...results];
    switch (sortBy) {
      case 'alpha':
        return sorted.sort((a, b) => a.label.localeCompare(b.label));
      case 'family':
        return sorted.sort((a, b) => a.family.localeCompare(b.family));
      case 'score':
      default:
        return sorted.sort((a, b) => b.match_score - a.match_score);
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
      // Use age range if selected, otherwise use specific age
      let ageValue = age;
      if (ageRange && !age) {
        const range = AGE_RANGES.find(r => r.id === ageRange);
        if (range) {
          ageValue = Math.floor((range.min + range.max) / 2);
        }
      }

      const requestBody = {
        symptoms: symptoms,
        ...(ageValue && { age: parseInt(ageValue) }),
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
    setAgeRange('');
    setSex('');
    setFamily('');
    setResults([]);
    setHasSearched(false);
    setError(null);
    setExpandedCards({});
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
          <div style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ marginTop: 0, marginBottom: '1rem', color: '#1a202c', fontSize: '1rem', fontWeight: '600' }}>
              📊 Refine Search (Optional)
            </h3>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '1rem'
            }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#374151', fontSize: '0.9rem' }}>
                  Age Range
                </label>
                <select
                  value={ageRange}
                  onChange={(e) => {
                    setAgeRange(e.target.value);
                    setAge(''); // Clear specific age when range selected
                  }}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.95rem',
                    background: 'white'
                  }}
                >
                  {AGE_RANGES.map(range => (
                    <option key={range.id} value={range.id}>{range.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#374151', fontSize: '0.9rem' }}>
                  Or Specific Age
                </label>
                <input
                  type="number"
                  value={age}
                  onChange={(e) => {
                    setAge(e.target.value);
                    setAgeRange(''); // Clear range when specific age entered
                  }}
                  placeholder="e.g., 45"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.95rem'
                  }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#374151', fontSize: '0.9rem' }}>
                  Sex
                </label>
                <select
                  value={sex}
                  onChange={(e) => setSex(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.95rem',
                    background: 'white'
                  }}
                >
                  <option value="">Any</option>
                  <option value="M">Male</option>
                  <option value="F">Female</option>
                </select>
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#374151', fontSize: '0.9rem' }}>
                  Specialty
                </label>
                <select
                  value={family}
                  onChange={(e) => setFamily(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.95rem',
                    background: 'white'
                  }}
                >
                  {FAMILIES.map(f => (
                    <option key={f.id} value={f.id}>{f.label}</option>
                  ))}
                </select>
              </div>
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
            {/* Results Header with Controls */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginBottom: '1.5rem',
              flexWrap: 'wrap',
              gap: '1rem'
            }}>
              <h2 style={{ margin: 0, color: '#1a202c', fontSize: '1.25rem' }}>
                Search Results
                {results.length > 0 && (
                  <span style={{ marginLeft: '1rem', color: '#6b7280', fontWeight: 'normal', fontSize: '1rem' }}>
                    ({results.length} {results.length === 1 ? 'match' : 'matches'})
                  </span>
                )}
              </h2>
              
              {results.length > 0 && (
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
                  {/* Sort Controls */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ fontSize: '0.85rem', color: '#6b7280', fontWeight: '500' }}>Sort:</span>
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                      style={{
                        padding: '0.5rem',
                        border: '1px solid #d1d5db',
                        borderRadius: '6px',
                        fontSize: '0.85rem',
                        background: 'white'
                      }}
                    >
                      <option value="score">Match Score</option>
                      <option value="alpha">Alphabetical</option>
                      <option value="family">Specialty</option>
                    </select>
                  </div>

                  {/* View Mode Toggle */}
                  <div style={{ display: 'flex', gap: '0.25rem', border: '1px solid #d1d5db', borderRadius: '6px', overflow: 'hidden' }}>
                    <button
                      onClick={() => setViewMode('card')}
                      style={{
                        padding: '0.5rem 1rem',
                        background: viewMode === 'card' ? '#3b82f6' : 'white',
                        color: viewMode === 'card' ? 'white' : '#374151',
                        border: 'none',
                        cursor: 'pointer',
                        fontSize: '0.85rem',
                        fontWeight: '500'
                      }}
                    >
                      Card View
                    </button>
                    <button
                      onClick={() => setViewMode('compact')}
                      style={{
                        padding: '0.5rem 1rem',
                        background: viewMode === 'compact' ? '#3b82f6' : 'white',
                        color: viewMode === 'compact' ? 'white' : '#374151',
                        border: 'none',
                        borderLeft: '1px solid #d1d5db',
                        cursor: 'pointer',
                        fontSize: '0.85rem',
                        fontWeight: '500'
                      }}
                    >
                      Compact View
                    </button>
                  </div>
                </div>
              )}
            </div>

            {results.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
                <p style={{ fontSize: '1.1rem', fontWeight: '500', marginBottom: '0.5rem' }}>
                  No diagnoses found
                </p>
                <p style={{ fontSize: '0.9rem' }}>
                  Try different symptoms or remove some filters to broaden your search
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: viewMode === 'card' ? '1.5rem' : '0.75rem' }}>
                {getSortedResults().map((result, idx) => (
                  viewMode === 'card' ? (
                    // Enhanced Card View
                    <div key={idx} style={{
                      border: '2px solid #e5e7eb',
                      borderLeft: `6px solid ${getFamilyColor(result.family)}`,
                      borderRadius: '8px',
                      padding: '1.5rem',
                      background: 'white',
                      transition: 'all 0.2s',
                      boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
                    }}>
                      {/* Card Header */}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem', gap: '1rem' }}>
                        <div style={{ flex: 1 }}>
                          <h3 style={{ margin: '0 0 0.75rem', color: '#1a202c', fontSize: '1.2rem', fontWeight: '600' }}>
                            {result.label}
                          </h3>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                            <span style={{
                              padding: '0.35rem 0.85rem',
                              background: getFamilyColor(result.family),
                              color: 'white',
                              borderRadius: '14px',
                              fontSize: '0.8rem',
                              fontWeight: '600',
                              textTransform: 'uppercase',
                              letterSpacing: '0.5px'
                            }}>
                              {getFamilyLabel(result.family)}
                            </span>
                            <span style={{ 
                              color: '#6b7280', 
                              fontSize: '0.85rem',
                              fontFamily: 'monospace',
                              background: '#f3f4f6',
                              padding: '0.25rem 0.75rem',
                              borderRadius: '6px'
                            }}>
                              {result.rule_id}
                            </span>
                          </div>
                        </div>
                        <div style={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          gap: '0.5rem'
                        }}>
                          <div style={{
                            padding: '0.75rem 1.25rem',
                            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                            color: 'white',
                            borderRadius: '8px',
                            fontWeight: '700',
                            fontSize: '1.1rem',
                            boxShadow: '0 4px 6px rgba(16, 185, 129, 0.2)',
                            textAlign: 'center',
                            minWidth: '100px'
                          }}>
                            <div style={{ fontSize: '0.7rem', fontWeight: '500', opacity: 0.9, marginBottom: '0.25rem' }}>MATCH</div>
                            {result.match_score.toFixed(1)}
                          </div>
                        </div>
                      </div>

                      {/* Matched Presentations (Always Visible) */}
                      <div style={{ 
                        marginBottom: '1rem',
                        padding: '1rem',
                        background: 'linear-gradient(to right, #ecfdf5, #f0fdf4)',
                        borderRadius: '6px',
                        borderLeft: '3px solid #10b981'
                      }}>
                        <h4 style={{ 
                          margin: '0 0 0.75rem', 
                          color: '#065f46', 
                          fontSize: '0.9rem', 
                          fontWeight: '700',
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem'
                        }}>
                          <span>✓</span> Matched Symptoms
                        </h4>
                        <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#047857' }}>
                          {result.matched_presentations.map((pres, i) => (
                            <li key={i} style={{ marginBottom: '0.5rem', lineHeight: '1.5', fontWeight: '500' }}>{pres}</li>
                          ))}
                        </ul>
                      </div>

                      {/* Expandable Section */}
                      <div>
                        <button
                          onClick={() => toggleCardExpand(idx)}
                          style={{
                            width: '100%',
                            padding: '0.75rem',
                            background: expandedCards[idx] ? '#3b82f6' : '#f3f4f6',
                            color: expandedCards[idx] ? 'white' : '#374151',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontWeight: '600',
                            fontSize: '0.9rem',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '0.5rem',
                            transition: 'all 0.2s'
                          }}
                        >
                          <span>{expandedCards[idx] ? '▼' : '▶'}</span>
                          {expandedCards[idx] ? 'Show Less' : 'Show All Details'}
                        </button>

                        {expandedCards[idx] && (
                          <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '2px solid #e5e7eb' }}>
                            {/* All Presentations */}
                            <div style={{ marginBottom: '1.5rem' }}>
                              <h4 style={{ 
                                margin: '0 0 0.75rem', 
                                color: '#374151', 
                                fontSize: '0.9rem', 
                                fontWeight: '700',
                                textTransform: 'uppercase',
                                letterSpacing: '0.5px'
                              }}>
                                All Typical Presentations
                              </h4>
                              <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#6b7280', fontSize: '0.9rem' }}>
                                {result.all_presentations.map((pres, i) => (
                                  <li key={i} style={{ marginBottom: '0.5rem', lineHeight: '1.5' }}>{pres}</li>
                                ))}
                              </ul>
                            </div>

                            {/* Diagnostic Codes */}
                            <div style={{ 
                              display: 'grid', 
                              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                              gap: '1rem',
                              padding: '1rem',
                              background: '#f9fafb',
                              borderRadius: '6px'
                            }}>
                              <div>
                                <h4 style={{ margin: '0 0 0.5rem', color: '#374151', fontSize: '0.85rem', fontWeight: '700' }}>
                                  📋 ICD-10 Codes
                                </h4>
                                <div style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: '#4b5563' }}>
                                  {result.icd10.length > 0 ? result.icd10.join(', ') : 'Not specified'}
                                </div>
                              </div>
                              <div>
                                <h4 style={{ margin: '0 0 0.5rem', color: '#374151', fontSize: '0.85rem', fontWeight: '700' }}>
                                  🏥 SNOMED Codes
                                </h4>
                                <div style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: '#4b5563' }}>
                                  {result.snomed.length > 0 ? result.snomed.join(', ') : 'Not specified'}
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ) : (
                    // Compact View
                    <div key={idx} style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '1rem',
                      padding: '1rem',
                      border: '1px solid #e5e7eb',
                      borderLeft: `4px solid ${getFamilyColor(result.family)}`,
                      borderRadius: '6px',
                      background: 'white',
                      transition: 'all 0.2s'
                    }}>
                      <div style={{
                        padding: '0.5rem 0.75rem',
                        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                        color: 'white',
                        borderRadius: '6px',
                        fontWeight: '700',
                        fontSize: '0.9rem',
                        minWidth: '60px',
                        textAlign: 'center'
                      }}>
                        {result.match_score.toFixed(1)}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: '600', color: '#1a202c', marginBottom: '0.25rem' }}>
                          {result.label}
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.8rem' }}>
                          <span style={{
                            padding: '0.2rem 0.6rem',
                            background: getFamilyColor(result.family),
                            color: 'white',
                            borderRadius: '10px',
                            fontWeight: '600'
                          }}>
                            {getFamilyLabel(result.family)}
                          </span>
                          <span style={{ color: '#6b7280' }}>
                            {result.matched_presentations.length} matched symptoms
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={() => toggleCardExpand(idx)}
                        style={{
                          padding: '0.5rem 1rem',
                          background: expandedCards[idx] ? '#3b82f6' : '#f3f4f6',
                          color: expandedCards[idx] ? 'white' : '#374151',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          fontSize: '0.85rem',
                          fontWeight: '500'
                        }}
                      >
                        {expandedCards[idx] ? 'Less' : 'Details'}
                      </button>
                    </div>
                  )
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
