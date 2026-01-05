/**
 * Role-Based Navigation Component
 * Shows different navigation items based on user role
 */
import { useEffect, useState } from 'react';

export default function RoleBasedNavigation() {
  const [userRole, setUserRole] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadUserRole() {
      // Load user role from localStorage
      const userStr = localStorage.getItem('realdiag_user');
      console.log('🔍 RoleBasedNav - Raw localStorage value:', userStr);
      
      if (userStr) {
        try {
          const user = JSON.parse(userStr);
          console.log('🔍 RoleBasedNav - Parsed user:', user);
          console.log('🔍 RoleBasedNav - User role:', user.role);
          setUserRole(user.role);
          setIsLoading(false);
          return;
        } catch (err) {
          console.error('Failed to parse user data:', err);
        }
      }
      
      // If no localStorage data, try to fetch from API (user might be logged in via cookies)
      console.log('🔍 RoleBasedNav - No localStorage, checking API...');
      try {
        const response = await fetch('https://realdiag-software.onrender.com/users/me', {
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const userData = await response.json();
          console.log('🔍 RoleBasedNav - Fetched user from API:', userData);
          
          // Store in localStorage for future use
          localStorage.setItem('realdiag_user', JSON.stringify(userData));
          localStorage.setItem('realdiag_authenticated', 'true');
          
          setUserRole(userData.role);
        } else {
          console.log('🔍 RoleBasedNav - Not logged in');
        }
      } catch (error) {
        console.error('🔍 RoleBasedNav - Error fetching user:', error);
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
    { href: '/education', label: '📚 Training', roles: ['all'] },
    { href: '/sources', label: '📖 Sources', roles: ['admin', 'provider', 'doctor'] },
    { href: '/patient-history', label: '📋 Patient History', roles: ['admin', 'provider', 'doctor'] },
    { href: '/health-manager', label: '🏥 Health Manager', roles: ['patient'] },
    { href: '/account', label: '👤 Account', roles: ['all'] }
  ];

  // Filter navigation based on user role
  const visibleNavItems = navItems.filter(item => {
    if (item.roles.includes('all')) return true;
    if (!userRole) return false; // Hide role-specific items if not logged in
    return item.roles.includes(userRole);
  });
  
  console.log('🔍 RoleBasedNav - User role:', userRole);
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
