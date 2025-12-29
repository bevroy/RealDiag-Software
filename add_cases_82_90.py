#!/usr/bin/env python3
"""
Add clinical cases 82-90 to the database
Block 1 of 2
"""

import json

with open('backend/data/clinical_cases.json', 'r') as f:
    data = json.load(f)

print(f"Current total: {len(data['cases'])} cases")

# Cases 82-90
new_cases = [
    {
        "case_id": "CASE-082",
        "title": "Woman with Painful Urination and Flank Pain",
        "specialty": "nephrology",
        "difficulty": "intermediate",
        "learning_objectives": [
            "Recognize acute pyelonephritis presentation",
            "Differentiate from uncomplicated UTI",
            "Determine admission vs outpatient management"
        ],
        "presentation": "28-year-old woman with 2 days of dysuria, fever, and right flank pain",
        "history": {
            "chief_complaint": "Fever, painful urination, and back pain",
            "hpi": "Started with typical UTI symptoms 3 days ago - burning with urination, frequency. Yesterday developed fever to 102.5°F, chills, severe right flank pain. Nausea with two episodes vomiting. Unable to keep down food/fluids. Back pain constant, radiates to groin. No vaginal discharge.",
            "pmh": "Recurrent UTIs (3 in past year)",
            "medications": "Oral contraceptive pills",
            "social": "Sexually active, works as nurse",
            "family": "Non-contributory"
        },
        "physical_exam": {
            "vitals": "Temp 102.8°F, HR 108, BP 102/68, RR 20",
            "general": "Appears ill, in moderate distress",
            "abdomen": "Suprapubic tenderness, positive right CVA tenderness",
            "back": "Severe tenderness right costovertebral angle",
            "pelvic": "No cervical motion tenderness, no adnexal masses"
        },
        "labs": {
            "urinalysis": "Cloudy, pH 6.8, positive leukocyte esterase and nitrites, WBC >100/hpf, moderate bacteria, WBC casts present",
            "urine_culture": "Pending (will grow >100,000 CFU/mL E. coli)",
            "cbc": "WBC 16,800 with left shift",
            "bmp": "Cr 1.3 (baseline 0.9)",
            "blood_cultures": "Drawn (pending)"
        },
        "imaging": {
            "renal_ultrasound": "Normal size kidneys, no hydronephrosis, no stones visible"
        },
        "correct_diagnosis": "NEPHRO-ACUTE-PYELONEPHRITIS",
        "differential": [
            "NEPHRO-ACUTE-PYELONEPHRITIS",
            "GU-NEPHROLITHIASIS",
            "GYN-PID",
            "GI-APPENDICITIS"
        ],
        "explanation": "Acute pyelonephritis: upper urinary tract infection involving renal parenchyma and collecting system. Classic triad: fever, flank pain, nausea/vomiting. Progression from cystitis when bacteria ascend from bladder. E. coli most common (80%). Key distinguishing features from cystitis: systemic symptoms (fever, chills, vomiting), CVA tenderness, WBC casts in urine (indicate renal inflammation). Risk factors: female gender, sexual activity, anatomic abnormalities, prior UTIs.",
        "management_pearls": [
            "Admission criteria: unable to tolerate PO, severe illness, pregnancy, suspected sepsis, immunocompromised, uncertain diagnosis",
            "Outpatient treatment (mild cases): Ciprofloxacin 500mg PO BID x 7 days OR Levofloxacin 750mg daily x 5 days",
            "Inpatient treatment: Ceftriaxone 1-2g IV daily OR Fluoroquinolone IV, transition to PO when afebrile 24-48h",
            "If gram-positive cocci on gram stain: add Ampicillin for Enterococcus coverage",
            "Antiemetics: Ondansetron 4-8mg IV/PO q8h PRN",
            "IV fluids for hydration",
            "Blood cultures before antibiotics if admitted",
            "Repeat urine culture after treatment completion if symptoms persist",
            "Imaging (CT urogram) if: no improvement 48-72h, recurrent pyelonephritis, suspected obstruction"
        ],
        "pitfalls": [
            "Emphysematous pyelonephritis: diabetics, gas in renal tissue on CT - life-threatening, may need nephrectomy",
            "Xanthogranulomatous pyelonephritis: chronic obstruction with staghorn calculus, destructive process",
            "Renal abscess: persistent fever despite antibiotics, needs CT and possible drainage",
            "Pregnancy: always admit, IV antibiotics, increased preterm labor risk",
            "Complicated pyelonephritis: diabetes, obstruction, immunosuppression - needs longer treatment (14 days)",
            "Papillary necrosis: diabetics, sickle cell, analgesic abuse - necrotic papillae in urine"
        ],
        "tags": ["pyelonephritis", "UTI", "nephrology", "kidney infection"],
        "created_at": "2025-12-29T22:00:00.000000",
        "author": "Dr. Nephrology"
    },
    
    {
        "case_id": "CASE-083",
        "title": "Man with Dizziness When Standing",
        "specialty": "cardiology",
        "difficulty": "intermediate",
        "learning_objectives": [
            "Recognize orthostatic hypotension",
            "Identify medication-related causes",
            "Prevent falls in elderly"
        ],
        "presentation": "75-year-old man with recurrent lightheadedness upon standing, one fall",
        "history": {
            "chief_complaint": "Dizzy every time I stand up, fell yesterday",
            "hpi": "Progressive lightheadedness for 2 weeks, occurs within seconds of standing from sitting/lying. Vision darkens, feels like passing out. Symptoms resolve after sitting back down. Yesterday fell in bathroom after standing from toilet, hit head but no loss of consciousness. No chest pain, palpitations, or shortness of breath. Recently started new blood pressure medication.",
            "pmh": "Hypertension, type 2 diabetes, BPH, Parkinson disease",
            "medications": "Amlodipine 10mg (started 3 weeks ago), lisinopril 20mg, metformin 1000mg BID, tamsulosin 0.4mg, carbidopa-levodopa 25/100 TID",
            "social": "Lives alone, former smoker",
            "family": "Father had stroke"
        },
        "physical_exam": {
            "vitals_supine": "BP 148/88, HR 72",
            "vitals_standing": "BP 102/64 (after 3 min standing), HR 76",
            "general": "Elderly man, slight tremor at rest",
            "neurologic": "Bradykinesia, mild rigidity, no focal deficits, gait shuffling",
            "cardiovascular": "Regular rate and rhythm, no murmurs",
            "head": "Small laceration on forehead from fall"
        },
        "labs": {
            "cbc": "Normal",
            "bmp": "Na 138, K 4.2, Cr 1.1, glucose 142",
            "tsh": "Normal"
        },
        "imaging": {
            "ct_head": "No acute intracranial hemorrhage or fracture from fall"
        },
        "correct_diagnosis": "CARDIO-ORTHOSTATIC-HYPOTENSION",
        "differential": [
            "CARDIO-ORTHOSTATIC-HYPOTENSION",
            "CARDIO-ARRHYTHMIA",
            "NEURO-VERTEBROBASILAR-INSUFFICIENCY",
            "ENDO-ADRENAL-INSUFFICIENCY"
        ],
        "explanation": "Orthostatic hypotension: sustained BP drop ≥20 mmHg systolic or ≥10 mmHg diastolic within 3 minutes of standing. Caused by failure of compensatory mechanisms (vasoconstriction, HR increase). Classic symptoms: lightheadedness, dizziness, syncope, falls - worse in morning, after meals, in heat. This patient has multiple risk factors: age, Parkinson's (autonomic dysfunction), polypharmacy (CCB, ACE-I, alpha-blocker for BPH, levodopa). Significant fall risk in elderly.",
        "management_pearls": [
            "Medication review: taper/discontinue offending agents - consider stopping amlodipine (recently added), reduce tamsulosin",
            "Non-pharmacologic first-line:",
            "- Rise slowly from lying/sitting (sit at edge of bed 1-2 min before standing)",
            "- Compression stockings (thigh-high, 15-20 mmHg)",
            "- Increase salt intake 6-10g daily (if no heart failure)",
            "- Adequate hydration 2-3L daily",
            "- Elevate head of bed 30 degrees (reduces nocturnal natriuresis)",
            "- Physical counter-maneuvers: leg crossing, squatting, tensing muscles before standing",
            "- Eat smaller, frequent meals (avoid postprandial hypotension)",
            "Pharmacologic (if non-pharm fails):",
            "- Fludrocortisone 0.1-0.2mg daily (mineralocorticoid, expands volume)",
            "- Midodrine 2.5-10mg TID (alpha agonist, vasoconstriction) - avoid evening dose",
            "Fall prevention: remove home hazards, PT evaluation, assistive devices"
        ],
        "pitfalls": [
            "Parkinson's disease: 30-50% have orthostatic hypotension (autonomic dysfunction)",
            "Diabetes: autonomic neuropathy causes OH - check for other autonomic symptoms",
            "Supine hypertension: paradoxical lying hypertension with standing hypotension - difficult to manage",
            "Dehydration: volume depletion worsens OH - assess volume status",
            "Postprandial hypotension: BP drops after eating (splanchnic vasodilation) - smaller meals, caffeine before eating",
            "Cardiac causes: arrhythmias, aortic stenosis, heart failure - may need ECG, echo"
        ],
        "tags": ["orthostatic hypotension", "falls", "syncope", "elderly", "cardiology"],
        "created_at": "2025-12-29T22:10:00.000000",
        "author": "Dr. Geriatrics"
    },
    
    {
        "case_id": "CASE-084",
        "title": "Child with Severe Sore Throat and Drooling",
        "specialty": "emergency medicine",
        "difficulty": "advanced",
        "learning_objectives": [
            "Recognize epiglottitis as medical emergency",
            "Differentiate from croup",
            "Understand airway management"
        ],
        "presentation": "4-year-old with high fever, severe sore throat, difficulty swallowing, drooling",
        "history": {
            "chief_complaint": "Can't swallow, drooling, very sick",
            "hpi": "Developed sore throat and fever to 104°F this morning. Rapidly progressive over 6 hours. Now refusing to eat/drink, drooling excessively, sitting leaning forward with chin up. Muffled voice. Parents very concerned - child looks very ill. No barking cough. Immunization status uncertain (recent immigrants).",
            "pmh": "Healthy previously",
            "medications": "None",
            "social": "Recent immigrants, unclear vaccine history",
            "family": "Parents and siblings well"
        },
        "physical_exam": {
            "vitals": "Temp 103.8°F, HR 148, RR 32, O2 sat 94% on RA",
            "general": "Toxic-appearing child, anxious, sitting upright in tripod position, leaning forward with chin extended, drooling",
            "oropharynx": "NOT EXAMINED - avoid agitating child or examining throat with tongue depressor (can precipitate complete airway obstruction)",
            "neck": "No stridor at rest initially, inspiratory stridor develops",
            "voice": "Muffled 'hot potato' voice"
        },
        "labs": {
            "none_initially": "Do NOT delay treatment for labs - airway emergency"
        },
        "imaging": {
            "lateral_neck_xray": "Only if child stable - 'thumbprint sign' (swollen epiglottis). Portable with physician present. NOT NECESSARY for diagnosis if clinical suspicion high."
        },
        "correct_diagnosis": "ENT-EPIGLOTTITIS-SUPRAGLOTTITIS",
        "differential": [
            "ENT-EPIGLOTTITIS-SUPRAGLOTTITIS",
            "PEDS-CROUP",
            "ENT-PERITONSILLAR-ABSCESS",
            "ENT-RETROPHARYNGEAL-ABSCESS"
        ],
        "explanation": "Acute epiglottitis (supraglottitis): life-threatening emergency from bacterial infection causing rapid epiglottic swelling → airway obstruction. Most common organism: Haemophilus influenzae type B (now rare with Hib vaccine), also Group A Strep, pneumococcus. Classic 4 D's: Drooling, Dysphagia, Distress, Dysphonia (muffled voice). Child prefers sitting upright, tripod position (maximizes airway). Toxic appearance distinguishes from croup. Peak age 2-7 years. AIRWAY EMERGENCY - can progress to complete obstruction in hours.",
        "management_pearls": [
            "DO NOT: examine throat, lay child flat, agitate child, leave child unattended, obtain labs/IV before securing airway",
            "IMMEDIATE: Call ENT, anesthesia, PICU - prepare for emergency airway",
            "Keep child calm, sitting upright in parent's arms, allow position of comfort",
            "Supplemental O2 (blow-by if child tolerates)",
            "Transport to OR for controlled intubation by anesthesia/ENT (most experienced provider)",
            "Equipment ready: various ETT sizes, surgical airway kit, emergency tracheostomy tray",
            "After airway secured:",
            "- Blood cultures",
            "- IV antibiotics: Ceftriaxone 50mg/kg (covers H. flu, Strep) OR Cefotaxime",
            "- Dexamethasone 0.6mg/kg to reduce edema",
            "- ICU admission, sedation while intubated",
            "- Usually extubate after 24-48h when edema resolves",
            "- Rifampin prophylaxis for household contacts (if H. flu)"
        ],
        "pitfalls": [
            "Croup vs epiglottitis: croup has barking cough, gradual onset, less toxic, no drooling, viral",
            "DO NOT examine throat: can precipitate laryngospasm and complete obstruction",
            "Adult epiglottitis: slower progression, may present with just severe sore throat, can often be managed without intubation",
            "Retropharyngeal abscess: similar presentation but lateral neck XR shows prevertebral soft tissue swelling",
            "Bacterial tracheitis: post-viral, purulent secretions, more gradual than epiglottitis"
        ],
        "tags": ["epiglottitis", "airway emergency", "pediatric emergency", "ENT"],
        "created_at": "2025-12-29T22:20:00.000000",
        "author": "Dr. Pediatric Emergency"
    },
    
    {
        "case_id": "CASE-085",
        "title": "Woman with Painful Mouth Sores",
        "specialty": "dermatology",
        "difficulty": "intermediate",
        "learning_objectives": [
            "Recognize Stevens-Johnson syndrome",
            "Identify drug-induced severe reactions",
            "Understand urgent management"
        ],
        "presentation": "32-year-old with painful mouth sores, eye redness, and spreading rash after starting new antibiotic",
        "history": {
            "chief_complaint": "Painful mouth sores and blistering rash",
            "hpi": "Started trimethoprim-sulfamethoxazole 10 days ago for UTI. Five days ago developed fever, sore throat, conjunctivitis. Three days ago noticed painful mouth ulcers and red patches on chest. Rash now spreading to face, trunk, arms. Skin painful to touch, some areas blistering. Unable to eat/drink due to mouth pain. Eyes burning, photophobia.",
            "pmh": "HIV positive (CD4 350, viral load undetectable), on antiretroviral therapy",
            "medications": "TMP-SMX (recent), tenofovir-emtricitabine-efavirenz",
            "social": "Non-smoker, social alcohol",
            "family": "Non-contributory"
        },
        "physical_exam": {
            "vitals": "Temp 101.2°F, HR 102, BP 118/74",
            "general": "Ill-appearing, in pain",
            "skin": "Erythematous macules and patches with dusky centers on face, trunk, arms (~15% BSA). Areas of epidermal detachment with positive Nikolsky sign. Targetoid lesions present.",
            "mucosa": "Severe hemorrhagic crusting of lips. Painful erosions on buccal mucosa, tongue, soft palate. Cannot open mouth fully.",
            "eyes": "Bilateral conjunctival injection, purulent discharge, corneal clouding",
            "genitals": "Erosions on vulva"
        },
        "labs": {
            "cbc": "WBC 3,200 (leukopenia), lymphopenia",
            "cmp": "Mild transaminitis (ALT 88, AST 76)",
            "skin_biopsy": "Full-thickness epidermal necrosis, subepidermal blister formation"
        },
        "imaging": {
            "cxr": "Clear, no infiltrates"
        },
        "correct_diagnosis": "DERM-STEVENS-JOHNSON-SYNDROME",
        "differential": [
            "DERM-STEVENS-JOHNSON-SYNDROME",
            "DERM-TOXIC-EPIDERMAL-NECROLYSIS",
            "DERM-ERYTHEMA-MULTIFORME-MAJOR",
            "ID-STAPHYLOCOCCAL-SCALDED-SKIN"
        ],
        "explanation": "Stevens-Johnson syndrome (SJS): severe, life-threatening mucocutaneous reaction. Spectrum: SJS (<10% BSA), SJS-TEN overlap (10-30%), TEN (>30%). Drug-induced in 80%: sulfonamides (TMP-SMX most common), anticonvulsants (phenytoin, carbamazepine, lamotrigine), allopurinol, NSAIDs. Higher risk: HIV, HLA-B*1502 (carbamazepine), HLA-B*5801 (allopurinol). Key features: (1) Prodrome of fever, flu-like symptoms, (2) Mucosal involvement (oral, ocular, genital) - distinguishes from other drug reactions, (3) Painful skin lesions, targetoid, dusky centers, (4) Positive Nikolsky sign (lateral pressure causes skin sloughing), (5) Epidermal detachment. Mortality 5-15% for SJS, up to 50% for TEN.",
        "management_pearls": [
            "STOP offending drug IMMEDIATELY - most important intervention",
            "ICU or burn unit admission for supportive care",
            "Fluid resuscitation: similar to burns, Parkland formula if extensive",
            "Wound care: non-adherent dressings, maintain warm environment",
            "Ophthalmology consult urgently: daily eye exams, aggressive lubrication, prevent synechiae (can cause blindness)",
            "Pain control: IV opioids",
            "Nutrition: NG tube if oral intake inadequate",
            "Monitor for sepsis: skin barrier disrupted, high infection risk",
            "Controversial treatments:",
            "- IVIG 2-3 g/kg over 3-5 days (may reduce mortality, expensive)",
            "- Cyclosporine 3-5 mg/kg/day (anti-inflammatory)",
            "- Systemic corticosteroids (controversial - no clear benefit, may increase infection)",
            "Avoid: corticosteroid eye drops (worsen healing)"
        ],
        "pitfalls": [
            "TEN vs SJS: same disease spectrum, TEN >30% BSA detachment, higher mortality",
            "SCORTEN: prognostic score (age, HR, cancer, BSA, glucose, BUN, bicarb) predicts mortality",
            "Long-term sequelae: ocular (scarring, dry eye, blindness), cutaneous (pigment changes), vaginal stenosis, esophageal strictures",
            "Chronic ocular complications: most common long-term problem, needs ongoing ophthalmology",
            "Recurrence: avoid all cross-reactive drugs (all sulfonamides, all aromatic anticonvulsants)",
            "HIV patients: 100x increased risk with sulfonamides (avoid TMP-SMX if possible)"
        ],
        "tags": ["Stevens-Johnson syndrome", "SJS", "drug reaction", "dermatology", "emergency"],
        "created_at": "2025-12-29T22:30:00.000000",
        "author": "Dr. Dermatology"
    },
    
    {
        "case_id": "CASE-086",
        "title": "Man with Yellow Eyes and Dark Urine",
        "specialty": "hepatology",
        "difficulty": "intermediate",
        "learning_objectives": [
            "Differentiate causes of jaundice",
            "Interpret liver function tests and bilirubin",
            "Recognize acute hepatitis"
        ],
        "presentation": "45-year-old man with 1 week of jaundice, dark urine, fatigue, and RUQ discomfort",
        "history": {
            "chief_complaint": "Yellow eyes, dark urine, very tired",
            "hpi": "Progressive fatigue for 2 weeks. One week ago noticed urine turning dark brown, eyes and skin yellowing. Mild RUQ discomfort, no severe pain. Nausea, poor appetite, no vomiting. Stools lighter colored. No fever. Recent unprotected sexual contact 2 months ago. Denies IVDU. Tried new 'natural supplements' for bodybuilding 3 weeks ago.",
            "pmh": "No known liver disease, obese (BMI 32)",
            "medications": "Recently started herbal supplements (unknown composition)",
            "social": "Social drinker (2-3 beers weekly), works in restaurant, sexually active",
            "family": "No liver disease"
        },
        "physical_exam": {
            "vitals": "Temp 99.1°F, BP 128/82, HR 76",
            "general": "Jaundiced, appears fatigued",
            "heent": "Scleral icterus, sublingual jaundice",
            "abdomen": "Soft, mild RUQ tenderness, liver edge palpable 2cm below costal margin, no splenomegaly, no ascites",
            "skin": "Jaundice, no spider angiomata or palmar erythema",
            "neurologic": "Alert, oriented, no asterixis"
        },
        "labs": {
            "lfts": "AST 1,240 U/L, ALT 1,680 U/L, Alk Phos 198 U/L, Total bili 8.2 mg/dL (direct 6.1 mg/dL)",
            "hepatitis_serologies": "HBsAg positive, Anti-HBc IgM positive, Anti-HAV IgM negative, Anti-HCV negative",
            "coagulation": "PT 14.2 sec (INR 1.3), albumin 3.6 g/dL",
            "cbc": "WBC 7,200, Hgb 14.2, Plt 185,000"
        },
        "imaging": {
            "ruq_ultrasound": "Normal liver size and echotexture, patent vessels, no biliary dilatation, gallbladder normal"
        },
        "correct_diagnosis": "HEPATO-ACUTE-HEPATITIS-B",
        "differential": [
            "HEPATO-ACUTE-HEPATITIS-B",
            "HEPATO-ACUTE-HEPATITIS-A",
            "HEPATO-DRUG-INDUCED-HEPATITIS",
            "HEPATO-AUTOIMMUNE-HEPATITIS"
        ],
        "explanation": "Acute hepatitis B: liver inflammation from HBV infection. Transmission: sexual, parenteral, perinatal. Clinical course: (1) Incubation 45-180 days, (2) Prodrome: fatigue, anorexia, nausea, (3) Icteric phase: jaundice, dark urine, light stools, RUQ pain. Labs: markedly elevated transaminases (ALT>AST, 1000-5000), elevated bilirubin (conjugated>unconjugated). Serologies: HBsAg = active infection, Anti-HBc IgM = acute infection, HBeAg = high infectivity. Most adults clear infection (95%), some develop chronic (5%). Fulminant hepatic failure rare (0.5-1%) but life-threatening.",
        "management_pearls": [
            "Assess severity: check PT/INR, albumin, factor V (synthetic function), mental status (hepatic encephalopathy)",
            "Most cases: supportive care only, no specific antiviral needed for acute HBV",
            "Indications for antiviral (tenofovir or entecavir): severe acute hepatitis, protracted course, immunosuppressed",
            "Monitor: LFTs weekly until improving, PT/INR to assess liver function",
            "Avoid hepatotoxins: alcohol (strict abstinence), acetaminophen, NSAIDs, herbal supplements",
            "Adequate nutrition and hydration",
            "Antiemetics: ondansetron 4-8mg q8h PRN",
            "Cholestyramine for pruritus if significant",
            "Follow-up: repeat HBsAg at 6 months - if persistent, chronic HBV",
            "Contacts: test sexual/household contacts, vaccinate if non-immune",
            "Prevention: HBV vaccine series for susceptible individuals",
            "Admission criteria: coagulopathy (INR >1.5), encephalopathy, severe nausea/vomiting, bilirubin >15"
        ],
        "pitfalls": [
            "Fulminant hepatic failure: rapid development of coagulopathy + encephalopathy - needs transplant evaluation urgently",
            "Acute liver failure criteria: INR ≥1.5 + any hepatic encephalopathy within 26 weeks of disease onset in patient without cirrhosis",
            "Hepatitis D co-infection: in HBV patients, HDV requires HBV for replication, increases severity",
            "Drug-induced liver injury: herbal supplements (kava, green tea extract, anabolic steroids) can cause acute hepatitis - stop all supplements",
            "Autoimmune hepatitis: elevated IgG, ANA/SMA positive, needs biopsy and immunosuppression",
            "Chronic HBV: if HBsAg persists >6 months, monitor for cirrhosis/HCC, may need antiviral"
        ],
        "tags": ["hepatitis B", "jaundice", "hepatology", "liver disease"],
        "created_at": "2025-12-29T22:40:00.000000",
        "author": "Dr. Hepatology"
    },
    
    {
        "case_id": "CASE-087",
        "title": "Teenager with Knee Pain After Sports",
        "specialty": "sports medicine",
        "difficulty": "beginner",
        "learning_objectives": [
            "Recognize ACL injury presentation",
            "Understand knee examination maneuvers",
            "Distinguish from other knee injuries"
        ],
        "presentation": "16-year-old male with acute knee pain, swelling, instability after basketball injury",
        "history": {
            "chief_complaint": "Knee popped and gave out during basketball",
            "hpi": "Playing basketball yesterday, planted left foot to pivot and felt sudden 'pop' in knee with immediate severe pain. Knee swelled within 2 hours. Today knee feels unstable, 'gives way' when walking. Cannot bear full weight. Iced overnight with some relief. No prior knee injuries.",
            "pmh": "Healthy, very active athlete",
            "medications": "Ibuprofen 600mg",
            "social": "High school varsity basketball player",
            "family": "Sister tore ACL playing soccer"
        },
        "physical_exam": {
            "vitals": "Temp 98.6°F, BP 118/72, HR 68",
            "left_knee": "Moderate effusion, limited flexion to 110° (pain), full extension. Tenderness along joint line. Positive Lachman test (increased anterior translation with soft endpoint). Positive anterior drawer test. Pivot shift test positive (apprehension, clunk). Negative posterior drawer. Negative varus/valgus stress at 0° and 30°. McMurray negative.",
            "right_knee": "Normal for comparison",
            "gait": "Antalgic, favoring left leg",
            "neurovascular": "Intact"
        },
        "labs": {
            "none_needed": "Clinical diagnosis"
        },
        "imaging": {
            "knee_xray": "No fracture, no tibial spine avulsion, normal joint space",
            "mri_knee": "Complete tear of ACL mid-substance, bone bruises in lateral femoral condyle and posterolateral tibial plateau, intact MCL/LCL, medial meniscus posterior horn tear"
        },
        "correct_diagnosis": "ORTHO-ACL-TEAR-COMPLETE",
        "differential": [
            "ORTHO-ACL-TEAR-COMPLETE",
            "ORTHO-MENISCUS-TEAR",
            "ORTHO-MCL-SPRAIN",
            "ORTHO-PCL-TEAR"
        ],
        "explanation": "Anterior cruciate ligament (ACL) tear: most common in athletes. Mechanism: non-contact deceleration with pivot/cutting, or direct blow to lateral knee. Classic presentation: audible 'pop', immediate pain and swelling (hemarthrosis within 2h), knee instability/giving way. ACL prevents anterior tibial translation and rotational instability. Associated injuries common (50%): meniscus tears (medial > lateral), bone bruises, MCL tear ('terrible triad' = ACL + MCL + medial meniscus). Physical exam: Lachman test most sensitive (85-95%), anterior drawer, pivot shift (most specific but difficult acutely).",
        "management_pearls": [
            "Acute management: RICE (rest, ice, compression, elevation), crutches for non-weight bearing, NSAIDs",
            "Orthopedic sports medicine referral within 1-2 weeks",
            "MRI to confirm diagnosis and assess for associated injuries",
            "Treatment options:",
            "1. Surgical reconstruction (ACL-R): preferred for young athletes, high activity level, knee instability, associated meniscus tear",
            "2. Non-operative: older, sedentary patients, partial tears, willing to modify activity",
            "Surgical technique: arthroscopic reconstruction using autograft (patellar tendon, hamstring) or allograft",
            "Timing of surgery: delay 2-4 weeks allows swelling to resolve, ROM to return (reduces arthrofibrosis risk)",
            "Pre-op PT: 'prehabilitation' - restore ROM, reduce swelling, quad strengthening",
            "Post-op rehab: 6-9 months return to sports, focus on quad/hamstring strengthening, proprioception",
            "Bracing: functional ACL brace for return to sports (debated efficacy)"
        ],
        "pitfalls": [
            "Terrible triad: ACL + MCL + medial meniscus tear - worse prognosis, more complex surgery",
            "Segond fracture: lateral tibial avulsion fracture on XR - highly specific for ACL tear (75-100%)",
            "PCL tear: less common, posterior drawer positive, dashboard injury mechanism",
            "Meniscus tears: McMurray test, joint line tenderness, locking/catching - often concurrent with ACL",
            "Arthrofibrosis: stiffness from early surgery before ROM restored - why delay surgery 2-4 weeks",
            "Second ACL injury: 15-20% risk, especially if return to sports too early"
        ],
        "tags": ["ACL tear", "knee injury", "sports medicine", "orthopedics"],
        "created_at": "2025-12-29T22:50:00.000000",
        "author": "Dr. Sports Medicine"
    },
    
    {
        "case_id": "CASE-088",
        "title": "Woman with Abnormal Vaginal Bleeding",
        "specialty": "gynecology",
        "difficulty": "intermediate",
        "learning_objectives": [
            "Evaluate abnormal uterine bleeding",
            "Recognize endometrial cancer risk",
            "Understand when to perform endometrial biopsy"
        ],
        "presentation": "52-year-old postmenopausal woman with irregular vaginal bleeding for 3 months",
        "history": {
            "chief_complaint": "Vaginal bleeding after not having periods for 2 years",
            "hpi": "Menopause at age 50 - no periods for 2 years. Three months ago started having irregular vaginal bleeding - sometimes spotting, sometimes heavier like period. Bleeding unpredictable, no pattern. No pain. Recently gained 25 lbs. No hormone replacement therapy.",
            "pmh": "Type 2 diabetes, hypertension, obesity (BMI 36), never pregnant (nulliparous)",
            "medications": "Metformin 1000mg BID, lisinopril 20mg",
            "social": "Non-smoker, sedentary lifestyle",
            "family": "Mother had 'female cancer' (details unknown)"
        },
        "physical_exam": {
            "vitals": "BP 142/88, HR 76, BMI 36",
            "general": "Obese woman, well-appearing",
            "abdomen": "Obese, soft, non-tender, no masses palpated",
            "pelvic": "External genitalia normal. Small amount blood in vaginal vault. Cervix normal appearing, no cervical motion tenderness. Uterus normal size, non-tender, no adnexal masses."
        },
        "labs": {
            "pregnancy_test": "Negative",
            "cbc": "Hgb 11.8 g/dL (mild anemia)",
            "tsh": "Normal"
        },
        "imaging": {
            "transvaginal_ultrasound": "Endometrial thickness 14mm (abnormal for postmenopausal, normal <4-5mm). No adnexal masses. Normal ovaries."
        },
        "correct_diagnosis": "GYN-ENDOMETRIAL-HYPERPLASIA-CANCER",
        "differential": [
            "GYN-ENDOMETRIAL-HYPERPLASIA-CANCER",
            "GYN-ENDOMETRIAL-POLYP",
            "GYN-CERVICAL-CANCER",
            "GYN-ATROPHIC-VAGINITIS"
        ],
        "explanation": "Postmenopausal bleeding (PMB): any vaginal bleeding >12 months after menopause. Endometrial cancer until proven otherwise (5-10% of PMB cases). Risk factors for endometrial cancer: obesity (peripheral aromatization of androgens to estrogen), nulliparity, diabetes, unopposed estrogen (PCOS, tamoxifen, HRT without progesterone), Lynch syndrome. Endometrial hyperplasia: precursor to cancer, caused by excess estrogen. Transvaginal ultrasound: endometrial thickness >4-5mm in postmenopausal woman warrants biopsy. This patient has multiple risk factors: obesity, nulliparity, diabetes.",
        "management_pearls": [
            "Endometrial biopsy MANDATORY in: all postmenopausal bleeding, premenopausal >45 with abnormal uterine bleeding + risk factors, endometrial thickness >4-5mm on TVUS",
            "Office endometrial biopsy: Pipelle device, quick outpatient procedure, 90% sensitive for cancer",
            "If biopsy shows:",
            "- Atrophy/benign: reassure, consider low-dose vaginal estrogen if atrophic vaginitis",
            "- Endometrial hyperplasia without atypia: progesterone therapy (Mirena IUD or medroxyprogesterone), repeat biopsy in 3-6 months",
            "- Endometrial hyperplasia with atypia: gynecologic oncology referral, high risk of concurrent cancer (30-50%), may need hysterectomy",
            "- Endometrial cancer: staging, surgery (TAH-BSO), possible chemotherapy/radiation",
            "If biopsy insufficient/negative but bleeding persists: hysteroscopy with D&C for better sampling",
            "Management of risk factors: weight loss, metformin (may reduce cancer risk in diabetics)"
        ],
        "pitfalls": [
            "Never attribute PMB to atrophy without tissue diagnosis - must rule out cancer first",
            "HRT: estrogen-only in women without uterus; estrogen+progesterone if uterus intact (progesterone protects endometrium)",
            "Tamoxifen: increases endometrial cancer risk 2-3x - monitor closely, any bleeding needs biopsy",
            "Lynch syndrome: hereditary cancer syndrome, high endometrial/colon cancer risk - screen family history",
            "Inadequate biopsy: if not enough tissue obtained and bleeding persists, must do D&C",
            "Premenopausal AUB: different algorithm, depends on age and risk factors"
        ],
        "tags": ["postmenopausal bleeding", "endometrial cancer", "abnormal uterine bleeding", "gynecology"],
        "created_at": "2025-12-29T23:00:00.000000",
        "author": "Dr. Gynecology"
    },
    
    {
        "case_id": "CASE-089",
        "title": "Man with Chest Tightness During Exercise",
        "specialty": "cardiology",
        "difficulty": "intermediate",
        "learning_objectives": [
            "Recognize stable angina presentation",
            "Understand stress testing indications",
            "Manage chronic stable angina"
        ],
        "presentation": "62-year-old man with 3 months of chest tightness with exertion, relieved by rest",
        "history": {
            "chief_complaint": "Chest tightness when walking uphill or climbing stairs",
            "hpi": "Progressive chest discomfort for 3 months. Occurs predictably with exertion - walking uphill, climbing 2 flights stairs, heavy lifting. Described as tightness/pressure across chest, no radiation. Resolves within 5 minutes of rest. No pain at rest. No shortness of breath at rest. Recently more frequent, now occurs with less exertion than before. No nausea, diaphoresis, or syncope.",
            "pmh": "Hypertension, hyperlipidemia, type 2 diabetes, former smoker",
            "medications": "Lisinopril 20mg, atorvastatin 40mg, metformin 1000mg BID, aspirin 81mg",
            "social": "Quit smoking 5 years ago (30 pack-year history), walks dog daily",
            "family": "Father had MI at age 58"
        },
        "physical_exam": {
            "vitals": "BP 148/88, HR 72, RR 14, BMI 29",
            "general": "Overweight man, no acute distress at rest",
            "cardiovascular": "Regular rate and rhythm, no murmurs, no S3/S4, no JVD",
            "lungs": "Clear to auscultation",
            "extremities": "No edema, distal pulses present"
        },
        "labs": {
            "fasting_lipids": "Total chol 185, LDL 105, HDL 38, TG 210",
            "hba1c": "7.2%",
            "troponin": "Negative (drawn at rest, asymptomatic)",
            "ecg_rest": "Normal sinus rhythm, no ST changes, no Q waves"
        },
        "imaging": {
            "cxr": "Cardiomegaly, no acute disease",
            "stress_test": "Exercise stress test: stopped at 7 METS due to chest tightness. 1.5mm ST depression in leads II, III, aVF, V4-V6. Symptoms and EKG changes resolved with rest."
        },
        "correct_diagnosis": "CARDIO-STABLE-ANGINA-CAD",
        "differential": [
            "CARDIO-STABLE-ANGINA-CAD",
            "GI-GERD",
            "PULM-PULMONARY-HYPERTENSION",
            "MSK-COSTOCHONDRITIS"
        ],
        "explanation": "Stable angina pectoris: chest discomfort from myocardial ischemia due to fixed coronary stenosis (typically >70%). Classic presentation: predictable, exertional substernal chest pressure/tightness, relieved by rest or nitroglycerin within 5 minutes. Pathophysiology: oxygen demand exceeds supply during exertion. Risk factors: smoking, diabetes, hypertension, hyperlipidemia, family history. Positive stress test: exercise-induced ST depression + symptoms confirms diagnosis. Canadian Cardiovascular Society (CCS) classification: Class II (slight limitation, symptoms with strenuous activity).",
        "management_pearls": [
            "Coronary angiography: gold standard to assess severity, determine if PCI or CABG needed",
            "Medical therapy (all patients):",
            "- Antiplatelet: aspirin 81mg daily (if already on, continue)",
            "- Statin: high-intensity (atorvastatin 80mg or rosuvastatin 40mg) - goal LDL <70",
            "- ACE inhibitor: continue lisinopril",
            "- Beta-blocker: metoprolol 25-50mg BID (first-line anti-anginal, improves mortality)",
            "Symptomatic relief:",
            "- Sublingual nitroglycerin 0.4mg PRN for angina (call 911 if not resolved after 3 doses 5 min apart)",
            "- Long-acting nitrate: isosorbide mononitrate 30-60mg daily (if frequent symptoms)",
            "- Calcium channel blocker: amlodipine 5-10mg daily (if beta-blocker contraindicated or inadequate)",
            "- Ranolazine: if refractory to above",
            "Lifestyle: cardiac rehab, Mediterranean diet, exercise, weight loss, strict BP/glucose control",
            "Revascularization: PCI or CABG if refractory to medical therapy, high-risk anatomy (left main, 3-vessel disease)"
        ],
        "pitfalls": [
            "Unstable angina: new-onset, crescendo pattern, rest symptoms - acute coronary syndrome, needs urgent catheterization",
            "Variant (Prinzmetal) angina: coronary vasospasm, often at rest/early morning, ST elevation during episode, responds to CCB/nitrates",
            "Microvascular angina (syndrome X): typical angina, positive stress test, normal coronaries on angiography - treat with BB, CCB, nitrates",
            "GERD vs angina: can be difficult to distinguish, may need GI workup if atypical features",
            "Adequate beta-blockade: goal resting HR 55-60, check compliance",
            "Women and elderly: atypical presentations more common (dyspnea, fatigue without chest pain)"
        ],
        "tags": ["stable angina", "CAD", "chest pain", "cardiology", "ischemic heart disease"],
        "created_at": "2025-12-29T23:10:00.000000",
        "author": "Dr. Cardiology"
    },
    
    {
        "case_id": "CASE-090",
        "title": "Child with Limp and Hip Pain",
        "specialty": "pediatric orthopedics",
        "difficulty": "intermediate",
        "learning_objectives": [
            "Recognize transient synovitis presentation",
            "Differentiate from septic arthritis",
            "Understand Kocher criteria"
        ],
        "presentation": "5-year-old boy with acute limp and refusal to bear weight on right leg",
        "history": {
            "chief_complaint": "Won't walk on right leg, says hip hurts",
            "hpi": "Woke up this morning complaining of right hip/thigh pain. Refuses to walk, cries when moved. No history of trauma or injury. Had viral URI with low-grade fevers 1 week ago, now resolved. No recent long trips. Appears uncomfortable but playful when sitting still. Eating and drinking normally.",
            "pmh": "Healthy, up to date on vaccinations",
            "medications": "Acetaminophen given today for pain",
            "social": "Attends preschool",
            "family": "No similar issues in family"
        },
        "physical_exam": {
            "vitals": "Temp 99.2°F, HR 98, RR 20",
            "general": "Well-appearing child when sitting, anxious about moving leg",
            "right_hip": "Limited ROM, especially internal rotation and abduction. Painful with passive ROM. Refuses to bear weight. No erythema, warmth, or swelling visible. No point tenderness over hip.",
            "left_hip": "Normal ROM, no pain",
            "spine": "Non-tender",
            "neurologic": "Normal, can move toes, sensation intact",
            "gait": "Refuses to walk"
        },
        "labs": {
            "wbc": "8,400 (normal)",
            "esr": "18 mm/hr (mildly elevated)",
            "crp": "0.8 mg/dL (normal <1.0)"
        },
        "imaging": {
            "hip_xray": "Normal bilateral hips, no fracture, no effusion visible, femoral heads normal",
            "hip_ultrasound": "Small effusion in right hip joint, no loculations"
        },
        "correct_diagnosis": "PEDS-ORTHO-TRANSIENT-SYNOVITIS",
        "differential": [
            "PEDS-ORTHO-TRANSIENT-SYNOVITIS",
            "ORTHO-SEPTIC-ARTHRITIS-HIP",
            "PEDS-LEGG-CALVE-PERTHES",
            "PEDS-SLIPPED-CAPITAL-FEMORAL-EPIPHYSIS"
        ],
        "explanation": "Transient synovitis (toxic synovitis): most common cause of acute hip pain in children age 3-8 years. Benign, self-limited inflammatory condition. Often follows viral URI by 1-2 weeks. Presents with acute hip pain, limp, refusal to bear weight, limited ROM (especially internal rotation/abduction). Kocher criteria predict septic arthritis risk: (1) fever >38.5°C, (2) non-weight bearing, (3) ESR >40, (4) WBC >12,000. Score 0: <0.2% septic; Score 4: >99% septic. This patient scores 1 (non-weight bearing only) = low risk.",
        "management_pearls": [
            "Kocher criteria: use to assess septic arthritis probability (must rule out septic joint - orthopedic emergency)",
            "Transient synovitis management:",
            "- Supportive care: rest, NSAIDs (ibuprofen 10mg/kg q6h)",
            "- Activity as tolerated, gradual return to normal",
            "- Symptoms typically resolve in 1-2 weeks",
            "- Follow-up in 2-3 days to ensure improvement",
            "If high suspicion for septic arthritis (Kocher ≥3, ill-appearing, high fever): urgent orthopedic consult for joint aspiration",
            "Joint aspiration (if performed): synovial fluid WBC >50,000 suggests septic arthritis",
            "Red flags requiring further workup: persistent symptoms >2 weeks (consider Legg-Calvé-Perthes), obese adolescent (consider SCFE)",
            "Return precautions: worsening pain, fever, inability to walk after several days"
        ],
        "pitfalls": [
            "Septic arthritis: EMERGENCY - fever, toxic appearance, very elevated WBC/ESR/CRP, severe pain - needs urgent aspiration and IV antibiotics",
            "Legg-Calvé-Perthes disease: avascular necrosis of femoral head, age 4-8, more insidious, XR shows flattened femoral head (may be normal early) - needs MRI",
            "SCFE: obese adolescent (age 10-16), chronic hip/knee pain, externally rotated leg, XR shows posterior/inferior displacement of epiphysis - needs urgent pinning",
            "Osteomyelitis: bone infection, more systemic symptoms, point tenderness over metaphysis, MRI shows bone changes",
            "Reactive arthritis: post-GI/GU infection, multiple joints, conjunctivitis, urethritis",
            "Do NOT miss septic arthritis: can destroy joint in 24-48h, high morbidity if delayed"
        ],
        "tags": ["transient synovitis", "hip pain", "pediatric limp", "pediatric orthopedics"],
        "created_at": "2025-12-29T23:20:00.000000",
        "author": "Dr. Pediatric Orthopedics"
    }
]

# Add to database
data['cases'].extend(new_cases)

# Save
with open('backend/data/clinical_cases.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"✓ Successfully added cases 82-90")
print(f"✓ Total cases in database: {len(data['cases'])}")
print(f"✓ Case range: CASE-001 to CASE-{len(data['cases']):03d}")
