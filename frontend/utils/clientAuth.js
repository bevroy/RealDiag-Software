// Authentication utility for client-side state management
// Used when cookies don't work across domains (Netlify + Render)

const APPROVED_PROVIDER_DOMAINS = new Set(['realdiag.com', 'elionyxhealth.com']);

export function normalizeUiRole(role, email) {
  const roleValue = String(role || 'user').trim().toLowerCase();
  const emailValue = String(email || '').trim().toLowerCase();
  const domain = emailValue.includes('@') ? emailValue.split('@').pop() : '';

  if (APPROVED_PROVIDER_DOMAINS.has(domain) && (roleValue === 'user' || roleValue === 'patient' || roleValue === '')) {
    return 'provider';
  }

  if (roleValue === 'user' || roleValue === 'patient') {
    return 'provider';
  }

  return roleValue || 'user';
}

export function normalizeStoredUser(user) {
  if (!user || typeof user !== 'object') return null;
  return {
    ...user,
    role: normalizeUiRole(user.role, user.email)
  };
}

export function getStoredUser() {
  if (typeof window === 'undefined') return null;
  
  try {
    const userStr = localStorage.getItem('realdiag_user');
    const parsed = userStr ? JSON.parse(userStr) : null;
    return normalizeStoredUser(parsed);
  } catch {
    return null;
  }
}

export function isStoredAuthenticated() {
  if (typeof window === 'undefined') return false;
  if (localStorage.getItem('realdiag_authenticated') === 'true') return true;
  return !!getStoredUser();
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
    const normalized = normalizeStoredUser(user);
    localStorage.setItem('realdiag_user', JSON.stringify(normalized));
    localStorage.setItem('realdiag_authenticated', 'true');
  }
  
  if (csrfToken) {
    sessionStorage.setItem('csrf_token', csrfToken);
  }
}
