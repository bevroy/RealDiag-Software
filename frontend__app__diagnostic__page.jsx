"use client";

import { useEffect, useMemo, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

const DEFAULT_TRIAGE_THRESHOLDS = {
	severe_htn_sbp: 180,
	severe_htn_dbp: 120,
	hypotension_sbp: 90,
	hypoxemia_o2: 92,
	tachycardia_hr: 130,
	tachypnea_resp: 30,
	high_fever_temp_c: 39.0,
};

const SYSTEM_PRESETS = {
	custom: DEFAULT_TRIAGE_THRESHOLDS,
	adult_ed_conservative: {
		...DEFAULT_TRIAGE_THRESHOLDS,
		hypoxemia_o2: 94,
		tachycardia_hr: 120,
		tachypnea_resp: 24,
	},
	adult_ed_standard: DEFAULT_TRIAGE_THRESHOLDS,
	peds_sensitive: {
		...DEFAULT_TRIAGE_THRESHOLDS,
		hypotension_sbp: 95,
		hypoxemia_o2: 94,
		tachycardia_hr: 140,
		tachypnea_resp: 34,
		high_fever_temp_c: 38.5,
	},
};

const splitCsv = (value) =>
	value
		.split(",")
		.map((part) => part.trim())
		.filter(Boolean);

const toNumberOrNull = (value) => {
	if (value === "" || value === null || value === undefined) {
		return null;
	}
	const n = Number(value);
	return Number.isFinite(n) ? n : null;
};

const userSettingsKey = (userId) => `realdiag.triageSettings.${(userId || "default").trim() || "default"}`;

export default function DiagnosticPage() {
	const [trees, setTrees] = useState([]);
	const [selectedTree, setSelectedTree] = useState("");
	const [loadingTrees, setLoadingTrees] = useState(true);
	const [submitting, setSubmitting] = useState(false);
	const [error, setError] = useState("");
	const [result, setResult] = useState(null);

	const [symptoms, setSymptoms] = useState("");
	const [exam, setExam] = useState("");
	const [redFlags, setRedFlags] = useState("");
	const [diagnosis, setDiagnosis] = useState("");
	const [age, setAge] = useState("");
	const [onsetHours, setOnsetHours] = useState("");

	const [bpSystolic, setBpSystolic] = useState("");
	const [bpDiastolic, setBpDiastolic] = useState("");
	const [heartRate, setHeartRate] = useState("");
	const [respRate, setRespRate] = useState("");
	const [o2Sat, setO2Sat] = useState("");
	const [temperature, setTemperature] = useState("");

	const [userId, setUserId] = useState("default");
	const [healthcareSystem, setHealthcareSystem] = useState("adult_ed_standard");
	const [thresholds, setThresholds] = useState(SYSTEM_PRESETS.adult_ed_standard);

	useEffect(() => {
		const loadTrees = async () => {
			setLoadingTrees(true);
			setError("");
			try {
				const response = await fetch(`${API_BASE}/diagnostic/trees`);
				if (!response.ok) {
					throw new Error(`Unable to fetch trees (${response.status})`);
				}
				const data = await response.json();
				const nextTrees = Array.isArray(data.trees) ? data.trees : [];
				setTrees(nextTrees);
				if (nextTrees.length > 0) {
					setSelectedTree(nextTrees[0].id);
				}
			} catch (e) {
				setError(e.message || "Failed to load diagnostic trees.");
			} finally {
				setLoadingTrees(false);
			}
		};

		loadTrees();
	}, []);

	useEffect(() => {
		const preset = SYSTEM_PRESETS[healthcareSystem] || SYSTEM_PRESETS.custom;
		setThresholds((current) => ({ ...preset, ...current }));
	}, [healthcareSystem]);

	useEffect(() => {
		const key = userSettingsKey(userId);
		try {
			const raw = window.localStorage.getItem(key);
			if (!raw) {
				return;
			}
			const parsed = JSON.parse(raw);
			if (!parsed || typeof parsed !== "object") {
				return;
			}
			if (typeof parsed.healthcareSystem === "string") {
				setHealthcareSystem(parsed.healthcareSystem);
			}
			if (parsed.thresholds && typeof parsed.thresholds === "object") {
				setThresholds((current) => ({ ...current, ...parsed.thresholds }));
			}
		} catch {
			// Ignore malformed local settings and continue with defaults.
		}
	}, [userId]);

	const saveUserSettings = () => {
		const key = userSettingsKey(userId);
		const payload = {
			healthcareSystem,
			thresholds,
		};
		window.localStorage.setItem(key, JSON.stringify(payload));
	};

	const resetThresholdsFromPreset = () => {
		const preset = SYSTEM_PRESETS[healthcareSystem] || SYSTEM_PRESETS.custom;
		setThresholds({ ...preset });
	};

	const payloadPreview = useMemo(() => {
		const vitals = {
			bp_systolic: toNumberOrNull(bpSystolic),
			bp_diastolic: toNumberOrNull(bpDiastolic),
			hr: toNumberOrNull(heartRate),
			resp: toNumberOrNull(respRate),
			o2: toNumberOrNull(o2Sat),
			temp_c: toNumberOrNull(temperature),
		};

		return {
			user_id: userId.trim() || "default",
			healthcare_system: healthcareSystem,
			triage_thresholds: {
				severe_htn_sbp: toNumberOrNull(thresholds.severe_htn_sbp),
				severe_htn_dbp: toNumberOrNull(thresholds.severe_htn_dbp),
				hypotension_sbp: toNumberOrNull(thresholds.hypotension_sbp),
				hypoxemia_o2: toNumberOrNull(thresholds.hypoxemia_o2),
				tachycardia_hr: toNumberOrNull(thresholds.tachycardia_hr),
				tachypnea_resp: toNumberOrNull(thresholds.tachypnea_resp),
				high_fever_temp_c: toNumberOrNull(thresholds.high_fever_temp_c),
			},
			diagnosis: diagnosis.trim() || undefined,
			symptoms: splitCsv(symptoms),
			exam: splitCsv(exam),
			red_flags: splitCsv(redFlags),
			age: toNumberOrNull(age),
			onset_hours: toNumberOrNull(onsetHours),
			vitals,
			// Also expose convenience top-level fields for simpler rule authoring.
			sbp: vitals.bp_systolic,
			dbp: vitals.bp_diastolic,
			hr: vitals.hr,
			resp: vitals.resp,
			o2: vitals.o2,
			temp_c: vitals.temp_c,
		};
	}, [
		age,
		bpDiastolic,
		bpSystolic,
		diagnosis,
		exam,
		healthcareSystem,
		heartRate,
		o2Sat,
		onsetHours,
		redFlags,
		respRate,
		symptoms,
		thresholds,
		temperature,
		userId,
	]);

	const onSubmit = async (event) => {
		event.preventDefault();
		if (!selectedTree) {
			setError("Please select a diagnostic tree.");
			return;
		}

		setSubmitting(true);
		setError("");
		setResult(null);

		try {
			const response = await fetch(
				`${API_BASE}/diagnostic/evaluate/${encodeURIComponent(selectedTree)}`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify(payloadPreview),
				}
			);

			if (!response.ok) {
				throw new Error(`Evaluation failed (${response.status})`);
			}

			const data = await response.json();
			setResult(data.tree_result || null);
		} catch (e) {
			setError(e.message || "Unable to evaluate diagnostic tree.");
		} finally {
			setSubmitting(false);
		}
	};

	return (
		<main style={{ maxWidth: 980, margin: "0 auto", padding: 24, fontFamily: "sans-serif" }}>
			<h1 style={{ marginBottom: 8 }}>Symptom Search</h1>
			<p style={{ marginTop: 0, color: "#555" }}>
				Enter symptoms and optional clinical details to evaluate a diagnostic tree.
			</p>

			<form onSubmit={onSubmit}>
				<fieldset disabled={submitting || loadingTrees} style={{ border: "1px solid #ddd", padding: 16 }}>
					<legend>Patient Inputs</legend>

					<fieldset style={{ border: "1px solid #ddd", marginBottom: 12, padding: 12 }}>
						<legend>User / Health System</legend>
						<div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12 }}>
							<label>
								User ID
								<input
									type="text"
									value={userId}
									onChange={(e) => setUserId(e.target.value)}
									placeholder="clinician-123"
									style={{ width: "100%", marginTop: 6, padding: 8 }}
								/>
							</label>
							<label>
								Healthcare System Preset
								<select
									value={healthcareSystem}
									onChange={(e) => setHealthcareSystem(e.target.value)}
									style={{ width: "100%", marginTop: 6, padding: 8 }}
								>
									<option value="adult_ed_standard">Adult ED Standard</option>
									<option value="adult_ed_conservative">Adult ED Conservative</option>
									<option value="peds_sensitive">Peds Sensitive</option>
									<option value="custom">Custom</option>
								</select>
							</label>
						</div>
					</fieldset>

					<label style={{ display: "block", marginBottom: 12 }}>
						Diagnostic Tree
						<select
							value={selectedTree}
							onChange={(e) => setSelectedTree(e.target.value)}
							style={{ width: "100%", marginTop: 6, padding: 8 }}
						>
							{trees.map((tree) => (
								<option key={tree.id} value={tree.id}>
									{tree.title ? `${tree.title} (${tree.id})` : tree.id}
								</option>
							))}
						</select>
					</label>

					<label style={{ display: "block", marginBottom: 12 }}>
						Symptoms (comma-separated)
						<input
							type="text"
							value={symptoms}
							onChange={(e) => setSymptoms(e.target.value)}
							placeholder="headache, dizziness, nausea"
							style={{ width: "100%", marginTop: 6, padding: 8 }}
						/>
					</label>

					<label style={{ display: "block", marginBottom: 12 }}>
						Exam Flags (comma-separated)
						<input
							type="text"
							value={exam}
							onChange={(e) => setExam(e.target.value)}
							placeholder="papilledema, nystagmus"
							style={{ width: "100%", marginTop: 6, padding: 8 }}
						/>
					</label>

					<label style={{ display: "block", marginBottom: 12 }}>
						Red Flags (comma-separated)
						<input
							type="text"
							value={redFlags}
							onChange={(e) => setRedFlags(e.target.value)}
							placeholder="worst headache of life, severe gait ataxia"
							style={{ width: "100%", marginTop: 6, padding: 8 }}
						/>
					</label>

					<div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12 }}>
						<label>
							Age
							<input
								type="number"
								value={age}
								onChange={(e) => setAge(e.target.value)}
								min="0"
								style={{ width: "100%", marginTop: 6, padding: 8 }}
							/>
						</label>
						<label>
							Onset Hours
							<input
								type="number"
								value={onsetHours}
								onChange={(e) => setOnsetHours(e.target.value)}
								min="0"
								step="0.1"
								style={{ width: "100%", marginTop: 6, padding: 8 }}
							/>
						</label>
						<label style={{ gridColumn: "1 / -1" }}>
							Free-text Diagnosis Context
							<input
								type="text"
								value={diagnosis}
								onChange={(e) => setDiagnosis(e.target.value)}
								placeholder="migraine pattern, central vertigo concern"
								style={{ width: "100%", marginTop: 6, padding: 8 }}
							/>
						</label>
					</div>

					<fieldset style={{ border: "1px solid #ddd", marginTop: 16, padding: 12 }}>
						<legend>Vital Signs (Optional)</legend>
						<div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 12 }}>
							<label>
								BP Systolic
								<input
									type="number"
									value={bpSystolic}
									onChange={(e) => setBpSystolic(e.target.value)}
									min="0"
									placeholder="120"
									style={{ width: "100%", marginTop: 6, padding: 8 }}
								/>
							</label>
							<label>
								BP Diastolic
								<input
									type="number"
									value={bpDiastolic}
									onChange={(e) => setBpDiastolic(e.target.value)}
									min="0"
									placeholder="80"
									style={{ width: "100%", marginTop: 6, padding: 8 }}
								/>
							</label>
							<label>
								HR (bpm)
								<input
									type="number"
									value={heartRate}
									onChange={(e) => setHeartRate(e.target.value)}
									min="0"
									placeholder="72"
									style={{ width: "100%", marginTop: 6, padding: 8 }}
								/>
							</label>
							<label>
								Respiratory Rate
								<input
									type="number"
									value={respRate}
									onChange={(e) => setRespRate(e.target.value)}
									min="0"
									placeholder="16"
									style={{ width: "100%", marginTop: 6, padding: 8 }}
								/>
							</label>
							<label>
								O2 Sat (%)
								<input
									type="number"
									value={o2Sat}
									onChange={(e) => setO2Sat(e.target.value)}
									min="0"
									max="100"
									placeholder="98"
									style={{ width: "100%", marginTop: 6, padding: 8 }}
								/>
							</label>
							<label>
								Temperature (C)
								<input
									type="number"
									value={temperature}
									onChange={(e) => setTemperature(e.target.value)}
									min="20"
									max="45"
									step="0.1"
									placeholder="37.0"
									style={{ width: "100%", marginTop: 6, padding: 8 }}
								/>
							</label>
						</div>
					</fieldset>

					<fieldset style={{ border: "1px solid #ddd", marginTop: 16, padding: 12 }}>
						<legend>Triage Threshold Settings</legend>
						<p style={{ marginTop: 0, color: "#555" }}>
							These thresholds are user-specific and can be tuned per healthcare system.
						</p>
						<div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12 }}>
							<label>
								Severe HTN SBP >=
								<input
									type="number"
									value={thresholds.severe_htn_sbp ?? ""}
									onChange={(e) => setThresholds((prev) => ({ ...prev, severe_htn_sbp: e.target.value }))}
									style={{ width: "100%", marginTop: 6, padding: 8 }}
								/>
							</label>
							<label>
								Severe HTN DBP >=
								<input
									type="number"
									value={thresholds.severe_htn_dbp ?? ""}
									onChange={(e) => setThresholds((prev) => ({ ...prev, severe_htn_dbp: e.target.value }))}
									style={{ width: "100%", marginTop: 6, padding: 8 }}
								/>
							</label>
							<label>
								Hypotension SBP <=
								<input
									type="number"
									value={thresholds.hypotension_sbp ?? ""}
									onChange={(e) => setThresholds((prev) => ({ ...prev, hypotension_sbp: e.target.value }))}
									style={{ width: "100%", marginTop: 6, padding: 8 }}
								/>
							</label>
							<label>
								Hypoxemia O2 <=
								<input
									type="number"
									value={thresholds.hypoxemia_o2 ?? ""}
									onChange={(e) => setThresholds((prev) => ({ ...prev, hypoxemia_o2: e.target.value }))}
									style={{ width: "100%", marginTop: 6, padding: 8 }}
								/>
							</label>
							<label>
								Tachycardia HR >=
								<input
									type="number"
									value={thresholds.tachycardia_hr ?? ""}
									onChange={(e) => setThresholds((prev) => ({ ...prev, tachycardia_hr: e.target.value }))}
									style={{ width: "100%", marginTop: 6, padding: 8 }}
								/>
							</label>
							<label>
								Tachypnea Resp >=
								<input
									type="number"
									value={thresholds.tachypnea_resp ?? ""}
									onChange={(e) => setThresholds((prev) => ({ ...prev, tachypnea_resp: e.target.value }))}
									style={{ width: "100%", marginTop: 6, padding: 8 }}
								/>
							</label>
							<label>
								High Fever Temp C >=
								<input
									type="number"
									step="0.1"
									value={thresholds.high_fever_temp_c ?? ""}
									onChange={(e) => setThresholds((prev) => ({ ...prev, high_fever_temp_c: e.target.value }))}
									style={{ width: "100%", marginTop: 6, padding: 8 }}
								/>
							</label>
						</div>
						<div style={{ display: "flex", gap: 8, marginTop: 12 }}>
							<button type="button" onClick={saveUserSettings} style={{ padding: "8px 12px" }}>
								Save User Settings
							</button>
							<button type="button" onClick={resetThresholdsFromPreset} style={{ padding: "8px 12px" }}>
								Reset From Preset
							</button>
						</div>
					</fieldset>

					<button type="submit" style={{ marginTop: 16, padding: "10px 14px" }}>
						{submitting ? "Evaluating..." : "Run Symptom Search"}
					</button>
				</fieldset>
			</form>

			{error && (
				<p style={{ marginTop: 16, color: "#b42318" }}>
					{error}
				</p>
			)}

			{result && (
				<section style={{ marginTop: 20, border: "1px solid #ddd", padding: 16 }}>
					<h2 style={{ marginTop: 0 }}>Diagnostic Result</h2>
					<p>
						<strong>Tree:</strong> {result?.tree?.title || result?.tree?.id}
					</p>
					<p>
						<strong>Path:</strong> {(result.path || []).join(" -> ") || "N/A"}
					</p>
					<p>
						<strong>Provisional Dx:</strong> {(result.provisional_dx || []).join(", ") || "None"}
					</p>
					<p>
						<strong>Suggested Tests:</strong> {(result.tests || []).join(", ") || "None"}
					</p>
					<details>
						<summary>Trace</summary>
						<pre style={{ whiteSpace: "pre-wrap" }}>{(result.trace || []).join("\n") || "No trace output"}</pre>
					</details>
				</section>
			)}
		</main>
	);
}
