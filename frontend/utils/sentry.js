// Sentry Configuration for Frontend
// ==================================

// Simplified Sentry setup for static export (compatible with Netlify)
let Sentry = null;

// Initialize Sentry on app startup (browser only)
if (typeof window !== 'undefined') {
  const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN;
  const ENVIRONMENT = process.env.NEXT_PUBLIC_ENVIRONMENT || 'development';
  
  if (SENTRY_DSN) {
    // Dynamic import to avoid build-time issues
    import("@sentry/nextjs").then((SentryModule) => {
      Sentry = SentryModule;
      
      Sentry.init({
        dsn: SENTRY_DSN,
        environment: ENVIRONMENT,
        
        // Adjust sample rates for production
        tracesSampleRate: parseFloat(process.env.NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE || '0.1'),
        
        // Simplified integrations for static export
        integrations: [],
        
        // Ignore common errors
        ignoreErrors: [
          // Browser extensions
          'Non-Error promise rejection captured',
          'ResizeObserver loop limit exceeded',
          // Network errors
          'NetworkError',
          'Failed to fetch',
        ],
        
        // Filter sensitive data
        beforeSend(event, hint) {
          // Remove sensitive data from error reports
          if (event.request) {
            delete event.request.cookies;
            if (event.request.headers) {
              delete event.request.headers['Authorization'];
              delete event.request.headers['Cookie'];
            }
          }
          
          // Don't send errors in development
          if (ENVIRONMENT === 'development') {
            return null;
          }
          
          return event;
        },
      });
      
      console.log('✅ Sentry initialized for environment:', ENVIRONMENT);
    }).catch((error) => {
      console.warn('⚠️ Sentry initialization failed:', error.message);
    });
  } else {
    console.log('ℹ️ Sentry DSN not configured, error tracking disabled');
  }
}

// Export for use in components
export { Sentry };

// Usage in components:
// import { Sentry } from '../utils/sentry';
// 
// try {
//   // Your code
// } catch (error) {
//   Sentry.captureException(error);
//   // Handle error
// }

// Usage for custom events:
// Sentry.captureMessage('Custom event', 'info');

// Set user context (after authentication):
// Sentry.setUser({
//   id: user.id,
//   email: user.email,
//   username: user.full_name
// });

// Clear user context (after logout):
// Sentry.setUser(null);
