"use client";
import { useEffect, useMemo, useState } from "react";

const FAMILIES = [
  { id: "neurology", label: "Neurology" },
  { id: "cardiology", label: "Cardiology" },
  { id: "endocrinology", label: "Endocrinology" },
];

function useApiBase() {
  return useMemo(() => {
    if (process.env.NEXT_PUBLIC_API_BASE) return process.env.NEXT_PUBLIC_API_BASE;
    if (typeof window !== "undefined") {
      const host = window.location.hostname.replace("-3000", "-8000");
      return `https://${host}`;
    }
    return "http://localhost:8000";
  }, []);
}

export default function ReferencePage() {
  const apiBase = useApiBase();
  const [family, setFamily] = useState("neurology");
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [query, setQuery] = useState("");
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setErr("");
      setExpandedId(null);
      try {
        const res = await fetch(`${apiBase}/reference/${family}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (!cancelled) {
          setRules(data.rules || []);
        }
      } catch (e) {
        if (!cancelled) {
          setErr(`Failed to load ${family} rules: ${e.message}`);
          setRules([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [apiBase, family]);

  const filtered = useMemo(() => {
    const q = (query || "").toLowerCase().trim();
    if (!q) return rules;

    return (rules || []).filter((r) => {
      const label = (r.label || "").toLowerCase();
      const id = (r.id || "").toLowerCase();
      const present = (r.presentations || []).join(" ").toLowerCase();
      const icd = (r.icd10 || []).join(" ").toLowerCase();
      const snomed = (r.snomed || []).join(" ").toLowerCase();
      return (
        label.includes(q) ||
        id.includes(q) ||
        present.includes(q) ||
        icd.includes(q) ||
        snomed.includes(q)
      );
    });
  }, [rules, query]);

  function toggleExpanded(id) {
    setExpandedId((prev) => (prev === id ? null : id));
  }

  return (
    <main style={{ padding: 16, maxWidth: 1100, margin: "0 auto" }}>
      <h1 style={{ marginBottom: 4 }}>Reference: Diagnostic Rules & Codes</h1>
      <p style={{ marginBottom: 12, fontSize: 14, color: "#555" }}>
        Browse RealDiag&apos;s structured rules for neurology, cardiology, and endocrinology.
        Use the search box to filter by diagnosis name, typical presentations, ICD-10, or SNOMED.
      </p>

      <p style={{ marginTop: -8, marginBottom: 16, fontSize: 12 }}>
        Need a printable cheat-sheet?{" "}
        <a href="/reference/printable" target="_blank" rel="noopener noreferrer">
          Open printable view
        </a>
        .
      </p>

      {/* Top controls: family buttons + export */}
      <div
        style={{
          marginBottom: 12,
          display: "flex",
          gap: 8,
          flexWrap: "wrap",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {FAMILIES.map((f) => (
            <button
              key={f.id}
              onClick={() => setFamily(f.id)}
              style={{
                padding: "6px 12px",
                borderRadius: 999,
                border: "1px solid #ccc",
                fontSize: 13,
                cursor: "pointer",
                background: family === f.id ? "#e0f2f1" : "#f5f5f5",
                fontWeight: family === f.id ? 600 : 400,
              }}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Export CSV button */}
        <a
          href="/diagnosis_codes_all.csv"
          download
          style={{
            padding: "6px 12px",
            borderRadius: 999,
            border: "1px solid #00796b",
            background: "#009688",
            color: "white",
            fontSize: 13,
            textDecoration: "none",
            fontWeight: 600,
          }}
        >
          Export CSV
        </a>
      </div>

      {/* Search */}
      <div style={{ marginBottom: 16 }}>
        <input
          type="text"
          placeholder="Search by diagnosis, symptom, ICD-10, or SNOMED..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{
            width: "100%",
            maxWidth: 420,
            padding: "6px 10px",
            borderRadius: 999,
            border: "1px solid #ccc",
            fontSize: 13,
          }}
        />
      </div>

      {/* Status / error */}
      {loading && (
        <div style={{ marginBottom: 8, fontSize: 13 }}>
          Loading {family} rules…
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
            gridTemplateColumns: "1.1fr 1.6fr 0.8fr 0.6fr",
            fontWeight: 600,
            background: "#fafafa",
            borderBottom: "1px solid #eee",
            padding: "8px 10px",
          }}
        >
          <div>Diagnosis</div>
          <div>Typical presentations</div>
          <div>ICD-10</div>
          <div>Details</div>
        </div>

        {/* Rows */}
        {(filtered || []).map((r) => {
          const isExpanded = expandedId === r.id;
          return (
            <div key={r.id}>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1.1fr 1.6fr 0.8fr 0.6fr",
                  borderBottom: "1px solid #f2f2f2",
                  padding: "8px 10px",
                  background: isExpanded ? "#f9fdfd" : "white",
                }}
              >
                <div>
                  <div style={{ fontWeight: 600 }}>{r.label || r.id}</div>
                  <div style={{ fontSize: 11, color: "#777" }}>{r.id}</div>
                </div>
                <div>
                  {(r.presentations || []).length === 0 ? (
                    <span style={{ color: "#999" }}>—</span>
                  ) : (
                    <ul style={{ margin: 0, paddingLeft: 18 }}>
                      {r.presentations.map((p, i) => (
                        <li key={i}>{p}</li>
                      ))}
                    </ul>
                  )}
                </div>
                <div>
                  {r.icd10 && r.icd10.length > 0 ? (
                    r.icd10.join(", ")
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
                    {r.snomed && r.snomed.length > 0 ? (
                      r.snomed.join(", ")
                    ) : (
                      <span style={{ color: "#999" }}>Not specified</span>
                    )}
                  </div>
                  {r.citations && r.citations.length > 0 && (
                    <div>
                      <strong>Guideline / reference notes:</strong>
                      <ol style={{ fontSize: 12, marginTop: 4, paddingLeft: 18 }}>
                        {r.citations.map((c, i) => (
                          <li key={i}>{c}</li>
                        ))}
                      </ol>
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
    </main>
  );
}
