/**
 * Symptom-Based Diagnostic Search Interface
 * Phase 3: Mobile-First Responsive Design & User Personalization
 * Last updated: 2025-11-17 - Comprehensive rule updates with clinical_pearls, management, tests, referrals
 * Build: 2025-11-17T14:30:00Z
 */

import { useState, useMemo, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { calculateLikelihood, getConfidenceLevel, getConfidenceColor } from '../utils/decisionSupport';

export default function SymptomSearch() {
  // Use runtime config for API base, with fallback to env var or Render URL
  const runtimeConfig = (typeof window !== 'undefined' && window.__RUNTIME_CONFIG) ? window.__RUNTIME_CONFIG : null;
  const apiBase = runtimeConfig?.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com';
  
  // Debug logging
  if (typeof window !== 'undefined') {
    console.log('🔍 API Base URL:', apiBase);
    console.log('🔍 Runtime Config:', runtimeConfig);
    console.log('🔍 Process Env:', process.env.NEXT_PUBLIC_API_BASE);
  }
  
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
  const [sortBy, setSortBy] = useState('likelihood'); // 'likelihood', 'score', 'alpha', 'family'
  const [expandedCards, setExpandedCards] = useState({});
  const [darkMode, setDarkMode] = useState(false);
  const [fontSize, setFontSize] = useState('medium'); // 'small', 'medium', 'large'
  const [showPreferences, setShowPreferences] = useState(false);
  const [recentSearches, setRecentSearches] = useState([]);
  const [displayLimit, setDisplayLimit] = useState(5); // New: Show only 5 results initially
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Load preferences from localStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedViewMode = localStorage.getItem('viewMode');
      const savedSortBy = localStorage.getItem('sortBy');
      const savedDarkMode = localStorage.getItem('darkMode');
      const savedFontSize = localStorage.getItem('fontSize');
      const savedRecentSearches = localStorage.getItem('recentSearches');
      
      if (savedViewMode) setViewMode(savedViewMode);
      if (savedSortBy) setSortBy(savedSortBy);
      if (savedDarkMode) setDarkMode(savedDarkMode === 'true');
      if (savedFontSize) setFontSize(savedFontSize);
      if (savedRecentSearches) {
        try {
          setRecentSearches(JSON.parse(savedRecentSearches));
        } catch (e) {
          console.error('Error loading recent searches:', e);
        }
      }
      
      // Check authentication
      const token = localStorage.getItem('realdiag_token');
      if (token) {
        fetchUserProfile(token);
      }
    }
  }, []);

  // Fetch user profile
  const fetchUserProfile = async (token) => {
    try {
      const response = await fetch(`${apiBase}/users/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setIsAuthenticated(true);
      } else {
        localStorage.removeItem('realdiag_token');
      }
    } catch (err) {
      console.error('Failed to fetch user profile:', err);
    }
  };

  // Save preferences to localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('viewMode', viewMode);
      localStorage.setItem('sortBy', sortBy);
      localStorage.setItem('darkMode', darkMode.toString());
      localStorage.setItem('fontSize', fontSize);
    }
  }, [viewMode, sortBy, darkMode, fontSize]);

  // Save recent searches
  const saveRecentSearch = (searchData) => {
    const newSearch = {
      symptoms: searchData.symptoms,
      timestamp: new Date().toISOString(),
      resultsCount: searchData.resultsCount
    };
    
    const updated = [newSearch, ...recentSearches.filter(
      s => JSON.stringify(s.symptoms) !== JSON.stringify(newSearch.symptoms)
    )].slice(0, 5); // Keep only 5 most recent
    
    setRecentSearches(updated);
    localStorage.setItem('recentSearches', JSON.stringify(updated));
  };

  const loadRecentSearch = (search) => {
    setSymptoms(search.symptoms);
    setShowPreferences(false);
  };

  // Theme and font size helper functions
  const getThemeStyles = () => {
    const baseStyle = {
      minHeight: '100vh',
      padding: '1rem',
      transition: 'background 0.3s, color 0.3s'
    };

    if (darkMode) {
      baseStyle.background = 'linear-gradient(135deg, #1a202c 0%, #2d3748 100%)';
      baseStyle.color = '#e5e7eb';
    } else {
      baseStyle.background = 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)';
      baseStyle.color = '#1a202c';
    }

    return baseStyle;
  };

  const getFontSizeMultiplier = () => {
    switch (fontSize) {
      case 'small': return 0.875;
      case 'large': return 1.125;
      default: return 1;
    }
  };

  const getCardBackground = () => darkMode ? '#2d3748' : 'white';
  const getTextColor = () => darkMode ? '#e5e7eb' : '#1a202c';
  const getSecondaryTextColor = () => darkMode ? '#9ca3af' : '#6b7280';
  const getBorderColor = () => darkMode ? '#4b5563' : '#e5e7eb';

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
      case 'likelihood':
        // Sort by Bayesian likelihood score (primary), then match score (secondary)
        return sorted.sort((a, b) => {
          const likelihoodA = calculateLikelihood(a) || 0;
          const likelihoodB = calculateLikelihood(b) || 0;
          if (Math.abs(likelihoodA - likelihoodB) > 0.1) {
            return likelihoodB - likelihoodA;
          }
          return b.match_score - a.match_score;
        });
      case 'alpha':
        return sorted.sort((a, b) => a.label.localeCompare(b.label));
      case 'family':
        return sorted.sort((a, b) => a.family.localeCompare(b.family));
      case 'score':
        return sorted.sort((a, b) => b.match_score - a.match_score);
      default:
        return sorted.sort((a, b) => {
          const likelihoodA = calculateLikelihood(a) || 0;
          const likelihoodB = calculateLikelihood(b) || 0;
          return likelihoodB - likelihoodA;
        });
    }
  };

  // Get limited results for display
  const getDisplayedResults = () => {
    const sorted = getSortedResults();
    const limited = sorted.slice(0, displayLimit);
    console.log('🔍 Display Debug:', {
      totalResults: sorted.length,
      displayLimit: displayLimit,
      showing: limited.length
    });
    return limited;
  };

  // Check if there are more results to show
  const hasMoreResults = () => {
    const hasMore = getSortedResults().length > displayLimit;
    console.log('🔍 hasMoreResults:', hasMore, 'total:', getSortedResults().length, 'limit:', displayLimit);
    return hasMore;
  };

  // Show more results
  const showMoreResults = () => {
    setDisplayLimit(prev => Math.min(prev + 5, results.length));
  };

  // Show all results
  const showAllResults = () => {
    setDisplayLimit(results.length);
  };

  // Reset display limit when new search
  const resetDisplayLimit = () => {
    setDisplayLimit(5);
  };

  const getSensitivityColor = (value) => {
    if (!value) return '#9ca3af';
    if (value >= 0.90) return '#10b981'; // High (green)
    if (value >= 0.80) return '#f59e0b'; // Moderate (amber)
    return '#ef4444'; // Low (red)
  };

  const getSpecificityColor = (value) => {
    if (!value) return '#9ca3af';
    if (value >= 0.90) return '#10b981'; // High (green)
    if (value >= 0.80) return '#f59e0b'; // Moderate (amber)
    return '#ef4444'; // Low (red)
  };

  const renderSensitivityBadge = (sensitivity) => {
    if (!sensitivity) return null;
    const percentage = (sensitivity * 100).toFixed(0);
    const color = getSensitivityColor(sensitivity);
    
    return (
      <div style={{
        display: 'inline-flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '0.5rem 0.75rem',
        background: 'white',
        border: `2px solid ${color}`,
        borderRadius: '8px',
        minWidth: '80px'
      }}>
        <div style={{ fontSize: '0.7rem', color: '#6b7280', fontWeight: '600', marginBottom: '0.25rem' }}>
          SENSITIVITY
        </div>
        <div style={{ fontSize: '1.1rem', fontWeight: '700', color }}>
          {percentage}%
        </div>
        <div style={{
          width: '100%',
          height: '4px',
          background: '#e5e7eb',
          borderRadius: '2px',
          marginTop: '0.25rem',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${percentage}%`,
            height: '100%',
            background: color,
            transition: 'width 0.3s'
          }} />
        </div>
      </div>
    );
  };

  const renderSpecificityBadge = (specificity) => {
    if (!specificity) return null;
    const percentage = (specificity * 100).toFixed(0);
    const color = getSpecificityColor(specificity);
    
    return (
      <div style={{
        display: 'inline-flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '0.5rem 0.75rem',
        background: 'white',
        border: `2px solid ${color}`,
        borderRadius: '8px',
        minWidth: '80px'
      }}>
        <div style={{ fontSize: '0.7rem', color: '#6b7280', fontWeight: '600', marginBottom: '0.25rem' }}>
          SPECIFICITY
        </div>
        <div style={{ fontSize: '1.1rem', fontWeight: '700', color }}>
          {percentage}%
        </div>
        <div style={{
          width: '100%',
          height: '4px',
          background: '#e5e7eb',
          borderRadius: '2px',
          marginTop: '0.25rem',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${percentage}%`,
            height: '100%',
            background: color,
            transition: 'width 0.3s'
          }} />
        </div>
      </div>
    );
  };

  const handleSearch = async () => {
    if (symptoms.length === 0) {
      setError('Please enter at least one symptom');
      return;
    }

    setLoading(true);
    setError(null);
    setHasSearched(true);
    resetDisplayLimit(); // Reset to show 5 results

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
      
      // Save to recent searches (local)
      if (data.results && data.results.length > 0) {
        saveRecentSearch({
          symptoms: symptoms,
          resultsCount: data.results.length
        });
      }
      
      // Track search in user history if authenticated
      if (isAuthenticated) {
        const token = localStorage.getItem('realdiag_token');
        if (token) {
          try {
            await fetch(`${apiBase}/users/me/history`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify({
                symptoms: symptoms,
                age: ageValue ? parseInt(ageValue) : null,
                sex: sex || null,
                family: family || null,
                result_count: data.results.length
              })
            });
          } catch (err) {
            console.error('Failed to track search:', err);
          }
        }
      }
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

  // Add to favorites
  const addToFavorites = async (result) => {
    if (!isAuthenticated) {
      alert('Please sign in to save favorites');
      window.location.href = '/account';
      return;
    }

    const token = localStorage.getItem('realdiag_token');
    if (!token) return;

    try {
      const response = await fetch(`${apiBase}/users/me/favorites`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          rule_id: result.rule_id,
          diagnosis_label: result.label,
          family: result.family,
          notes: ''
        })
      });

      if (response.ok) {
        alert('✅ Added to favorites!');
      } else if (response.status === 400) {
        alert('ℹ️ Already in favorites');
      } else {
        throw new Error('Failed to add favorite');
      }
    } catch (err) {
      console.error('Error adding favorite:', err);
      alert('❌ Failed to add favorite');
    }
  };

  return (
    <div style={getThemeStyles()}>
      {/* Mobile-optimized header */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto 1rem',
        background: getCardBackground(),
        padding: '1rem',
        borderRadius: '8px',
        boxShadow: darkMode ? '0 1px 3px rgba(0,0,0,0.3)' : '0 1px 3px rgba(0,0,0,0.1)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: '1 1 auto' }}>
          <Image 
            src="/logo.png" 
            alt="RealDiag Logo" 
            width={50} 
            height={50}
            style={{ maxHeight: '50px', width: 'auto' }}
          />
          <div>
            <h1 style={{ 
              margin: 0, 
              fontSize: `${1.5 * getFontSizeMultiplier()}rem`, 
              color: getTextColor(),
              fontWeight: '700'
            }}>
              Symptom Search
            </h1>
            <p style={{ 
              margin: '0.25rem 0 0', 
              color: getSecondaryTextColor(), 
              fontSize: `${0.85 * getFontSizeMultiplier()}rem` 
            }}>
              Find diagnoses by symptoms
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button
            onClick={() => setShowPreferences(!showPreferences)}
            style={{
              padding: '0.5rem 1rem',
              background: darkMode ? '#4b5563' : '#f3f4f6',
              color: getTextColor(),
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: `${0.85 * getFontSizeMultiplier()}rem`,
              fontWeight: '500',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              minHeight: '44px'
            }}
          >
            ⚙️ Settings
          </button>
          <Link href="/" style={{
            padding: '0.5rem 1rem',
            background: '#3b82f6',
            color: 'white',
            borderRadius: '6px',
            textDecoration: 'none',
            fontSize: `${0.85 * getFontSizeMultiplier()}rem`,
            fontWeight: '500',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            minHeight: '44px'
          }}>
            ← Home
          </Link>
          <Link href="/account" style={{
            padding: '0.5rem 1rem',
            background: isAuthenticated ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#10b981',
            color: 'white',
            borderRadius: '6px',
            textDecoration: 'none',
            fontSize: `${0.85 * getFontSizeMultiplier()}rem`,
            fontWeight: '500',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            minHeight: '44px',
            boxShadow: '0 2px 8px rgba(102, 126, 234, 0.3)'
          }}>
            {isAuthenticated ? `👤 ${user?.full_name?.split(' ')[0] || 'Account'}` : '👤 Sign In'}
          </Link>
        </div>
      </div>

      {/* Preferences Panel */}
      {showPreferences && (
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto 1rem',
          background: getCardBackground(),
          padding: '1.5rem',
          borderRadius: '8px',
          boxShadow: darkMode ? '0 4px 6px rgba(0,0,0,0.3)' : '0 4px 6px rgba(0,0,0,0.1)',
          border: `2px solid ${darkMode ? '#3b82f6' : '#3b82f6'}`
        }}>
          <h3 style={{ 
            margin: '0 0 1rem', 
            color: getTextColor(), 
            fontSize: `${1.1 * getFontSizeMultiplier()}rem`,
            fontWeight: '600'
          }}>
            ⚙️ Preferences
          </h3>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '1rem', 
            marginBottom: '1rem' 
          }}>
            {/* Dark Mode */}
            <div>
              <label style={{ 
                display: 'block', 
                marginBottom: '0.5rem', 
                fontWeight: '500', 
                color: getTextColor(), 
                fontSize: `${0.9 * getFontSizeMultiplier()}rem` 
              }}>
                Theme
              </label>
              <button
                onClick={() => setDarkMode(!darkMode)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: darkMode ? '#3b82f6' : '#f3f4f6',
                  color: darkMode ? 'white' : '#1a202c',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: `${0.9 * getFontSizeMultiplier()}rem`,
                  fontWeight: '500',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem',
                  minHeight: '44px'
                }}
              >
                {darkMode ? '🌙 Dark Mode' : '☀️ Light Mode'}
              </button>
            </div>

            {/* Font Size */}
            <div>
              <label style={{ 
                display: 'block', 
                marginBottom: '0.5rem', 
                fontWeight: '500', 
                color: getTextColor(), 
                fontSize: `${0.9 * getFontSizeMultiplier()}rem` 
              }}>
                Font Size
              </label>
              <select
                value={fontSize}
                onChange={(e) => setFontSize(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: darkMode ? '#374151' : 'white',
                  color: getTextColor(),
                  border: `1px solid ${getBorderColor()}`,
                  borderRadius: '6px',
                  fontSize: `${0.9 * getFontSizeMultiplier()}rem`,
                  minHeight: '44px'
                }}
              >
                <option value="small">Small (0.875×)</option>
                <option value="medium">Medium (1×)</option>
                <option value="large">Large (1.125×)</option>
              </select>
            </div>
          </div>

          {/* Recent Searches */}
          {recentSearches.length > 0 && (
            <div>
              <h4 style={{ 
                margin: '1rem 0 0.5rem', 
                color: getTextColor(), 
                fontSize: `${0.95 * getFontSizeMultiplier()}rem`,
                fontWeight: '600'
              }}>
                📝 Recent Searches
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {recentSearches.map((search, idx) => (
                  <button
                    key={idx}
                    onClick={() => loadRecentSearch(search)}
                    style={{
                      padding: '0.75rem',
                      background: darkMode ? '#374151' : '#f9fafb',
                      color: getTextColor(),
                      border: `1px solid ${getBorderColor()}`,
                      borderRadius: '6px',
                      cursor: 'pointer',
                      textAlign: 'left',
                      fontSize: `${0.85 * getFontSizeMultiplier()}rem`,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      minHeight: '44px',
                      transition: 'background 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = darkMode ? '#4b5563' : '#f3f4f6';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = darkMode ? '#374151' : '#f9fafb';
                    }}
                  >
                    <span style={{ flex: 1 }}>
                      {search.symptoms.join(', ')} 
                    </span>
                    <span style={{ 
                      color: getSecondaryTextColor(), 
                      fontSize: `${0.8 * getFontSizeMultiplier()}rem`,
                      marginLeft: '0.5rem',
                      whiteSpace: 'nowrap'
                    }}>
                      {search.resultsCount} results
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Main Content */}
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Search Form */}
        <div style={{
          background: getCardBackground(),
          padding: '1.5rem',
          borderRadius: '8px',
          boxShadow: darkMode ? '0 1px 3px rgba(0,0,0,0.3)' : '0 1px 3px rgba(0,0,0,0.1)',
          marginBottom: '1.5rem'
        }}>
          <h2 style={{ 
            marginTop: 0, 
            color: getTextColor(), 
            fontSize: `${1.25 * getFontSizeMultiplier()}rem`,
            fontWeight: '600'
          }}>
            Enter Patient Symptoms
          </h2>

          {/* Symptom Input */}
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '0.5rem', 
              fontWeight: '500', 
              color: getTextColor(),
              fontSize: `${0.9 * getFontSizeMultiplier()}rem`
            }}>
              Add Symptoms
            </label>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <input
                type="text"
                value={symptomInput}
                onChange={(e) => setSymptomInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="e.g., chest pain, shortness of breath, fever"
                style={{
                  flex: '1 1 200px',
                  padding: '0.75rem',
                  border: `1px solid ${getBorderColor()}`,
                  borderRadius: '6px',
                  fontSize: `${1 * getFontSizeMultiplier()}rem`,
                  background: darkMode ? '#374151' : 'white',
                  color: getTextColor(),
                  minHeight: '44px'
                }}
              />
              <button
                onClick={handleAddSymptom}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: '500',
                  fontSize: `${1 * getFontSizeMultiplier()}rem`,
                  minHeight: '44px'
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
                  background: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
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
                background: symptoms.length === 0 || loading ? '#9ca3af' : 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
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
                    (Showing {Math.min(displayLimit, results.length)} of {results.length} {results.length === 1 ? 'match' : 'matches'})
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
                      <option value="likelihood">Likelihood (Recommended)</option>
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
              <>
              <div style={{ display: 'flex', flexDirection: 'column', gap: viewMode === 'card' ? '1.5rem' : '0.75rem' }}>
                {getDisplayedResults().map((result, idx) => (
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
                          alignItems: 'flex-end',
                          gap: '0.75rem'
                        }}>
                          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                            <button
                              onClick={() => addToFavorites(result)}
                              style={{
                                padding: '0.5rem 1rem',
                                background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                                color: 'white',
                                border: 'none',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                fontWeight: '600',
                                fontSize: '0.85rem',
                                boxShadow: '0 2px 4px rgba(245, 158, 11, 0.3)',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.25rem'
                              }}
                              title="Add to favorites"
                            >
                              ⭐ Favorite
                            </button>
                          </div>
                          {/* Likelihood Score */}
                          {(() => {
                            const likelihood = calculateLikelihood(result);
                            const confidenceLevel = getConfidenceLevel(likelihood);
                            const confidenceColor = getConfidenceColor(likelihood);
                            return likelihood ? (
                              <div style={{
                                padding: '0.75rem 1.25rem',
                                background: `linear-gradient(135deg, ${confidenceColor} 0%, ${confidenceColor}dd 100%)`,
                                color: 'white',
                                borderRadius: '8px',
                                fontWeight: '700',
                                fontSize: '1.1rem',
                                boxShadow: `0 4px 6px rgba(16, 185, 129, 0.2)`,
                                textAlign: 'center',
                                minWidth: '120px',
                                border: `2px solid ${confidenceColor}`
                              }}>
                                <div style={{ fontSize: '0.7rem', fontWeight: '500', opacity: 0.9, marginBottom: '0.25rem' }}>LIKELIHOOD</div>
                                <div style={{ fontSize: '1.3rem' }}>{likelihood.toFixed(0)}%</div>
                                <div style={{ fontSize: '0.65rem', opacity: 0.9, marginTop: '0.15rem' }}>{confidenceLevel}</div>
                              </div>
                            ) : null;
                          })()}
                          {/* Test Characteristics */}
                          {(result.sensitivity || result.specificity) && (
                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                              {renderSensitivityBadge(result.sensitivity)}
                              {renderSpecificityBadge(result.specificity)}
                            </div>
                          )}
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
                            {/* Work-Up Section */}
                            {(result.tests || result.referrals) && (
                              <div style={{ 
                                marginBottom: '1.5rem',
                                padding: '1rem',
                                background: 'linear-gradient(to right, #e0f2fe, #f0f9ff)',
                                borderRadius: '8px',
                                borderLeft: '4px solid #0ea5e9'
                              }}>
                                <h4 style={{ 
                                  margin: '0 0 0.75rem', 
                                  color: '#075985', 
                                  fontSize: '0.95rem', 
                                  fontWeight: '700',
                                  textTransform: 'uppercase',
                                  letterSpacing: '0.5px',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '0.5rem'
                                }}>
                                  <span>🔬</span> Recommended Work-Up
                                </h4>
                                
                                {result.tests && result.tests.length > 0 && (
                                  <div style={{ marginBottom: result.referrals && result.referrals.length > 0 ? '1rem' : '0' }}>
                                    <h5 style={{ 
                                      margin: '0 0 0.5rem', 
                                      color: '#0c4a6e', 
                                      fontSize: '0.85rem', 
                                      fontWeight: '600'
                                    }}>
                                      📋 Diagnostic Tests:
                                    </h5>
                                    <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#075985' }}>
                                      {result.tests.map((test, i) => (
                                        <li key={i} style={{ 
                                          marginBottom: '0.5rem', 
                                          lineHeight: '1.6',
                                          fontSize: '0.9rem',
                                          fontWeight: '500'
                                        }}>
                                          {test}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                                
                                {result.referrals && result.referrals.length > 0 && (
                                  <div>
                                    <h5 style={{ 
                                      margin: '0 0 0.5rem', 
                                      color: '#0c4a6e', 
                                      fontSize: '0.85rem', 
                                      fontWeight: '600'
                                    }}>
                                      👨‍⚕️ Specialist Referrals:
                                    </h5>
                                    <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#075985' }}>
                                      {result.referrals.map((referral, i) => (
                                        <li key={i} style={{ 
                                          marginBottom: '0.5rem', 
                                          lineHeight: '1.6',
                                          fontSize: '0.9rem',
                                          fontWeight: '500'
                                        }}>
                                          {referral}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </div>
                            )}
                            
                            {/* Clinical Pearls */}
                            {result.clinical_pearls && result.clinical_pearls.length > 0 && (
                              <div style={{ 
                                marginBottom: '1.5rem',
                                padding: '1rem',
                                background: 'linear-gradient(to right, #fef3c7, #fef9e7)',
                                borderRadius: '8px',
                                borderLeft: '4px solid #f59e0b'
                              }}>
                                <h4 style={{ 
                                  margin: '0 0 0.75rem', 
                                  color: '#92400e', 
                                  fontSize: '0.95rem', 
                                  fontWeight: '700',
                                  textTransform: 'uppercase',
                                  letterSpacing: '0.5px',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '0.5rem'
                                }}>
                                  <span>💡</span> Clinical Pearls
                                </h4>
                                <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#78350f' }}>
                                  {result.clinical_pearls.map((pearl, i) => (
                                    <li key={i} style={{ 
                                      marginBottom: '0.5rem', 
                                      lineHeight: '1.6',
                                      fontSize: '0.9rem',
                                      fontWeight: '500'
                                    }}>
                                      {pearl}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Management */}
                            {result.management && result.management.length > 0 && (
                              <div style={{ 
                                marginBottom: '1.5rem',
                                padding: '1rem',
                                background: 'linear-gradient(to right, #dbeafe, #eff6ff)',
                                borderRadius: '8px',
                                borderLeft: '4px solid #3b82f6'
                              }}>
                                <h4 style={{ 
                                  margin: '0 0 0.75rem', 
                                  color: '#1e40af', 
                                  fontSize: '0.95rem', 
                                  fontWeight: '700',
                                  textTransform: 'uppercase',
                                  letterSpacing: '0.5px',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '0.5rem'
                                }}>
                                  <span>💊</span> Management
                                </h4>
                                <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#1e3a8a' }}>
                                  {result.management.map((step, i) => (
                                    <li key={i} style={{ 
                                      marginBottom: '0.5rem', 
                                      lineHeight: '1.6',
                                      fontSize: '0.9rem',
                                      fontWeight: '500'
                                    }}>
                                      {step}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

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
                        onClick={() => addToFavorites(result)}
                        style={{
                          padding: '0.5rem 0.75rem',
                          background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          fontSize: '0.85rem',
                          fontWeight: '600'
                        }}
                        title="Add to favorites"
                      >
                        ⭐
                      </button>
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
              
              {/* Show More Button */}
              {hasMoreResults() && (
                <div style={{ 
                  marginTop: '2rem', 
                  display: 'flex', 
                  gap: '1rem',
                  justifyContent: 'center',
                  alignItems: 'center',
                  flexWrap: 'wrap'
                }}>
                  <button
                    onClick={showMoreResults}
                    style={{
                      padding: '1rem 2rem',
                      background: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontSize: '1rem',
                      fontWeight: '600',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                      transition: 'all 0.2s',
                      minHeight: '48px'
                    }}
                    onMouseEnter={(e) => e.target.style.background = 'linear-gradient(135deg, #0d9488 0%, #0f766e 100%)'}
                    onMouseLeave={(e) => e.target.style.background = 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)'}
                  >
                    📊 Show 5 More Results ({getSortedResults().length - displayLimit} remaining)
                  </button>
                  <button
                    onClick={showAllResults}
                    style={{
                      padding: '1rem 2rem',
                      background: 'white',
                      color: '#14b8a6',
                      border: '2px solid #14b8a6',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontSize: '1rem',
                      fontWeight: '600',
                      transition: 'all 0.2s',
                      minHeight: '48px'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = '#eff6ff';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'white';
                    }}
                  >
                    📋 Show All {results.length} Results
                  </button>
                </div>
              )}
              </>
            )}
          </div>
        )}
      </div>

      {/* Mobile-responsive CSS */}
      <style jsx>{`
        @media (max-width: 640px) {
          /* Stack items vertically on mobile */
          div[style*="display: flex"] {
            flex-wrap: wrap;
          }
          
          /* Full-width buttons on mobile */
          button, input, select {
            width: 100% !important;
            flex: 1 1 100% !important;
          }
          
          /* Increase padding for touch targets */
          button {
            padding: 0.875rem 1rem !important;
            min-height: 48px !important;
          }
          
          /* Larger text on mobile */
          input, select, textarea {
            font-size: 16px !important; /* Prevents zoom on iOS */
          }
          
          /* Reduce container padding */
          div[style*="padding: 1.5rem"] {
            padding: 1rem !important;
          }
          
          /* Stack header items */
          header > div {
            flex-direction: column;
            align-items: stretch !important;
          }
        }
        
        @media (min-width: 641px) and (max-width: 1024px) {
          /* Tablet adjustments */
          div[style*="gridTemplateColumns"] {
            grid-template-columns: repeat(2, 1fr) !important;
          }
        }
        
        /* Smooth transitions for theme changes */
        * {
          transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
        }
        
        /* Touch-friendly hover states */
        @media (hover: hover) {
          button:hover {
            opacity: 0.9;
          }
        }
        
        /* Focus states for accessibility */
        button:focus, input:focus, select:focus {
          outline: 2px solid #3b82f6;
          outline-offset: 2px;
        }
        
        /* Print styles */
        @media print {
          button, nav, header {
            display: none !important;
          }
        }
      `}</style>
    </div>
  );
}
