import React, {useEffect, useState} from 'react'

export default function Diagnostic(){
  const [info, setInfo] = useState({status: 'checking'})
  useEffect(()=>{
    async function fetchInfo(){
      try{
        // Compute API base at runtime if NEXT_PUBLIC_API_BASE wasn't baked into the build
        // Prefer an injected runtime config written by the container entrypoint
        const runtimeConfig = (typeof window !== 'undefined' && window.__RUNTIME_CONFIG) ? window.__RUNTIME_CONFIG : null
        // If running in a preview environment (like GitHub Codespaces / Remote Preview)
        // the hostname may be something like "<id>-3000.app.github.dev". In that case
        // the API will be exposed on the same hostname but port 8000 (i.e. "-8000").
        // Detect that pattern and compute the preview API base accordingly so the
        // client can reach the API from the preview browser.
        let runtimeBase = ''
        if (typeof window !== 'undefined' && window.location){
          const {protocol, hostname} = window.location
          // match names that include a "-3000" token before the preview domain
          const previewMatch = hostname.match(/^(.+)-3000(\..+)$/)
          if (previewMatch){
            // replace '-3000' with '-8000' to reach the API preview host
            const apiHost = `${previewMatch[1]}-8000${previewMatch[2]}`
            runtimeBase = `${protocol}//${apiHost}`
          } else {
            // default local fallback to the same host on port 8000
            runtimeBase = `${protocol}//${hostname}:8000`
          }
        }
        // Decide which base to use. Runtime config (NEXT_PUBLIC_API_BASE) takes
        // precedence for normal local development, but when we're running inside
        // a preview hostname (for example `...-3000.app.github.dev`) the preview
        // heuristic should be preferred even if the runtime config was set to
        // `http://localhost:8000` (which would be unreachable from the preview).
        const configBase = runtimeConfig?.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_BASE || ''
        const isPreviewHost = (typeof window !== 'undefined' && window.location && /-3000\./.test(window.location.hostname))
        let base = ''
        if (isPreviewHost && runtimeBase){
          base = runtimeBase
        } else if (configBase){
          base = configBase
        } else {
          base = runtimeBase
        }
        base = (base || '').replace(/\/$/, '')

        // Helper to fetch and capture full details (status, headers, raw text, parsed JSON)
        async function fetchDetails(url){
          const res = await fetch(url, {cache: 'no-store'})
          const ct = res.headers.get('content-type') || ''
          let raw = null
          try{
            raw = await res.clone().text()
          }catch(e){
            raw = `<failed to read body: ${String(e)}>`
          }
          let parsed = null
          if (ct.includes('application/json')){
            try{ parsed = JSON.parse(raw) }catch(e){ parsed = {__json_parse_error: String(e), __raw: raw} }
          }
          return {
            url,
            ok: res.ok,
            status: res.status,
            statusText: res.statusText,
            contentType: ct,
            headers: Object.fromEntries(Array.from(res.headers.entries())),
            raw,
            json: parsed,
          }
        }

        const h = await fetchDetails(base + '/health')
        const v = await fetchDetails(base + '/version')
        // Also include any last unhandled error captured globally
        const lastUnhandled = (typeof window !== 'undefined' && window.__LAST_UNHANDLED) ? window.__LAST_UNHANDLED : null
        setInfo({health: h, version: v, base, lastUnhandled})
      }catch(e){
        // keep the real Error object details
        setInfo({error: e && e.message ? e.message : String(e)})
      }
    }
    fetchInfo()
  }, [])

  return (
    <main style={{fontFamily:'system-ui, -apple-system, Roboto, Arial', padding:20}}>
      <h1>RealDiag — Diagnostic UI (Next)</h1>
      <p>This minimal Next.js page calls the API backend.</p>

      {/* Result div for E2E testing - shows backend health status */}
      <div id="result" style={{
        padding: 16,
        marginTop: 16,
        background: info.health?.ok ? '#d4edda' : (info.error ? '#f8d7da' : '#fff3cd'),
        border: `1px solid ${info.health?.ok ? '#c3e6cb' : (info.error ? '#f5c6cb' : '#ffeaa7')}`,
        borderRadius: 6,
        color: '#333'
      }}>
        {info.status === 'checking' && 'Checking backend...'}
        {info.error && `Error: ${info.error}`}
        {info.health && !info.error && (
          info.health.ok 
            ? `✅ Backend is healthy (${info.health.status})` 
            : `❌ Backend returned error (${info.health.status} ${info.health.statusText})`
        )}
      </div>

      <section style={{marginTop:16}}>
        <h2>Runtime</h2>
        <pre style={{background:'#f6f8fa',padding:12,borderRadius:6}}>{JSON.stringify({base: info.base, lastUnhandled: info.lastUnhandled}, null, 2)}</pre>
      </section>

      <section style={{marginTop:16}}>
        <h2>Health</h2>
        {info.health ? (
          <div>
            <div>Status: {info.health.ok ? 'OK' : 'ERROR'} — {info.health.status} {info.health.statusText}</div>
            <details style={{marginTop:8, background:'#fff', padding:8, borderRadius:6}}>
              <summary style={{cursor:'pointer'}}>View details (headers + raw body)</summary>
              <div style={{marginTop:8}}>
                <strong>URL:</strong> {info.health.url}
                <pre style={{background:'#f6f8fa',padding:8,borderRadius:6,overflowX:'auto'}}>{JSON.stringify(info.health.headers, null, 2)}</pre>
                <strong>Content-Type:</strong> {info.health.contentType}
                <strong>Raw body:</strong>
                <pre style={{background:'#f6f8fa',padding:8,borderRadius:6,overflowX:'auto'}}>{info.health.raw}</pre>
                <strong>Parsed JSON (if any):</strong>
                <pre style={{background:'#f6f8fa',padding:8,borderRadius:6,overflowX:'auto'}}>{JSON.stringify(info.health.json, null, 2)}</pre>
              </div>
            </details>
          </div>
        ) : <div>Loading...</div>}
      </section>

      <section style={{marginTop:16}}>
        <h2>Version</h2>
        {info.version ? (
          <div>
            <div>Status: {info.version.ok ? 'OK' : 'ERROR'} — {info.version.status} {info.version.statusText}</div>
            <details style={{marginTop:8, background:'#fff', padding:8, borderRadius:6}}>
              <summary style={{cursor:'pointer'}}>View details (headers + raw body)</summary>
              <div style={{marginTop:8}}>
                <strong>URL:</strong> {info.version.url}
                <pre style={{background:'#f6f8fa',padding:8,borderRadius:6,overflowX:'auto'}}>{JSON.stringify(info.version.headers, null, 2)}</pre>
                <strong>Content-Type:</strong> {info.version.contentType}
                <strong>Raw body:</strong>
                <pre style={{background:'#f6f8fa',padding:8,borderRadius:6,overflowX:'auto'}}>{info.version.raw}</pre>
                <strong>Parsed JSON (if any):</strong>
                <pre style={{background:'#f6f8fa',padding:8,borderRadius:6,overflowX:'auto'}}>{JSON.stringify(info.version.json, null, 2)}</pre>
              </div>
            </details>
          </div>
        ) : <div>Loading...</div>}
      </section>
    </main>
  )
}
