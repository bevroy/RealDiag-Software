import React, { useState, useEffect } from "react";
import Head from "next/head";

export default function SourcesPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sources, setSources] = useState([]);

  useEffect(() => {
    async function loadSources() {
      try {
        const runtimeConfig = (typeof window !== 'undefined' && window.__RUNTIME_CONFIG) ? window.__RUNTIME_CONFIG : null;
        const apiBase = runtimeConfig?.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com';
        
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
        ];

        const sourcesData = [];

        for (const family of families) {
          try {
            const res = await fetch(`${apiBase}/reference/${family}`);
            if (!res.ok) continue;
            const data = await res.json();
            
            sourcesData.push({
              family: family,
              familyLabel: family.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()),
              version: data.version || "N/A",
              source: data.source || "RealDiag Clinical Guidelines",
              rules: data.rules || [],
            });
          } catch (err) {
            console.error(`Failed to load ${family}:`, err);
          }
        }

        setSources(sourcesData);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setError(err.message);
        setLoading(false);
      }
    }

    loadSources();
  }, []);

  // Collect all unique citations across all rules
  const allCitations = [];
  sources.forEach((fam) => {
    fam.rules.forEach((rule) => {
      if (rule.citations && Array.isArray(rule.citations)) {
        rule.citations.forEach((citation) => {
          if (!allCitations.includes(citation)) {
            allCitations.push(citation);
          }
        });
      }
    });
  });

  return (
    <>
      <Head>
        <title>Medical Sources & References | RealDiag</title>
        <meta
          name="description"
          content="Medical guidelines, references, and sources used in RealDiag diagnostic system"
        />
      </Head>
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          fontFamily: "system-ui, sans-serif",
          background: 'linear-gradient(135deg, #f0fdfa 0%, #e7f5f3 100%)',
          padding: '2rem'
        }}
      >
        {/* Navigation Dropdown */}
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto 1rem',
          width: '100%'
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
              <a href="/symptom-search" style={{
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
                🔍 Symptom Search
              </a>
              <a href="/rules" style={{
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
                📋 Browse Rules
              </a>
              <a href="/integration" style={{
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
                🔌 API
              </a>
              <a href="/features-demo" style={{
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
                ✨ Features
              </a>
              <a href="/education" style={{
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
                📚 Training
              </a>
              <a href="/account" style={{
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
                👤 Account
              </a>
            </div>
          </details>
        </div>

        {/* Header */}
        <div style={{ maxWidth: 1200, margin: "0 auto", width: '100%' }}>
          <div style={{ background: 'white', borderRadius: '12px', padding: '1.5rem', marginBottom: '1rem', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <img src="/logo.png" alt="RealDiag Logo" style={{ height: '50px' }} />
              <h1 style={{ marginBottom: 0, color: '#92400e' }}>Medical Sources & References</h1>
            </div>
            <a
              href="/"
              style={{
                padding: "8px 16px",
                background: "linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)",
                color: "white",
                textDecoration: "none",
                borderRadius: "6px",
                fontSize: 14,
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                gap: "6px",
                whiteSpace: "nowrap"
              }}
            >
              🏠 Home
            </a>
          </div>

        {/* Content */}
        <div
          style={{
            background: 'white',
            borderRadius: '12px',
            padding: '1rem',
            marginBottom: '1rem',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}
        >
          <div style={{ maxWidth: 1000, margin: "0 auto" }}>
            <p style={{ fontSize: 16, color: "#6b7280", marginBottom: 16 }}>
              RealDiag integrates evidence-based clinical guidelines and medical literature
              to support diagnostic decision-making. Below are the sources used across
              our diagnostic modules.
            </p>

            {loading && (
              <div style={{ textAlign: "center", padding: 40, color: "#6b7280" }}>
                Loading sources...
              </div>
            )}

            {error && (
              <div
                style={{
                  background: "#fee",
                  border: "1px solid #fcc",
                  padding: 16,
                  borderRadius: 8,
                  color: "#c00",
                }}
              >
                Error loading sources: {error}
              </div>
            )}

            {!loading && !error && (
              <>
                {/* Family-Level Sources */}
                <section style={{ marginBottom: 48 }}>
                  <h2 style={{ fontSize: 24, marginBottom: 16, color: "#0f766e" }}>
                    Core Clinical Guidelines by Specialty
                  </h2>
                  <div style={{ display: "grid", gap: 16 }}>
                    {sources.map((fam) => (
                      <div
                        key={fam.family}
                        style={{
                          background: "white",
                          border: "1px solid #e5e7eb",
                          borderRadius: 8,
                          padding: 16,
                          boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
                        }}
                      >
                        <div style={{ display: "flex", alignItems: "center", marginBottom: 8 }}>
                          <span
                            style={{
                              display: "inline-block",
                              padding: "4px 12px",
                              borderRadius: 999,
                              fontSize: 12,
                              marginRight: 12,
                              background: "#ccfbf1",
                              color: "#0f766e",
                              fontWeight: 600,
                            }}
                          >
                            {fam.familyLabel}
                          </span>
                          <span style={{ fontSize: 12, color: "#9ca3af" }}>
                            Version {fam.version}
                          </span>
                        </div>
                        <div style={{ fontSize: 14, color: "#374151" }}>
                          <strong>Source:</strong> {fam.source}
                        </div>
                        <div style={{ fontSize: 13, color: "#6b7280", marginTop: 4 }}>
                          {fam.rules.length} diagnostic rule{fam.rules.length !== 1 ? "s" : ""} available
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

                {/* Rule-Specific Citations */}
                {allCitations.length > 0 && (
                  <section>
                    <h2 style={{ fontSize: 24, marginBottom: 16, color: "#0f766e" }}>
                      Specific Guidelines & References
                    </h2>
                    <div
                      style={{
                        background: "white",
                        border: "1px solid #e5e7eb",
                        borderRadius: 8,
                        padding: 24,
                        boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
                      }}
                    >
                      <ol style={{ fontSize: 14, lineHeight: 1.8, paddingLeft: 20 }}>
                        {allCitations.map((citation, idx) => (
                          <li key={idx} style={{ marginBottom: 12 }}>
                            {citation}
                          </li>
                        ))}
                      </ol>
                    </div>
                  </section>
                )}

                {allCitations.length === 0 && (
                  <section>
                    <div
                      style={{
                        background: "#fefce8",
                        border: "1px solid #fde047",
                        borderRadius: 8,
                        padding: 16,
                        fontSize: 14,
                        color: "#854d0e",
                      }}
                    >
                      <strong>Note:</strong> Specific citations are being compiled and will be added
                      to individual diagnostic rules. All rules are based on established clinical
                      guidelines and evidence-based medical literature.
                    </div>
                  </section>
                )}

                {/* Disclaimer */}
                <section style={{ marginTop: 48, paddingTop: 24, borderTop: "1px solid #e5e7eb" }}>
                  <h3 style={{ fontSize: 18, marginBottom: 12, color: "#0f766e" }}>
                    Medical Disclaimer
                  </h3>
                  <p style={{ fontSize: 14, color: "#6b7280", lineHeight: 1.7 }}>
                    RealDiag is designed to support clinical decision-making and should not
                    replace professional medical judgment. All diagnostic recommendations should
                    be verified with current clinical guidelines and adapted to individual
                    patient circumstances. This system aggregates information from multiple
                    authoritative sources but may not reflect the most recent updates to all
                    guidelines. Healthcare providers are responsible for confirming diagnostic
                    criteria and treatment recommendations.
                  </p>
                </section>
              </>
            )}
          </div>
        </div>
        </div>

        {/* Footer */}
        <footer
          style={{
            background: "#f3f4f6",
            borderTop: "1px solid #e5e7eb",
            padding: "24px",
            textAlign: "center",
            fontSize: 14,
            color: "#6b7280",
          }}
        >
          <div style={{ maxWidth: 1000, margin: "0 auto" }}>
            <div style={{ marginBottom: 12 }}>
              <a href="/" style={{ marginRight: 16, color: "#667eea" }}>Home</a>
              <a href="/symptom" style={{ marginRight: 16, color: "#667eea" }}>Symptom Checker</a>
              <a href="/rules" style={{ marginRight: 16, color: "#667eea" }}>Diagnostic Rules</a>
              <a href="/sources" style={{ color: "#667eea" }}>Medical Sources</a>
            </div>
            <div>© 2025 RealDiag. All rights reserved.</div>
          </div>
        </footer>
      </div>
    </>
  );
}
