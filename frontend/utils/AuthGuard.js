import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { getStoredUser, isStoredAuthenticated, storeAuthData } from './clientAuth';
import { getCurrentUser } from './auth';

// Pages that don't require authentication
const PUBLIC_ROUTES = [
  '/',                    // Landing page with demo video
  '/account',             // Login/Register page
  '/legal-disclaimer',    // Legal information
  '/symptom-search',      // Core diagnostic workflow
  '/search',              // Diagnosis search
  '/rules',               // Rule browser
  '/integration',         // API/EHR integration page
  '/features-demo',       // Feature showcase
  '/education',           // Education module
  '/sources',             // Source references
  '/patient-history',     // Clinical documentation tools
  '/technical-medical',   // Technical and medical overview
  '/user-guide',          // Printable guide
  '/health-manager',      // Patient-facing health manager
  '/pricing',             // Plan/pricing page
  '/_error',              // Error pages
  '/404'                  // Not found page
];

export function AuthGuard({ children }) {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      setIsChecking(true);
      
      // Check if current route is public
      const isPublicRoute = PUBLIC_ROUTES.some(route => {
        // Exact match for most routes
        if (route === '/') {
          return router.pathname === '/';
        }
        // For other routes, match exact or with trailing content (like /account?redirect=...)
        return router.pathname === route || router.pathname.startsWith(route + '/');
      });

      if (isPublicRoute) {
        setIsAuthorized(true);
        setIsChecking(false);
        return;
      }

      // Check if user is authenticated
      const authenticated = isStoredAuthenticated();
      const user = getStoredUser();

      if (!authenticated || !user) {
        try {
          const currentUser = await getCurrentUser();
          if (currentUser) {
            storeAuthData(currentUser, null);
            setIsAuthorized(true);
            setIsChecking(false);
            return;
          }
        } catch (error) {
          console.error('AuthGuard profile check failed:', error);
        }

        // Not authenticated - redirect to account page (login/register)
        setIsAuthorized(false);
        setIsChecking(false);
        router.push('/account?redirect=' + encodeURIComponent(router.asPath));
      } else {
        // Authenticated - allow access
        setIsAuthorized(true);
        setIsChecking(false);
      }
    };

    // Check auth whenever pathname changes
    checkAuth();
  }, [router.pathname, router.asPath]);

  // Show loading while checking authentication
  if (isChecking) {
    return (
      <div style={styles.loading}>
        <div style={styles.spinner}></div>
        <p>Checking authentication...</p>
      </div>
    );
  }

  // Don't render protected content if not authorized
  if (!isAuthorized) {
    return null;
  }

  // Render children if authorized
  return <>{children}</>;
}

const styles = {
  loading: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    fontFamily: 'system-ui, -apple-system, sans-serif'
  },
  spinner: {
    width: '50px',
    height: '50px',
    border: '4px solid rgba(255,255,255,0.3)',
    borderTop: '4px solid white',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    marginBottom: '20px'
  }
};

// Add CSS animation for spinner
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  `;
  document.head.appendChild(style);
}
