"use client";

import { useMemo, useState } from "react";
import type {
  AnalyzeRequest,
  AnalyzeResponse,
  DifferentialDiagnosis,
} from "../lib/types";
import { analyzeDiagnosticCase } from "../lib/api";

const initialForm: AnalyzeRequest = {
  patient_age: 57,
  patient_sex: "Female",
  symptoms: ["Chest pain", "Exertional dyspnea", "Nausea"],
  history: ["Hypertension", "Hyperlipidemia", "Tobacco exposure"],
  include_variations: true,
  codes: {
    icd10: [],
    snomed: [],
    cpt: [],
  },
};

const fallbackResponse: AnalyzeResponse = {
  differential: [
    {
      name: "Acute coronary syndrome",
      confidence: 82,
      summary:
        "Supported by exertional chest pain, dyspnea, nausea, and cardiac risk factors.",
    },
    {
      name: "Stable ischemic heart disease",
      confidence: 65,
      summary:
        "Alternative explanation with symptom overlap that still requires targeted workup.",
    },
    {
      name: "Pulmonary embolic process",
      confidence: 41,
      summary:
        "Lower-ranked possibility to evaluate if symptom pattern or risk profile changes.",
    },
  ],
  workup: [
    "Obtain ECG and serial troponins.",
    "Order CBC, CMP, and targeted cardiac risk labs.",
    "Escalate imaging if instability or persistent concern emerges.",
  ],
  referral: [
    "Cardiology evaluation if acute findings or high-risk profile is present.",
    "Urgency: same day if active ischemic concern exists.",
    "Rationale: symptom cluster and coded history elevate risk.",
  ],
  codes: {
    icd10: ["I20.9", "R07.9"],
    snomed: ["29857009", "53741008"],
    cpt: ["93000", "71045"],
  },
  rationale:
    "Leading pathway is supported by symptom timing, exertional pattern, and mapped synonym expansion.",
};

