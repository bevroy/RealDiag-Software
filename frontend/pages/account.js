"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { isAuthenticated, getCurrentUser, login as authLogin, register as authRegister, logout as authLogout, authenticatedFetch } from '../utils/auth';

export default function AccountPage() {
  const router = useRouter();
  const [apiBase, setApiBase] = useState('');
  const [activeTab, setActiveTab] = useState('login');
  const [isUserAuthenticated, setIsUserAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Form states
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerName, setRegisterName] = useState('');
  const [registerSpecialty, setRegisterSpecialty] = useState('');
  const [registerInstitution, setRegisterInstitution] = useState('');

  // Dashboard data
  const [searchHistory, setSearchHistory] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [customLists, setCustomLists] = useState([]);
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    const runtimeConfig = (typeof window !== 'undefined' && window.__RUNTIME_CONFIG) ? window.__RUNTIME_CONFIG : null;
    const base = runtimeConfig?.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com';
    setApiBase(base.replace(/\/$/, ''));

    // Check if already logged in (via HttpOnly cookie)
    if (isAuthenticated()) {
      fetchUserProfile();
    }
  }, []);

  const fetchUserProfile = async () => {
    try {
      const userData = await getCurrentUser();
      if (userData) {
        setUser(userData);
        setIsUserAuthenticated(true);
        setActiveTab('dashboard');
        loadDashboardData();
      } else {
        setIsUserAuthenticated(false);
        setUser(null);
      }
    } catch (err) {
      console.error('Failed to fetch profile:', err);
      setIsUserAuthenticated(false);
      setUser(null);
    }
  };

  const loadDashboardData = async () => {
    try {
      // Load search history
      const historyRes = await authenticatedFetch(`${apiBase}/users/me/history?limit=10`);
      if (historyRes.ok) {
        const historyData = await historyRes.json();
        setSearchHistory(historyData.history || []);
      }

      // Load favorites
      const favRes = await authenticatedFetch(`${apiBase}/users/me/favorites`);
      if (favRes.ok) {
        const favData = await favRes.json();
        setFavorites(favData.favorites || []);
      }

      // Load custom lists
      const listsRes = await authenticatedFetch(`${apiBase}/users/me/lists`);
      if (listsRes.ok) {
        const listsData = await listsRes.json();
        setCustomLists(listsData.lists || []);
      }

      // Load analytics
      const analyticsRes = await authenticatedFetch(`${apiBase}/users/me/analytics`);
      if (analyticsRes.ok) {
        const analyticsData = await analyticsRes.json();
        setAnalytics(analyticsData);
      }
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await authLogin(loginEmail, loginPassword);
      setUser(data.user);
      setIsUserAuthenticated(true);
      setActiveTab('dashboard');
      loadDashboardData();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await authRegister({
        email: registerEmail,
        password: registerPassword,
        full_name: registerName,
        specialty: registerSpecialty || null,
        institution: registerInstitution || null
      });
      setUser(data.user);
      setIsUserAuthenticated(true);
      setActiveTab('dashboard');
      loadDashboardData();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await authLogout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setUser(null);
      setIsUserAuthenticated(false);
      setActiveTab('login');
      setSearchHistory([]);
      setFavorites([]);
      setCustomLists([]);
      setAnalytics(null);
    }
  };

  const specialties = [
    'Cardiology', 'Dermatology', 'Emergency Medicine', 'Endocrinology',
    'ENT', 'Gastroenterology', 'Geriatrics', 'Hematology/Oncology',
    'Infectious Disease', 'Nephrology', 'Neurology', 'OB/GYN',
    'Ophthalmology', 'Orthopedics', 'Pediatrics', 'Psychiatry',
    'Pulmonology', 'Rheumatology', 'Surgery', 'Toxicology', 'Urology'
  ];

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f0fdfa 0%, #e7f5f3 100%)',
      padding: '2rem'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Navigation Dropdown */}
        <div style={{ marginBottom: '1rem' }}>
          <details style={{
            background: 'white',
            padding: '0.75rem 1.25rem',
            borderRadius: '10px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            border: '1px solid #e2e8f0',
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
                🔍 Symptom Search
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
        </div>

        {/* Header */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '1.5rem',
          marginBottom: '2rem',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '16px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flex: 1 }}>
            <img src="/logo.png" alt="RealDiag Logo" style={{ height: '50px' }} />
            <div>
              <h1 style={{ marginBottom: 0, color: '#78350f' }}>
                My Account
              </h1>
              <p style={{ margin: '0.25rem 0 0', color: '#666', fontSize: '0.9rem' }}>
                {isUserAuthenticated ? `Welcome back, ${user?.full_name || 'User'}!` : 'Sign in to save your diagnostic searches'}
              </p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', whiteSpace: 'nowrap' }}>
            <a href="/" style={{
              padding: '0.75rem 1.5rem',
              background: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '1rem',
              cursor: 'pointer',
              fontWeight: '600',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              🏠 Home
            </a>
            {isUserAuthenticated && (
              <button
                onClick={handleLogout}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: '#ef4444',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                Logout
              </button>
            )}
          </div>
        </div>

        {/* Tabs */}
        {!isUserAuthenticated && (
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem' }}>
            {['login', 'register'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: activeTab === tab ? 'white' : 'rgba(255,255,255,0.2)',
                  color: activeTab === tab ? '#14b8a6' : 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  textTransform: 'capitalize'
                }}
              >
                {tab}
              </button>
            ))}
          </div>
        )}

        {isUserAuthenticated && (
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
            {['dashboard', 'history', 'favorites', 'lists', 'analytics'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: activeTab === tab ? 'white' : 'rgba(255,255,255,0.2)',
                  color: activeTab === tab ? '#14b8a6' : 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  textTransform: 'capitalize'
                }}
              >
                {tab}
              </button>
            ))}
          </div>
        )}

        {/* Content */}
        <div style={{
          background: 'white',
          borderRadius: '16px',
          padding: '2rem',
          boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
        }}>
          {error && (
            <div style={{
              padding: '1rem',
              background: '#fee2e2',
              color: '#991b1b',
              borderRadius: '8px',
              marginBottom: '1.5rem',
              border: '2px solid #fecaca'
            }}>
              {error}
            </div>
          )}

          {/* Login Tab */}
          {activeTab === 'login' && !isUserAuthenticated && (
            <div>
              <h2 style={{ margin: '0 0 1.5rem', color: '#333' }}>Sign In</h2>
              <form onSubmit={handleLogin} style={{ maxWidth: '400px' }}>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                    Email
                  </label>
                  <input
                    type="email"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    required
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '1rem'
                    }}
                  />
                </div>
                <div style={{ marginBottom: '1.5rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                    Password
                  </label>
                  <input
                    type="password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    required
                    minLength={8}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '1rem'
                    }}
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    background: '#14b8a6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    opacity: loading ? 0.6 : 1
                  }}
                >
                  {loading ? 'Signing In...' : 'Sign In'}
                </button>
              </form>
            </div>
          )}

          {/* Register Tab */}
          {activeTab === 'register' && !isUserAuthenticated && (
            <div>
              <h2 style={{ margin: '0 0 1.5rem', color: '#333' }}>Create Account</h2>
              <form onSubmit={handleRegister} style={{ maxWidth: '500px' }}>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                    Full Name *
                  </label>
                  <input
                    type="text"
                    value={registerName}
                    onChange={(e) => setRegisterName(e.target.value)}
                    required
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '1rem'
                    }}
                  />
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                    Email *
                  </label>
                  <input
                    type="email"
                    value={registerEmail}
                    onChange={(e) => setRegisterEmail(e.target.value)}
                    required
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '1rem'
                    }}
                  />
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                    Password * (min 8 characters)
                  </label>
                  <input
                    type="password"
                    value={registerPassword}
                    onChange={(e) => setRegisterPassword(e.target.value)}
                    required
                    minLength={8}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '1rem'
                    }}
                  />
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                    Specialty (optional)
                  </label>
                  <select
                    value={registerSpecialty}
                    onChange={(e) => setRegisterSpecialty(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '1rem'
                    }}
                  >
                    <option value="">Select specialty...</option>
                    {specialties.map(s => (
                      <option key={s} value={s.toLowerCase().replace(/\//g, '_').replace(/ /g, '_')}>
                        {s}
                      </option>
                    ))}
                  </select>
                </div>
                <div style={{ marginBottom: '1.5rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                    Institution (optional)
                  </label>
                  <input
                    type="text"
                    value={registerInstitution}
                    onChange={(e) => setRegisterInstitution(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '1rem'
                    }}
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    background: '#14b8a6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    opacity: loading ? 0.6 : 1
                  }}
                >
                  {loading ? 'Creating Account...' : 'Create Account'}
                </button>
              </form>
            </div>
          )}

          {/* Dashboard Tab */}
          {activeTab === 'dashboard' && isAuthenticated && (
            <div>
              <h2 style={{ margin: '0 0 1.5rem', color: '#333' }}>Dashboard</h2>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
                <div style={{ padding: '1.5rem', background: '#f0fdfa', borderRadius: '12px', border: '2px solid #14b8a6' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#14b8a6' }}>
                    {analytics?.total_searches || 0}
                  </div>
                  <div style={{ color: '#0f766e', marginTop: '0.5rem' }}>Total Searches</div>
                </div>
                <div style={{ padding: '1.5rem', background: '#fef3c7', borderRadius: '12px', border: '2px solid #f59e0b' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f59e0b' }}>
                    {analytics?.total_favorites || 0}
                  </div>
                  <div style={{ color: '#92400e', marginTop: '0.5rem' }}>Favorites</div>
                </div>
                <div style={{ padding: '1.5rem', background: '#ccfbf1', borderRadius: '12px', border: '2px solid #14b8a6' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#14b8a6' }}>
                    {analytics?.total_custom_lists || 0}
                  </div>
                  <div style={{ color: '#4338ca', marginTop: '0.5rem' }}>Custom Lists</div>
                </div>
              </div>

              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ color: '#14b8a6' }}>Quick Actions</h3>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                  <button
                    onClick={() => router.push('/symptom-search')}
                    style={{
                      padding: '0.75rem 1.5rem',
                      background: '#14b8a6',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontWeight: '600'
                    }}
                  >
                    🔍 New Search
                  </button>
                  <button
                    onClick={() => setActiveTab('history')}
                    style={{
                      padding: '0.75rem 1.5rem',
                      background: '#10b981',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontWeight: '600'
                    }}
                  >
                    📜 View History
                  </button>
                  <button
                    onClick={() => setActiveTab('favorites')}
                    style={{
                      padding: '0.75rem 1.5rem',
                      background: '#f59e0b',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontWeight: '600'
                    }}
                  >
                    ⭐ My Favorites
                  </button>
                </div>
              </div>

              <div>
                <h3 style={{ color: '#14b8a6' }}>Recent Searches</h3>
                {searchHistory.length === 0 ? (
                  <p style={{ color: '#666' }}>No searches yet. Start searching to see your history here!</p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {searchHistory.slice(0, 5).map(search => (
                      <div key={search.search_id} style={{
                        padding: '1rem',
                        background: '#f9fafb',
                        borderRadius: '8px',
                        border: '1px solid #e5e7eb'
                      }}>
                        <div style={{ fontWeight: '600', marginBottom: '0.5rem' }}>
                          {search.symptoms.join(', ')}
                        </div>
                        <div style={{ fontSize: '0.875rem', color: '#666' }}>
                          {search.result_count} results • {new Date(search.timestamp).toLocaleString()}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* History Tab */}
          {activeTab === 'history' && isAuthenticated && (
            <div>
              <h2 style={{ margin: '0 0 1.5rem', color: '#333' }}>Search History</h2>
              {searchHistory.length === 0 ? (
                <p style={{ color: '#666' }}>No search history yet.</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {searchHistory.map(search => (
                    <div key={search.search_id} style={{
                      padding: '1.5rem',
                      background: '#f9fafb',
                      borderRadius: '12px',
                      border: '2px solid #e5e7eb'
                    }}>
                      <div style={{ fontWeight: '600', fontSize: '1.1rem', marginBottom: '0.75rem' }}>
                        {search.symptoms.join(', ')}
                      </div>
                      <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.875rem', color: '#666' }}>
                        <span>📊 {search.result_count} results</span>
                        {search.age && <span>👤 Age: {search.age}</span>}
                        {search.sex && <span>🔹 {search.sex}</span>}
                        {search.family && <span>🏥 {search.family}</span>}
                      </div>
                      <div style={{ fontSize: '0.875rem', color: '#999', marginTop: '0.5rem' }}>
                        {new Date(search.timestamp).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Favorites Tab */}
          {activeTab === 'favorites' && isAuthenticated && (
            <div>
              <h2 style={{ margin: '0 0 1.5rem', color: '#333' }}>My Favorites</h2>
              {favorites.length === 0 ? (
                <p style={{ color: '#666' }}>No favorites yet. Click the star icon on any diagnosis to add it here!</p>
              ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
                  {favorites.map(fav => (
                    <div key={fav.favorite_id} style={{
                      padding: '1.5rem',
                      background: '#fffbeb',
                      borderRadius: '12px',
                      border: '2px solid #fcd34d'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                        <div>
                          <div style={{ fontWeight: '600', fontSize: '1.1rem', marginBottom: '0.5rem' }}>
                            {fav.diagnosis_label}
                          </div>
                          <div style={{ fontSize: '0.875rem', color: '#92400e', marginBottom: '0.75rem' }}>
                            {fav.family}
                          </div>
                        </div>
                        <span style={{ fontSize: '1.5rem' }}>⭐</span>
                      </div>
                      {fav.notes && (
                        <div style={{ fontSize: '0.875rem', color: '#666', fontStyle: 'italic', marginTop: '0.75rem' }}>
                          Note: {fav.notes}
                        </div>
                      )}
                      <div style={{ fontSize: '0.75rem', color: '#999', marginTop: '0.75rem' }}>
                        Added {new Date(fav.added_at).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Lists Tab */}
          {activeTab === 'lists' && isAuthenticated && (
            <div>
              <h2 style={{ margin: '0 0 1.5rem', color: '#333' }}>Custom Differential Lists</h2>
              {customLists.length === 0 ? (
                <p style={{ color: '#666' }}>No custom lists yet. Create lists to organize differential diagnoses by specialty or clinical scenario!</p>
              ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1.5rem' }}>
                  {customLists.map(list => (
                    <div key={list.list_id} style={{
                      padding: '1.5rem',
                      background: '#f0f9ff',
                      borderRadius: '12px',
                      border: '2px solid #60a5fa'
                    }}>
                      <h3 style={{ margin: '0 0 0.5rem', color: '#1e40af' }}>{list.name}</h3>
                      {list.description && (
                        <p style={{ margin: '0 0 1rem', fontSize: '0.875rem', color: '#666' }}>
                          {list.description}
                        </p>
                      )}
                      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', fontSize: '0.875rem' }}>
                        {list.specialty && (
                          <span style={{ padding: '0.25rem 0.75rem', background: '#dbeafe', color: '#1e40af', borderRadius: '999px' }}>
                            {list.specialty}
                          </span>
                        )}
                        {list.is_public && (
                          <span style={{ padding: '0.25rem 0.75rem', background: '#d1fae5', color: '#065f46', borderRadius: '999px' }}>
                            Public
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: '0.875rem', color: '#666' }}>
                        📋 {list.diagnoses.length} diagnoses
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#999', marginTop: '0.75rem' }}>
                        Updated {new Date(list.updated_at).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && isAuthenticated && analytics && (
            <div>
              <h2 style={{ margin: '0 0 1.5rem', color: '#333' }}>Usage Analytics</h2>
              
              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ color: '#14b8a6' }}>Top Symptoms Searched</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {analytics.top_symptoms?.slice(0, 10).map((item, idx) => (
                    <div key={idx} style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '1rem',
                      padding: '0.75rem',
                      background: '#f9fafb',
                      borderRadius: '8px'
                    }}>
                      <span style={{ fontWeight: 'bold', color: '#14b8a6', minWidth: '30px' }}>{idx + 1}</span>
                      <span style={{ flex: 1 }}>{item.symptom}</span>
                      <span style={{ color: '#666', fontSize: '0.875rem' }}>{item.count} searches</span>
                    </div>
                  )) || <p style={{ color: '#666' }}>No data yet</p>}
                </div>
              </div>

              <div>
                <h3 style={{ color: '#14b8a6' }}>Most Viewed Specialties</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem' }}>
                  {analytics.top_specialties?.map((item, idx) => (
                    <div key={idx} style={{
                      padding: '1rem',
                      background: '#f0f9ff',
                      borderRadius: '8px',
                      border: '2px solid #60a5fa'
                    }}>
                      <div style={{ fontWeight: 'bold', fontSize: '1.25rem', color: '#1e40af' }}>
                        {item.count}
                      </div>
                      <div style={{ color: '#666', marginTop: '0.25rem', textTransform: 'capitalize' }}>
                        {item.specialty.replace(/_/g, ' ')}
                      </div>
                    </div>
                  )) || <p style={{ color: '#666' }}>No data yet</p>}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
