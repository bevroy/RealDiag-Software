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
import { isAuthenticated } from '../utils/auth';
import { detectRedFlags, getSeverityStyle, formatTimeWindow, getActionList } from '../utils/redFlagAlerts';
import { assessUrgency, getUrgencyBadge } from '../utils/timeSensitiveAlerts';
import { analyzeManagementInteractions, getSeverityColor as getDrugSeverityColor, getSeverityIcon } from '../utils/drugInteractions';
import { analyzePathways } from '../utils/costEffectiveness';
import { compareDifferentialDiagnoses, findDistinguishingFeatures } from '../utils/differentialComparison';
import { availableCalculators } from '../utils/pretestCalculators';
import { 
  downloadAllRules, 
  getOfflineStats, 
  isOnline, 
  onConnectionChange,
  requestBackgroundSync 
} from '../utils/offlineManager';
import {
  isVoiceInputSupported,
  createVoiceRecognition,
  normalizeMedicalText,
  detectVoiceCommand,
  requestMicrophonePermission,
  speak
} from '../utils/voiceInput';
import {
  isScannerSupported,
  createBarcodeDetector,
  requestCameraPermission,
  startCameraStream,
  stopCameraStream,
  startContinuousScanning,
  parsePatientID,
  validatePatientID
} from '../utils/barcodeScanner';

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
  const [isUserAuthenticated, setIsUserAuthenticated] = useState(false);
  
  // Advanced features state
  const [expandedRedFlags, setExpandedRedFlags] = useState({});
  const [expandedUrgency, setExpandedUrgency] = useState({});
  const [expandedDrugInteractions, setExpandedDrugInteractions] = useState({});
  const [expandedCostAnalysis, setExpandedCostAnalysis] = useState({});
  const [expandedComparison, setExpandedComparison] = useState({});
  const [selectedCalculator, setSelectedCalculator] = useState(null);
  const [calculatorResults, setCalculatorResults] = useState({});
  const [homeopathyData, setHomeopathyData] = useState({});
  const [expandedHomeopathy, setExpandedHomeopathy] = useState({});
  
  // Mobile features state
  const [offlineStats, setOfflineStats] = useState(null);
  const [isDownloadingRules, setIsDownloadingRules] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [connectionStatus, setConnectionStatus] = useState(true);
  const [showOfflinePanel, setShowOfflinePanel] = useState(false);
  const [voiceRecognition, setVoiceRecognition] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [voiceTranscript, setVoiceTranscript] = useState('');
  const [showVoicePanel, setShowVoicePanel] = useState(false);
  const [barcodeDetector, setBarcodeDetector] = useState(null);
  const [showScanner, setShowScanner] = useState(false);
  const [scannerStream, setScannerStream] = useState(null);
  const [scannedPatientId, setScannedPatientId] = useState(null);
  const [showMobileFeatures, setShowMobileFeatures] = useState(false);

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
      
      // Check authentication (via HttpOnly cookie)
      if (isAuthenticated()) {
        fetchUserProfile();
      }
      
      // Initialize mobile features
      initializeMobileFeatures();
    }
  }, []);

  // Fetch user profile
  const fetchUserProfile = async () => {
    try {
      const userData = await getCurrentUser();
      if (userData) {
        setUser(userData);
        setIsUserAuthenticated(true);
      } else {
        setUser(null);
        setIsUserAuthenticated(false);
      }
    } catch (err) {
      console.error('Failed to fetch user profile:', err);
      setUser(null);
      setIsUserAuthenticated(false);
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
      baseStyle.background = 'linear-gradient(135deg, #0f766e 0%, #0d9488 100%)';
      baseStyle.color = '#e5e7eb';
    } else {
      baseStyle.background = 'linear-gradient(135deg, #f0fdfa 0%, #e7f5f3 100%)';
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
      neurology: "#14b8a6", cardiology: "#0d9488", endocrinology: "#0f766e",
      pulmonology: "#14b8a6", gastroenterology: "#0d9488", infectious_disease: "#0f766e",
      nephrology: "#14b8a6", rheumatology: "#0d9488", dermatology: "#0f766e",
      psychiatry: "#14b8a6", obstetrics_gynecology: "#0d9488",
      hematology_oncology: "#0f766e", orthopedics: "#14b8a6",
      pediatrics: "#0d9488", geriatrics: "#0f766e", emergency_medicine: "#14b8a6",
      surgery: "#0d9488", ent: "#0f766e", ophthalmology: "#14b8a6",
      toxicology: "#0d9488", urology: "#0f766e"
    };
    return colorMap[fam] || "#64748b";
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

  // Mobile features initialization
  const initializeMobileFeatures = async () => {
    // Check connection status
    setConnectionStatus(isOnline());
    onConnectionChange((online) => {
      setConnectionStatus(online);
      if (online) {
        speak('Connection restored');
        requestBackgroundSync('search-sync');
        requestBackgroundSync('favorites-sync');
      } else {
        speak('You are now offline. Cached data is available.');
      }
    });

    // Load offline stats
    const stats = await getOfflineStats();
    setOfflineStats(stats);

    // Initialize voice recognition
    if (isVoiceInputSupported()) {
      const recognition = createVoiceRecognition({
        continuous: false,
        interimResults: true,
        lang: 'en-US'
      });
      setVoiceRecognition(recognition);
    }

    // Initialize barcode detector
    if (isScannerSupported()) {
      const detector = await createBarcodeDetector(['qr_code', 'code_128', 'ean_13']);
      setBarcodeDetector(detector);
    }
  };

  // Download all rules for offline use
  const handleDownloadRules = async () => {
    if (isDownloadingRules) return;

    setIsDownloadingRules(true);
    setDownloadProgress(0);

    try {
      await downloadAllRules(apiBase, (progress) => {
        setDownloadProgress(progress);
      });

      const stats = await getOfflineStats();
      setOfflineStats(stats);

      speak('Rules downloaded successfully');
    } catch (error) {
      console.error('Failed to download rules:', error);
      speak('Failed to download rules');
    } finally {
      setIsDownloadingRules(false);
      setDownloadProgress(0);
    }
  };

  // Voice input handlers
  const handleStartVoiceInput = async () => {
    if (!voiceRecognition) {
      speak('Voice input not supported');
      return;
    }

    const permission = await requestMicrophonePermission();
    if (!permission.granted) {
      speak(permission.message);
      return;
    }

    setIsListening(true);
    setVoiceTranscript('');
    setShowVoicePanel(true);

    voiceRecognition.onstart = () => {
      speak('Listening');
    };

    voiceRecognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map(result => result[0].transcript)
        .join('');
      
      const normalized = normalizeMedicalText(transcript);
      setVoiceTranscript(normalized);

      if (event.results[event.results.length - 1].isFinal) {
        const command = detectVoiceCommand(normalized);
        
        if (command) {
          handleVoiceCommand(command, normalized);
        } else {
          // Add as symptom
          const trimmed = normalized.trim();
          if (trimmed && !symptoms.includes(trimmed)) {
            setSymptoms([...symptoms, trimmed]);
            speak('Symptom added');
          }
        }
      }
    };

    voiceRecognition.onerror = (event) => {
      console.error('Voice recognition error:', event.error);
      setIsListening(false);
      speak('Voice input error');
    };

    voiceRecognition.onend = () => {
      setIsListening(false);
    };

    voiceRecognition.start();
  };

  const handleStopVoiceInput = () => {
    if (voiceRecognition && isListening) {
      voiceRecognition.stop();
      setIsListening(false);
    }
  };

  const handleVoiceCommand = (command, transcript) => {
    switch (command.action) {
      case 'add':
        if (command.value && !symptoms.includes(command.value)) {
          setSymptoms([...symptoms, command.value]);
          speak('Symptom added');
        }
        break;
      case 'search':
        if (symptoms.length > 0) {
          handleSearch();
          speak('Searching');
        } else {
          speak('Please add symptoms first');
        }
        break;
      case 'clear':
        handleClearAll();
        speak('Cleared');
        break;
      case 'help':
        speak('You can say: add symptom, search, clear all');
        break;
    }
  };

  // Barcode scanner handlers
  const handleStartScanner = async () => {
    if (!barcodeDetector) {
      speak('Barcode scanner not supported');
      return;
    }

    const permission = await requestCameraPermission();
    if (!permission.granted) {
      speak(permission.message);
      return;
    }

    setShowScanner(true);

    // Wait for video element to be available
    setTimeout(async () => {
      const video = document.getElementById('scanner-video');
      if (!video) return;

      const result = await startCameraStream(video, { facingMode: 'environment' });
      if (!result.success) {
        speak(result.message);
        setShowScanner(false);
        return;
      }

      setScannerStream(result.stream);

      // Start continuous scanning
      const scanner = startContinuousScanning(barcodeDetector, video, (scanResult) => {
        if (scanResult.success && scanResult.found) {
          const barcode = scanResult.barcodes[0];
          const parsed = parsePatientID(barcode.rawValue, barcode.format);
          const validation = validatePatientID(parsed.patientId);

          if (validation.valid) {
            setScannedPatientId(validation.patientId);
            speak('Patient ID scanned');
            handleStopScanner();
          } else {
            speak(validation.error);
          }
        }
      });

      // Store scanner for cleanup
      video.dataset.scanner = JSON.stringify(scanner);
    }, 100);
  };

  const handleStopScanner = () => {
    const video = document.getElementById('scanner-video');
    if (video) {
      stopCameraStream(video);
      
      // Stop continuous scanning
      const scannerData = video.dataset.scanner;
      if (scannerData) {
        try {
          const scanner = JSON.parse(scannerData);
          if (scanner && scanner.stop) {
            scanner.stop();
          }
        } catch (e) {
          console.error('Failed to stop scanner:', e);
        }
      }
    }

    if (scannerStream) {
      scannerStream.getTracks().forEach(track => track.stop());
      setScannerStream(null);
    }

    setShowScanner(false);
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
    
    return (
      <span style={{
        fontSize: '0.9rem',
        color: '#0f766e',
        fontWeight: '500'
      }}>
        Sensitivity: <strong style={{ color: '#14b8a6' }}>{percentage}%</strong>
      </span>
    );
  };

  const renderSpecificityBadge = (specificity) => {
    if (!specificity) return null;
    const percentage = (specificity * 100).toFixed(0);
    
    return (
      <span style={{
        fontSize: '0.9rem',
        color: '#0f766e',
        fontWeight: '500'
      }}>
        Specificity: <strong style={{ color: '#14b8a6' }}>{percentage}%</strong>
      </span>
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

  const fetchHomeopathyForResult = async (diagnosis, index) => {
    if (homeopathyData[index]) return; // Already fetched
    
    try {
      const response = await fetch(`${apiBase}/homeopathy/suggest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ condition: diagnosis })
      });
      
      if (response.ok) {
        const data = await response.json();
        setHomeopathyData(prev => ({
          ...prev,
          [index]: data
        }));
      }
    } catch (err) {
      console.error('Failed to fetch homeopathy suggestions:', err);
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
      {/* Navigation Dropdown */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto 1rem'
      }}>
        <details style={{
          background: getCardBackground(),
          padding: '0.75rem 1.25rem',
          borderRadius: '10px',
          boxShadow: darkMode ? '0 1px 3px rgba(0,0,0,0.3)' : '0 1px 3px rgba(0,0,0,0.1)',
          border: `1px solid ${darkMode ? '#374151' : '#e2e8f0'}`,
          cursor: 'pointer'
        }}>
          <summary style={{ 
            color: darkMode ? '#5eead4' : '#0f766e', 
            fontSize: `${1 * getFontSizeMultiplier()}rem`,
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
            borderTop: `1px solid ${darkMode ? '#374151' : '#e2e8f0'}`
          }}>
            <a href="/rules" style={{
              padding: '0.75rem',
              background: darkMode ? '#1f2937' : '#f0fdfa',
              border: `1px solid ${darkMode ? '#374151' : '#ccfbf1'}`,
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: darkMode ? '#5eead4' : '#0f766e',
              fontWeight: '600',
              fontSize: `${0.9 * getFontSizeMultiplier()}rem`
            }}>
              📋 Browse Rules
            </a>
            <a href="/search" style={{
              padding: '0.75rem',
              background: darkMode ? '#1f2937' : '#f0fdfa',
              border: `1px solid ${darkMode ? '#374151' : '#ccfbf1'}`,
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: darkMode ? '#5eead4' : '#0f766e',
              fontWeight: '600',
              fontSize: `${0.9 * getFontSizeMultiplier()}rem`
            }}>
              🔍 Diagnosis Search
            </a>
            <a href="/integration" style={{
              padding: '0.75rem',
              background: darkMode ? '#1f2937' : '#f0fdfa',
              border: `1px solid ${darkMode ? '#374151' : '#ccfbf1'}`,
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: darkMode ? '#5eead4' : '#0f766e',
              fontWeight: '600',
              fontSize: `${0.9 * getFontSizeMultiplier()}rem`
            }}>
              🔌 API
            </a>
            <a href="/features-demo" style={{
              padding: '0.75rem',
              background: darkMode ? '#1f2937' : '#f0fdfa',
              border: `1px solid ${darkMode ? '#374151' : '#ccfbf1'}`,
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: darkMode ? '#5eead4' : '#0f766e',
              fontWeight: '600',
              fontSize: `${0.9 * getFontSizeMultiplier()}rem`
            }}>
              ✨ Features
            </a>
            <a href="/education" style={{
              padding: '0.75rem',
              background: darkMode ? '#1f2937' : '#f0fdfa',
              border: `1px solid ${darkMode ? '#374151' : '#ccfbf1'}`,
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: darkMode ? '#5eead4' : '#0f766e',
              fontWeight: '600',
              fontSize: `${0.9 * getFontSizeMultiplier()}rem`
            }}>
              📚 Training
            </a>
            <a href="/sources" style={{
              padding: '0.75rem',
              background: darkMode ? '#1f2937' : '#f0fdfa',
              border: `1px solid ${darkMode ? '#374151' : '#ccfbf1'}`,
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: darkMode ? '#5eead4' : '#0f766e',
              fontWeight: '600',
              fontSize: `${0.9 * getFontSizeMultiplier()}rem`
            }}>
              📖 Sources
            </a>
            <a href="/patient-history" style={{
              padding: '0.75rem',
              background: darkMode ? '#1f2937' : '#f0fdfa',
              border: `1px solid ${darkMode ? '#374151' : '#ccfbf1'}`,
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: darkMode ? '#5eead4' : '#0f766e',
              fontWeight: '600',
              fontSize: `${0.9 * getFontSizeMultiplier()}rem`
            }}>
              📋 Patient History
            </a>
            <a href="/account" style={{
              padding: '0.75rem',
              background: darkMode ? '#1f2937' : '#f0fdfa',
              border: `1px solid ${darkMode ? '#374151' : '#ccfbf1'}`,
              borderRadius: '8px',
              textDecoration: 'none',
              textAlign: 'center',
              color: darkMode ? '#5eead4' : '#0f766e',
              fontWeight: '600',
              fontSize: `${0.9 * getFontSizeMultiplier()}rem`
            }}>
              👤 Account
            </a>
          </div>
        </details>
      </div>

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
          <h1 style={{ 
            margin: 0, 
            fontSize: `${1.5 * getFontSizeMultiplier()}rem`, 
            color: '#78350f',
            fontWeight: '700'
          }}>
            🔍 Symptom Search
          </h1>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <Link href="/" style={{
            padding: '0.5rem 1rem',
            background: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: `${0.85 * getFontSizeMultiplier()}rem`,
            fontWeight: '500',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            minHeight: '44px',
            textDecoration: 'none'
          }}>
            🏠 Home
          </Link>
          <button
            onClick={() => setShowPreferences(!showPreferences)}
            style={{
              padding: '0.5rem 1rem',
              background: darkMode ? '#0d9488' : '#ccfbf1',
              color: darkMode ? 'white' : '#0f766e',
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
          <Link href="/account" style={{
            padding: '0.5rem 1rem',
            background: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
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
            {isUserAuthenticated ? `👤 ${user?.full_name?.split(' ')[0] || 'Account'}` : '👤 Sign In'}
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
          border: `2px solid ${darkMode ? '#14b8a6' : '#14b8a6'}`
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
                  background: darkMode ? '#14b8a6' : '#ccfbf1',
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
              {/* Voice Input Button */}
              {typeof window !== 'undefined' && isVoiceInputSupported() && (
                <button
                  onClick={isListening ? handleStopVoiceInput : handleStartVoiceInput}
                  style={{
                    padding: '0.75rem',
                    background: isListening ? '#ef4444' : '#14b8a6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '1.2rem',
                    minHeight: '44px',
                    minWidth: '44px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                  title={isListening ? 'Stop listening' : 'Voice input'}
                >
                  {isListening ? '⏹️' : '🎤'}
                </button>
              )}
              {/* Barcode Scanner Button */}
              {typeof window !== 'undefined' && isScannerSupported() && (
                <button
                  onClick={handleStartScanner}
                  style={{
                    padding: '0.75rem',
                    background: '#14b8a6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '1.2rem',
                    minHeight: '44px',
                    minWidth: '44px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                  title="Scan patient ID"
                >
                  📷
                </button>
              )}
              {/* Mobile Features Toggle */}
              <button
                onClick={() => setShowMobileFeatures(!showMobileFeatures)}
                style={{
                  padding: '0.75rem',
                  background: '#14b8a6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '1.2rem',
                  minHeight: '44px',
                  minWidth: '44px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  position: 'relative'
                }}
                title="Mobile features"
              >
                📱
                {!connectionStatus && (
                  <span style={{
                    position: 'absolute',
                    top: '4px',
                    right: '4px',
                    width: '8px',
                    height: '8px',
                    background: '#ef4444',
                    borderRadius: '50%',
                    border: '2px solid white'
                  }}></span>
                )}
              </button>
            </div>
          </div>

          {/* Voice Transcript Panel */}
          {showVoicePanel && voiceTranscript && (
            <div style={{
              marginBottom: '1rem',
              padding: '1rem',
              background: isListening ? '#fef3c7' : '#f0fdf4',
              border: `2px solid ${isListening ? '#f59e0b' : '#14b8a6'}`,
              borderRadius: '6px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                {isListening && (
                  <span style={{ fontSize: '1.2rem' }}>🎤</span>
                )}
                <strong style={{ color: isListening ? '#92400e' : '#065f46' }}>
                  {isListening ? 'Listening...' : 'Voice Input'}
                </strong>
              </div>
              <p style={{ margin: '0', color: isListening ? '#78350f' : '#047857' }}>
                {voiceTranscript}
              </p>
            </div>
          )}

          {/* Scanned Patient ID */}
          {scannedPatientId && (
            <div style={{
              marginBottom: '1rem',
              padding: '1rem',
              background: '#ecfdf5',
              border: '2px solid #10b981',
              borderRadius: '6px'
            }}>
              <strong style={{ color: '#065f46' }}>Patient ID:</strong>
              <span style={{ marginLeft: '0.5rem', fontSize: '1.1rem', fontWeight: '600', color: '#047857' }}>
                {scannedPatientId}
              </span>
              <button
                onClick={() => setScannedPatientId(null)}
                style={{
                  marginLeft: '1rem',
                  padding: '0.25rem 0.75rem',
                  background: '#ef4444',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '0.85rem'
                }}
              >
                Clear
              </button>
            </div>
          )}

          {/* Mobile Features Panel */}
          {showMobileFeatures && (
            <div style={{
              marginBottom: '1.5rem',
              padding: '1.5rem',
              background: darkMode ? '#374151' : '#f9fafb',
              borderRadius: '8px',
              border: `2px solid ${connectionStatus ? '#10b981' : '#ef4444'}`
            }}>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                marginBottom: '1rem' 
              }}>
                <h3 style={{ margin: 0, color: getTextColor(), fontSize: '1.1rem', fontWeight: '600' }}>
                  📱 Mobile Features
                </h3>
                <button
                  onClick={() => setShowMobileFeatures(false)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: getTextColor(),
                    cursor: 'pointer',
                    fontSize: '1.5rem',
                    padding: '0',
                    lineHeight: '1'
                  }}
                >
                  ×
                </button>
              </div>

              {/* Connection Status */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem',
                background: connectionStatus ? '#d1fae5' : '#fee2e2',
                border: `1px solid ${connectionStatus ? '#10b981' : '#ef4444'}`,
                borderRadius: '6px',
                marginBottom: '1rem'
              }}>
                <span style={{ fontSize: '1.2rem' }}>
                  {connectionStatus ? '🟢' : '🔴'}
                </span>
                <strong style={{ color: connectionStatus ? '#065f46' : '#991b1b' }}>
                  {connectionStatus ? 'Online' : 'Offline'}
                </strong>
              </div>

              {/* Offline Storage Stats */}
              {offlineStats && (
                <div style={{
                  padding: '1rem',
                  background: darkMode ? '#4b5563' : 'white',
                  borderRadius: '6px',
                  marginBottom: '1rem'
                }}>
                  <h4 style={{ margin: '0 0 0.5rem', color: getTextColor(), fontSize: '0.95rem' }}>
                    📊 Offline Storage
                  </h4>
                  <div style={{ fontSize: '0.85rem', color: getSecondaryTextColor(), lineHeight: '1.6' }}>
                    <div>Rules: {offlineStats.rules.count}</div>
                    <div>Searches: {offlineStats.searches.count}</div>
                    <div>Favorites: {offlineStats.favorites.count}</div>
                    {offlineStats.rules.byFamily && Object.keys(offlineStats.rules.byFamily).length > 0 && (
                      <div style={{ marginTop: '0.5rem' }}>
                        <strong>By Specialty:</strong>
                        {Object.entries(offlineStats.rules.byFamily).slice(0, 5).map(([fam, count]) => (
                          <div key={fam} style={{ marginLeft: '1rem' }}>
                            {getFamilyLabel(fam)}: {count}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Download Rules Button */}
              <button
                onClick={handleDownloadRules}
                disabled={isDownloadingRules || !connectionStatus}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: isDownloadingRules ? '#9ca3af' : 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: isDownloadingRules || !connectionStatus ? 'not-allowed' : 'pointer',
                  fontWeight: '600',
                  fontSize: '0.95rem',
                  minHeight: '44px',
                  marginBottom: '1rem'
                }}
              >
                {isDownloadingRules ? `Downloading... ${Math.round(downloadProgress)}%` : '⬇️ Download All Rules'}
              </button>

              {/* Download Progress Bar */}
              {isDownloadingRules && (
                <div style={{
                  width: '100%',
                  height: '8px',
                  background: darkMode ? '#4b5563' : '#e5e7eb',
                  borderRadius: '4px',
                  overflow: 'hidden',
                  marginBottom: '1rem'
                }}>
                  <div style={{
                    width: `${downloadProgress}%`,
                    height: '100%',
                    background: 'linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%)',
                    transition: 'width 0.3s'
                  }}></div>
                </div>
              )}

              {/* Feature Status */}
              <div style={{ fontSize: '0.85rem', color: getSecondaryTextColor() }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                  <span>{typeof window !== 'undefined' && isVoiceInputSupported() ? '✅' : '❌'}</span>
                  <span>Voice Input</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                  <span>{typeof window !== 'undefined' && isScannerSupported() ? '✅' : '❌'}</span>
                  <span>Barcode Scanner</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span>{offlineStats && offlineStats.rules.count > 0 ? '✅' : '❌'}</span>
                  <span>Offline Data</span>
                </div>
              </div>
            </div>
          )}

          {/* Barcode Scanner Modal */}
          {showScanner && (
            <div style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0,0,0,0.9)',
              zIndex: 9999,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '1rem'
            }}>
              <div style={{
                width: '100%',
                maxWidth: '600px',
                background: '#1a202c',
                borderRadius: '12px',
                padding: '1.5rem',
                position: 'relative'
              }}>
                <button
                  onClick={handleStopScanner}
                  style={{
                    position: 'absolute',
                    top: '1rem',
                    right: '1rem',
                    background: '#ef4444',
                    color: 'white',
                    border: 'none',
                    borderRadius: '50%',
                    width: '44px',
                    height: '44px',
                    cursor: 'pointer',
                    fontSize: '1.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 10
                  }}
                >
                  ×
                </button>
                
                <h3 style={{ color: 'white', marginTop: 0, marginBottom: '1rem', textAlign: 'center' }}>
                  📷 Scan Patient ID
                </h3>
                
                <video
                  id="scanner-video"
                  autoPlay
                  playsInline
                  style={{
                    width: '100%',
                    borderRadius: '8px',
                    background: '#000'
                  }}
                ></video>
                
                <p style={{ 
                  color: '#9ca3af', 
                  fontSize: '0.85rem', 
                  textAlign: 'center',
                  marginTop: '1rem',
                  marginBottom: 0
                }}>
                  Position the barcode or QR code within the camera view
                </p>
              </div>
            </div>
          )}

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
                background: symptoms.length === 0 || loading ? '#99f6e4' : 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
                color: symptoms.length === 0 || loading ? '#0d9488' : 'white',
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
                background: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
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

        {/* Clinical Decision Calculators */}
        {hasSearched && results.length > 0 && (
          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            marginBottom: '1.5rem'
          }}>
            <details style={{
              cursor: 'pointer'
            }}>
              <summary style={{
                listStyle: 'none',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontSize: '1.25rem',
                fontWeight: '600',
                color: '#0f766e',
                padding: '0.5rem',
                borderRadius: '6px',
                transition: 'background 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = '#f0fdfa'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <span>🧮 Clinical Decision Calculators</span>
                <span style={{ fontSize: '0.8rem', color: '#64748b' }}>▼</span>
              </summary>
              
              <div style={{ marginTop: '1rem' }}>
                <p style={{ marginBottom: '1rem', color: '#6b7280', fontSize: '0.9rem' }}>
                  Use validated clinical scores to support your diagnostic decisions
                </p>
                
                <div style={{ 
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
                  gap: '1rem'
                }}>
                  {availableCalculators.map((calc) => (
                    <button
                      key={calc.id}
                      onClick={() => setSelectedCalculator(calc.id)}
                      style={{
                        padding: '1rem',
                        background: selectedCalculator === calc.id ? '#ccfbf1' : '#f9fafb',
                        border: selectedCalculator === calc.id ? '2px solid #14b8a6' : '2px solid #e5e7eb',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        textAlign: 'left',
                        transition: 'all 0.2s'
                      }}
                    >
                      <div style={{ fontWeight: '700', marginBottom: '0.5rem', color: '#1a202c' }}>
                        {calc.name}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '0.5rem' }}>
                        {calc.category}
                      </div>
                      <div style={{ fontSize: '0.85rem', color: '#374151' }}>
                        {calc.description}
                      </div>
                    </button>
                  ))}
                </div>

                {selectedCalculator && (
                  <div style={{ 
                    marginTop: '1.5rem',
                    padding: '1.5rem',
                    background: '#f0fdfa',
                    borderRadius: '8px',
                    border: '2px solid #14b8a6'
                  }}>
                    <div style={{ 
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '1rem'
                    }}>
                      <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#0f766e' }}>
                        {availableCalculators.find(c => c.id === selectedCalculator)?.name}
                      </h3>
                      <button
                        onClick={() => setSelectedCalculator(null)}
                        style={{
                          padding: '0.5rem 1rem',
                          background: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          fontWeight: '600',
                          fontSize: '0.85rem'
                        }}
                      >
                        Close
                      </button>
                    </div>
                    <div style={{ 
                      padding: '1rem',
                      background: 'white',
                      borderRadius: '6px',
                      fontSize: '0.9rem',
                      color: '#6b7280'
                    }}>
                      <em>Calculator interface would go here - requires user input for specific criteria</em>
                      <div style={{ marginTop: '0.5rem', fontSize: '0.85rem' }}>
                        Note: Full interactive calculators will be implemented in the next phase
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </details>
          </div>
        )}

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
                        background: viewMode === 'card' ? '#14b8a6' : 'white',
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
                        background: viewMode === 'compact' ? '#14b8a6' : 'white',
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
                                background: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
                                color: 'white',
                                border: 'none',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                fontWeight: '600',
                                fontSize: '0.85rem',
                                boxShadow: '0 2px 4px rgba(20, 184, 166, 0.3)',
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
                            return likelihood ? (
                              <span style={{
                                fontSize: '0.9rem',
                                color: '#0f766e',
                                fontWeight: '500'
                              }}>
                                Likelihood: <strong style={{ color: '#14b8a6', fontSize: '1rem' }}>{likelihood.toFixed(0)}%</strong> <span style={{ fontSize: '0.8rem', color: '#64748b' }}>({confidenceLevel})</span>
                              </span>
                            ) : null;
                          })()}
                          {/* Test Characteristics */}
                          {(result.sensitivity || result.specificity) && (
                            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
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
                            background: expandedCards[idx] ? '#14b8a6' : '#ccfbf1',
                            color: expandedCards[idx] ? 'white' : '#0f766e',
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
                                background: 'linear-gradient(to right, #ccfbf1, #f0fdfa)',
                                borderRadius: '8px',
                                borderLeft: '4px solid #14b8a6'
                              }}>
                                <h4 style={{ 
                                  margin: '0 0 0.75rem', 
                                  color: '#0f766e', 
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
                                      color: '#0f766e', 
                                      fontSize: '0.85rem', 
                                      fontWeight: '600'
                                    }}>
                                      📋 Diagnostic Tests:
                                    </h5>
                                    <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#0f766e' }}>
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
                                      color: '#0f766e', 
                                      fontSize: '0.85rem', 
                                      fontWeight: '600'
                                    }}>
                                      👨‍⚕️ Specialist Referrals:
                                    </h5>
                                    <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#0f766e' }}>
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
                                borderLeft: '4px solid #92400e'
                              }}>
                                <h4 style={{ 
                                  margin: '0 0 0.75rem', 
                                  color: '#78350f', 
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
                                background: 'linear-gradient(to right, #ccfbf1, #f0fdfa)',
                                borderRadius: '8px',
                                borderLeft: '4px solid #14b8a6'
                              }}>
                                <h4 style={{ 
                                  margin: '0 0 0.75rem', 
                                  color: '#0f766e', 
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
                                <ul style={{ margin: '0 0 0.75rem', paddingLeft: '1.5rem', color: '#0f766e' }}>
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
                                <div style={{
                                  marginTop: '0.75rem',
                                  padding: '0.5rem',
                                  background: '#f0fdfa',
                                  borderRadius: '4px',
                                  fontSize: '0.8rem',
                                  fontStyle: 'italic',
                                  color: '#0f766e'
                                }}>
                                  These options are based on published guidelines and are not a substitute for clinical judgment.
                                </div>
                              </div>
                            )}

                            {/* Homeopathic Remedies Section (Optional/Complementary) */}
                            <div style={{ 
                              marginBottom: '1.5rem',
                              border: '2px solid #e0e7ff',
                              borderRadius: '8px',
                              overflow: 'hidden'
                            }}>
                              <button
                                onClick={() => {
                                  const isExpanding = !expandedHomeopathy[idx];
                                  setExpandedHomeopathy({...expandedHomeopathy, [idx]: isExpanding});
                                  if (isExpanding && !homeopathyData[idx]) {
                                    fetchHomeopathyForResult(result.label, idx);
                                  }
                                }}
                                style={{
                                  width: '100%',
                                  padding: '1rem',
                                  background: 'linear-gradient(to right, #e0e7ff, #ede9fe)',
                                  color: '#4c1d95',
                                  border: 'none',
                                  cursor: 'pointer',
                                  fontWeight: '700',
                                  fontSize: '0.95rem',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'space-between',
                                  textAlign: 'left'
                                }}
                              >
                                <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                  🌿 Complementary Homeopathic Remedies
                                  <span style={{ 
                                    fontSize: '0.75rem', 
                                    padding: '0.2rem 0.5rem', 
                                    background: '#c7d2fe', 
                                    borderRadius: '4px',
                                    fontWeight: '600'
                                  }}>
                                    OPTIONAL
                                  </span>
                                </span>
                                <span>{expandedHomeopathy[idx] ? '▼' : '▶'}</span>
                              </button>
                              
                              {expandedHomeopathy[idx] && (
                                <div style={{ padding: '1.5rem', background: 'white' }}>
                                  {/* Disclaimer */}
                                  <div style={{ 
                                    padding: '1rem', 
                                    background: '#fef3c7', 
                                    border: '2px solid #f59e0b',
                                    borderRadius: '6px',
                                    marginBottom: '1rem',
                                    fontSize: '0.85rem',
                                    lineHeight: '1.6'
                                  }}>
                                    <strong style={{ color: '#92400e', display: 'block', marginBottom: '0.5rem' }}>
                                      ⚠️ IMPORTANT DISCLAIMER
                                    </strong>
                                    <p style={{ margin: '0 0 0.5rem', color: '#78350f' }}>
                                      Homeopathic remedies are complementary suggestions based on classical homeopathic literature. 
                                      <strong> These should NOT replace conventional medical diagnosis, treatment, or medications.</strong>
                                    </p>
                                    <p style={{ margin: 0, color: '#78350f' }}>
                                      Always consult with a licensed healthcare provider for medical conditions. 
                                      Homeopathy should be used as a complementary approach under professional guidance.
                                    </p>
                                  </div>
                                  
                                  {/* Loading state */}
                                  {!homeopathyData[idx] && (
                                    <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
                                      Loading homeopathic suggestions...
                                    </div>
                                  )}
                                  
                                  {/* Remedies */}
                                  {homeopathyData[idx] && homeopathyData[idx].remedies && homeopathyData[idx].remedies.length > 0 ? (
                                    <>
                                      <div style={{ marginBottom: '1rem' }}>
                                        {homeopathyData[idx].remedies.map((remedy, remedyIdx) => (
                                          <div key={remedyIdx} style={{ 
                                            marginBottom: '1.5rem',
                                            padding: '1rem',
                                            background: '#f8fafc',
                                            border: '1px solid #cbd5e1',
                                            borderRadius: '6px'
                                          }}>
                                            <div style={{ marginBottom: '0.75rem' }}>
                                              <strong style={{ 
                                                color: '#4c1d95', 
                                                fontSize: '1.05rem',
                                                display: 'block',
                                                marginBottom: '0.25rem'
                                              }}>
                                                {remedy.name}
                                              </strong>
                                              {remedy.common_name && (
                                                <span style={{ 
                                                  fontSize: '0.85rem', 
                                                  color: '#64748b',
                                                  fontStyle: 'italic'
                                                }}>
                                                  ({remedy.common_name})
                                                </span>
                                              )}
                                              <span style={{ 
                                                marginLeft: '0.5rem',
                                                padding: '0.2rem 0.5rem',
                                                background: '#ddd6fe',
                                                color: '#5b21b6',
                                                borderRadius: '4px',
                                                fontSize: '0.75rem',
                                                fontWeight: '600'
                                              }}>
                                                {remedy.potency}
                                              </span>
                                            </div>
                                            
                                            {remedy.indications && remedy.indications.length > 0 && (
                                              <div style={{ marginBottom: '0.75rem' }}>
                                                <div style={{ 
                                                  fontSize: '0.8rem', 
                                                  color: '#475569', 
                                                  fontWeight: '600',
                                                  marginBottom: '0.5rem'
                                                }}>
                                                  Key Indications:
                                                </div>
                                                <ul style={{ 
                                                  margin: 0, 
                                                  paddingLeft: '1.5rem',
                                                  fontSize: '0.85rem',
                                                  color: '#334155'
                                                }}>
                                                  {remedy.indications.map((indication, i) => (
                                                    <li key={i} style={{ marginBottom: '0.25rem' }}>
                                                      {indication}
                                                    </li>
                                                  ))}
                                                </ul>
                                              </div>
                                            )}
                                            
                                            {remedy.modalities && (
                                              <div style={{ 
                                                fontSize: '0.8rem', 
                                                color: '#64748b',
                                                fontStyle: 'italic',
                                                marginBottom: '0.5rem'
                                              }}>
                                                <strong>Modalities:</strong> {remedy.modalities}
                                              </div>
                                            )}
                                            
                                            {remedy.constitution && (
                                              <div style={{ 
                                                fontSize: '0.8rem', 
                                                color: '#64748b',
                                                fontStyle: 'italic'
                                              }}>
                                                <strong>Constitutional type:</strong> {remedy.constitution}
                                              </div>
                                            )}
                                          </div>
                                        ))}
                                      </div>
                                      
                                      {/* Sources */}
                                      <div style={{ 
                                        padding: '0.75rem',
                                        background: '#f1f5f9',
                                        borderRadius: '4px',
                                        fontSize: '0.75rem',
                                        color: '#475569'
                                      }}>
                                        <strong>Sources:</strong> {homeopathyData[idx].sources && homeopathyData[idx].sources.join(', ')}
                                      </div>
                                    </>
                                  ) : homeopathyData[idx] && (
                                    <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
                                      No homeopathic suggestions available for this condition.
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>

                            {/* Advanced Clinical Decision Support Features */}
                            
                            {/* Red Flag Alerts */}
                            {(() => {
                              const redFlags = detectRedFlags(result.diagnosis);
                              if (redFlags.length === 0) return null;
                              
                              return (
                                <div style={{ 
                                  marginBottom: '1.5rem',
                                  border: `3px solid ${getSeverityStyle(redFlags[0].severity).border}`,
                                  borderRadius: '8px',
                                  overflow: 'hidden',
                                  animation: redFlags[0].severity === 'critical' ? 'pulse 2s ease-in-out infinite' : 'none'
                                }}>
                                  <button
                                    onClick={() => setExpandedRedFlags({...expandedRedFlags, [idx]: !expandedRedFlags[idx]})}
                                    style={{
                                      width: '100%',
                                      padding: '1rem',
                                      background: getSeverityStyle(redFlags[0].severity).bg,
                                      color: getSeverityStyle(redFlags[0].severity).text,
                                      border: 'none',
                                      cursor: 'pointer',
                                      fontWeight: '700',
                                      fontSize: '0.95rem',
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'space-between',
                                      textAlign: 'left'
                                    }}
                                  >
                                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                      {getSeverityStyle(redFlags[0].severity).icon} RED FLAG ALERT: {redFlags[0].alert}
                                    </span>
                                    <span>{expandedRedFlags[idx] ? '▼' : '▶'}</span>
                                  </button>
                                  
                                  {expandedRedFlags[idx] && (
                                    <div style={{ padding: '1rem', background: 'white' }}>
                                      {redFlags.map((flag, flagIdx) => (
                                        <div key={flagIdx} style={{ marginBottom: flagIdx < redFlags.length - 1 ? '1.5rem' : '0' }}>
                                          <div style={{ marginBottom: '0.75rem' }}>
                                            <strong style={{ color: '#dc2626' }}>⏱️ {formatTimeWindow(flag.timeWindow)}</strong>
                                          </div>
                                          <div style={{ marginBottom: '0.75rem' }}>
                                            <strong>Outcome if Delayed:</strong> {flag.mortality}
                                          </div>
                                          <div>
                                            <strong style={{ display: 'block', marginBottom: '0.5rem' }}>Critical Actions:</strong>
                                            <ol style={{ margin: 0, paddingLeft: '1.5rem' }}>
                                              {getActionList(flag).map((action, actionIdx) => (
                                                <li key={actionIdx} style={{ marginBottom: '0.5rem', lineHeight: '1.5' }}>
                                                  {action.action}
                                                </li>
                                              ))}
                                            </ol>
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  )}
                                </div>
                              );
                            })()}

                            {/* Time-Sensitive Urgency Alert */}
                            {(() => {
                              const urgencyInfo = assessUrgency(result.diagnosis);
                              if (!urgencyInfo.hasTimeWindow) return null;
                              
                              const badge = getUrgencyBadge(urgencyInfo.urgency.level);
                              
                              return (
                                <div style={{ 
                                  marginBottom: '1.5rem',
                                  border: `2px solid ${badge.color}`,
                                  borderRadius: '8px',
                                  overflow: 'hidden'
                                }}>
                                  <button
                                    onClick={() => setExpandedUrgency({...expandedUrgency, [idx]: !expandedUrgency[idx]})}
                                    style={{
                                      width: '100%',
                                      padding: '1rem',
                                      background: badge.bgColor,
                                      color: badge.color,
                                      border: 'none',
                                      cursor: 'pointer',
                                      fontWeight: '700',
                                      fontSize: '0.95rem',
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'space-between',
                                      textAlign: 'left'
                                    }}
                                  >
                                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                      {badge.icon} URGENCY: {badge.label} - {urgencyInfo.urgency.timeWindow}
                                    </span>
                                    <span>{expandedUrgency[idx] ? '▼' : '▶'}</span>
                                  </button>
                                  
                                  {expandedUrgency[idx] && (
                                    <div style={{ padding: '1rem', background: 'white' }}>
                                      <div style={{ marginBottom: '1rem' }}>
                                        <strong>Time to Treatment:</strong> {urgencyInfo.timeToTreatment}
                                      </div>
                                      {urgencyInfo.outcomeWithDelay && (
                                        <div style={{ marginBottom: '1rem' }}>
                                          <strong>Outcome if Delayed:</strong> {urgencyInfo.outcomeWithDelay}
                                        </div>
                                      )}
                                      {urgencyInfo.criticalActions && (
                                        <div>
                                          <strong style={{ display: 'block', marginBottom: '0.5rem' }}>Critical Actions:</strong>
                                          <ol style={{ margin: 0, paddingLeft: '1.5rem' }}>
                                            {urgencyInfo.criticalActions.map((action, actionIdx) => (
                                              <li key={actionIdx} style={{ marginBottom: '0.5rem', lineHeight: '1.5' }}>
                                                {action}
                                              </li>
                                            ))}
                                          </ol>
                                        </div>
                                      )}
                                      {urgencyInfo.milestones && (
                                        <div style={{ marginTop: '1rem' }}>
                                          <strong style={{ display: 'block', marginBottom: '0.5rem' }}>Treatment Milestones:</strong>
                                          <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                                            {urgencyInfo.milestones.map((milestone, mIdx) => (
                                              <li key={mIdx} style={{ marginBottom: '0.5rem' }}>
                                                <strong>{milestone.time}:</strong> {milestone.action}
                                              </li>
                                            ))}
                                          </ul>
                                        </div>
                                      )}
                                    </div>
                                  )}
                                </div>
                              );
                            })()}

                            {/* Drug Interactions Checker */}
                            {result.management && result.management.length > 0 && (() => {
                              const managementText = result.management.join(' ');
                              const interactionAnalysis = analyzeManagementInteractions(managementText);
                              
                              if (!interactionAnalysis.hasInteractions) return null;
                              
                              return (
                                <div style={{ 
                                  marginBottom: '1.5rem',
                                  border: interactionAnalysis.hasMajorInteractions ? '2px solid #dc2626' : '2px solid #f59e0b',
                                  borderRadius: '8px',
                                  overflow: 'hidden'
                                }}>
                                  <button
                                    onClick={() => setExpandedDrugInteractions({...expandedDrugInteractions, [idx]: !expandedDrugInteractions[idx]})}
                                    style={{
                                      width: '100%',
                                      padding: '1rem',
                                      background: interactionAnalysis.hasMajorInteractions ? '#fee2e2' : '#fef3c7',
                                      color: interactionAnalysis.hasMajorInteractions ? '#7f1d1d' : '#92400e',
                                      border: 'none',
                                      cursor: 'pointer',
                                      fontWeight: '700',
                                      fontSize: '0.95rem',
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'space-between',
                                      textAlign: 'left'
                                    }}
                                  >
                                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                      💊 DRUG INTERACTIONS DETECTED ({interactionAnalysis.interactions.length})
                                    </span>
                                    <span>{expandedDrugInteractions[idx] ? '▼' : '▶'}</span>
                                  </button>
                                  
                                  {expandedDrugInteractions[idx] && (
                                    <div style={{ padding: '1rem', background: 'white' }}>
                                      {interactionAnalysis.interactions.map((interaction, intIdx) => {
                                        const severityColors = getDrugSeverityColor(interaction.severity);
                                        return (
                                          <div 
                                            key={intIdx} 
                                            style={{ 
                                              marginBottom: intIdx < interactionAnalysis.interactions.length - 1 ? '1rem' : '0',
                                              padding: '0.75rem',
                                              background: severityColors.bg,
                                              borderLeft: `4px solid ${severityColors.border}`,
                                              borderRadius: '4px'
                                            }}
                                          >
                                            <div style={{ marginBottom: '0.5rem' }}>
                                              <strong style={{ textTransform: 'capitalize' }}>
                                                {getSeverityIcon(interaction.severity)} {interaction.severity} Interaction
                                              </strong>
                                            </div>
                                            <div style={{ marginBottom: '0.5rem' }}>
                                              <strong>{interaction.drug1}</strong> + <strong>{interaction.drug2}</strong>
                                            </div>
                                            <div style={{ marginBottom: '0.5rem' }}>
                                              <strong>Effect:</strong> {interaction.effect}
                                            </div>
                                            <div style={{ marginBottom: '0.5rem' }}>
                                              <strong>Alternative:</strong> {interaction.alternative}
                                            </div>
                                            {interaction.monitoring && (
                                              <div style={{ fontSize: '0.85rem', fontStyle: 'italic', color: '#6b7280' }}>
                                                {interaction.monitoring}
                                              </div>
                                            )}
                                          </div>
                                        );
                                      })}
                                    </div>
                                  )}
                                </div>
                              );
                            })()}

                            {/* Cost-Effectiveness Analysis */}
                            {(() => {
                              const pathwayAnalysis = analyzePathways(result.diagnosis);
                              if (!pathwayAnalysis) return null;
                              
                              return (
                                <div style={{ 
                                  marginBottom: '1.5rem',
                                  border: '2px solid #14b8a6',
                                  borderRadius: '8px',
                                  overflow: 'hidden'
                                }}>
                                  <button
                                    onClick={() => setExpandedCostAnalysis({...expandedCostAnalysis, [idx]: !expandedCostAnalysis[idx]})}
                                    style={{
                                      width: '100%',
                                      padding: '1rem',
                                      background: '#ccfbf1',
                                      color: '#134e4a',
                                      border: 'none',
                                      cursor: 'pointer',
                                      fontWeight: '700',
                                      fontSize: '0.95rem',
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'space-between',
                                      textAlign: 'left'
                                    }}
                                  >
                                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                      💰 COST-EFFECTIVENESS ANALYSIS
                                    </span>
                                    <span>{expandedCostAnalysis[idx] ? '▼' : '▶'}</span>
                                  </button>
                                  
                                  {expandedCostAnalysis[idx] && (
                                    <div style={{ padding: '1rem', background: 'white' }}>
                                      {/* Quick Recommendations */}
                                      <div style={{ marginBottom: '1.5rem' }}>
                                        <h5 style={{ margin: '0 0 0.75rem', fontSize: '0.9rem', fontWeight: '700' }}>
                                          Quick Recommendations:
                                        </h5>
                                        {pathwayAnalysis.recommendations.map((rec, recIdx) => (
                                          <div key={recIdx} style={{ 
                                            marginBottom: '0.75rem',
                                            padding: '0.75rem',
                                            background: '#f0fdfa',
                                            borderRadius: '4px',
                                            borderLeft: '3px solid #14b8a6'
                                          }}>
                                            <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>
                                              {rec.title}: {rec.pathway}
                                            </div>
                                            <div style={{ fontSize: '0.85rem', color: '#6b7280' }}>
                                              {rec.reason}
                                            </div>
                                          </div>
                                        ))}
                                      </div>

                                      {/* Pathway Comparison */}
                                      <div>
                                        <h5 style={{ margin: '0 0 0.75rem', fontSize: '0.9rem', fontWeight: '700' }}>
                                          Diagnostic Pathways:
                                        </h5>
                                        {pathwayAnalysis.pathways.map((pathway, pIdx) => (
                                          <div key={pIdx} style={{ 
                                            marginBottom: '1rem',
                                            padding: '1rem',
                                            border: '1px solid #d1d5db',
                                            borderRadius: '6px'
                                          }}>
                                            <div style={{ 
                                              display: 'flex', 
                                              justifyContent: 'space-between',
                                              alignItems: 'start',
                                              marginBottom: '0.75rem'
                                            }}>
                                              <strong>{pathway.name}</strong>
                                              <span style={{ 
                                                padding: '0.25rem 0.75rem',
                                                background: pathway === pathwayAnalysis.cheapest ? '#d1fae5' : 
                                                           pathway === pathwayAnalysis.fastest ? '#dbeafe' : '#f3f4f6',
                                                color: pathway === pathwayAnalysis.cheapest ? '#065f46' : 
                                                       pathway === pathwayAnalysis.fastest ? '#1e40af' : '#374151',
                                                borderRadius: '4px',
                                                fontSize: '0.75rem',
                                                fontWeight: '600'
                                              }}>
                                                {pathway === pathwayAnalysis.cheapest ? '💰 Cheapest' : 
                                                 pathway === pathwayAnalysis.fastest ? '⚡ Fastest' : 
                                                 pathway === pathwayAnalysis.mostEfficient ? '🎯 Most Efficient' : ''}
                                              </span>
                                            </div>
                                            <div style={{ 
                                              display: 'grid',
                                              gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                                              gap: '0.75rem',
                                              marginBottom: '0.75rem',
                                              fontSize: '0.85rem'
                                            }}>
                                              <div>
                                                <strong>Cost:</strong> ${pathway.totalCost}
                                              </div>
                                              <div>
                                                <strong>Time:</strong> {pathway.timeDescription}
                                              </div>
                                              <div>
                                                <strong>Sensitivity:</strong> {pathway.sensitivity}%
                                              </div>
                                              <div>
                                                <strong>Specificity:</strong> {pathway.specificity}%
                                              </div>
                                            </div>
                                            <div style={{ fontSize: '0.85rem', color: '#6b7280', marginBottom: '0.5rem' }}>
                                              {pathway.notes}
                                            </div>
                                            <div style={{ fontSize: '0.8rem' }}>
                                              <strong>Tests:</strong> {pathway.tests.join(', ')}
                                            </div>
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              );
                            })()}

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
                          background: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
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
                          background: expandedCards[idx] ? '#14b8a6' : '#ccfbf1',
                          color: expandedCards[idx] ? 'white' : '#0f766e',
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
