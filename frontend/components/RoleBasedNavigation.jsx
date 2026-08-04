/**
 * Role-Based Navigation Component
 * Shows different navigation items based on user role
 */
import { useEffect, useState } from 'react';
import { getStoredUser, isStoredAuthenticated, storeAuthData } from '../utils/clientAuth';

export default function RoleBasedNavigation() {
  const [userRole, setUserRole] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const normalizeRole = (role) => {
    // Backward compatibility: older accounts are often persisted as "user"
    // even though they should see the core clinician/provider tools.
    if (role === 'user' || role === 'patient') return 'provider';
    return role;
  };

  useEffect(() => {
    async function loadUserRole() {
      const apiBase =
        (typeof window !== 'undefined' && (window.__RUNTIME_CONFIG?.NEXT_PUBLIC_API_BASE || window.__RUNTIME_CONFIG__?.NEXT_PUBLIC_API_BASE)) ||
        'https://realdiag-software.onrender.com';

      // Load user role from localStorage
      const storedUser = getStoredUser();
      console.log('🔍 RoleBasedNav - Parsed stored user:', storedUser);

      if (storedUser) {
        // Show cached role immediately for responsiveness.
        setUserRole(normalizeRole(storedUser.role));
      }
      
      // ...but always refresh from API to avoid stale cached roles.
      console.log('🔍 RoleBasedNav - Checking API for fresh role...');
      try {
        const response = await fetch(`${apiBase}/users/me`, {
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const userData = await response.json();
          console.log('🔍 RoleBasedNav - Fetched user from API:', userData);

          // Store normalized user in localStorage for future use
          storeAuthData(userData, null);
          
          setUserRole(normalizeRole(userData.role));
        } else {
          console.log('🔍 RoleBasedNav - Not logged in');
          setUserRole(storedUser ? normalizeRole(storedUser.role) : null);
        }
      } catch (error) {
        console.error('🔍 RoleBasedNav - Error fetching user:', error);
        setUserRole(storedUser ? normalizeRole(storedUser.role) : null);
      }
      
      setIsLoading(false);
    }
    
    loadUserRole();
  }, []);

  // Define navigation items with role requirements
  const navItems = [
    { href: '/', label: '🏠 Home', roles: ['all'] },
    { href: '/symptom-search', label: '🔬 Symptom Search', roles: ['all'] },
    { href: '/search', label: '🔍 Diagnosis Search', roles: ['admin', 'provider', 'doctor'] },
    { href: '/rules', label: '📋 Browse Rules', roles: ['admin', 'provider', 'doctor'] },
    { href: '/integration', label: '🔌 API', roles: ['admin', 'provider', 'doctor'] },
    { href: '/features-demo', label: '✨ Features', roles: ['admin', 'provider'] },
    { href: '/education', label: '📚 Training', roles: ['admin', 'provider', 'doctor'] },
    { href: '/sources', label: '📖 Sources', roles: ['admin', 'provider', 'doctor'] },
    { href: '/patient-history', label: '📋 Patient History', roles: ['admin', 'provider', 'doctor'] },
    { href: '/technical-medical', label: '🧠 Technical/Medical', roles: ['all'] },
    { href: '/user-guide', label: '🖨️ User Guide', roles: ['all'] },
    { href: '/health-manager/', label: '🏥 Health Manager', roles: ['patient'] },
    { href: '/account', label: '👤 Account', roles: ['all'] }
  ];

  const isAuthenticatedHint = typeof window !== 'undefined' && isStoredAuthenticated();

  // Operational safety: default to provider-level navigation even if auth
  // signals are inconsistent across domains/cookies, so users are not locked
  // into a reduced menu due to client-side state drift.
  const effectiveRole = userRole || (isAuthenticatedHint ? 'provider' : 'provider');

  // Filter navigation based on user role
  const visibleNavItems = navItems.filter(item => {
    if (item.roles.includes('all')) return true;
    if (!effectiveRole) return false;
    return item.roles.includes(effectiveRole);
  });
  
  console.log('🔍 RoleBasedNav - User role:', userRole, 'effective role:', effectiveRole);
  console.log('🔍 RoleBasedNav - Visible items:', visibleNavItems.map(i => i.label));

  return (
    <div style={{
      maxWidth: '1200px',
      margin: '0 auto 1rem'
    }}>
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
          {visibleNavItems.map((item) => (
            <a 
              key={item.href}
              href={item.href} 
              style={{
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
              {item.label}
            </a>
          ))}
        </div>
      </details>
    </div>
  );
}