export default function RealDiagWorkspace() {
  const [form, setForm] = useState<AnalyzeRequest>(initialForm);
  const [results, setResults] = useState<AnalyzeResponse>(fallbackResponse);
  const [activeTab, setActiveTab] = useState<"Differential" | "Workup" | "Referral" | "Codes">(
    "Differential"
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const activeInputChips = useMemo(() => {
    return [
      ...form.symptoms,
      ...form.history,
      ...(form.include_variations ? ["Synonym expansion on"] : []),
    ].slice(0, 8);
  }, [form]);

  async function handleSubmit() {
    setIsLoading(true);
    setError(null);
    try {
      const data = await analyzeDiagnosticCase(form);
      setResults(data);
    } catch (err) {
      console.error(err);
      setError("Live backend unavailable. Showing a local demonstration response.");
      setResults(fallbackResponse);
    } finally {
      setIsLoading(false);
    }
  }

  function updateListField(field: "symptoms" | "history", rawValue: string) {
    setForm((prev) => ({
      ...prev,
      [field]: rawValue
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
    }));
  }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.22em] text-teal-800">
              RealDiag
            </div>
            <h1 className="text-2xl font-semibold tracking-tight">
              Diagnostic Workspace
            </h1>
          </div>
          <div className="flex items-center gap-3 text-sm text-slate-600">
            <span className="rounded-md border border-slate-300 bg-slate-50 px-3 py-1.5">
              Clinical Demo
            </span>
            <span className="rounded-md bg-teal-800 px-3 py-1.5 font-medium text-white">
              Enterprise Ready
            </span>
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-6 py-6 xl:grid-cols-[320px_minmax(0,1fr)_320px]">
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-5">
            <h2 className="text-lg font-semibold text-slate-900">Patient Context</h2>
            <p className="mt-1 text-sm text-slate-600">
              Structured input for symptoms, history, and code-aware filtering.
            </p>
          </div>

          <div className="space-y-4">
            <EditableField
              label="Age"
              value={String(form.patient_age)}
              onChange={(value) =>
                setForm((prev) => ({ ...prev, patient_age: Number(value) || 0 }))
              }
            />
            <EditableField
              label="Sex"
              value={form.patient_sex}
              onChange={(value) => setForm((prev) => ({ ...prev, patient_sex: value }))}
            />
            <EditableField
              label="Presenting symptoms"
              value={form.symptoms.join(", ")}
              onChange={(value) => updateListField("symptoms", value)}
              multiline
            />
            <EditableField
              label="Relevant history"
              value={form.history.join(", ")}
              onChange={(value) => updateListField("history", value)}
              multiline
            />
          </div>

          <button
            type="button"
            className="mt-5 flex w-full items-start justify-between rounded-xl border border-slate-200 bg-slate-50 p-4 text-left"
            onClick={() =>
              setForm((prev) => ({
                ...prev,
                include_variations: !prev.include_variations,
              }))
            }
          >
            <div>
              <div className="text-sm font-medium text-slate-900">
                Include known clinical variations
              </div>
              <div className="mt-1 text-sm text-slate-600">
                Maps common synonyms and coding variants such as MI and myocardial
                infarction.
              </div>
            </div>
            <div
              className={`mt-1 h-6 w-11 rounded-full p-1 ${
                form.include_variations ? "bg-teal-800" : "bg-slate-300"
              }`}
            >
              <div
                className={`h-4 w-4 rounded-full bg-white transition ${
                  form.include_variations ? "ml-auto" : "ml-0"
                }`}
              />
            </div>
          </button>

          <div className="mt-5">
            <div className="mb-2 text-sm font-medium text-slate-900">Active inputs</div>
            <div className="flex flex-wrap gap-2">
              {activeInputChips.map((chip) => (
                <span
                  key={chip}
                  className="rounded-md border border-slate-300 bg-white px-2.5 py-1 text-xs font-medium text-slate-700"
                >
                  {chip}
                </span>
              ))}
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={isLoading}
            className="mt-6 w-full rounded-md bg-teal-800 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isLoading ? "Running analysis..." : "Run Diagnostic Analysis"}
          </button>

          {error ? <p className="mt-3 text-sm text-amber-700">{error}</p> : null}
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-col gap-4 border-b border-slate-200 pb-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-800">
                Real-Time Output
              </div>
              <h2 className="mt-1 text-xl font-semibold tracking-tight">
                Diagnostic Pathway Analysis
              </h2>
              <p className="mt-1 text-sm text-slate-600">
                Prioritized differential diagnoses, workup guidance, referral logic,
                and coded outputs.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 text-sm">
              {(["Differential", "Workup", "Referral", "Codes"] as const).map((tab) => (
                <button
                  key={tab}
                  className={`rounded-md px-3 py-2 font-medium ${
                    activeTab === tab
                      ? "bg-slate-900 text-white"
                      : "border border-slate-300 bg-white text-slate-700"
                  }`}
                  onClick={() => setActiveTab(tab)}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-5">
            {activeTab === "Differential" ? (
              <div className="grid gap-4">
                {results.differential.map((dx, idx) => (
                  <DifferentialCard key={`${dx.name}-${idx}`} diagnosis={dx} rank={idx + 1} />
                ))}
              </div>
            ) : null}

            {activeTab === "Workup" ? (
              <InfoCard title="Recommended workup" items={results.workup} />
            ) : null}

            {activeTab === "Referral" ? (
              <InfoCard title="Referral recommendation" items={results.referral} />
            ) : null}

            {activeTab === "Codes" ? (
              <div className="grid gap-4 lg:grid-cols-3">
                <InfoCard title="ICD-10" items={results.codes.icd10} />
                <InfoCard title="SNOMED" items={results.codes.snomed} />
                <InfoCard title="CPT" items={results.codes.cpt} />
              </div>
            ) : null}
          </div>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Clinical Context</h2>
          <p className="mt-1 text-sm text-slate-600">
            Keep logic concise and reviewable for clinician trust.
          </p>

          <div className="mt-5 space-y-4">
            <AsideBlock title="Rationale" body={results.rationale} />
            <AsideBlock
              title="Coding output"
              body="ICD-10, CPT, and SNOMED mappings can be surfaced per diagnosis or bundled into the final export layer."
            />
            <AsideBlock
              title="Implementation note"
              body="This component is wired for a POST request to your backend and can be extended with organization-specific rules, citations, or guideline logic."
            />
          </div>
        </section>
      </main>
    </div>
  );
}

function EditableField({
  label,
  value,
  onChange,
  multiline = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  multiline?: boolean;
}) {
  return (
    <div>
      <label className="mb-1.5 block text-sm font-medium text-slate-800">{label}</label>
      {multiline ? (
        <textarea
          value={value}
          onChange={(event) => onChange(event.target.value)}
          className="min-h-[92px] w-full rounded-xl border border-slate-300 bg-white px-3 py-3 text-sm text-slate-700 outline-none ring-0"
        />
      ) : (
        <input
          value={value}
          onChange={(event) => onChange(event.target.value)}
          className="w-full rounded-xl border border-slate-300 bg-white px-3 py-3 text-sm text-slate-700 outline-none ring-0"
        />
      )}
    </div>
  );
}

function DifferentialCard({
  diagnosis,
  rank,
}: {
  diagnosis: DifferentialDiagnosis;
  rank: number;
}) {
  return (
    <article className="rounded-xl border border-slate-200 p-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
            Rank {rank}
          </div>
          <h3 className="mt-1 text-lg font-semibold text-slate-900">{diagnosis.name}</h3>
          <p className="mt-1 text-sm leading-6 text-slate-600">{diagnosis.summary}</p>
        </div>
        <div className="min-w-[120px] rounded-xl bg-slate-50 px-4 py-3 text-center">
          <div className="text-xs uppercase tracking-[0.16em] text-slate-500">
            Confidence
          </div>
          <div className="mt-1 text-2xl font-semibold text-teal-800">
            {diagnosis.confidence}%
          </div>
        </div>
      </div>
    </article>
  );
}

function InfoCard({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <h3 className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-700">
        {title}
      </h3>
      <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-700">
        {items.map((item) => (
          <li key={item} className="flex gap-2">
            <span className="mt-2 h-1.5 w-1.5 rounded-full bg-teal-800" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function AsideBlock({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-xl border border-slate-200 p-4">
      <div className="text-sm font-semibold text-slate-900">{title}</div>
      <p className="mt-2 text-sm leading-6 text-slate-600">{body}</p>
    </div>
  );
}
