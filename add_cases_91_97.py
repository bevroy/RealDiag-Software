#!/usr/bin/env python3
"""
Add clinical cases 91-97 to the database
Replacing removed duplicates with unique cases
"""

import json

with open('backend/data/clinical_cases.json', 'r') as f:
    data = json.load(f)

print(f"Current total: {len(data['cases'])} cases")

# Cases 91-97 - All unique diagnoses
new_cases = [
    {
        "case_id": "CASE-091",
        "title": "Woman with Recurrent Nosebleeds",
        "specialty": "hematology",
        "difficulty": "intermediate",
        "learning_objectives": [
            "Recognize hereditary hemorrhagic telangiectasia",
            "Differentiate from common epistaxis",
            "Understand genetic bleeding disorders"
        ],
        "presentation": "42-year-old woman with lifelong recurrent nosebleeds, recently worsening in frequency",
        "history": {
            "chief_complaint": "Nosebleeds almost daily now, very hard to stop",
            "hpi": "Has had nosebleeds since childhood, but manageable. Past 6 months having them 4-5 times weekly, lasting 15-30 minutes. Now occurring daily, difficult to control. Also noticed small red spots on lips and inside mouth. Occasional bloody stools. Feeling more fatigued. Brother and father also have frequent nosebleeds.",
            "pmh": "Iron deficiency anemia (chronic), no known bleeding disorders",
            "medications": "Iron sulfate 325mg daily",
            "social": "Non-smoker, works as accountant",
            "family": "Father and brother with frequent nosebleeds, father died of 'lung problem' at 55"
        },
        "physical_exam": {
            "vitals": "BP 118/76, HR 88, RR 14, O2 sat 98%",
            "general": "Pale woman, no acute distress",
            "heent": "Multiple small red telangiectasias on lips, tongue, buccal mucosa, nasal mucosa. Active slow ooze from left anterior nasal septum.",
            "skin": "Multiple small red telangiectasias on fingertips, palms",
            "lungs": "Clear to auscultation",
            "abdomen": "Soft, non-tender, no hepatosplenomegaly",
            "rectal": "Guaiac positive stool"
        },
        "labs": {
            "cbc": "Hgb 9.2 g/dL, MCV 72 (microcytic), WBC 7,200, Plt 245,000",
            "iron_studies": "Ferritin 8 ng/mL (low), TIBC elevated, iron saturation 8%",
            "coagulation": "PT/INR normal, aPTT normal",
            "bleeding_time": "Normal",
            "vwf_studies": "Normal"
        },
        "imaging": {
            "cxr": "Multiple small nodular opacities bilaterally",
            "ct_chest": "Multiple pulmonary arteriovenous malformations",
            "mri_brain": "No evidence of cerebral AVMs"
        },
        "correct_diagnosis": "HEME-HEREDITARY-HEMORRHAGIC-TELANGIECTASIA",
        "differential": [
            "HEME-HEREDITARY-HEMORRHAGIC-TELANGIECTASIA",
            "HEME-VON-WILLEBRAND-DISEASE",
            "ENT-CHRONIC-EPISTAXIS",
            "GI-ANGIODYSPLASIA"
        ],
        "explanation": "Hereditary hemorrhagic telangiectasia (HHT, Osler-Weber-Rendu syndrome): autosomal dominant disorder causing abnormal blood vessel formation. Diagnostic Curaçao criteria (3 of 4 needed): (1) Spontaneous recurrent epistaxis, (2) Mucocutaneous telangiectasias (lips, oral cavity, fingers), (3) Visceral AVMs (pulmonary, hepatic, cerebral, GI), (4) First-degree relative with HHT. This patient has all 4. Telangiectasias are small dilated vessels that bleed easily. Pulmonary AVMs (15-50% of HHT patients) can cause hypoxemia, paradoxical emboli, brain abscess. Chronic blood loss leads to severe iron deficiency anemia.",
        "management_pearls": [
            "Diagnosis confirmed by genetic testing (ENG or ACVRL1 gene mutations)",
            "Epistaxis management:",
            "- Nasal humidification, saline spray, petroleum jelly",
            "- Estrogen-progesterone therapy (decreases bleeding)",
            "- Tranexamic acid 1g TID during bleeding episodes",
            "- Laser ablation or cautery for accessible telangiectasias",
            "- Severe cases: YAG laser, nasal closure (Young's procedure)",
            "Iron replacement: IV iron if severe anemia or poor PO absorption",
            "Screen for visceral AVMs:",
            "- Pulmonary AVMs: CT chest, treat if >3mm (risk paradoxical emboli, stroke)",
            "- Cerebral AVMs: MRI brain every 5-10 years",
            "- Hepatic AVMs: Doppler ultrasound",
            "- GI telangiectasias: endoscopy if GI bleeding",
            "Pulmonary AVMs: treat with coil embolization if feeding vessel >3mm",
            "Antibiotic prophylaxis before dental procedures (prevent brain abscess via pulmonary AVMs)",
            "Genetic counseling: 50% transmission to offspring"
        ],
        "pitfalls": [
            "Pulmonary AVMs: can cause paradoxical emboli (bypass lung capillary filter) → stroke, brain abscess",
            "Cerebral AVMs: 10% of HHT patients, risk hemorrhagic stroke - screen with MRI",
            "High-output heart failure: from hepatic AVMs causing arteriovenous shunting",
            "Pregnancy: epistaxis often worsens, screen for pulmonary AVMs before conception",
            "Iron deficiency: chronic blood loss requires lifelong iron supplementation",
            "DO NOT use bevacizumab (anti-VEGF) except severe refractory cases - not standard therapy"
        ],
        "tags": ["HHT", "epistaxis", "telangiectasia", "bleeding disorder", "hematology"],
        "created_at": "2025-12-29T23:30:00.000000",
        "author": "Dr. Hematology"
    },
    
    {
        "case_id": "CASE-092",
        "title": "Man with Difficulty Swallowing Solids",
        "specialty": "gastroenterology",
        "difficulty": "intermediate",
        "learning_objectives": [
            "Recognize esophageal stricture presentation",
            "Differentiate dysphagia causes",
            "Understand management of GERD complications"
        ],
        "presentation": "67-year-old man with progressive difficulty swallowing solid foods over 6 months",
        "history": {
            "chief_complaint": "Food gets stuck in chest, can only eat soft foods now",
            "hpi": "Started 6 months ago with occasional difficulty swallowing meat and bread. Progressive - now unable to swallow any solid foods. Must drink water to wash food down. Liquids swallow normally. Occasional regurgitation of undigested food. 15-pound weight loss. Long history of heartburn for 20 years, takes antacids occasionally. No chest pain currently. No hoarseness. Denies smoking.",
            "pmh": "GERD (untreated for years), hypertension",
            "medications": "Lisinopril 10mg, calcium carbonate PRN",
            "social": "Non-smoker, minimal alcohol, retired teacher",
            "family": "No GI cancers"
        },
        "physical_exam": {
            "vitals": "BP 132/84, HR 76, BMI 22 (down from 26)",
            "general": "Thin man, appears older than stated age",
            "oropharynx": "Normal, good dentition",
            "neck": "No masses, no lymphadenopathy",
            "abdomen": "Soft, non-tender, no masses",
            "neurologic": "Cranial nerves intact, normal strength"
        },
        "labs": {
            "cbc": "Hgb 12.8 g/dL, WBC 6,800",
            "cmp": "Normal",
            "albumin": "3.4 g/dL (low normal)"
        },
        "imaging": {
            "barium_swallow": "Smooth, tapered narrowing in distal esophagus. Bird-beak appearance. Proximal esophageal dilation.",
            "upper_endoscopy": "Tight peptic stricture at 35cm from incisors, unable to pass scope initially. Circumferential scarring. No masses. Salmon-colored mucosa extending 4cm above GE junction (Barrett's esophagus). Biopsies taken.",
            "biopsy": "Intestinal metaplasia consistent with Barrett's esophagus, no dysplasia. Chronic inflammation."
        },
        "correct_diagnosis": "GI-ESOPHAGEAL-STRICTURE-PEPTIC",
        "differential": [
            "GI-ESOPHAGEAL-STRICTURE-PEPTIC",
            "GI-ESOPHAGEAL-CANCER",
            "GI-ACHALASIA",
            "NEURO-ESOPHAGEAL-DYSMOTILITY"
        ],
        "explanation": "Peptic esophageal stricture: narrowing of esophageal lumen from chronic GERD causing repeated injury, inflammation, and fibrosis. Classic presentation: progressive dysphagia to solids first, then liquids (mechanical obstruction pattern). Long-standing GERD history (often undertreated). Complications of chronic GERD: (1) Esophagitis, (2) Stricture, (3) Barrett's esophagus (intestinal metaplasia - premalignant), (4) Adenocarcinoma. Risk factors: male, white, chronic GERD, age >50. Barrett's esophagus found in 10-15% of chronic GERD patients.",
        "management_pearls": [
            "Endoscopic dilation: wire-guided (Savary) or balloon dilators - goal is restore lumen >14-15mm",
            "Serial dilations usually needed: typically 3-4 sessions over weeks to months",
            "PPI therapy: HIGH-DOSE - omeprazole 40mg BID or esomeprazole 40mg BID (heal inflammation, prevent recurrence)",
            "Dilation technique: start conservative (9-10mm), increase gradually to avoid perforation",
            "Rule three: don't dilate >3mm per session (reduces perforation risk)",
            "Intralesional steroid injection: triamcinolone into stricture after dilation (reduces recurrence in refractory cases)",
            "Refractory strictures: consider temporary esophageal stent placement",
            "Barrett's esophagus surveillance:",
            "- No dysplasia: EGD every 3-5 years",
            "- Low-grade dysplasia: EGD every 6-12 months or ablation therapy",
            "- High-grade dysplasia: endoscopic ablation (radiofrequency) or esophagectomy",
            "Nutritional support: high-calorie diet, nutritionist referral if significant weight loss"
        ],
        "pitfalls": [
            "Esophageal cancer: similar presentation but irregular stricture, hard, friable - ALWAYS biopsy strictures",
            "Achalasia: also has dysphagia with bird-beak on barium swallow, but affects solids AND liquids equally from onset, has absent peristalsis on manometry",
            "Perforation risk: 0.1-0.5% with dilation - watch for chest pain, fever, subcutaneous emphysema post-procedure",
            "Eosinophilic esophagitis: younger patients, food impaction, corrugated/ringed esophagus, eosinophils on biopsy",
            "Barrett's progression to cancer: 0.5% per year - requires surveillance",
            "Schatzki ring: thin mucosal ring at GE junction, intermittent dysphagia, easy to dilate"
        ],
        "tags": ["esophageal stricture", "dysphagia", "GERD", "Barrett's esophagus", "gastroenterology"],
        "created_at": "2025-12-29T23:40:00.000000",
        "author": "Dr. Gastroenterology"
    },
    
    {
        "case_id": "CASE-093",
        "title": "Child with Persistent Cough After Choking",
        "specialty": "pediatrics",
        "difficulty": "intermediate",
        "learning_objectives": [
            "Recognize foreign body aspiration",
            "Understand delayed presentation",
            "Differentiate from asthma or pneumonia"
        ],
        "presentation": "3-year-old with 2 weeks of persistent cough after choking episode on peanuts",
        "history": {
            "chief_complaint": "Cough won't go away, wheezing on one side",
            "hpi": "Two weeks ago was eating peanuts and started coughing/choking. Parents performed back blows, child seemed to recover. Since then has persistent cough, worse at night. Coughing fits sometimes cause gagging. Right-sided wheeze noticed by parents. Tried over-the-counter cough medicine without improvement. No fever. Eating and drinking normally. No prior respiratory issues.",
            "pmh": "Healthy, no asthma",
            "medications": "None, tried dextromethorphan without benefit",
            "social": "Attends daycare",
            "family": "No asthma, mother has allergies"
        },
        "physical_exam": {
            "vitals": "Temp 98.8°F, HR 110, RR 28, O2 sat 96% on RA",
            "general": "Well-appearing child, occasional cough during exam",
            "heent": "Normal oropharynx, no stridor",
            "chest": "Decreased breath sounds right middle/lower lung fields, unilateral wheeze on right, occasional rhonchi",
            "cardiovascular": "Regular rate and rhythm",
            "abdomen": "Soft, non-tender"
        },
        "labs": {
            "wbc": "Normal",
            "cxr_ap": "Subtle increased lucency right lung, possible air trapping"
        },
        "imaging": {
            "cxr_inspiratory": "Appears relatively symmetric",
            "cxr_expiratory": "Hyperinflation right lung with mediastinal shift to left (air trapping)",
            "cxr_lateral_decubitus": "Right lung remains hyperinflated when dependent",
            "ct_chest": "Hypodense foreign body in right mainstem bronchus with distal air trapping"
        },
        "correct_diagnosis": "PEDS-FOREIGN-BODY-ASPIRATION-BRONCHIAL",
        "differential": [
            "PEDS-FOREIGN-BODY-ASPIRATION-BRONCHIAL",
            "PEDS-ASTHMA-EXACERBATION",
            "PULM-BRONCHIOLITIS",
            "PULM-PNEUMONIA-BACTERIAL"
        ],
        "explanation": "Foreign body aspiration: common in children age 1-3 years. Classic presentation: choking episode (may be unwitnessed) followed by persistent unilateral symptoms. Triad: cough, wheeze, decreased breath sounds (present in <40%). Right bronchus more common (wider, more vertical). Radiolucent objects (nuts, seeds, plastic) won't show on XR directly. Diagnostic clues: unilateral findings, air trapping on expiratory/decubitus films, history of choking. Three phases: (1) Initial choking with coughing, (2) Asymptomatic interval (hours to weeks), (3) Complications (persistent cough, wheeze, recurrent pneumonia, abscess). Delayed diagnosis common - average 1-4 weeks.",
        "management_pearls": [
            "Rigid bronchoscopy under general anesthesia: gold standard for diagnosis and treatment",
            "ENT or pediatric pulmonology referral urgently",
            "NPO once diagnosis suspected (preparing for bronchoscopy)",
            "Do NOT perform Heimlich if child stable and tolerating position (risk complete obstruction)",
            "Bronchoscopy findings: direct visualization and removal with optical forceps",
            "Post-removal: observe for complications (edema, laryngospasm, pneumothorax)",
            "Corticosteroids: dexamethasone 0.6mg/kg x1 (reduce post-procedure edema)",
            "Antibiotics if secondary infection present",
            "CXR after removal to confirm re-expansion and no pneumothorax",
            "Prevention counseling: avoid high-risk foods age <4 (nuts, popcorn, grapes, hot dogs, hard candy)"
        ],
        "pitfalls": [
            "Expiratory or decubitus films: essential if inspiratory CXR normal but high suspicion - shows air trapping from ball-valve effect",
            "Bilateral or normal exam: doesn't exclude foreign body, especially if lodged in trachea",
            "Unwitnessed aspiration: 40% no clear history, diagnosed by persistent unilateral symptoms",
            "Negative XR: radiolucent objects (nuts, plastic) invisible - CT or bronchoscopy needed",
            "Asthma misdiagnosis: unilateral findings should raise suspicion for foreign body",
            "Complications of retained foreign body: recurrent pneumonia, bronchiectasis, abscess, hemoptysis",
            "Flexible bronchoscopy: can visualize but rigid preferred for removal (better airway control)"
        ],
        "tags": ["foreign body aspiration", "pediatric emergency", "bronchoscopy", "pediatrics"],
        "created_at": "2025-12-29T23:50:00.000000",
        "author": "Dr. Pediatric Pulmonology"
    },
    
    {
        "case_id": "CASE-094",
        "title": "Woman with Facial Swelling and Proteinuria",
        "specialty": "nephrology",
        "difficulty": "intermediate",
        "learning_objectives": [
            "Recognize nephrotic syndrome presentation",
            "Understand causes in adults",
            "Differentiate from nephritic syndrome"
        ],
        "presentation": "34-year-old woman with progressive facial and leg swelling, foamy urine for 3 weeks",
        "history": {
            "chief_complaint": "Face and legs very swollen, urine looks foamy",
            "hpi": "Noticed periorbital swelling 3 weeks ago, thought was allergies. Progressive facial puffiness, leg swelling to knees, tight-fitting shoes. Urine appears foamy/frothy. 12-pound weight gain in 3 weeks. Feeling fatigued. No hematuria, dysuria, or flank pain. Recently started NSAIDs for chronic back pain 6 weeks ago (ibuprofen 800mg TID). No sick contacts.",
            "pmh": "Hypothyroidism, chronic back pain",
            "medications": "Levothyroxine 100mcg, ibuprofen 800mg TID (recent)",
            "social": "Non-smoker, no drugs, works as nurse",
            "family": "Mother has lupus, father has diabetes"
        },
        "physical_exam": {
            "vitals": "BP 142/88, HR 78, RR 16, weight 168 lbs (was 156 lbs 3 weeks ago)",
            "general": "Cushingoid appearance, puffy face",
            "heent": "Marked periorbital edema, no thyromegaly",
            "chest": "Clear to auscultation",
            "cardiovascular": "Regular, no murmurs, no JVD",
            "abdomen": "Soft, ascites with fluid wave present",
            "extremities": "3+ pitting edema to thighs bilaterally",
            "skin": "No rash"
        },
        "labs": {
            "urinalysis": "3+ protein, no blood, no WBCs, oval fat bodies present, lipiduria",
            "24hr_urine": "Protein 8.5 g/day (massive proteinuria, normal <150mg/day)",
            "urine_protein_creatinine_ratio": "6.2 (nephrotic range >3.5)",
            "cbc": "Normal",
            "bmp": "Na 134, K 4.1, Cr 1.2, albumin 2.1 g/dL (low)",
            "lipid_panel": "Total chol 320 mg/dL, LDL 210, TG 285",
            "complement": "C3 and C4 normal",
            "ana": "Negative",
            "hbsag_hcv": "Negative"
        },
        "imaging": {
            "renal_ultrasound": "Normal-sized kidneys, increased echogenicity, no obstruction",
            "renal_biopsy": "Minimal change disease - effacement of podocyte foot processes on EM, normal light microscopy, negative immunofluorescence"
        },
        "correct_diagnosis": "NEPHRO-NEPHROTIC-SYNDROME-MINIMAL-CHANGE",
        "differential": [
            "NEPHRO-NEPHROTIC-SYNDROME-MINIMAL-CHANGE",
            "NEPHRO-FSGS",
            "NEPHRO-MEMBRANOUS-NEPHROPATHY",
            "NEPHRO-DIABETIC-NEPHROPATHY"
        ],
        "explanation": "Nephrotic syndrome: triad of (1) Heavy proteinuria >3.5g/day, (2) Hypoalbuminemia <3.0g/dL, (3) Edema. Also associated with hyperlipidemia, lipiduria (oval fat bodies, fatty casts). Loss of albumin → decreased oncotic pressure → edema. Liver compensates by increasing lipid synthesis → hyperlipidemia. Minimal change disease (MCD): most common cause nephrotic syndrome in children, also occurs adults (10-15% cases). Often triggered by NSAIDs, infections, malignancy, allergies. Podocyte injury → loss of glomerular charge barrier → massive proteinuria. Selective proteinuria (albumin only). Excellent prognosis with treatment.",
        "management_pearls": [
            "Stop NSAIDs immediately - likely trigger for MCD",
            "Corticosteroids: prednisone 1 mg/kg/day (max 80mg) for 4-16 weeks, then taper",
            "Response usually within 2-8 weeks (faster than other causes)",
            "Diuretics for edema: furosemide 40-80mg daily, spironolactone 25-50mg daily",
            "Salt restriction <2g/day",
            "ACE inhibitor: enalapril 5-10mg daily (reduce proteinuria)",
            "Statin: atorvastatin 20-40mg (treat hyperlipidemia)",
            "Anticoagulation: if albumin <2.0 (hypercoagulable state) - consider prophylactic LMWH or warfarin",
            "Vaccinations: pneumococcal, influenza (increased infection risk)",
            "Monitor: weekly weights, daily urine dipstick, BP checks",
            "Renal biopsy indications: atypical features (hematuria, renal insufficiency, age >60, poor response to steroids)",
            "Relapse: 30-40% relapse after initial response - retreat with steroids"
        ],
        "pitfalls": [
            "Complications: thromboembolism (renal vein thrombosis, PE, DVT) from loss of anticoagulant proteins - anticoagulate if albumin <2.0",
            "Infections: loss of immunoglobulins in urine → increased infection risk, especially encapsulated organisms",
            "FSGS: more common in African Americans, worse prognosis, steroid-resistant, progresses to ESRD",
            "Membranous nephropathy: most common primary nephrotic syndrome in Caucasian adults, associated with malignancy, hepatitis B, NSAIDs, lupus",
            "Amyloidosis: systemic disease, Congo red staining, apple-green birefringence",
            "Diabetic nephropathy: Kimmelstiel-Wilson nodules, requires years of diabetes",
            "Secondary causes: always check ANA (lupus), HIV, hepatitis B/C, malignancy (lymphoma, solid tumors)"
        ],
        "tags": ["nephrotic syndrome", "minimal change disease", "proteinuria", "edema", "nephrology"],
        "created_at": "2025-12-30T00:00:00.000000",
        "author": "Dr. Nephrology"
    },
    
    {
        "case_id": "CASE-095",
        "title": "Man with Progressive Weakness and Muscle Wasting",
        "specialty": "neurology",
        "difficulty": "advanced",
        "learning_objectives": [
            "Recognize ALS presentation",
            "Differentiate from other motor neuron diseases",
            "Understand management of progressive neurodegenerative disease"
        ],
        "presentation": "58-year-old man with 9 months of progressive weakness, muscle twitching, and difficulty speaking",
        "history": {
            "chief_complaint": "Weakness in hands, trouble speaking clearly, muscles twitching all over",
            "hpi": "Started 9 months ago with right hand weakness - difficulty buttoning shirts, using tools. Spread to left hand. Noticed muscle twitching (fasciculations) in arms, then legs, now trunk. Voice has changed - nasal quality, slurred speech, difficulty articulating. Chewing and swallowing becoming difficult - takes longer to eat, occasionally chokes on liquids. 20-pound weight loss. No sensory changes, bowel/bladder normal. Emotional lability - crying inappropriately. Denies pain.",
            "pmh": "Hypertension, hyperlipidemia",
            "medications": "Lisinopril 20mg, atorvastatin 40mg",
            "social": "Former military, works in construction, married",
            "family": "No known neurologic diseases"
        },
        "physical_exam": {
            "vitals": "BP 138/82, HR 74, RR 14, weight 162 lbs (down from 182)",
            "general": "Thin man, visible muscle atrophy in hands and arms",
            "cranial_nerves": "Tongue atrophy with fasciculations, dysarthria (bulbar speech), weak palate elevation, intact sensation",
            "motor": "Weakness: hands 3/5, arms 4/5, legs 4/5. Severe atrophy of hand intrinsic muscles (thenar, hypothenar, interossei). Widespread fasciculations in arms, legs, trunk.",
            "tone": "Increased tone with spasticity in legs",
            "reflexes": "Hyperreflexia throughout (3+ to 4+), upgoing toes bilaterally (Babinski positive), jaw jerk brisk",
            "sensory": "Intact to all modalities",
            "coordination": "Difficult to assess due to weakness, no ataxia",
            "gait": "Spastic gait, difficulty with toe/heel walk"
        },
        "labs": {
            "cbc": "Normal",
            "cmp": "Normal",
            "ck": "Mildly elevated 380 U/L (normal <200)",
            "tsh": "Normal",
            "vitamin_b12": "Normal",
            "lyme_antibody": "Negative",
            "hiv": "Negative"
        },
        "imaging": {
            "mri_cervical_spine": "No significant cord compression or lesions. Subtle T2 signal in corticospinal tracts.",
            "mri_brain": "Age-appropriate changes, no masses or strokes",
            "emg": "Widespread acute denervation (fibrillations, positive sharp waves) in bulbar, cervical, thoracic, lumbosacral regions. Chronic changes (large motor units, reduced recruitment). Normal nerve conduction studies."
        },
        "correct_diagnosis": "NEURO-AMYOTROPHIC-LATERAL-SCLEROSIS",
        "differential": [
            "NEURO-AMYOTROPHIC-LATERAL-SCLEROSIS",
            "NEURO-CERVICAL-MYELOPATHY",
            "NEURO-MULTIFOCAL-MOTOR-NEUROPATHY",
            "NEURO-KENNEDY-DISEASE"
        ],
        "explanation": "Amyotrophic lateral sclerosis (ALS, Lou Gehrig disease): progressive neurodegenerative disease affecting upper and lower motor neurons. Diagnostic criteria (El Escorial): UMN + LMN signs in ≥3 regions (bulbar, cervical, thoracic, lumbosacral). This patient has: LMN signs (weakness, atrophy, fasciculations, denervation on EMG), UMN signs (spasticity, hyperreflexia, Babinski), bulbar involvement (dysarthria, dysphagia, tongue atrophy), spread across multiple regions. Median survival 3-5 years from symptom onset. Riluzole prolongs survival ~3 months. Death typically from respiratory failure.",
        "management_pearls": [
            "Riluzole 50mg BID: only FDA-approved disease-modifying drug, prolongs survival 2-3 months, slows progression",
            "Edaravone: IV or PO, may slow functional decline in select patients (recent evidence)",
            "Multidisciplinary ALS clinic: neurology, pulmonology, nutrition, PT/OT, speech, palliative care",
            "Respiratory management:",
            "- Monitor FVC every 3 months (noninvasive ventilation when FVC <50%)",
            "- BiPAP at night initially, then continuous",
            "- Mechanical ventilation vs comfort care - discuss goals early",
            "Nutrition:",
            "- PEG tube when significant dysphagia or weight loss >10% (before FVC <50%)",
            "- High-calorie diet, thickened liquids initially",
            "Symptomatic treatment:",
            "- Sialorrhea: glycopyrrolate, scopolamine patch, botulinum toxin to salivary glands",
            "- Pseudobulbar affect: dextromethorphan/quinidine (Nuedexta)",
            "- Spasticity: baclofen 10-20mg TID, tizanidine",
            "- Cramps: quinine, gabapentin",
            "Communication: speech therapy, assistive devices (eye-gaze technology)",
            "Advance directives: early discussions about ventilation, feeding tubes, hospice"
        ],
        "pitfalls": [
            "Bulbar-onset ALS: starts with dysarthria/dysphagia, faster progression, worse prognosis (2-3 year survival)",
            "Spinal-onset ALS: starts with limb weakness, slower progression",
            "Primary lateral sclerosis: pure UMN disease, much slower progression, better prognosis",
            "Progressive muscular atrophy: pure LMN disease, slower than ALS",
            "Kennedy disease (X-linked bulbospinal muscular atrophy): gynecomastia, sensory neuropathy, CAG repeat testing",
            "Multifocal motor neuropathy: LMN only, demyelinating on EMG, responds to IVIG, conduction block on NCS",
            "Cervical stenosis with myelopathy: can mimic ALS but has sensory signs, cord compression on MRI",
            "Do NOT: give high-dose vitamins, experimental stem cells outside trials - no proven benefit"
        ],
        "tags": ["ALS", "motor neuron disease", "neurodegenerative", "neurology"],
        "created_at": "2025-12-30T00:10:00.000000",
        "author": "Dr. Neurology"
    },
    
    {
        "case_id": "CASE-096",
        "title": "Teenager with Elbow Pain After Pitching",
        "specialty": "sports medicine",
        "difficulty": "intermediate",
        "learning_objectives": [
            "Recognize ulnar collateral ligament injury",
            "Understand throwing mechanics and overuse",
            "Prevent youth baseball injuries"
        ],
        "presentation": "16-year-old baseball pitcher with medial elbow pain worsening over season",
        "history": {
            "chief_complaint": "Inside of elbow hurts when throwing, getting worse",
            "hpi": "Star pitcher on high school team. Gradual onset medial elbow pain over past 2 months of baseball season. Initially only during hard throwing, now hurts with every pitch. Pain most severe during acceleration phase of throwing. Velocity has decreased. Occasional numbness in 4th and 5th fingers. Pitched 3 games per week recently plus practice. No acute injury or pop.",
            "pmh": "Healthy, no prior elbow injuries",
            "medications": "Ibuprofen PRN",
            "social": "High school junior, varsity pitcher, pitches year-round (travel team in summer)",
            "family": "Father pitched in college"
        },
        "physical_exam": {
            "vitals": "Temp 98.6°F, BP 118/72, HR 68",
            "right_elbow": "Tenderness over medial epicondyle and along ulnar collateral ligament. Pain with valgus stress test at 30° flexion. No laxity or endpoint. Full ROM but pain at terminal extension. No effusion.",
            "left_elbow": "Normal for comparison",
            "neurovascular": "Intact radial pulse. Positive Tinel sign at cubital tunnel (ulnar nerve). Decreased sensation in ulnar distribution.",
            "shoulder": "Normal ROM, strength, no impingement signs"
        },
        "labs": {
            "none_needed": "Clinical diagnosis"
        },
        "imaging": {
            "elbow_xray": "AP and lateral normal. No fracture, normal growth plates, no loose bodies.",
            "mri_elbow": "Increased T2 signal and partial thickness tear of ulnar collateral ligament (UCL) at 50% thickness. Mild edema in adjacent structures. No complete tear. Mild ulnar neuritis."
        },
        "correct_diagnosis": "ORTHO-UCL-INJURY-PARTIAL-TEAR",
        "differential": [
            "ORTHO-UCL-INJURY-PARTIAL-TEAR",
            "ORTHO-MEDIAL-EPICONDYLITIS",
            "ORTHO-ULNAR-NEURITIS",
            "ORTHO-LITTLE-LEAGUE-ELBOW"
        ],
        "explanation": "Ulnar collateral ligament (UCL) injury: common in overhead throwing athletes. UCL is primary restraint to valgus stress during throwing. Most stress occurs during late cocking and early acceleration phases - can generate 64 Nm of valgus torque (exceeds UCL tensile strength of 34 Nm). Repetitive microtrauma leads to ligament attenuation, partial tears, eventual complete rupture. Risk factors: high pitch counts, year-round throwing, poor mechanics, pitching while fatigued, breaking pitches at young age. Presentation: medial elbow pain during throwing, decreased velocity, loss of control. Valgus stress test reproduces pain (incomplete endpoint suggests laxity).",
        "management_pearls": [
            "STOP THROWING immediately - continued pitching risks complete tear",
            "Initial conservative management (partial tears):",
            "- Rest from throwing: minimum 6-12 weeks",
            "- NSAIDs: ibuprofen 600mg TID x 2 weeks",
            "- Physical therapy: strengthen flexor-pronator mass, scapular stabilizers, core",
            "- Correct throwing mechanics with sports PT/coach",
            "- Interval throwing program: gradual return over 3-4 months",
            "Pitch count limits (evidence-based):",
            "- Age 13-14: 75 pitches/game, 125/week",
            "- Age 15-16: 90 pitches/game, 150/week",
            "- Age 17-18: 105 pitches/game, 175/week",
            "- No pitching >8 months/year",
            "- Rest 4 months/year from competitive throwing",
            "Surgery (Tommy John - UCL reconstruction):",
            "- Indications: complete tear, failed conservative management after 3-6 months, desire to return to competitive throwing",
            "- Technique: palmaris longus autograft or hamstring allograft",
            "- Return to pitching: 12-18 months post-op",
            "- Success rate: 85-90% return to same level"
        ],
        "pitfalls": [
            "Complete UCL tear: needs surgical reconstruction for return to competitive pitching",
            "Ulnar neuritis: often coexists with UCL injury (20-40%), transposition may be needed",
            "Little League elbow: pediatric medial apophysitis (growth plate inflammation) - treat with rest, usually heal well",
            "Medial epicondylitis: flexor-pronator tendinopathy, less severe, better prognosis than UCL tear",
            "Valgus extension overload: posterior elbow pain, olecranon osteophytes, loose bodies",
            "Prevention: enforce pitch counts, 3-4 months rest/year, don't pitch on consecutive days, no curveballs/sliders <14 years old"
        ],
        "tags": ["UCL injury", "Tommy John", "baseball pitcher", "overuse injury", "sports medicine"],
        "created_at": "2025-12-30T00:20:00.000000",
        "author": "Dr. Sports Medicine"
    },
    
    {
        "case_id": "CASE-097",
        "title": "Woman with Hair Loss and Nail Changes",
        "specialty": "dermatology",
        "difficulty": "intermediate",
        "learning_objectives": [
            "Recognize alopecia areata presentation",
            "Differentiate from other causes of hair loss",
            "Understand autoimmune hair loss"
        ],
        "presentation": "28-year-old woman with sudden onset patchy hair loss on scalp over 2 months",
        "history": {
            "chief_complaint": "Bald spots on my head, getting bigger",
            "hpi": "Noticed first circular bald patch on back of scalp 2 months ago, size of quarter. Now has 4-5 patches, some growing larger. Hair comes out easily when touched. Coworkers have commented. Feeling very distressed. No itching, scaling, or pain. No hair loss elsewhere. Recently went through stressful divorce. No new medications or hair products.",
            "pmh": "Vitiligo (depigmented patches on hands), seasonal allergies, hypothyroidism",
            "medications": "Levothyroxine 75mcg, cetirizine 10mg PRN",
            "social": "Marketing executive, recent divorce, non-smoker",
            "family": "Mother has rheumatoid arthritis, sister has type 1 diabetes"
        },
        "physical_exam": {
            "vitals": "Normal",
            "general": "Anxious woman, otherwise well-appearing",
            "scalp": "Five well-demarcated, round/oval patches of complete hair loss varying 2-5cm diameter. Skin smooth, no scaling, erythema, or scarring. 'Exclamation point hairs' at periphery (broken hairs wider at distal end). Positive hair pull test at edge of patches (gentle traction removes 4-5 hairs easily).",
            "eyebrows": "Intact, no loss",
            "body": "No alopecia in other areas",
            "nails": "Pitting on multiple fingernails, no onycholysis",
            "skin": "Depigmented patches on hands consistent with known vitiligo"
        },
        "labs": {
            "cbc": "Normal",
            "tsh": "2.1 (normal, well-controlled)",
            "ana": "Negative",
            "iron_studies": "Normal",
            "vitamin_d": "28 ng/mL",
            "zinc": "Normal"
        },
        "imaging": {
            "none_needed": "Clinical diagnosis"
        },
        "correct_diagnosis": "DERM-ALOPECIA-AREATA",
        "differential": [
            "DERM-ALOPECIA-AREATA",
            "DERM-TINEA-CAPITIS",
            "DERM-TRICHOTILLOMANIA",
            "ENDO-HYPOTHYROID-ALOPECIA"
        ],
        "explanation": "Alopecia areata: autoimmune condition causing non-scarring hair loss. T-cell mediated attack on hair follicles in anagen (growth) phase. Classic presentation: sudden onset, well-demarcated round/oval patches of complete hair loss on scalp. 'Exclamation point hairs' pathognomonic (short broken hairs tapered at base). Associated with other autoimmune diseases (20%): thyroid disease, vitiligo, diabetes, rheumatoid arthritis. Severity spectrum: patchy (most common, 80%), alopecia totalis (entire scalp), alopecia universalis (entire body). Triggered by stress, illness. Prognosis: 50% spontaneous regrowth within 1 year, 80% eventually regrow. Worse prognosis: extensive involvement, young age at onset, atopy, nail changes, >1 year duration.",
        "management_pearls": [
            "Reassurance: most patients regrow hair, though may take 6-12 months",
            "First-line treatment (limited patches <50% scalp):",
            "- Intralesional corticosteroids: triamcinolone 5-10 mg/mL injected into patches every 4-6 weeks (most effective)",
            "- Topical corticosteroids: clobetasol 0.05% foam/solution BID (less effective but try first in children)",
            "Second-line (extensive/refractory):",
            "- Topical immunotherapy: DPCP or SADBE (contact sensitization therapy) - 60% response in severe cases",
            "- JAK inhibitors: tofacitinib, baricitinib, ruxolitinib (expensive, new promising option)",
            "- Systemic corticosteroids: prednisone 40mg daily x 6 weeks (high relapse rate after stopping)",
            "Third-line:",
            "- Minoxidil 5% foam: may help regrowth, safe adjunct",
            "- Anthralin cream",
            "- Methotrexate (severe cases)",
            "Cosmetic: wigs, hairpieces, eyebrow makeup, scalp micropigmentation",
            "Psychological support: counseling, support groups (National Alopecia Areata Foundation)",
            "No treatment needed if asymptomatic and patient comfortable"
        ],
        "pitfalls": [
            "Tinea capitis: fungal infection, look for scaling, erythema, broken hairs at scalp surface, KOH prep positive",
            "Trichotillomania: hair-pulling disorder, irregular patches, hairs of varying lengths, often frontal/parietal, psych history",
            "Telogen effluvium: diffuse thinning (not patchy), post-stressful event/illness, resolves spontaneously",
            "Scarring alopecia: permanent hair loss with scarring (lichen planopilaris, discoid lupus) - needs biopsy",
            "Ophiasis pattern: band-like loss at occipital/temporal margins - worse prognosis",
            "Nail changes: pitting, Beau's lines, onycholysis - present in 10-20%, suggests more extensive disease",
            "Monitor thyroid: screen TSH even if history negative (high association with thyroid disease)"
        ],
        "tags": ["alopecia areata", "hair loss", "autoimmune", "dermatology"],
        "created_at": "2025-12-30T00:30:00.000000",
        "author": "Dr. Dermatology"
    }
]

# Add to database
data['cases'].extend(new_cases)

# Save
with open('backend/data/clinical_cases.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"✓ Successfully added cases 91-97")
print(f"✓ Total cases in database: {len(data['cases'])}")
print(f"✓ Case range: CASE-001 to CASE-{len(data['cases']):03d}")

# Verify no duplicates
from collections import Counter
diagnoses = [c['correct_diagnosis'] for c in data['cases']]
duplicate_diagnoses = {k: v for k, v in Counter(diagnoses).items() if v > 1}

if duplicate_diagnoses:
    print("\n⚠️  WARNING: Duplicate diagnoses found:")
    for diag, count in duplicate_diagnoses.items():
        print(f"  {diag}: {count} cases")
else:
    print("\n✓ All diagnoses are unique")
