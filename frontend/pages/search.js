import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import { AuthGuard } from '../utils/AuthGuard';

export default function Search() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState(null);
  const [families, setFamilies] = useState([]);
  const [selectedFamily, setSelectedFamily] = useState('');
  const [expandedResults, setExpandedResults] = useState({});

  const toggleExpanded = (idx) => {
    setExpandedResults(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }));
  };

  // Load available families on mount
  useEffect(() => {
    // Get API base inside useEffect to ensure runtime-config.js has loaded
    const runtimeConfig = (typeof window !== 'undefined' && window.__RUNTIME_CONFIG) ? window.__RUNTIME_CONFIG : null;
    const apiBase = runtimeConfig?.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com';
    
    fetch(`${apiBase}/api/search/families`)
      .then(res => res.json())
      .then(data => setFamilies(data.families || []))
      .catch(err => console.error('Failed to load families:', err));
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setError(null);

    try {
      const runtimeConfig = (typeof window !== 'undefined' && window.__RUNTIME_CONFIG) ? window.__RUNTIME_CONFIG : null;
      const apiBase = runtimeConfig?.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com';
      
      const response = await fetch(
        `${apiBase}/api/search?q=${encodeURIComponent(searchQuery)}`
      );
      
      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setSearchResults(data.results || []);
    } catch (err) {
      setError('Failed to search. Please try again.');
      console.error('Search error:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleFamilyFilter = async (family) => {
    setSelectedFamily(family);
    setIsSearching(true);
    setError(null);

    try {
      const runtimeConfig = (typeof window !== 'undefined' && window.__RUNTIME_CONFIG) ? window.__RUNTIME_CONFIG : null;
      const apiBase = runtimeConfig?.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com';
      
      const response = await fetch(
        `${apiBase}/api/search/by-family?family=${encodeURIComponent(family)}`
      );
      
      if (!response.ok) {
        throw new Error('Filter failed');
      }

      const data = await response.json();
      setSearchResults(data.results || []);
      setSearchQuery('');
    } catch (err) {
      setError('Failed to filter. Please try again.');
      console.error('Filter error:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const clearFilters = () => {
    setSelectedFamily('');
    setSearchQuery('');
    setSearchResults([]);
  };

  const navigateToDiagnosis = (treeId) => {
    router.push(`/diagnostic?tree=${treeId}`);
  };

  return (
    <AuthGuard>
      <Head>
        <title>Search Diagnoses - RealDiag</title>
        <meta name="description" content="Search medical diagnoses by name, ICD-10 code, or specialty" />
      </Head>

      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f0fdfa 0%, #e7f5f3 100%)',
        padding: '1rem'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          {/* Navigation Dropdown */}
          <details style={{
            background: 'white',
            padding: '0.75rem 1.25rem',
            borderRadius: '10px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            border: '1px solid #e2e8f0',
            marginBottom: '1rem',
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

          {/* Header */}
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '1.5rem',
            marginBottom: '1rem',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <h1 style={{
              margin: '0 0 0.5rem 0',
              color: '#0d9488',
              fontSize: '1.75rem',
              fontWeight: '700'
            }}>
              🔍 Search Diagnoses
            </h1>
            <p style={{
              margin: 0,
              color: '#6b7280',
              fontSize: '0.95rem'
            }}>
              Search by diagnosis name, ICD-10 code, or browse by specialty
            </p>
          </div>

          {/* Search Form */}
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '1.5rem',
            marginBottom: '1rem',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <form onSubmit={handleSearch} style={{ marginBottom: '1rem' }}>
              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by name or ICD-10 code (e.g., 'pneumonia', 'I21.9')..."
                  style={{
                    flex: '1 1 300px',
                    padding: '0.75rem',
                    border: '2px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '1rem',
                    outline: 'none',
                    transition: 'border-color 0.2s'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#0d9488'}
                  onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                />
                <button
                  type="submit"
                  disabled={isSearching || !searchQuery.trim()}
                  style={{
                    padding: '0.75rem 1.5rem',
                    background: '#0d9488',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: isSearching || !searchQuery.trim() ? 'not-allowed' : 'pointer',
                    opacity: isSearching || !searchQuery.trim() ? 0.6 : 1,
                    transition: 'all 0.2s',
                    whiteSpace: 'nowrap'
                  }}
                  onMouseEnter={(e) => {
                    if (!isSearching && searchQuery.trim()) {
                      e.target.style.background = '#0f766e';
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.background = '#0d9488';
                  }}
                >
                  {isSearching ? '🔍 Searching...' : '🔍 Search'}
                </button>
              </div>
            </form>

            {/* Family Filter */}
            <div>
              <label style={{
                display: 'block',
                marginBottom: '0.5rem',
                fontWeight: '600',
                color: '#0d9488',
                fontSize: '0.95rem'
              }}>
                Or browse by specialty:
              </label>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
                <select
                  value={selectedFamily}
                  onChange={(e) => handleFamilyFilter(e.target.value)}
                  style={{
                    flex: '1 1 300px',
                    padding: '0.75rem',
                    fontSize: '1rem',
                    border: '2px solid #e5e7eb',
                    borderRadius: '8px',
                    outline: 'none',
                    cursor: 'pointer',
                    background: 'white'
                  }}
                  disabled={isSearching}
                >
                  <option value="">Select a specialty...</option>
                  {families.map(family => (
                    <option key={family} value={family}>
                      {family}
                    </option>
                  ))}
                </select>
                {(selectedFamily || searchResults.length > 0) && (
                  <button
                    onClick={clearFilters}
                    style={{
                      padding: '0.75rem 1.5rem',
                      fontSize: '1rem',
                      fontWeight: '600',
                      color: '#0d9488',
                      background: 'white',
                      border: '2px solid #0d9488',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      whiteSpace: 'nowrap'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = '#f0fdfa';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'white';
                    }}
                  >
                    Clear
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div style={{
              background: '#fed7d7',
              color: '#c53030',
              padding: '1rem',
              borderRadius: '8px',
              marginBottom: '2rem'
            }}>
              {error}
            </div>
          )}

          {/* Results */}
          {searchResults.length > 0 && (
            <div style={{
              background: 'white',
              borderRadius: '12px',
              padding: '1.5rem',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <h2 style={{
                margin: '0 0 1rem 0',
                color: '#0d9488',
                fontSize: '1.25rem',
                fontWeight: '700'
              }}>
                Found {searchResults.length} result{searchResults.length !== 1 ? 's' : ''}
              </h2>

              <div style={{
                display: 'grid',
                gap: '1rem'
              }}>
                {searchResults.map((result, index) => (
                  <div
                    key={index}
                    style={{
                      padding: '1.5rem',
                      border: '2px solid #e5e7eb',
                      borderRadius: '12px',
                      background: 'white'
                    }}
                  >
                    {/* Header */}
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start',
                      marginBottom: '1rem',
                      gap: '1rem',
                      flexWrap: 'wrap',
                      paddingBottom: '1rem',
                      borderBottom: '2px solid #e7f5f3'
                    }}>
                      <h3 style={{
                        margin: 0,
                        color: '#0d9488',
                        fontSize: '1.5rem',
                        fontWeight: '700'
                      }}>
                        {result.name}
                      </h3>
                      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                        {result.icd10 && (
                          <span style={{
                            padding: '0.5rem 1rem',
                            background: '#0d9488',
                            color: 'white',
                            borderRadius: '6px',
                            fontSize: '0.875rem',
                            fontWeight: '600'
                          }}>
                            ICD-10: {result.icd10}
                          </span>
                        )}
                        {result.urgency && (
                          <span style={{
                            padding: '0.5rem 1rem',
                            background: result.urgency === 'critical' ? '#dc2626' : result.urgency === 'urgent' ? '#f59e0b' : '#10b981',
                            color: 'white',
                            borderRadius: '6px',
                            fontSize: '0.875rem',
                            fontWeight: '600'
                          }}>
                            {result.urgency.toUpperCase()}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Description */}
                    {result.description && (
                      <p style={{
                        margin: '0 0 1rem',
                        color: '#4b5563',
                        fontSize: '1rem',
                        lineHeight: '1.6'
                      }}>
                        {result.description}
                      </p>
                    )}

                    {/* Metadata */}
                    <div style={{
                      display: 'flex',
                      gap: '0.5rem',
                      marginBottom: '1rem',
                      flexWrap: 'wrap'
                    }}>
                      {result.family && (
                        <span style={{
                          padding: '0.25rem 0.75rem',
                          background: '#e7f5f3',
                          color: '#0d9488',
                          borderRadius: '6px',
                          fontSize: '0.875rem',
                          fontWeight: '500'
                        }}>
                          📚 {result.family}
                        </span>
                      )}
                      {result.specialty && (
                        <span style={{
                          padding: '0.25rem 0.75rem',
                          background: '#e7f5f3',
                          color: '#0d9488',
                          borderRadius: '6px',
                          fontSize: '0.875rem',
                          fontWeight: '500'
                        }}>
                          🏥 {result.specialty}
                        </span>
                      )}
                    </div>

                    {/* Expand/Collapse Button */}
                    <button
                      onClick={() => toggleExpanded(index)}
                      style={{
                        width: '100%',
                        padding: '0.75rem',
                        background: expandedResults[index] ? '#14b8a6' : '#ccfbf1',
                        color: expandedResults[index] ? 'white' : '#0f766e',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontWeight: '600',
                        fontSize: '0.9rem',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '0.5rem',
                        transition: 'all 0.2s',
                        marginTop: '1rem'
                      }}
                    >
                      <span>{expandedResults[index] ? '▼' : '▶'}</span>
                      {expandedResults[index] ? 'Show Less' : 'Show All Details'}
                    </button>

                    {/* Clinical Details - Horizontal Grid Layout (Collapsible) */}
                    {expandedResults[index] && (
                    <div style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                      gap: '1rem',
                      marginTop: '1rem'
                    }}>
                      {/* Presentations */}
                      {result.presentations && result.presentations.length > 0 && (
                        <div style={{
                          padding: '1rem',
                          background: 'linear-gradient(to right, #ecfdf5, #f0fdf4)',
                          borderLeft: '4px solid #10b981',
                          borderRadius: '8px',
                          height: 'fit-content'
                        }}>
                          <h4 style={{
                            margin: '0 0 0.75rem',
                            color: '#065f46',
                            fontSize: '0.875rem',
                            fontWeight: '700',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                          }}>
                            <span>🩺</span> Presentations
                          </h4>
                          <div style={{
                            display: 'flex',
                            flexWrap: 'wrap',
                            gap: '0.5rem'
                          }}>
                            {result.presentations.map((pres, i) => (
                              <span key={i} style={{ padding: '0.25rem 0.75rem', background: '#d1fae5', color: '#065f46', borderRadius: '6px', fontSize: '0.75rem', fontWeight: '600' }}>{pres}</span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Workup */}
                      {result.workup && result.workup.length > 0 && (
                        <div style={{
                          padding: '1rem',
                          background: 'linear-gradient(to right, #ccfbf1, #f0fdfa)',
                          borderLeft: '4px solid #14b8a6',
                          borderRadius: '8px',
                          height: 'fit-content'
                        }}>
                          <h4 style={{
                            margin: '0 0 0.75rem',
                            color: '#0f766e',
                            fontSize: '0.875rem',
                            fontWeight: '700',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                          }}>
                            <span>🔬</span> Diagnostic Workup
                          </h4>
                          <ul style={{
                            margin: 0,
                            paddingLeft: '1.25rem',
                            color: '#0f766e',
                            fontSize: '0.875rem',
                            lineHeight: '1.6'
                          }}>
                            {result.workup.map((test, i) => (
                              <li key={i} style={{ marginBottom: '0.5rem', fontWeight: '500' }}>{test}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Treatment */}
                      {result.treatment && result.treatment.length > 0 && (
                        <div style={{
                          padding: '1rem',
                          background: 'linear-gradient(to right, #fce7f3, #fdf2f8)',
                          borderLeft: '4px solid #ec4899',
                          borderRadius: '8px',
                          height: 'fit-content'
                        }}>
                          <h4 style={{
                            margin: '0 0 0.75rem',
                            color: '#9f1239',
                            fontSize: '0.875rem',
                            fontWeight: '700',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                          }}>
                            <span>💊</span> Treatment
                          </h4>
                          <div style={{
                            display: 'flex',
                            flexWrap: 'wrap',
                            gap: '0.5rem'
                          }}>
                            {result.treatment.map((tx, i) => (
                              <span key={i} style={{ padding: '0.25rem 0.75rem', background: '#fce7f3', color: '#9f1239', borderRadius: '6px', fontSize: '0.75rem', fontWeight: '600' }}>{tx}</span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Clinical Pearls */}
                      {result.clinical_pearls && result.clinical_pearls.length > 0 && (
                        <div style={{
                          padding: '1rem',
                          background: 'linear-gradient(to right, #fef3c7, #fef9e7)',
                          borderLeft: '4px solid #f59e0b',
                          borderRadius: '8px',
                          height: 'fit-content'
                        }}>
                          <h4 style={{
                            margin: '0 0 0.75rem',
                            color: '#92400e',
                            fontSize: '0.875rem',
                            fontWeight: '700',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                          }}>
                            <span>💎</span> Clinical Pearls
                          </h4>
                          <div style={{
                            display: 'flex',
                            flexWrap: 'wrap',
                            gap: '0.5rem'
                          }}>
                            {result.clinical_pearls.map((pearl, i) => (
                              <span key={i} style={{ padding: '0.25rem 0.75rem', background: '#fef3c7', color: '#92400e', borderRadius: '6px', fontSize: '0.75rem', fontWeight: '600' }}>{pearl}</span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Referrals */}
                      {result.referrals && result.referrals.length > 0 && (
                        <div style={{
                          padding: '1rem',
                          background: 'linear-gradient(to right, #dbeafe, #eff6ff)',
                          borderLeft: '4px solid #3b82f6',
                          borderRadius: '8px',
                          height: 'fit-content'
                        }}>
                          <h4 style={{
                            margin: '0 0 0.75rem',
                            color: '#1e40af',
                            fontSize: '0.875rem',
                            fontWeight: '700',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                          }}>
                            <span>👨‍⚕️</span> Referrals
                          </h4>
                          <div style={{
                            display: 'flex',
                            flexWrap: 'wrap',
                            gap: '0.5rem'
                          }}>
                            {result.referrals.map((ref, i) => (
                              <span key={i} style={{ padding: '0.25rem 0.75rem', background: '#dbeafe', color: '#1e40af', borderRadius: '6px', fontSize: '0.75rem', fontWeight: '600' }}>{ref}</span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Homeopathic Remedies */}
                      {result.homeopathic_remedies && result.homeopathic_remedies.length > 0 && (
                        <div style={{
                          padding: '1rem',
                          background: 'linear-gradient(to right, #e0e7ff, #eef2ff)',
                          borderLeft: '4px solid #6366f1',
                          borderRadius: '8px',
                          height: 'fit-content'
                        }}>
                          <h4 style={{
                            margin: '0 0 0.75rem',
                            color: '#4338ca',
                            fontSize: '0.875rem',
                            fontWeight: '700',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                          }}>
                            <span>🌿</span> Homeopathic Options
                          </h4>
                          <ul style={{
                            margin: 0,
                            paddingLeft: '1.25rem',
                            color: '#4338ca',
                            fontSize: '0.875rem',
                            lineHeight: '1.6'
                          }}>
                            {result.homeopathic_remedies.map((remedy, i) => (
                              <li key={i} style={{ marginBottom: '0.5rem', fontWeight: '500' }}>{remedy}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* SNOMED Codes */}
                      {result.snomed && result.snomed.length > 0 && (
                        <div style={{
                          padding: '1rem',
                          background: 'linear-gradient(to right, #f3f4f6, #f9fafb)',
                          borderLeft: '4px solid #6b7280',
                          borderRadius: '8px',
                          height: 'fit-content'
                        }}>
                          <h4 style={{
                            margin: '0 0 0.75rem',
                            color: '#374151',
                            fontSize: '0.875rem',
                            fontWeight: '700',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                          }}>
                            <span>🔖</span> SNOMED Codes
                          </h4>
                          <div style={{
                            display: 'flex',
                            flexWrap: 'wrap',
                            gap: '0.5rem'
                          }}>
                            {result.snomed.map((code, i) => (
                              <span key={i} style={{
                                padding: '0.25rem 0.75rem',
                                background: '#e5e7eb',
                                color: '#374151',
                                borderRadius: '6px',
                                fontSize: '0.75rem',
                                fontWeight: '600',
                                fontFamily: 'monospace'
                              }}>
                                {code}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    )}
                    {/* End collapsible section */}

                    {/* ICD-10 Code (always visible) */}
                    {result.icd10 && (
                      <div style={{
                        marginTop: '1rem',
                        padding: '0.75rem',
                        background: 'linear-gradient(to right, #f9fafb, #ffffff)',
                        border: '1px solid #e5e7eb',
                        borderRadius: '6px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                      }}>
                        <span style={{
                          fontSize: '0.75rem',
                          fontWeight: '600',
                          color: '#6b7280',
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px'
                        }}>
                          ICD-10:
                        </span>
                        <span style={{
                          padding: '0.25rem 0.75rem',
                          background: '#f3f4f6',
                          color: '#374151',
                          borderRadius: '6px',
                          fontSize: '0.875rem',
                          fontWeight: '700',
                          fontFamily: 'monospace'
                        }}>
                          {result.icd10}
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* No Results */}
          {!isSearching && searchResults.length === 0 && (searchQuery || selectedFamily) && (
            <div style={{
              background: 'white',
              borderRadius: '12px',
              padding: '2rem',
              textAlign: 'center',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
              <h3 style={{
                margin: '0 0 0.5rem 0',
                color: '#0d9488',
                fontSize: '1.25rem',
                fontWeight: '600'
              }}>
                No results found
              </h3>
              <p style={{
                margin: 0,
                color: '#6b7280',
                fontSize: '0.95rem'
              }}>
                Try a different search term or browse by specialty
              </p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div style={{
              background: '#fee',
              border: '2px solid #fcc',
              borderRadius: '8px',
              padding: '1rem',
              color: '#c33',
              textAlign: 'center'
            }}>
              {error}
            </div>
          )}
        </div>
      </div>
    </AuthGuard>
  );
}
