import React, { useState, useEffect } from 'react'
import styles from '../styles/Rules.module.css'

export default function Rules() {
  const [families, setFamilies] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [selectedFamily, setSelectedFamily] = useState(null)
  const [loading, setLoading] = useState(false)
  const [apiBase, setApiBase] = useState('')

  // Get API base from runtime config or environment
  useEffect(() => {
    const runtimeConfig = (typeof window !== 'undefined' && window.__RUNTIME_CONFIG) ? window.__RUNTIME_CONFIG : null
    const base = runtimeConfig?.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com'
    setApiBase(base.replace(/\/$/, ''))
  }, [])

  // Fetch available rule families
  useEffect(() => {
    if (!apiBase) return
    fetch(`${apiBase}/rules/families`)
      .then(res => res.json())
      .then(data => setFamilies(data.families || []))
      .catch(err => console.error('Failed to load families:', err))
  }, [apiBase])

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    setLoading(true)
    setSearchResults([])

    try {
      const url = selectedFamily 
        ? `${apiBase}/rules/search?q=${encodeURIComponent(searchQuery)}&family=${selectedFamily}`
        : `${apiBase}/rules/search?q=${encodeURIComponent(searchQuery)}`
      
      const response = await fetch(url)
      const data = await response.json()
      setSearchResults(data.results || [])
    } catch (err) {
      console.error('Search failed:', err)
      alert('Search failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setSearchQuery('')
    setSearchResults([])
    setSelectedFamily(null)
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>📚 Clinical Rules Reference</h1>
        <p>Search diagnostic criteria, presentations, and ICD-10 codes</p>
      </header>

      <div className={styles.main}>
        {/* Search Section */}
        <section className={styles.section}>
          <h2>Search Clinical Rules</h2>
          
          <div className={styles.familyFilter}>
            <label>Filter by Family:</label>
            <select 
              value={selectedFamily || ''} 
              onChange={(e) => setSelectedFamily(e.target.value || null)}
              className={styles.select}
            >
              <option value="">All Families</option>
              {families.map(fam => (
                <option key={fam.family} value={fam.family}>
                  {fam.family} ({fam.rule_count} rules)
                </option>
              ))}
            </select>
          </div>

          <form onSubmit={handleSearch} className={styles.searchForm}>
            <input
              type="text"
              placeholder="Search by condition, symptom, or ICD-10 code..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={styles.searchInput}
            />
            <div className={styles.searchButtons}>
              <button type="submit" disabled={loading} className={styles.searchButton}>
                {loading ? '🔍 Searching...' : '🔍 Search'}
              </button>
              <button type="button" onClick={handleClear} className={styles.clearButton}>
                Clear
              </button>
            </div>
          </form>
        </section>

        {/* Results Section */}
        {searchResults.length > 0 && (
          <section className={styles.section}>
            <h2>Search Results ({searchResults.length})</h2>
            <div className={styles.resultsGrid}>
              {searchResults.map((result, idx) => (
                <div key={idx} className={styles.resultCard}>
                  <div className={styles.resultHeader}>
                    <h3>{result.label}</h3>
                    <span className={styles.badge}>{result.family}</span>
                  </div>
                  
                  <div className={styles.resultSection}>
                    <h4>Presentations:</h4>
                    <ul>
                      {result.presentations.map((pres, i) => (
                        <li key={i}>{pres}</li>
                      ))}
                    </ul>
                  </div>

                  {result.icd10 && result.icd10.length > 0 && (
                    <div className={styles.resultSection}>
                      <h4>ICD-10 Codes:</h4>
                      <div className={styles.icd10List}>
                        {result.icd10.map((code, i) => (
                          <code key={i} className={styles.icd10Code}>{code}</code>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className={styles.resultId}>ID: {result.id}</div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Available Families */}
        <section className={styles.section}>
          <h2>Available Rule Families</h2>
          <div className={styles.familiesGrid}>
            {families.map(fam => (
              <div key={fam.family} className={styles.familyCard}>
                <h3>{fam.family}</h3>
                <p><strong>Version:</strong> {fam.version}</p>
                <p><strong>Rules:</strong> {fam.rule_count}</p>
                {fam.source && <p className={styles.source}>{fam.source}</p>}
              </div>
            ))}
          </div>
        </section>

        {searchResults.length === 0 && searchQuery && !loading && (
          <div className={styles.noResults}>
            <p>No results found for "{searchQuery}"</p>
            <p>Try different search terms or select a different family filter.</p>
          </div>
        )}
      </div>
    </div>
  )
}
