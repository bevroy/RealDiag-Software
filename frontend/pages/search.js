import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import AuthGuard from '../utils/AuthGuard';

export default function Search() {
  const router = useRouter();
  
  // Use the same API base pattern as other pages
  const apiBase = typeof window !== 'undefined' 
    ? (window.runtimeConfig?.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com')
    : 'https://realdiag-software.onrender.com';
  
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState(null);
  const [families, setFamilies] = useState([]);
  const [selectedFamily, setSelectedFamily] = useState('');

  // Load available families on mount
  useEffect(() => {
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
      </Head>

      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '2rem'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          {/* Header */}
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '2rem',
            marginBottom: '2rem',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}>
            <h1 style={{
              margin: '0 0 1rem 0',
              color: '#2d3748',
              fontSize: '2rem'
            }}>
              🔍 Search Diagnoses
            </h1>
            <p style={{
              margin: 0,
              color: '#718096'
            }}>
              Search by diagnosis name, ICD-10 code, or browse by specialty
            </p>
          </div>

          {/* Search Form */}
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '2rem',
            marginBottom: '2rem',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}>
            <form onSubmit={handleSearch} style={{ marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by name or ICD-10 code (e.g., 'pneumonia', 'I21.9', 'diabetes')..."
                  style={{
                    flex: 1,
                    padding: '0.75rem 1rem',
                    fontSize: '1rem',
                    border: '2px solid #e2e8f0',
                    borderRadius: '8px',
                    outline: 'none'
                  }}
                  disabled={isSearching}
                />
                <button
                  type="submit"
                  disabled={isSearching || !searchQuery.trim()}
                  style={{
                    padding: '0.75rem 2rem',
                    fontSize: '1rem',
                    fontWeight: '600',
                    color: 'white',
                    background: isSearching || !searchQuery.trim() ? '#cbd5e0' : '#667eea',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: isSearching || !searchQuery.trim() ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  {isSearching ? 'Searching...' : 'Search'}
                </button>
              </div>
            </form>

            {/* Family Filter */}
            <div>
              <label style={{
                display: 'block',
                marginBottom: '0.5rem',
                fontWeight: '600',
                color: '#2d3748'
              }}>
                Or browse by specialty:
              </label>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <select
                  value={selectedFamily}
                  onChange={(e) => handleFamilyFilter(e.target.value)}
                  style={{
                    flex: 1,
                    padding: '0.75rem 1rem',
                    fontSize: '1rem',
                    border: '2px solid #e2e8f0',
                    borderRadius: '8px',
                    outline: 'none',
                    cursor: 'pointer'
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
                      color: '#667eea',
                      background: 'white',
                      border: '2px solid #667eea',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
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
              padding: '2rem',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
            }}>
              <h2 style={{
                margin: '0 0 1.5rem 0',
                color: '#2d3748',
                fontSize: '1.5rem'
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
                    onClick={() => navigateToDiagnosis(result.tree_id)}
                    style={{
                      padding: '1.5rem',
                      border: '2px solid #e2e8f0',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      ':hover': {
                        borderColor: '#667eea',
                        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                      }
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#667eea';
                      e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#e2e8f0';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  >
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start',
                      marginBottom: '0.5rem'
                    }}>
                      <h3 style={{
                        margin: 0,
                        color: '#2d3748',
                        fontSize: '1.25rem',
                        fontWeight: '600'
                      }}>
                        {result.name}
                      </h3>
                      {result.icd10 && (
                        <span style={{
                          padding: '0.25rem 0.75rem',
                          background: '#667eea',
                          color: 'white',
                          borderRadius: '6px',
                          fontSize: '0.875rem',
                          fontWeight: '600'
                        }}>
                          {result.icd10}
                        </span>
                      )}
                    </div>

                    {result.description && (
                      <p style={{
                        margin: '0.5rem 0',
                        color: '#718096',
                        fontSize: '0.95rem'
                      }}>
                        {result.description}
                      </p>
                    )}

                    <div style={{
                      display: 'flex',
                      gap: '1rem',
                      marginTop: '0.75rem',
                      flexWrap: 'wrap'
                    }}>
                      {result.family && (
                        <span style={{
                          padding: '0.25rem 0.75rem',
                          background: '#edf2f7',
                          color: '#4a5568',
                          borderRadius: '6px',
                          fontSize: '0.875rem'
                        }}>
                          📚 {result.family}
                        </span>
                      )}
                      {result.specialty && (
                        <span style={{
                          padding: '0.25rem 0.75rem',
                          background: '#edf2f7',
                          color: '#4a5568',
                          borderRadius: '6px',
                          fontSize: '0.875rem'
                        }}>
                          🏥 {result.specialty}
                        </span>
                      )}
                      {result.chief_complaint && (
                        <span style={{
                          padding: '0.25rem 0.75rem',
                          background: '#edf2f7',
                          color: '#4a5568',
                          borderRadius: '6px',
                          fontSize: '0.875rem'
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
              padding: '3rem',
              textAlign: 'center',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🔍</div>
              <h3 style={{
                margin: '0 0 0.5rem 0',
                color: '#2d3748',
                fontSize: '1.5rem'
              }}>
                No results found
              </h3>
              <p style={{
                margin: 0,
                color: '#718096'
              }}>
                Try a different search term or browse by specialty
              </p>
            </div>
          )}
        </div>
      </div>
    </AuthGuard>
  );
}
