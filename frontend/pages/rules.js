import { useEffect, useMemo, useState } from "react";

const FAMILIES = [
  { id: "neurology", label: "Neurology" },
  { id: "cardiology", label: "Cardiology" },
  { id: "endocrinology", label: "Endocrinology" },
  { id: "pulmonology", label: "Pulmonology" },
  { id: "gastroenterology", label: "Gastroenterology" },
  { id: "infectious_disease", label: "Infectious Disease" },
  { id: "nephrology", label: "Nephrology" },
  { id: "rheumatology", label: "Rheumatology" },
  { id: "dermatology", label: "Dermatology" },
  { id: "psychiatry", label: "Psychiatry" },
  { id: "obstetrics_gynecology", label: "OB/GYN" },
];

export default function ReferencePage() {
  const [allRules, setAllRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [query, setQuery] = useState("");
  const [expandedId, setExpandedId] = useState(null);
  const [selectedFamily, setSelectedFamily] = useState("all");

  useEffect(() => {
    let cancelled = false;
    async function loadAll() {
      // Get API base inside useEffect to ensure runtime-config.js has loaded
      const runtimeConfig = (typeof window !== 'undefined' && window.__RUNTIME_CONFIG) ? window.__RUNTIME_CONFIG : null;
      const apiBase = runtimeConfig?.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com';
      
      setLoading(true);
      setErr("");
      setExpandedId(null);
      try {
        const results = await Promise.all(
          FAMILIES.map(async (f) => {
            const res = await fetch(`${apiBase}/reference/${f.id}`);
            if (!res.ok) throw new Error(`Failed to load ${f.label}`);
            const data = await res.json();
            return (data.rules || [])
              .filter(rule => rule && rule.id) // Filter out invalid rules
              .map(rule => ({
                ...rule,
                family: f.label,
                familyId: f.id,
                // Ensure arrays are actually arrays and normalize to strings
                presentations: Array.isArray(rule.presentations) ? rule.presentations.map(String) : [],
                icd10: Array.isArray(rule.icd10) ? rule.icd10.map(String) : [],
                snomed: Array.isArray(rule.snomed) ? rule.snomed.map(String) : [],
                citations: Array.isArray(rule.citations) ? rule.citations.map(String) : [],
              }));
          })
        );
        if (!cancelled) {
          setAllRules(results.flat().filter(r => r && r.id));
        }
      } catch (e) {
        if (!cancelled) {
          setErr(`Failed to load rules: ${e.message}`);
          setAllRules([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    loadAll();
    return () => {
      cancelled = true;
    };
  }, []);

  const filtered = useMemo(() => {
    const q = (query || "").toLowerCase().trim();
    
    // Filter by family first
    let rulesToFilter = allRules;
    if (selectedFamily !== "all") {
      rulesToFilter = allRules.filter(r => r.familyId === selectedFamily);
    }
    
    // Then filter by search query
    if (!q) return rulesToFilter;

    return (rulesToFilter || []).filter((r) => {
      const label = (r.label || "").toLowerCase();
      const id = (r.id || "").toLowerCase();
      const family = (r.family || "").toLowerCase();
      const present = (r.presentations || []).join(" ").toLowerCase();
      const icd = (r.icd10 || []).join(" ").toLowerCase();
      const snomed = (r.snomed || []).join(" ").toLowerCase();
      return (
        label.includes(q) ||
        id.includes(q) ||
        family.includes(q) ||
        present.includes(q) ||
        icd.includes(q) ||
        snomed.includes(q)
      );
    });
  }, [allRules, query, selectedFamily]);

  function toggleExpanded(id) {
    setExpandedId((prev) => (prev === id ? null : id));
  }

  return (
    <main style={{ padding: 16, maxWidth: 1100, margin: "0 auto", minHeight: '100vh', background: 'linear-gradient(135deg, #f0fdfa 0%, #e7f5f3 100%)' }}>
      <div style={{ background: 'white', borderRadius: '12px', padding: '1.5rem', marginBottom: '1rem', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', display: 'flex', alignItems: 'center', gap: '16px' }}>
        <img src="/logo.png" alt="RealDiag Logo" style={{ height: '50px' }} />
        <h1 style={{ marginBottom: 0, color: '#0f766e' }}>Reference: Diagnostic Rules & Codes</h1>
      </div>
      
      <div style={{ background: 'white', borderRadius: '12px', padding: '1rem', marginBottom: '1rem', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <p style={{ marginBottom: 8, fontSize: 14, color: "#64748b" }}>
          Search across all disease processes (neurology, cardiology, endocrinology) to find
          relevant diagnoses based on symptoms, ICD-10, or SNOMED codes.
        </p>
        <p style={{ margin: 0, fontSize: 12, color: "#94a3b8" }}>
          Need a printable cheat-sheet?{" "}
          <a href="/reference/printable" target="_blank" rel="noopener noreferrer" style={{ color: '#14b8a6' }}>
            Open printable view
          </a>{" "}
          • View{" "}
          <a href="/sources" style={{ color: '#14b8a6' }}>
            medical sources & references
          </a>.
        </p>
      </div>

      {/* Top controls: family filters + export */}
      <div style={{ background: 'white', borderRadius: '12px', padding: '1rem', marginBottom: '1rem', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <div
          style={{
            display: "flex",
            gap: 8,
            flexWrap: "wrap",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
          <span style={{ fontSize: 13, fontWeight: 600, marginRight: 4 }}>Filter:</span>
          <button
            onClick={() => setSelectedFamily("all")}
            style={{
              padding: "6px 12px",
              borderRadius: 999,
              border: "1px solid #ccc",
              fontSize: 13,
              cursor: "pointer",
              background: selectedFamily === "all" ? "#ccfbf1" : "#f5f5f5",
              fontWeight: selectedFamily === "all" ? 600 : 400,
            }}
          >
            All ({allRules.length})
          </button>
          {FAMILIES.map((f) => {
            const count = allRules.filter(r => r.familyId === f.id).length;
            return (
              <button
                key={f.id}
                onClick={() => setSelectedFamily(f.id)}
                style={{
                  padding: "6px 12px",
                  borderRadius: 999,
                  border: "1px solid #ccc",
                  fontSize: 13,
                  cursor: "pointer",
                  background: selectedFamily === f.id ? "#ccfbf1" : "#f5f5f5",
                  fontWeight: selectedFamily === f.id ? 600 : 400,
                }}
              >
                {f.label} ({count})
              </button>
            );
          })}
        </div>

        {/* Export CSV button */}
        <a
          href="/diagnosis_codes_all.csv"
          download
          style={{
            padding: "6px 12px",
            borderRadius: 999,
            border: "1px solid #0d9488",
            background: "linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)",
            color: "white",
            fontSize: 13,
            textDecoration: "none",
            fontWeight: 600,
          }}
        >
          Export CSV
        </a>
      </div>
      </div>

      {/* Search */}
      <div style={{ background: 'white', borderRadius: '12px', padding: '1rem', marginBottom: '1rem', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <input
          type="text"
          placeholder="Search across all diseases by diagnosis, symptom, ICD-10, or SNOMED..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{
            width: "100%",
            maxWidth: 500,
            padding: "8px 12px",
            borderRadius: 999,
            border: "1px solid #ccc",
            fontSize: 14,
          }}
        />
        {query && (
          <div style={{ marginTop: 6, fontSize: 12, color: "#666" }}>
            Found {filtered.length} result{filtered.length !== 1 ? "s" : ""}
          </div>
        )}
      </div>

      {/* Status / error */}
      {loading && (
        <div style={{ marginBottom: 8, fontSize: 13 }}>
          Loading all disease rules…
        </div>
      )}
      {err && (
        <div
          style={{
            background: "#FFE8E6",
            color: "#A61B1B",
            padding: 10,
            borderRadius: 8,
            marginBottom: 8,
            fontSize: 13,
          }}
        >
          {err}
        </div>
      )}

      {/* Table */}
      <div style={{ background: 'white', borderRadius: '12px', padding: '1rem', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <div
        style={{
          border: "1px solid #eee",
          borderRadius: 12,
          overflow: "hidden",
          fontSize: 13,
        }}
      >
        {/* Header */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "0.8fr 1.1fr 1.6fr 0.8fr 0.6fr",
            fontWeight: 600,
            background: "#fafafa",
            borderBottom: "1px solid #eee",
            padding: "8px 10px",
          }}
        >
          <div>Family</div>
          <div>Diagnosis</div>
          <div>Typical presentations</div>
          <div>ICD-10</div>
          <div>Details</div>
        </div>

        {/* Rows */}
        {(filtered || []).map((r, idx) => {
          if (!r || !r.id) return null;
          const isExpanded = expandedId === r.id;
          
          // Safe value extraction with fallbacks
          const label = r.label || r.id || '';
          const family = r.family || '';
          const presentations = r.presentations || [];
          const icd10 = r.icd10 || [];
          const snomed = r.snomed || [];
          const citations = r.citations || [];
          
          return (
            <div key={r.id}>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "0.8fr 1.1fr 1.6fr 0.8fr 0.6fr",
                  borderBottom: "1px solid #f2f2f2",
                  padding: "8px 10px",
                  background: isExpanded ? "#f9fdfd" : "white",
                }}
              >
                <div>
                  <span
                    style={{
                      display: "inline-block",
                      fontSize: 11,
                      padding: "2px 8px",
                      borderRadius: 999,
                      background: 
                        r.familyId === "neurology" ? "#E3F2FD" :
                        r.familyId === "cardiology" ? "#FCE4EC" :
                        r.familyId === "endocrinology" ? "#FFF3E0" :
                        r.familyId === "pulmonology" ? "#E8F5E9" :
                        r.familyId === "gastroenterology" ? "#FFF9C4" :
                        r.familyId === "infectious_disease" ? "#FFEBEE" :
                        r.familyId === "nephrology" ? "#E0F7FA" :
                        r.familyId === "rheumatology" ? "#F3E5F5" :
                        r.familyId === "dermatology" ? "#FBE9E7" :
                        r.familyId === "psychiatry" ? "#E8EAF6" :
                        r.familyId === "obstetrics_gynecology" ? "#FCE4EC" : "#F5F5F5",
                      color: 
                        r.familyId === "neurology" ? "#1565C0" :
                        r.familyId === "cardiology" ? "#C2185B" :
                        r.familyId === "endocrinology" ? "#E65100" :
                        r.familyId === "pulmonology" ? "#2E7D32" :
                        r.familyId === "gastroenterology" ? "#F57F17" :
                        r.familyId === "infectious_disease" ? "#C62828" :
                        r.familyId === "nephrology" ? "#006064" :
                        r.familyId === "rheumatology" ? "#6A1B9A" :
                        r.familyId === "dermatology" ? "#BF360C" :
                        r.familyId === "psychiatry" ? "#283593" :
                        r.familyId === "obstetrics_gynecology" ? "#AD1457" : "#616161",
                      fontWeight: 600,
                    }}
                  >
                    {family}
                  </span>
                </div>
                <div>
                  <div style={{ fontWeight: 600 }}>{label}</div>
                  <div style={{ fontSize: 11, color: "#777" }}>{r.id}</div>
                </div>
                <div>
                  {presentations.length === 0 ? (
                    <span style={{ color: "#999" }}>—</span>
                  ) : (
                    <ul style={{ margin: 0, paddingLeft: 18 }}>
                      {presentations.map((p, i) => (
                        <li key={i}>{p}</li>
                      ))}
                    </ul>
                  )}
                </div>
                <div>
                  {icd10.length > 0 ? (
                    icd10.join(", ")
                  ) : (
                    <span style={{ color: "#999" }}>—</span>
                  )}
                </div>
                <div>
                  <button
                    type="button"
                    onClick={() => toggleExpanded(r.id)}
                    style={{
                      fontSize: 12,
                      padding: "4px 8px",
                      borderRadius: 999,
                      border: "1px solid #ccc",
                      background: "white",
                      cursor: "pointer",
                    }}
                  >
                    {isExpanded ? "Hide" : "Show"} details
                  </button>
                </div>
              </div>

              {/* Expanded details */}
              {isExpanded && (
                <div
                  style={{
                    borderBottom: "1px solid #f2f2f2",
                    padding: "8px 16px 10px 16px",
                    background: "#f9fdfd",
                    fontSize: 12,
                  }}
                >
                  <div style={{ marginBottom: 4 }}>
                    <strong>SNOMED:</strong>{" "}
                    {snomed.length > 0 ? (
                      snomed.join(", ")
                    ) : (
                      <span style={{ color: "#999" }}>Not specified</span>
                    )}
                  </div>
                  {citations.length > 0 && (
                    <div style={{ marginTop: 8 }}>
                      <strong>📚 Sources & References:</strong>
                      <ol style={{ fontSize: 12, marginTop: 4, paddingLeft: 18 }}>
                        {citations.map((c, i) => (
                          <li key={i}>{c}</li>
                        ))}
                      </ol>
                    </div>
                  )}
                  {citations.length === 0 && (
                    <div style={{ marginTop: 8, fontSize: 11, color: "#666" }}>
                      <strong>Sources:</strong> Clinical guidelines and medical literature. See{" "}
                      <a href="/sources" style={{ color: "#667eea" }}>Medical Sources page</a> for complete references.
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}

        {(!loading && filtered.length === 0) && (
          <div style={{ padding: 12, fontSize: 13, color: "#777" }}>
            No rules match your search.
          </div>
        )}
      </div>
      </div>
    </main>
  );
}
