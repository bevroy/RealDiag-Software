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
                gap: '0.75rem'
              }}>
                {searchResults.map((result, index) => (
                  <div
                    key={index}
                    onClick={() => navigateToDiagnosis(result.tree_id)}
                    style={{
                      padding: '1.25rem',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      background: 'white'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#0d9488';
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(13,148,136,0.15)';
                      e.currentTarget.style.background = '#f0fdfa';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#e5e7eb';
                      e.currentTarget.style.boxShadow = 'none';
                      e.currentTarget.style.background = 'white';
                    }}
                  >
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start',
                      marginBottom: '0.5rem',
                      gap: '1rem',
                      flexWrap: 'wrap'
                    }}>
                      <h3 style={{
                        margin: 0,
                        color: '#1a202c',
                        fontSize: '1.125rem',
                        fontWeight: '600'
                      }}>
                        {result.name}
                      </h3>
                      {result.icd10 && (
                        <span style={{
                          padding: '0.25rem 0.75rem',
                          background: '#0d9488',
                          color: 'white',
                          borderRadius: '6px',
                          fontSize: '0.875rem',
                          fontWeight: '600',
                          whiteSpace: 'nowrap'
                        }}>
                          {result.icd10}
                        </span>
                      )}
                    </div>

                    {result.description && (
                      <p style={{
                        margin: '0.5rem 0',
                        color: '#6b7280',
                        fontSize: '0.95rem',
                        lineHeight: '1.5'
                      }}>
                        {result.description}
                      </p>
                    )}

                    <div style={{
                      display: 'flex',
                      gap: '0.5rem',
                      marginTop: '0.75rem',
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
                      {result.chief_complaint && (
                        <span style={{
                          padding: '0.25rem 0.75rem',
                          background: '#e7f5f3',
                          color: '#0d9488',
                          borderRadius: '6px',
                          fontSize: '0.875rem',
                          fontWeight: '500'
                        }}>
                          💬 {result.chief_complaint}
                        </span>
                      )}
                    </div>
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
