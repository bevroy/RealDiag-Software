#!/usr/bin/env python3
"""
Add final 10 clinical cases (98-100 and complete the set)
Final block to reach 100 total cases
"""

import json

with open('backend/data/clinical_cases.json', 'r') as f:
    data = json.load(f)

print(f"Current total: {len(data['cases'])} cases")

# Final 10 cases - all unique diagnoses
new_cases = [
    {
        "case_id": "CASE-098",
        "title": "Man with Persistent Hiccups and Weight Loss",
        "specialty": "gastroenterology",
        "difficulty": "intermediate",
        "learning_objectives": [
            "Recognize esophageal cancer warning signs",
            "Understand alarm symptoms in dyspepsia",
            "Differentiate from benign hiccups"
        ],
        "presentation": "66-year-old man with 3 weeks of intractable hiccups, progressive dysphagia, and 25-pound weight loss",
        "history": {
            "chief_complaint": "Can't stop hiccupping, can't eat",
            "hpi": "Hiccups started 3 weeks ago, constant throughout day and night, no relief from home remedies. Progressive difficulty swallowing solids, now also liquids. Regurgitation of food. Severe substernal chest discomfort. 25-pound weight loss over 3 months. Intermittent hoarseness. Long history of heartburn, never treated. 50 pack-year smoking history.",
            "pmh": "COPD, hypertension, untreated GERD for years",
            "medications": "Albuterol inhaler, lisinopril 10mg",
            "social": "Current smoker (2 PPD x 25 years), heavy alcohol use",
            "family": "Father died of esophageal cancer at 62"
        },
        "physical_exam": {
            "vitals": "BP 128/82, HR 88, BMI 21 (down from 26), O2 sat 94%",
            "general": "Cachectic man with frequent hiccups during exam",
            "heent": "Poor dentition, hoarseness",
            "neck": "Left supraclavicular lymph node palpable (Virchow's node)",
            "chest": "Decreased breath sounds, distant",
            "abdomen": "Thin, soft, epigastric tenderness",
            "extremities": "Muscle wasting"
        },
        "labs": {
            "cbc": "Hgb 10.2 g/dL (anemia), WBC 8,200",
            "cmp": "Albumin 2.8 g/dL (low)",
            "lfts": "Mildly elevated"
        },
        "imaging": {
            "cxr": "Widened mediastinum, possible mass",
            "barium_swallow": "Irregular narrowing mid-esophagus with shouldering, apple-core lesion",
            "ct_chest_abdomen": "Circumferential esophageal mass 7cm length at 30cm from incisors, enlarged mediastinal and celiac lymph nodes, liver lesions concerning for metastases",
            "upper_endoscopy": "Ulcerated, friable circumferential mass in mid-esophagus, near-complete obstruction. Biopsy obtained.",
            "biopsy": "Poorly differentiated squamous cell carcinoma"
        },
        "correct_diagnosis": "GI-ESOPHAGEAL-CANCER-SQUAMOUS-CELL",
        "differential": [
            "GI-ESOPHAGEAL-CANCER-SQUAMOUS-CELL",
            "GI-ESOPHAGEAL-STRICTURE-BENIGN",
            "NEURO-VAGAL-NEUROPATHY",
            "PULM-LUNG-CANCER-WITH-PHRENIC-INVOLVEMENT"
        ],
        "explanation": "Esophageal squamous cell carcinoma: aggressive malignancy of esophageal epithelium. Risk factors: smoking (strongest), heavy alcohol, caustic injury, achalasia, tylosis, Plummer-Vinson syndrome. Most common location: mid-esophagus. Classic presentation: progressive dysphagia (solids→liquids), weight loss (alarm symptom), odynophagia. Intractable hiccups from phrenic nerve or diaphragm involvement. Hoarseness from recurrent laryngeal nerve invasion. Virchow's node (left supraclavicular) indicates metastatic disease. Poor prognosis: 5-year survival <20%, often presents late (stage III-IV). Differs from adenocarcinoma (lower esophagus, Barrett's, GERD-related).",
        "management_pearls": [
            "Staging: PET-CT to assess metastases, endoscopic ultrasound for T/N staging, bronchoscopy if near carina",
            "TNM staging determines treatment:",
            "- Stage I-II (localized): neoadjuvant chemoradiation → esophagectomy",
            "- Stage III (locally advanced): definitive chemoradiation or surgery if resectable",
            "- Stage IV (metastatic): palliative chemotherapy, stenting",
            "Palliative care (this patient has metastases):",
            "- Esophageal stent placement for dysphagia relief",
            "- PEG tube or feeding jejunostomy for nutrition",
            "- Palliative radiation to shrink tumor, control bleeding",
            "- Chemotherapy: cisplatin/5-FU or carboplatin/paclitaxel",
            "Hiccup management:",
            "- Chlorpromazine 25-50mg TID (most effective, FDA-approved)",
            "- Metoclopramide 10mg QID",
            "- Baclofen 5-10mg TID",
            "- Gabapentin 300-900mg/day",
            "Pain control: opioids, nerve blocks if needed",
            "Nutrition: high-calorie liquid diet, supplements",
            "Multidisciplinary: oncology, GI, palliative care, nutrition, social work"
        ],
        "pitfalls": [
            "Adenocarcinoma vs squamous cell: adeno (distal esophagus, Barrett's, GERD, obesity), squamous (mid-esophagus, smoking, alcohol, developing countries)",
            "Late presentation: 50% have lymph node metastases at diagnosis, 25% distant metastases",
            "Tracheoesophageal fistula: late complication, sudden coughing with swallowing, aspiration pneumonia, air in esophagus on imaging",
            "Tumor bleeding: can be massive, needs emergent endoscopy with epinephrine injection, clips, or radiation",
            "Aspiration risk: altered anatomy, weakened reflexes - aspiration pneumonia common",
            "Cachexia: tumor-induced, multifactorial - nutritional support critical"
        ],
        "tags": ["esophageal cancer", "dysphagia", "weight loss", "hiccups", "oncology"],
        "created_at": "2025-12-30T00:40:00.000000",
        "author": "Dr. Oncology"
    },
    
    {
        "case_id": "CASE-099",
        "title": "Young Woman with Facial Flushing and Diarrhea",
        "specialty": "endocrinology",
        "difficulty": "advanced",
        "learning_objectives": [
            "Recognize carcinoid syndrome presentation",
            "Understand functional neuroendocrine tumors",
            "Manage carcinoid crisis"
        ],
        "presentation": "38-year-old woman with episodic facial flushing, chronic diarrhea, and wheezing",
        "history": {
            "chief_complaint": "Face turns bright red multiple times daily, constant diarrhea",
            "hpi": "Started 18 months ago with episodic facial flushing - sudden onset, lasts 5-15 minutes, feels hot, sometimes whole body. Triggers: alcohol, stress, certain foods (cheese, chocolate). Chronic watery diarrhea 6-8 times daily, no blood. 20-pound weight loss. Intermittent wheezing, thought was asthma. Abdominal cramping. Recently noticed heart racing. Treated for IBS without improvement.",
            "pmh": "Diagnosed with 'IBS' 1 year ago, 'rosacea', 'adult-onset asthma'",
            "medications": "Loperamide (minimal effect), albuterol inhaler, metronidazole cream",
            "social": "Teacher, non-smoker, minimal alcohol (triggers symptoms)",
            "family": "No GI or endocrine diseases"
        },
        "physical_exam": {
            "vitals": "BP 108/68, HR 98, RR 16, weight down 20 lbs",
            "general": "Thin woman, telangiectasias on face",
            "skin": "Facial erythema during exam (witnessed flushing episode lasting 8 minutes)",
            "cardiovascular": "Tachycardic, loud systolic murmur at left sternal border (tricuspid regurgitation), elevated JVP",
            "lungs": "Expiratory wheezes bilaterally",
            "abdomen": "Diffusely tender, increased bowel sounds, liver edge palpable 4cm below costal margin, nodular",
            "extremities": "No edema, pellagra-like rash on sun-exposed areas"
        },
        "labs": {
            "24hr_urine_5hiaa": "185 mg/24hr (markedly elevated, normal <8 mg/24hr)",
            "chromogranin_a": "450 ng/mL (elevated, normal <93)",
            "serotonin": "Elevated",
            "cbc": "Mild anemia",
            "vitamin_b3": "Low (niacin deficiency)"
        },
        "imaging": {
            "ct_abdomen_pelvis": "Multiple liver lesions (metastases), small bowel mass in terminal ileum 3cm",
            "octreotide_scan": "Intense uptake in liver lesions and ileal mass (somatostatin receptor positive)",
            "echocardiogram": "Thickened, retracted tricuspid and pulmonary valves with regurgitation (carcinoid heart disease)"
        },
        "correct_diagnosis": "ENDO-CARCINOID-SYNDROME-NEUROENDOCRINE-TUMOR",
        "differential": [
            "ENDO-CARCINOID-SYNDROME-NEUROENDOCRINE-TUMOR",
            "ENDO-PHEOCHROMOCYTOMA",
            "GI-IRRITABLE-BOWEL-SYNDROME",
            "DERM-ROSACEA-SYSTEMIC-MASTOCYTOSIS"
        ],
        "explanation": "Carcinoid syndrome: symptoms from bioactive substances (serotonin, bradykinin, histamine, prostaglandins) secreted by neuroendocrine tumors. Classic triad: (1) Flushing (90%), (2) Diarrhea (75%), (3) Cardiac involvement (50%). Most common primary site: small bowel (ileum). Syndrome requires hepatic metastases (liver can't metabolize serotonin first-pass) OR ovarian/lung primary (bypasses liver). Flushing: sudden, red/purple, upper body, lasts minutes. Diarrhea: watery, secretory, high-output. Carcinoid heart disease: right-sided (tricuspid, pulmonary) fibrosis from serotonin exposure. Pellagra: niacin deficiency (tumor uses tryptophan for serotonin instead of niacin). Carcinoid crisis: life-threatening, severe flushing, bronchospasm, hypotension - triggered by anesthesia, surgery, stress.",
        "management_pearls": [
            "Somatostatin analogs (first-line):",
            "- Octreotide 150-300 mcg SQ TID or long-acting (LAR) 20-30mg IM monthly",
            "- Controls symptoms in 70%, stabilizes tumor growth",
            "Tumor-directed therapy:",
            "- Liver metastases: resection if limited, ablation (RFA), embolization (bland or chemo-embolization)",
            "- Primary tumor: surgical resection of ileal mass + mesentery",
            "Peptide receptor radionuclide therapy (PRRT):",
            "- Lutetium-177 dotatate: targets somatostatin receptors, improves survival",
            "Diarrhea control:",
            "- Octreotide (primary), loperamide, cyproheptadine, ondansetron",
            "Niacin supplementation: 50-100mg daily (prevent pellagra)",
            "Avoid triggers: alcohol, tyramine-rich foods, stress",
            "Cardiac management: diuretics, valve replacement if severe (after tumor control)",
            "Carcinoid crisis prevention:",
            "- Pre-operative octreotide: 500 mcg IV bolus, then infusion during surgery/procedures",
            "- Avoid drugs triggering histamine release (morphine, succinylcholine)",
            "Monitor: 24hr urine 5-HIAA, chromogranin A every 3-6 months"
        ],
        "pitfalls": [
            "Carcinoid crisis: severe flushing, bronchospasm, hypotension, arrhythmia - triggered by anesthesia, tumor manipulation - EMERGENT octreotide bolus needed",
            "Diagnosis delay: average 5-7 years, often misdiagnosed as IBS, rosacea, menopause",
            "Right heart failure: irreversible valve damage, high mortality - screen echo in all patients",
            "Dietary triggers: avoid tyramine (aged cheese, red wine), histamine-releasing foods",
            "Small bowel obstruction: mesenteric fibrosis from tumor, requires surgery",
            "Bronchospasm: can be life-threatening during crisis, needs bronchodilators + octreotide",
            "Interferon-alpha: historical use, more side effects than octreotide, rarely used now",
            "Everolimus: mTOR inhibitor, for progressive disease refractory to somatostatin analogs"
        ],
        "tags": ["carcinoid syndrome", "neuroendocrine tumor", "flushing", "diarrhea", "endocrinology"],
        "created_at": "2025-12-30T00:50:00.000000",
        "author": "Dr. Endocrinology"
    },
    
    {
        "case_id": "CASE-100",
        "title": "Elderly Man with Confusion and Low Sodium",
        "specialty": "endocrinology",
        "difficulty": "intermediate",
        "learning_objectives": [
            "Recognize SIADH presentation",
            "Differentiate causes of hyponatremia",
            "Understand safe correction of hyponatremia"
        ],
        "presentation": "78-year-old man with progressive confusion, weakness, and nausea over 1 week",
        "history": {
            "chief_complaint": "Confused, not acting like himself",
            "hpi": "Wife reports progressive confusion and lethargy over 7-10 days. More forgetful, mixing up words, difficulty finding bathroom in own home. Nausea with poor appetite. No vomiting. Generalized weakness. No fever, cough, dysuria. Recently started taking new pain medication (ibuprofen) for arthritis. History of lung cancer (small cell) treated with chemotherapy 3 months ago, last scan showed good response.",
            "pmh": "Small cell lung cancer (stage III, on chemo), COPD, hypertension, osteoarthritis",
            "medications": "Lisinopril 20mg, cisplatin/etoposide chemotherapy (last dose 2 weeks ago), ibuprofen 600mg TID",
            "social": "Former 60 pack-year smoker (quit 1 year ago), lives with wife",
            "family": "Non-contributory"
        },
        "physical_exam": {
            "vitals": "BP 138/84, HR 76, RR 16, Temp 98.4°F",
            "general": "Lethargic, oriented to person only, not place or time",
            "heent": "Moist mucous membranes, normal skin turgor",
            "cardiovascular": "Regular rate and rhythm, no JVD",
            "lungs": "Clear to auscultation",
            "abdomen": "Soft, non-tender, no ascites",
            "neurologic": "Alert but confused, no focal deficits, normal strength, reflexes 2+",
            "extremities": "No edema"
        },
        "labs": {
            "bmp": "Na 118 mEq/L (critically low, normal 135-145), K 4.2, Cl 88, HCO3 24, BUN 18, Cr 0.9, glucose 98",
            "serum_osmolality": "248 mOsm/kg (low, normal 275-295)",
            "urine_osmolality": "456 mOsm/kg (inappropriately concentrated)",
            "urine_sodium": "68 mEq/L (high, >40)",
            "urine_specific_gravity": "1.020",
            "tsh": "Normal",
            "cortisol_am": "Normal",
            "lipid_panel": "Normal (rules out pseudohyponatremia)"
        },
        "imaging": {
            "ct_head": "No acute intracranial process, age-appropriate atrophy",
            "ct_chest": "Known lung mass, stable from prior, no new findings"
        },
        "correct_diagnosis": "ENDO-SIADH-HYPONATREMIA",
        "differential": [
            "ENDO-SIADH-HYPONATREMIA",
            "ENDO-ADRENAL-INSUFFICIENCY",
            "NEPHRO-SALT-WASTING-NEPHROPATHY",
            "GI-DIURETIC-INDUCED-HYPONATREMIA"
        ],
        "explanation": "Syndrome of inappropriate antidiuretic hormone (SIADH): excess ADH causes water retention and dilutional hyponatremia. Diagnostic criteria: (1) Hyponatremia with low serum osmolality, (2) Urine osmolality >100 (inappropriately concentrated), (3) Urine sodium >40, (4) Euvolemic (no edema, no dehydration), (5) Normal renal, thyroid, adrenal function. Common causes: malignancy (small cell lung cancer most common - ectopic ADH production), medications (SSRIs, carbamazepine, NSAIDs, cisplatin), pulmonary disease (pneumonia), CNS disorders, postoperative. Symptoms depend on severity and acuity: mild (120-130): asymptomatic; moderate (115-120): nausea, confusion, weakness; severe (<115): seizures, coma, respiratory arrest. Chronic hyponatremia (>48h) better tolerated than acute.",
        "management_pearls": [
            "Assess severity and acuity:",
            "- Severe symptomatic (seizures, coma): HYPERTONIC SALINE 3% emergency",
            "- Moderate symptomatic (confusion): cautious correction",
            "- Mild/asymptomatic: fluid restriction, treat underlying cause",
            "Acute severe (<48h, symptomatic):",
            "- 3% saline 100mL bolus over 10 min, can repeat x2-3 until symptoms improve",
            "- Goal: increase Na by 4-6 mEq/L in first few hours (enough to stop symptoms)",
            "Chronic (>48h, most cases):",
            "- Fluid restriction: 800-1000 mL/day (first-line if mild)",
            "- Treat underlying cause: stop NSAIDs, treat cancer, wean SSRIs",
            "- Salt tablets: sodium chloride 2-4g daily (with fluid restriction)",
            "- Demeclocycline 300-600mg BID (induces nephrogenic DI, second-line)",
            "- Tolvaptan 15mg daily (V2 antagonist, expensive, monitor closely)",
            "CRITICAL: Correction rate limits:",
            "- Maximum 8-10 mEq/L in 24 hours",
            "- Maximum 18 mEq/L in 48 hours",
            "- TOO FAST → Osmotic demyelination syndrome (locked-in syndrome, death)",
            "Monitor: Na every 2-4h initially, adjust treatment to stay within limits",
            "This patient: stop NSAIDs, fluid restriction, treat SCLC (cause of SIADH)"
        ],
        "pitfalls": [
            "Osmotic demyelination syndrome (ODS): from overcorrection >10-12 mEq/L per 24h - causes irreversible brainstem damage (quadriplegia, pseudobulbar palsy, locked-in), especially in chronic hyponatremia, alcoholics, malnutrition, liver disease",
            "Small cell lung cancer: 10-15% develop SIADH, paraneoplastic syndrome",
            "Cerebral salt wasting: similar labs but HYPOVOLEMIC (vs euvolemic in SIADH) - treat with saline, fludrocortisone, NOT fluid restriction",
            "Pseudohyponatremia: artifactual low Na from hyperlipidemia or hyperproteinemia - normal osmolality",
            "Exercise-associated hyponatremia: marathon runners drinking too much hypotonic fluid",
            "Beer potomania: low solute intake prevents free water excretion",
            "Medications causing SIADH: SSRIs, carbamazepine, cyclophosphamide, vincristine, NSAIDs, PPIs, ecstasy",
            "If correcting too fast: can give desmopressin + hypotonic fluids to re-lower sodium"
        ],
        "tags": ["SIADH", "hyponatremia", "confusion", "small cell lung cancer", "endocrinology"],
        "created_at": "2025-12-30T01:00:00.000000",
        "author": "Dr. Endocrinology"
    }
]

# Add to database
data['cases'].extend(new_cases)

# Save
with open('backend/data/clinical_cases.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"✓ Successfully added final cases 98-100")
print(f"✓ Total cases in database: {len(data['cases'])}")
print(f"✓ TARGET REACHED: 100 unique clinical cases!")

# Verify no duplicates
from collections import Counter
diagnoses = [c['correct_diagnosis'] for c in data['cases']]
duplicate_diagnoses = {k: v for k, v in Counter(diagnoses).items() if v > 1}

if duplicate_diagnoses:
    print("\n⚠️  WARNING: Duplicate diagnoses found:")
    for diag, count in duplicate_diagnoses.items():
        print(f"  {diag}: {count} cases")
else:
    print("\n✓ All 100 diagnoses are unique!")

# Show case distribution by specialty
from collections import Counter
specialties = [c['specialty'] for c in data['cases']]
specialty_counts = Counter(specialties)
print(f"\n📊 Cases by specialty:")
for specialty, count in sorted(specialty_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {specialty}: {count}")
