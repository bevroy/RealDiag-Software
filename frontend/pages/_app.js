import React, {useEffect} from 'react'
import '../styles/globals.css'

export default function App({Component, pageProps}){
  useEffect(()=>{
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
      window.removeEventListener('unhandledrejection', onUnhandledRejection)
      window.removeEventListener('error', onError)
    }
  }, [])

  return <Component {...pageProps} />
}
