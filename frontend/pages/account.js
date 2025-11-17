"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/router";

export default function AccountPage() {
  const router = useRouter();
  const [apiBase, setApiBase] = useState('');
  const [activeTab, setActiveTab] = useState('login');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
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

    // Check if already logged in
    const token = localStorage.getItem('realdiag_token');
    if (token) {
      fetchUserProfile(token);
    }
  }, []);

  const fetchUserProfile = async (token) => {
    try {
      const response = await fetch(`${apiBase}/users/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setIsAuthenticated(true);
        setActiveTab('dashboard');
        loadDashboardData(token);
      } else {
        localStorage.removeItem('realdiag_token');
      }
    } catch (err) {
      console.error('Failed to fetch profile:', err);
    }
  };

  const loadDashboardData = async (token) => {
    try {
      // Load search history
      const historyRes = await fetch(`${apiBase}/users/me/history?limit=10`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (historyRes.ok) {
        const historyData = await historyRes.json();
        setSearchHistory(historyData.history || []);
      }

      // Load favorites
      const favRes = await fetch(`${apiBase}/users/me/favorites`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (favRes.ok) {
        const favData = await favRes.json();
        setFavorites(favData.favorites || []);
      }

      // Load custom lists
      const listsRes = await fetch(`${apiBase}/users/me/lists`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (listsRes.ok) {
        const listsData = await listsRes.json();
        setCustomLists(listsData.lists || []);
      }

      // Load analytics
      const analyticsRes = await fetch(`${apiBase}/users/me/analytics`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
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
      const response = await fetch(`${apiBase}/users/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: loginEmail, password: loginPassword })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      localStorage.setItem('realdiag_token', data.access_token);
      setUser(data.user);
      setIsAuthenticated(true);
      setActiveTab('dashboard');
      loadDashboardData(data.access_token);
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
      const response = await fetch(`${apiBase}/users/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: registerEmail,
          password: registerPassword,
          full_name: registerName,
          specialty: registerSpecialty || null,
          institution: registerInstitution || null
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }

      const data = await response.json();
      localStorage.setItem('realdiag_token', data.access_token);
      setUser(data.user);
      setIsAuthenticated(true);
      setActiveTab('dashboard');
      loadDashboardData(data.access_token);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('realdiag_token');
    setUser(null);
    setIsAuthenticated(false);
    setActiveTab('login');
    setSearchHistory([]);
    setFavorites([]);
    setCustomLists([]);
    setAnalytics(null);
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
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '2rem'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{
          background: 'white',
          borderRadius: '16px',
          padding: '2rem',
          marginBottom: '2rem',
          boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <h1 style={{ margin: '0 0 0.5rem', fontSize: '2.5rem', color: '#667eea' }}>
              👤 My Account
            </h1>
            <p style={{ margin: 0, color: '#666' }}>
              {isAuthenticated ? `Welcome back, ${user?.full_name || 'User'}!` : 'Sign in to save your diagnostic searches and personalize your experience'}
            </p>
          </div>
          {isAuthenticated && (
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

        {/* Tabs */}
        {!isAuthenticated && (
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem' }}>
            {['login', 'register'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: activeTab === tab ? 'white' : 'rgba(255,255,255,0.2)',
                  color: activeTab === tab ? '#667eea' : 'white',
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

        {isAuthenticated && (
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
            {['dashboard', 'history', 'favorites', 'lists', 'analytics'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: activeTab === tab ? 'white' : 'rgba(255,255,255,0.2)',
                  color: activeTab === tab ? '#667eea' : 'white',
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
          {activeTab === 'login' && !isAuthenticated && (
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
                    background: '#667eea',
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
          {activeTab === 'register' && !isAuthenticated && (
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
                    background: '#667eea',
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
                <div style={{ padding: '1.5rem', background: '#e0e7ff', borderRadius: '12px', border: '2px solid #667eea' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#667eea' }}>
                    {analytics?.total_custom_lists || 0}
                  </div>
                  <div style={{ color: '#4338ca', marginTop: '0.5rem' }}>Custom Lists</div>
                </div>
              </div>

              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ color: '#667eea' }}>Quick Actions</h3>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                  <button
                    onClick={() => router.push('/symptom-search')}
                    style={{
                      padding: '0.75rem 1.5rem',
                      background: '#667eea',
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
                <h3 style={{ color: '#667eea' }}>Recent Searches</h3>
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
                <h3 style={{ color: '#667eea' }}>Top Symptoms Searched</h3>
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
                      <span style={{ fontWeight: 'bold', color: '#667eea', minWidth: '30px' }}>{idx + 1}</span>
                      <span style={{ flex: 1 }}>{item.symptom}</span>
                      <span style={{ color: '#666', fontSize: '0.875rem' }}>{item.count} searches</span>
                    </div>
                  )) || <p style={{ color: '#666' }}>No data yet</p>}
                </div>
              </div>

              <div>
                <h3 style={{ color: '#667eea' }}>Most Viewed Specialties</h3>
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
