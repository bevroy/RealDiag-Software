import React, { useState, useEffect } from "react";
import Head from "next/head";

export default function SourcesDebugPage() {
  const [logs, setLogs] = useState([]);
  const [treeCount, setTreeCount] = useState(null);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const addLog = (message, type = 'info') => {
    setLogs(prev => [...prev, { time: new Date().toISOString(), message, type }]);
    console.log(`[${type}] ${message}`);
  };

  useEffect(() => {
    async function loadSourcesWithDebug() {
      try {
        addLog('Starting sources load...');
        
        const runtimeConfig = (typeof window !== 'undefined' && window.__RUNTIME_CONFIG) ? window.__RUNTIME_CONFIG : null;
        const apiBase = runtimeConfig?.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com';
        
        addLog(`API Base: ${apiBase}`);
        
        // Fetch the total tree count from backend
        try {
          addLog('Fetching tree count from /diagnostic/trees...');
          const treesRes = await fetch(`${apiBase}/diagnostic/trees`);
          addLog(`Tree count response status: ${treesRes.status}`);
          
          if (treesRes.ok) {
            const treesData = await treesRes.json();
            if (treesData.trees) {
              setTreeCount(treesData.trees.length);
              addLog(`Tree count loaded: ${treesData.trees.length}`, 'success');
            }
          } else {
            addLog(`Tree count fetch failed: ${treesRes.statusText}`, 'error');
          }
        } catch (err) {
          addLog(`Tree count error: ${err.message}`, 'error');
        }
        
        const families = [
          "neurology",
          "cardiology",
          "endocrinology",
          "pulmonology",
          "gastroenterology",
          "infectious_disease",
          "nephrology",
          "rheumatology",
          "dermatology",
          "psychiatry",
          "obstetrics_gynecology",
          "orthopedics",
          "emergency",
          "hematology",
          "allergy",
          "dentistry",
          "ent",
          "general",
          "oncology",
          "ophthalmology",
          "pediatrics",
          "surgery",
          "trauma",
          "urology",
        ];

        addLog(`Loading ${families.length} specialties...`);

        // Load all families in parallel with timeout
        const fetchPromises = families.map(async (family, index) => {
          try {
            addLog(`[${index + 1}/${families.length}] Fetching ${family}...`);
            
            const controller = new AbortController();
            const timeoutId = setTimeout(() => {
              controller.abort();
              addLog(`${family} - TIMEOUT after 10s`, 'warn');
            }, 10000);
            
            const res = await fetch(`${apiBase}/reference/${family}`, {
              signal: controller.signal
            });
            clearTimeout(timeoutId);
            
            addLog(`${family} - Status: ${res.status}`);
            
            if (!res.ok) {
              addLog(`${family} - Failed: ${res.statusText}`, 'warn');
              return null;
            }
            
            const data = await res.json();
            addLog(`${family} - Success: ${data.count || 0} trees`, 'success');
            
            return {
              family: family,
              familyLabel: family.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()),
              version: data.version || "N/A",
              source: data.source || "RealDiag Clinical Guidelines",
              rules: data.rules || [],
              count: data.count || (data.rules || []).length,
            };
          } catch (err) {
            if (err.name === 'AbortError') {
              addLog(`${family} - Request aborted (timeout)`, 'error');
            } else {
              addLog(`${family} - Error: ${err.message}`, 'error');
            }
            return null;
          }
        });

        addLog('Waiting for all requests to complete...');
        const results = await Promise.all(fetchPromises);
        const sourcesData = results.filter(s => s !== null);
        
        addLog(`Loaded ${sourcesData.length}/${families.length} specialties`, 'success');
        setSources(sourcesData);
        setLoading(false);
        addLog('Page load complete!', 'success');
      } catch (err) {
        addLog(`Fatal error: ${err.message}`, 'error');
        console.error(err);
        setError(err.message);
        setLoading(false);
      }
    }

    loadSourcesWithDebug();
  }, []);

  return (
    <>
      <Head>
        <title>Sources Debug Page | RealDiag</title>
      </Head>
      <div style={{
        minHeight: "100vh",
        fontFamily: "system-ui, sans-serif",
        background: '#f9fafb',
        padding: '2rem'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h1 style={{ fontSize: 28, marginBottom: 16, color: "#0f766e" }}>
            Sources Page Debug Tool
          </h1>

          <div style={{ 
            background: 'white', 
            borderRadius: 8, 
            padding: 20, 
            marginBottom: 20,
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <h2 style={{ fontSize: 20, marginBottom: 12 }}>Status</h2>
            <p>Loading: {loading ? '🔄 Yes' : '✅ Complete'}</p>
            <p>Tree Count: {treeCount || 'Loading...'}</p>
            <p>Specialties Loaded: {sources.length}</p>
            {error && <p style={{ color: 'red' }}>Error: {error}</p>}
          </div>

          <div style={{ 
            background: 'white', 
            borderRadius: 8, 
            padding: 20, 
            marginBottom: 20,
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <h2 style={{ fontSize: 20, marginBottom: 12 }}>Loaded Specialties</h2>
            {sources.length > 0 ? (
              <div style={{ display: 'grid', gap: 12 }}>
                {sources.map(s => (
                  <div key={s.family} style={{ 
                    padding: 12, 
                    background: '#f9fafb', 
                    borderRadius: 6,
                    border: '1px solid #e5e7eb'
                  }}>
                    <strong>{s.familyLabel}</strong> - {s.count} trees (v{s.version})
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: '#6b7280' }}>No specialties loaded yet...</p>
            )}
          </div>

          <div style={{ 
            background: 'white', 
            borderRadius: 8, 
            padding: 20,
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <h2 style={{ fontSize: 20, marginBottom: 12 }}>Debug Logs</h2>
            <div style={{ 
              maxHeight: '400px', 
              overflowY: 'auto',
              fontFamily: 'monospace',
              fontSize: 12
            }}>
              {logs.map((log, i) => (
                <div 
                  key={i} 
                  style={{ 
                    padding: '4px 8px',
                    borderBottom: '1px solid #e5e7eb',
                    color: log.type === 'error' ? '#dc2626' : 
                           log.type === 'warn' ? '#f59e0b' : 
                           log.type === 'success' ? '#10b981' : '#6b7280'
                  }}
                >
                  [{log.time.split('T')[1].split('.')[0]}] {log.message}
                </div>
              ))}
            </div>
          </div>

          <div style={{ marginTop: 20 }}>
            <a 
              href="/sources" 
              style={{ 
                color: '#0f766e', 
                textDecoration: 'underline' 
              }}
            >
              ← Back to Sources Page
            </a>
          </div>
        </div>
      </div>
    </>
  );
}
