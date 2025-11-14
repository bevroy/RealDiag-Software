import React, {useEffect, useState} from 'react'
import '../styles/globals.css'

export default function App({Component, pageProps}){
  const [installPrompt, setInstallPrompt] = useState(null)
  const [showInstallButton, setShowInstallButton] = useState(false)

  useEffect(()=>{
    // Register service worker for PWA
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then(registration => {
          console.log('Service Worker registered:', registration.scope)
        })
        .catch(error => {
          console.error('Service Worker registration failed:', error)
        })
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
      <Component {...pageProps} />
    </>
  )
}
