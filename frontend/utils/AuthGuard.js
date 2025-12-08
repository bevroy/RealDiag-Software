import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { getStoredUser, isStoredAuthenticated } from './clientAuth';

// Pages that don't require authentication
const PUBLIC_ROUTES = [
  '/login',
  '/register',
  '/pricing',
  '/verify-email',
  '/legal-disclaimer',
  '/_error',
  '/404'
];

export function AuthGuard({ children }) {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    // Check if current route is public
    const isPublicRoute = PUBLIC_ROUTES.some(route => 
      router.pathname === route || router.pathname.startsWith(route)
    );

    if (isPublicRoute) {
      setIsAuthorized(true);
      setIsChecking(false);
      return;
    }

    // Check if user is authenticated
    const authenticated = isStoredAuthenticated();
    const user = getStoredUser();

    if (!authenticated || !user) {
      // Not authenticated - redirect to login
      router.push('/login?redirect=' + encodeURIComponent(router.asPath));
      setIsAuthorized(false);
      setIsChecking(false);
    } else {
      // Authenticated - allow access
      setIsAuthorized(true);
      setIsChecking(false);
    }
  }, [router.pathname]);

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
