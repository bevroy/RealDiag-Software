// Authentication utility for client-side state management
// Used when cookies don't work across domains (Netlify + Render)

export function getStoredUser() {
  if (typeof window === 'undefined') return null;
  
  try {
    const userStr = localStorage.getItem('realdiag_user');
    return userStr ? JSON.parse(userStr) : null;
  } catch {
    return null;
  }
}

export function isStoredAuthenticated() {
  if (typeof window === 'undefined') return false;
  return localStorage.getItem('realdiag_authenticated') === 'true';
}

export function clearStoredAuth() {
  if (typeof window === 'undefined') return;
  
  // Clear localStorage
  localStorage.removeItem('realdiag_user');
  localStorage.removeItem('realdiag_authenticated');
  sessionStorage.removeItem('csrf_token');
  
  // Clear cookies - set them to expire immediately
  // Note: These are the readable cookies. HttpOnly cookies can only be cleared by the backend
  document.cookie = 'csrf_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  document.cookie = 'refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
}

export function storeAuthData(user, csrfToken) {
  if (typeof window === 'undefined') return;
  
  if (user) {
    localStorage.setItem('realdiag_user', JSON.stringify(user));
    localStorage.setItem('realdiag_authenticated', 'true');
  }
  
  if (csrfToken) {
    sessionStorage.setItem('csrf_token', csrfToken);
  }
}
