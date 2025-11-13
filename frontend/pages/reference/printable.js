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

export default function PrintableReferencePage() {
  const apiBase = useApiBase();
  const [grouped, setGrouped] = useState({});
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadAll() {
      setLoading(true);
      setErr("");
      try {
        const results = await Promise.all(
          FAMILIES.map(async (f) => {
            const res = await fetch(`${apiBase}/reference/${f.id}`);
            if (!res.ok) throw new Error(`HTTP ${res.status} for ${f.id}`);
            const data = await res.json();
            return {
              family: f.label,
              rules: (data.rules || []).map((r) => ({
                family: f.label,
                id: r.id,
                label: r.label || r.id,
                presentations: r.presentations || [],
                icd10: r.icd10 || [],
                snomed: r.snomed || [],
                citations: r.citations || [],
              })),
            };
          })
        );
        if (!cancelled) {
          const byFamily = {};
          for (const block of results) {
            const rows = [...block.rules];
            rows.sort((a, b) => a.label.localeCompare(b.label));
            byFamily[block.family] = rows;
          }
          setGrouped(byFamily);
        }
      } catch (e) {
        if (!cancelled) {
          setErr(`Failed to load reference data: ${e.message}`);
          setGrouped({});
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadAll();
    return () => {
      cancelled = true;
    };
  }, [apiBase]);

  const familiesWithData = FAMILIES.filter(
    (f) => grouped[f.label] && grouped[f.label].length > 0
  );

  return (
    <html>
      <head>
        <title>RealDiag Reference Cheat-Sheet</title>
        <style>{`
          @page {
            size: A4 landscape;
            margin: 10mm;
          }

          body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            margin: 16px;
            color: #111;
            background: #ffffff;
          }

          h1, h2, h3 {
            margin: 0;
            padding: 0;
          }

          .toolbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
          }
          .toolbar button, .toolbar a {
            font-size: 13px;
            padding: 4px 12px;
            border-radius: 999px;
            border: 1px solid #ccc;
            background: #f5f5f5;
            cursor: pointer;
            text-decoration: none;
            color: #111;
          }

          .page {
            page-break-after: always;
          }
          .page:last-of-type {
            page-break-after: auto;
          }

          table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
          }
          thead {
            background: #e0f2f1;
          }
          th, td {
            border: 1px solid #ddd;
            padding: 4px 6px;
            vertical-align: top;
          }
          th {
            text-align: left;
            font-weight: 600;
          }

          .family-title {
            margin-bottom: 6px;
            font-size: 18px;
          }
          .family-subtitle {
            margin-bottom: 8px;
            font-size: 11px;
            color: #555;
          }

          .presentations-list {
            margin: 0;
            padding-left: 16px;
          }
          .presentations-list li {
            margin: 0;
          }
          .small {
            font-size: 11px;
            color: #555;
          }

          @media print {
            .toolbar {
              display: none;
            }
            body {
              margin: 0;
              font-size: 11px;
            }
            table {
              font-size: 11px;
            }
          }
        `}</style>
      </head>
      <body>
        <div className="toolbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <img src="/logo.png" alt="RealDiag Logo" style={{ height: '30px' }} />
            <strong>RealDiag – Reference Cheat-Sheet</strong>
          </div>
          <div>
            <button type="button" onClick={() => window.print()}>
              Print / Save as PDF
            </button>
            <a href="/reference" style={{ marginLeft: 8 }}>
              Back to Reference
            </a>
          </div>
        </div>

        <h1 style={{ marginBottom: 4 }}>Diagnostic Rules & Codes</h1>
        <p className="small" style={{ marginBottom: 12 }}>
          Neurology, Cardiology, and Endocrinology. For best results, select{" "}
          <strong>Landscape</strong> when printing and use a larger paper size (e.g., A4 or US Letter).
        </p>

        {err && (
          <div
            style={{
              marginBottom: 12,
              padding: 8,
              borderRadius: 8,
              border: "1px solid #f0b5b5",
              background: "#ffe8e6",
              fontSize: 12,
            }}
          >
            {err}
          </div>
        )}

        {loading && !err && (
          <div style={{ marginBottom: 8, fontSize: 12 }}>Loading reference data…</div>
        )}

        {!loading && familiesWithData.length === 0 && !err && (
          <div style={{ marginTop: 12, fontSize: 12 }}>
            No reference rules available.
          </div>
        )}

        {!loading &&
          familiesWithData.map((f) => {
            const rows = grouped[f.label] || [];
            if (!rows.length) return null;

            return (
              <section className="page" key={f.id + "-page"}>
                <h2 className="family-title">{f.label}</h2>
                <p className="family-subtitle">
                  RealDiag rules and coding for {f.label.toLowerCase()} presentations.
                </p>

                <table>
                  <thead>
                    <tr>
                      <th style={{ width: "25%" }}>Diagnosis</th>
                      <th style={{ width: "35%" }}>Typical presentations</th>
                      <th style={{ width: "15%" }}>ICD-10</th>
                      <th style={{ width: "25%" }}>SNOMED / notes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((r) => (
                      <tr key={r.id}>
                        <td>
                          <div style={{ fontWeight: 600 }}>{r.label}</div>
                          <div className="small">{r.id}</div>
                        </td>
                        <td>
                          {r.presentations.length ? (
                            <ul className="presentations-list">
                              {r.presentations.map((p, i) => (
                                <li key={i}>{p}</li>
                              ))}
                            </ul>
                          ) : (
                            <span className="small">—</span>
                          )}
                        </td>
                        <td>
                          {r.icd10.length ? (
                            r.icd10.join(", ")
                          ) : (
                            <span className="small">—</span>
                          )}
                        </td>
                        <td>
                          {r.snomed.length ? (
                            <div className="small">
                              SNOMED: {r.snomed.join(", ")}
                            </div>
                          ) : (
                            <span className="small">SNOMED: not specified</span>
                          )}
                          {r.citations && r.citations.length > 0 && (
                            <div className="small" style={{ marginTop: 4 }}>
                              <strong>Refs:</strong>{" "}
                              {r.citations.length === 1
                                ? r.citations[0]
                                : r.citations
                                    .map((c, i) => `${i + 1}. ${c}`)
                                    .join("  ")}
                            </div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </section>
            );
          })}
      </body>
    </html>
  );
}
