import React, {useEffect, useState} from 'react'
import '../styles/globals.css'
import '../styles/accessibility-tablet.css'
import { AuthGuard } from '../utils/AuthGuard'

export default function App({Component, pageProps}){
  const [installPrompt, setInstallPrompt] = useState(null)
  const [showInstallButton, setShowInstallButton] = useState(false)
  const appVersion = '2026-08-04-nav-cache-fix-1'

  useEffect(()=>{
    // Initialize Sentry (client-side only)
    if (typeof window !== 'undefined') {
      import('../utils/sentry').catch(err => {
        console.warn('Sentry initialization skipped:', err.message)
      })
    }

    const storedVersion = typeof window !== 'undefined' ? localStorage.getItem('realdiag_app_version') : null
    if (typeof window !== 'undefined' && storedVersion !== appVersion) {
      localStorage.setItem('realdiag_app_version', appVersion)
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistrations().then((regs) => {
          regs.forEach((reg) => reg.unregister())
        }).catch(() => {})
      }
      if (window.caches) {
        caches.keys().then((keys) => Promise.all(keys.map((key) => caches.delete(key)))).catch(() => {})
      }
      window.location.reload()
      return
    }

    // Register service worker for PWA, with auto-update on new versions.
    // Skip in dev (localhost / codespaces) and proactively unregister any
    // SW left over from a previous prod visit so hot-reload works cleanly.
    const isDevHost =
      typeof window !== 'undefined' &&
      (window.location.hostname === 'localhost' ||
        window.location.hostname === '127.0.0.1' ||
        window.location.hostname.endsWith('.github.dev') ||
        window.location.hostname.endsWith('.app.github.dev'));

    if ('serviceWorker' in navigator && isDevHost) {
      navigator.serviceWorker.getRegistrations().then((regs) => {
        regs.forEach((reg) => reg.unregister());
      });
      if (window.caches) {
        caches.keys().then((keys) => keys.forEach((k) => caches.delete(k)));
      }
    } else if ('serviceWorker' in navigator) {
      let reloading = false;
      // When a new SW takes control, reload once so the page picks up fresh assets.
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        if (reloading) return;
        reloading = true;
        window.location.reload();
      });

      navigator.serviceWorker.register('/sw.js')
        .then(registration => {
          console.log('Service Worker registered:', registration.scope);

          // Helper: tell a waiting SW to take over immediately.
          const promote = (worker) => {
            if (worker && worker.state === 'installed' && navigator.serviceWorker.controller) {
              worker.postMessage({ type: 'SKIP_WAITING' });
            }
          };

          // If an update is already waiting at load time, promote it.
          if (registration.waiting) promote(registration.waiting);

          // Watch for updates installed after page load.
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            if (!newWorker) return;
            newWorker.addEventListener('statechange', () => promote(newWorker));
          });

          // Poll for updates periodically so long-lived tabs notice new deploys.
          setInterval(() => registration.update().catch(() => {}), 60 * 1000);
        })
        .catch(error => {
          console.error('Service Worker registration failed:', error);
        });
    }

    // Handle PWA install prompt
    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault()
      setInstallPrompt(e)
      setShowInstallButton(true)
    }

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)

    // Hide install button if already installed
    window.addEventListener('appinstalled', () => {
      setShowInstallButton(false)
      setInstallPrompt(null)
    })

    function onUnhandledRejection(ev){
      try{
        const reason = ev && ev.reason ? ev.reason : ev
        const msg = reason && reason.message ? reason.message : String(reason)
        // expose for debugging in the page
        window.__LAST_UNHANDLED = {type: 'unhandledrejection', message: msg, raw: reason}
        console.error('UnhandledRejection captured:', reason)
      }catch(e){
        console.error('Error capturing unhandledrejection', e)
      }
    }
    function onError(ev){
      try{
        const msg = ev && ev.message ? ev.message : String(ev)
        window.__LAST_UNHANDLED = {type: 'error', message: msg, raw: ev}
        console.error('Window error captured:', ev)
      }catch(e){
        console.error('Error capturing window.onerror', e)
      }
    }
    window.addEventListener('unhandledrejection', onUnhandledRejection)
    window.addEventListener('error', onError)
    return ()=>{
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
      window.removeEventListener('unhandledrejection', onUnhandledRejection)
      window.removeEventListener('error', onError)
    }
  }, [])

  const handleInstallClick = async () => {
    if (!installPrompt) return
    
    installPrompt.prompt()
    const { outcome } = await installPrompt.userChoice
    
    if (outcome === 'accepted') {
      console.log('PWA installed')
    }
    
    setShowInstallButton(false)
    setInstallPrompt(null)
  }

  return (
    <>
      {showInstallButton && (
        <button
          onClick={handleInstallClick}
          style={{
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 24px',
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
          onMouseOver={(e) => e.target.style.backgroundColor = '#2563eb'}
          onMouseOut={(e) => e.target.style.backgroundColor = '#3b82f6'}
        >
          <span style={{fontSize: '18px'}}>📱</span>
          Install App
        </button>
      )}
      <AuthGuard>
        <Component {...pageProps} />
      </AuthGuard>
    </>
  )
}
