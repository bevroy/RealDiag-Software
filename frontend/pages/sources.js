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
        }}
      >
        {/* Header */}
        <header
          style={{
            background: "linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)",
            color: "white",
            padding: "16px 24px",
            boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
          }}
        >
          <div style={{ maxWidth: 1200, margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <a
              href="/"
              style={{
                color: "white",
                textDecoration: "none",
                fontSize: 20,
                fontWeight: 600,
              }}
            >
              RealDiag
            </a>
            <a
              href="/"
              style={{
                padding: "8px 16px",
                background: "rgba(255, 255, 255, 0.2)",
                color: "white",
                textDecoration: "none",
                borderRadius: "6px",
                fontSize: 14,
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                gap: "6px"
              }}
            >
              🏠 Home
            </a>
          </div>
        </header>

        {/* Main Content */}
        <main
          style={{
            flex: 1,
            padding: "24px",
            background: "#f9fafb",
          }}
        >
          <div style={{ maxWidth: 1000, margin: "0 auto" }}>
            <h1 style={{ fontSize: 32, marginBottom: 8, color: "#1f2937" }}>
              📚 Medical Sources & References
            </h1>
            <p style={{ fontSize: 16, color: "#6b7280", marginBottom: 32 }}>
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
                  <h2 style={{ fontSize: 24, marginBottom: 16, color: "#374151" }}>
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
                              background:
                                fam.family === "neurology" ? "#E3F2FD" :
                                fam.family === "cardiology" ? "#FCE4EC" :
                                fam.family === "endocrinology" ? "#FFF3E0" :
                                fam.family === "pulmonology" ? "#E8F5E9" :
                                fam.family === "gastroenterology" ? "#FFFDE7" :
                                fam.family === "infectious_disease" ? "#FFEBEE" :
                                fam.family === "nephrology" ? "#E0F7FA" :
                                fam.family === "rheumatology" ? "#F3E5F5" :
                                fam.family === "dermatology" ? "#FBE9E7" :
                                fam.family === "psychiatry" ? "#E8EAF6" :
                                fam.family === "obstetrics_gynecology" ? "#FCE4EC" : "#F5F5F5",
                              color:
                                fam.family === "neurology" ? "#1565C0" :
                                fam.family === "cardiology" ? "#C2185B" :
                                fam.family === "endocrinology" ? "#E65100" :
                                fam.family === "pulmonology" ? "#2E7D32" :
                                fam.family === "gastroenterology" ? "#F57F17" :
                                fam.family === "infectious_disease" ? "#C62828" :
                                fam.family === "nephrology" ? "#006064" :
                                fam.family === "rheumatology" ? "#6A1B9A" :
                                fam.family === "dermatology" ? "#BF360C" :
                                fam.family === "psychiatry" ? "#283593" :
                                fam.family === "obstetrics_gynecology" ? "#AD1457" : "#616161",
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
                    <h2 style={{ fontSize: 24, marginBottom: 16, color: "#374151" }}>
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
                  <h3 style={{ fontSize: 18, marginBottom: 12, color: "#374151" }}>
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
        </main>

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
