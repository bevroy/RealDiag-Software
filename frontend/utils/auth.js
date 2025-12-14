/**
 * Authentication Utility - HttpOnly Cookie Based
 * ==============================================
 * 
 * Secure authentication using HttpOnly cookies instead of localStorage.
 * Tokens are automatically sent with requests via cookies.
 * 
 * CSRF token management for POST/PUT/DELETE requests.
 */

/**
 * Get API base URL from runtime config
 */
function getApiBase() {
  if (typeof window !== 'undefined') {
    const runtimeConfig = window.__RUNTIME_CONFIG || window.__RUNTIME_CONFIG__;
    return runtimeConfig?.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com';
  }
  return 'https://realdiag-software.onrender.com';
}

/**
 * Get CSRF token from response or cookie
 * This token must be sent in X-CSRF-Token header for state-changing requests
 */
export function getCsrfToken() {
  // CSRF token is stored in a readable cookie (not HttpOnly) so JS can access it
  const match = document.cookie.match(/csrf_token=([^;]+)/);
  return match ? match[1] : null;
}

/**
 * Check if user is authenticated
 * We check if the access_token cookie exists
 */
export function isAuthenticated() {
  // Check if access_token cookie exists
  return document.cookie.includes('access_token=');
}

/**
 * Make authenticated API request with CSRF protection
 * Automatically includes credentials (cookies) and CSRF token
 */
export async function authenticatedFetch(url, options = {}) {
  const csrfToken = getCsrfToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };
  
  // Add CSRF token for state-changing requests
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method?.toUpperCase())) {
    if (csrfToken) {
      headers['X-CSRF-Token'] = csrfToken;
    }
  }
  
  const response = await fetch(url, {
    ...options,
    credentials: 'include', // Important: sends cookies with request
    headers
  });
  
  return response;
}

/**
 * Login user
 * Tokens are set in HttpOnly cookies by the backend
 */
export async function login(email, password) {
  const apiBase = getApiBase();
  const response = await fetch(`${apiBase}/users/login`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }
  
  const data = await response.json();
  
  // CSRF token is returned in response body and also set in cookie
  // Store it for future requests (also available from cookie)
  if (data.csrf_token) {
    sessionStorage.setItem('csrf_token', data.csrf_token);
  }
  
  return data;
}

/**
 * Register new user
 * Tokens are set in HttpOnly cookies by the backend
 */
export async function register(userData) {
  const apiBase = getApiBase();
  const response = await fetch(`${apiBase}/users/register`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Registration failed');
  }
  
  const data = await response.json();
  
  if (data.csrf_token) {
    sessionStorage.setItem('csrf_token', data.csrf_token);
  }
  
  return data;
}

/**
 * Logout user
 * Backend clears HttpOnly cookies
 */
export async function logout() {
  try {
    const apiBase = getApiBase();
    const response = await authenticatedFetch(`${apiBase}/users/logout`, {
      method: 'POST'
    });
    
    // Clear CSRF token from sessionStorage
    sessionStorage.removeItem('csrf_token');
    
    if (response.ok) {
      try {
        return await response.json();
      } catch (e) {
        // If JSON parsing fails, that's okay - logout still worked
        return { message: 'Logout successful' };
      }
    }
  } catch (error) {
    console.error('Logout API error:', error);
    // Don't throw - we want to clear local state even if API fails
  }
  
  // Always clear sessionStorage even if API call failed
  sessionStorage.removeItem('csrf_token');
  return { message: 'Logged out' };
}

/**
 * Get current user profile
 */
export async function getCurrentUser() {
  const apiBase = getApiBase();
  const response = await authenticatedFetch(`${apiBase}/users/me`);
  
  if (!response.ok) {
    if (response.status === 401) {
      return null; // Not authenticated
    }
    throw new Error('Failed to get user profile');
  }
  
  return await response.json();
}

/**
 * Migration helper: Remove old localStorage tokens
 * Call this once on app initialization to clean up
 */
export function cleanupOldTokens() {
  // Remove old localStorage tokens (security vulnerability)
  localStorage.removeItem('realdiag_token');
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  
  console.log('✅ Cleaned up old localStorage tokens');
}

// Clean up on module load
if (typeof window !== 'undefined') {
  cleanupOldTokens();
}
