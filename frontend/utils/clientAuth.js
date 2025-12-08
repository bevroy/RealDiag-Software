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
  
  localStorage.removeItem('realdiag_user');
  localStorage.removeItem('realdiag_authenticated');
  sessionStorage.removeItem('csrf_token');
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
