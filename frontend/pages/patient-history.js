import React, { useState, useEffect, useRef } from 'react'
import styles from '../styles/PatientHistory.module.css'
import RoleBasedNavigation from '../components/RoleBasedNavigation'
import PageHeader from '../components/PageHeader'

export default function PatientHistory() {
  const [apiBase, setApiBase] = useState('')
  const [showNav, setShowNav] = useState(false)
  const [searchTerms, setSearchTerms] = useState({})
  const [patientData, setPatientData] = useState({
    patient_id: '',
    patient_name: '',
    age: '',
    gender: '',
    vital_signs: [],
    visit_notes: [],
    diagnostic_tests: [],
    history_and_physicals: [],
    procedures: [],
    imaging_studies: [],
    active_conditions: [],
    current_medications: [],
    allergies: [],
    family_history: '',
    social_history: ''
  })
  
  const [currentSection, setCurrentSection] = useState('demographics')
  const [savedMessage, setSavedMessage] = useState('')
  const [medicationSafetyResult, setMedicationSafetyResult] = useState(null)
  const [showSafetyModal, setShowSafetyModal] = useState(false)
  const [checkingSafety, setCheckingSafety] = useState(false)

  // Get API base
  useEffect(() => {
    const runtimeConfig = (typeof window !== 'undefined' && window.__RUNTIME_CONFIG) ? window.__RUNTIME_CONFIG : null
    const base = runtimeConfig?.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com'
    setApiBase(base.replace(/\/$/, ''))
  }, [])

  // Dropdown options
  const VISIT_NOTE_TYPES = [
    'Admission Note',
    'Consultation Note',
    'Discharge Summary',
    'Emergency Department Note',
    'Follow-up Note',
    'Observation Note',
    'Pre-operative Note',
    'Post-operative Note',
    'Procedure Note',
    'Progress Note',
    'Referral Note',
    'Telephone Encounter',
    'Transfer Note'
  ]

  const SPECIALTIES = [
    'Allergy & Immunology',
    'Anesthesiology',
    'Cardiology',
    'Critical Care',
    'Dermatology',
    'Emergency Medicine',
    'Endocrinology',
    'Family Medicine',
    'Gastroenterology',
    'General Surgery',
    'Geriatrics',
    'Hematology',
    'Hospitalist',
    'Infectious Disease',
    'Internal Medicine',
    'Nephrology',
    'Neurology',
    'Neurosurgery',
    'Obstetrics & Gynecology',
    'Oncology',
    'Ophthalmology',
    'Orthopedic Surgery',
    'Otolaryngology (ENT)',
    'Pain Medicine',
    'Palliative Care',
    'Pathology',
    'Pediatrics',
    'Physical Medicine & Rehabilitation',
    'Plastic Surgery',
    'Psychiatry',
    'Pulmonology',
    'Radiology',
    'Rheumatology',
    'Thoracic Surgery',
    'Urology',
    'Vascular Surgery'
  ]

  const TEST_TYPES = [
    'Chemistry',
    'Coagulation',
    'Culture',
    'Cytology',
    'Genetic',
    'Hematology',
    'Immunology',
    'Laboratory',
    'Microbiology',
    'Molecular',
    'Pathology',
    'Serology',
    'Toxicology',
    'Urinalysis'
  ]

  // Common lab tests (most frequently ordered)
  const COMMON_LAB_TESTS = [
    'Arterial Blood Gas (ABG)',
    'Basic Metabolic Panel (BMP)',
    'Blood Culture',
    'BNP/NT-proBNP',
    'Complete Blood Count (CBC)',
    'Comprehensive Metabolic Panel (CMP)',
    'C-Reactive Protein (CRP)',
    'D-Dimer',
    'Hemoglobin A1c',
    'Lipid Panel',
    'Liver Function Tests (LFTs)',
    'Prothrombin Time (PT/INR)',
    'Thyroid Stimulating Hormone (TSH)',
    'Troponin I/T',
    'Urinalysis',
    'Urine Culture'
  ]

  // Comprehensive lab tests (A-Z)
  const ALL_LAB_TESTS = [
    '5-HIAA (Urine)',
    'ACE (Angiotensin Converting Enzyme)',
    'Acetaminophen Level',
    'Acetylcholine Receptor Antibody',
    'Acid-Fast Bacilli (AFB) Smear',
    'ACTH (Adrenocorticotropic Hormone)',
    'Activated Clotting Time (ACT)',
    'Activated Protein C Resistance',
    'Adrenal Antibodies',
    'AFP (Alpha-Fetoprotein)',
    'Albumin',
    'Alcohol Level (Ethanol)',
    'Aldolase',
    'Aldosterone',
    'Alkaline Phosphatase (ALP)',
    'ALT (Alanine Aminotransferase)',
    'Ammonia',
    'Amylase',
    'ANA (Antinuclear Antibody)',
    'ANCA (Antineutrophil Cytoplasmic Antibodies)',
    'Androstenedione',
    'Angiotensin Converting Enzyme (ACE)',
    'Anion Gap',
    'Anti-CCP (Anti-Cyclic Citrullinated Peptide)',
    'Anti-DNase B',
    'Anti-dsDNA',
    'Antihistone Antibodies',
    'Anti-Mullerian Hormone (AMH)',
    'Antiphospholipid Antibodies',
    'Anti-Smooth Muscle Antibody',
    'Antistreptolysin O (ASO)',
    'Antithrombin III',
    'Anti-TPO (Thyroid Peroxidase Antibody)',
    'Apolipoprotein A1',
    'Apolipoprotein B',
    'Arterial Blood Gas (ABG)',
    'AST (Aspartate Aminotransferase)',
    'B-type Natriuretic Peptide (BNP)',
    'Basic Metabolic Panel (BMP)',
    'Basophil Count',
    'Beta-2 Microglobulin',
    'Beta-hCG (Pregnancy Test)',
    'Bicarbonate',
    'Bilirubin (Direct)',
    'Bilirubin (Indirect)',
    'Bilirubin (Total)',
    'Blood Culture',
    'Blood Type (ABO/Rh)',
    'BUN (Blood Urea Nitrogen)',
    'C-Peptide',
    'C-Reactive Protein (CRP)',
    'C3 Complement',
    'C4 Complement',
    'CA 15-3 (Cancer Antigen)',
    'CA 19-9 (Cancer Antigen)',
    'CA 27-29',
    'CA-125 (Cancer Antigen)',
    'Calcitonin',
    'Calcium (Ionized)',
    'Calcium (Total)',
    'Carbamazepine Level',
    'Carboxyhemoglobin',
    'Carcinoembryonic Antigen (CEA)',
    'Cardiolipin Antibodies (IgG, IgM)',
    'Carotene',
    'Catecholamines (Plasma)',
    'Catecholamines (Urine)',
    'CBC with Differential',
    'CD4 Count',
    'CD8 Count',
    'CEA (Carcinoembryonic Antigen)',
    'Celiac Panel (tTG-IgA)',
    'Ceruloplasmin',
    'Chloride',
    'Cholesterol (HDL)',
    'Cholesterol (LDL)',
    'Cholesterol (Total)',
    'Cholinesterase',
    'Chromogranin A',
    'Clostridium Difficile Toxin',
    'CMV IgG/IgM',
    'Coagulation Factor Assays',
    'Cold Agglutinins',
    'Complement (Total)',
    'Complete Blood Count (CBC)',
    'Complete Metabolic Panel (CMP)',
    'Coombs Test (Direct)',
    'Coombs Test (Indirect)',
    'Copper (Serum)',
    'Copper (Urine)',
    'Cortisol (AM)',
    'Cortisol (PM)',
    'Cortisol (Random)',
    'CPK (Creatine Phosphokinase)',
    'CPK-MB',
    'Creatine Kinase (CK)',
    'Creatinine',
    'Creatinine Clearance',
    'Cryoglobulins',
    'CSF Analysis (Cerebrospinal Fluid)',
    'Cyclosporine Level',
    'Cystatin C',
    'D-Dimer',
    'DHEA-Sulfate',
    'Digoxin Level',
    'Direct Bilirubin',
    'EBV IgG/IgM (Epstein-Barr Virus)',
    'Eosinophil Count',
    'Eosinophils (Absolute)',
    'Epinephrine',
    'Erythrocyte Sedimentation Rate (ESR)',
    'Erythropoietin (EPO)',
    'Estradiol',
    'Estrogen',
    'Ethanol Level',
    'Factor V Leiden Mutation',
    'Fecal Calprotectin',
    'Fecal Fat',
    'Fecal Occult Blood Test (FOBT)',
    'Ferritin',
    'Fibrin D-Dimer',
    'Fibrinogen',
    'Folate (Folic Acid)',
    'Follicle Stimulating Hormone (FSH)',
    'Free T3',
    'Free T4',
    'Fructosamine',
    'Fungal Culture',
    'Gamma-Glutamyl Transferase (GGT)',
    'Gastrin',
    'Gentamicin Level',
    'GFR (Glomerular Filtration Rate)',
    'Glucose (Fasting)',
    'Glucose (Random)',
    'Glucose Tolerance Test (GTT)',
    'Glycated Hemoglobin (HbA1c)',
    'Growth Hormone (GH)',
    'HAV IgM (Hepatitis A)',
    'HBsAg (Hepatitis B Surface Antigen)',
    'HBV DNA',
    'hCG (Human Chorionic Gonadotropin)',
    'HCV Antibody (Hepatitis C)',
    'HCV RNA',
    'HDL Cholesterol',
    'Hematocrit (Hct)',
    'Hemoglobin (Hgb)',
    'Hemoglobin A1c (HbA1c)',
    'Hemoglobin Electrophoresis',
    'Heparin Anti-Xa',
    'Hepatitis A Antibody',
    'Hepatitis B Core Antibody',
    'Hepatitis B Surface Antibody',
    'Hepatitis B Surface Antigen',
    'Hepatitis C Antibody',
    'HIV 1/2 Antibody',
    'HIV RNA (Viral Load)',
    'HLA-B27',
    'Homocysteine',
    'IgA',
    'IgE (Total)',
    'IgG',
    'IgM',
    'Immunofixation Electrophoresis',
    'Immunoglobulins',
    'Indirect Bilirubin',
    'INR (International Normalized Ratio)',
    'Insulin (Fasting)',
    'Insulin-Like Growth Factor (IGF-1)',
    'Iron (Serum)',
    'Iron Binding Capacity (TIBC)',
    'Lactate',
    'Lactate Dehydrogenase (LDH)',
    'Lead Level',
    'Legionella Antigen',
    'Lipase',
    'Lipoprotein (a)',
    'Lithium Level',
    'Liver Function Tests (LFTs)',
    'Luteinizing Hormone (LH)',
    'Lyme Disease Antibody',
    'Lymphocyte Count',
    'Magnesium',
    'MCH (Mean Corpuscular Hemoglobin)',
    'MCHC (Mean Corpuscular Hemoglobin Concentration)',
    'MCV (Mean Corpuscular Volume)',
    'Metanephrines (Plasma)',
    'Metanephrines (Urine)',
    'Methemoglobin',
    'Methylmalonic Acid',
    'Microalbumin (Urine)',
    'Monocyte Count',
    'Mycoplasma Pneumoniae IgM',
    'Myoglobin',
    'Neutrophil Count (Absolute)',
    'Norepinephrine',
    'NT-proBNP',
    'Osmolality (Serum)',
    'Osmolality (Urine)',
    'Osteocalcin',
    'Parathyroid Hormone (PTH)',
    'Partial Thromboplastin Time (PTT/aPTT)',
    'Parvovirus B19 IgM',
    'Phenobarbital Level',
    'Phenytoin Level',
    'Phosphate',
    'Phosphorus',
    'Platelet Count',
    'Pneumococcal Antigen',
    'Porphyrins',
    'Potassium',
    'Prealbumin',
    'Progesterone',
    'Prolactin',
    'Prostate Specific Antigen (PSA)',
    'Protein C',
    'Protein Electrophoresis (Serum)',
    'Protein Electrophoresis (Urine)',
    'Protein S',
    'Protein (Total)',
    'Prothrombin Gene Mutation',
    'Prothrombin Time (PT)',
    'Pyruvate Kinase',
    'Quantiferon-TB Gold',
    'Red Blood Cell Count (RBC)',
    'Renin',
    'Respiratory Pathogen Panel (PCR)',
    'Reticulocyte Count',
    'Rheumatoid Factor (RF)',
    'RPR (Syphilis)',
    'Salicylate Level',
    'Sedimentation Rate (ESR)',
    'Selenium',
    'SIADH Workup',
    'Sickle Cell Screen',
    'Sodium',
    'Sputum Culture',
    'Stool Culture',
    'Strep Throat Test (Rapid)',
    'T3 (Total)',
    'T3 (Free)',
    'T4 (Total)',
    'T4 (Free)',
    'Tacrolimus Level',
    'Testosterone (Free)',
    'Testosterone (Total)',
    'Theophylline Level',
    'Throat Culture',
    'Thrombin Time',
    'Thyroglobulin',
    'Thyroid Antibodies',
    'Thyroid Stimulating Hormone (TSH)',
    'TIBC (Total Iron Binding Capacity)',
    'Tobramycin Level',
    'Toxoplasma IgG/IgM',
    'Transferrin',
    'Transferrin Saturation',
    'Triglycerides',
    'Troponin I',
    'Troponin T',
    'Tryptase',
    'TSH (Thyroid Stimulating Hormone)',
    'Tuberculosis (TB) Culture',
    'Uric Acid',
    'Urinalysis',
    'Urine Culture',
    'Urine Electrolytes',
    'Urine Protein',
    'Valproic Acid Level',
    'Varicella IgG',
    'VDRL (Syphilis)',
    'Venous Blood Gas (VBG)',
    'Viral Culture',
    'Vitamin A',
    'Vitamin B1 (Thiamine)',
    'Vitamin B12',
    'Vitamin B6 (Pyridoxine)',
    'Vitamin C',
    'Vitamin D (25-hydroxy)',
    'Vitamin E',
    'Vitamin K',
    'VLDL Cholesterol',
    'von Willebrand Factor',
    'WBC (White Blood Cell Count)',
    'West Nile Virus Antibody',
    'White Blood Cell Count with Differential',
    'Wound Culture',
    'Zinc'
  ]

  const IMAGING_MODALITIES = [
    'Angiography',
    'Arthrography',
    'Bone Density Scan (DEXA)',
    'Cardiac Catheterization',
    'CT Angiography (CTA)',
    'CT Scan',
    'CT Scan (with contrast)',
    'CT Scan (without contrast)',
    'Echocardiography (Transthoracic)',
    'Echocardiography (Transesophageal)',
    'Fluoroscopy',
    'Hysterosalpingography',
    'Mammography',
    'MR Angiography (MRA)',
    'MRI',
    'MRI (with contrast)',
    'MRI (without contrast)',
    'Myelography',
    'Nuclear Medicine Scan',
    'PET/CT Scan',
    'PET Scan',
    'Ultrasound (Doppler)',
    'Ultrasound (Standard)',
    'Venography',
    'X-Ray'
  ]

  const BODY_SITES = [
    'Abdomen',
    'Ankle',
    'Arm',
    'Bladder',
    'Brain',
    'Breast',
    'Cervical Spine',
    'Chest',
    'Elbow',
    'Esophagus',
    'Foot',
    'Gallbladder',
    'Hand',
    'Head',
    'Heart',
    'Hip',
    'Kidney',
    'Knee',
    'Leg',
    'Liver',
    'Lower Extremity',
    'Lumbar Spine',
    'Lung',
    'Neck',
    'Pancreas',
    'Pelvis',
    'Shoulder',
    'Sinus',
    'Skull',
    'Spine',
    'Spleen',
    'Stomach',
    'Thoracic Spine',
    'Thyroid',
    'Upper Extremity',
    'Uterus',
    'Wrist'
  ]

  // Common conditions (most frequently seen)
  const COMMON_CONDITIONS = [
    'Asthma',
    'Atrial Fibrillation',
    'Chronic Kidney Disease',
    'Chronic Obstructive Pulmonary Disease (COPD)',
    'Coronary Artery Disease',
    'Depression',
    'Diabetes Mellitus Type 1',
    'Diabetes Mellitus Type 2',
    'Gastroesophageal Reflux Disease (GERD)',
    'Heart Failure',
    'Hyperlipidemia',
    'Hypertension',
    'Hypothyroidism',
    'Obstructive Sleep Apnea',
    'Osteoarthritis'
  ]

  // Comprehensive conditions list (A-Z)
  const ALL_CONDITIONS = [
    'Achalasia',
    'Acne Vulgaris',
    'Acoustic Neuroma',
    'Acromegaly',
    'Acute Coronary Syndrome',
    'Acute Kidney Injury',
    'Acute Lymphoblastic Leukemia (ALL)',
    'Acute Myeloid Leukemia (AML)',
    'Addison\'s Disease',
    'ADHD (Attention Deficit Hyperactivity Disorder)',
    'Adrenal Insufficiency',
    'Age-Related Macular Degeneration',
    'Agoraphobia',
    'Alcohol Use Disorder',
    'Allergic Rhinitis',
    'Alopecia Areata',
    'Alzheimer\'s Disease',
    'Amyotrophic Lateral Sclerosis (ALS)',
    'Anal Fissure',
    'Anaphylaxis',
    'Anemia (Iron Deficiency)',
    'Anemia (Pernicious)',
    'Anemia (Sickle Cell)',
    'Aneurysm (Abdominal Aortic)',
    'Aneurysm (Cerebral)',
    'Angina Pectoris',
    'Ankylosing Spondylitis',
    'Anorexia Nervosa',
    'Anxiety Disorder (Generalized)',
    'Aortic Dissection',
    'Aortic Regurgitation',
    'Aortic Stenosis',
    'Appendicitis',
    'Arrhythmia (Cardiac)',
    'Arterial Thrombosis',
    'Arthritis (Psoriatic)',
    'Arthritis (Rheumatoid)',
    'Asbestosis',
    'Ascites',
    'Asthma',
    'Atelectasis',
    'Atherosclerosis',
    'Atrial Fibrillation',
    'Atrial Flutter',
    'Autism Spectrum Disorder',
    'Autoimmune Hepatitis',
    'Avascular Necrosis',
    'Bacterial Meningitis',
    'Barrett\'s Esophagus',
    'Basal Cell Carcinoma',
    'Bell\'s Palsy',
    'Benign Prostatic Hyperplasia (BPH)',
    'Bipolar Disorder',
    'Bladder Cancer',
    'Blepharitis',
    'Bone Metastases',
    'Borderline Personality Disorder',
    'Botulism',
    'Brain Tumor',
    'Breast Cancer',
    'Bronchiectasis',
    'Bronchiolitis',
    'Bronchitis (Acute)',
    'Bronchitis (Chronic)',
    'Brugada Syndrome',
    'Bulimia Nervosa',
    'Burns (Thermal)',
    'Bursitis',
    'Candidiasis',
    'Carbon Monoxide Poisoning',
    'Cardiac Arrest',
    'Cardiomyopathy (Dilated)',
    'Cardiomyopathy (Hypertrophic)',
    'Cardiomyopathy (Restrictive)',
    'Carotid Artery Stenosis',
    'Carpal Tunnel Syndrome',
    'Cataracts',
    'Celiac Disease',
    'Cellulitis',
    'Cerebral Palsy',
    'Cerebrovascular Accident (Stroke)',
    'Cervical Cancer',
    'Charcot-Marie-Tooth Disease',
    'Chickenpox (Varicella)',
    'Cholangitis',
    'Cholecystitis',
    'Cholelithiasis (Gallstones)',
    'Chronic Fatigue Syndrome',
    'Chronic Kidney Disease',
    'Chronic Lymphocytic Leukemia (CLL)',
    'Chronic Myeloid Leukemia (CML)',
    'Chronic Obstructive Pulmonary Disease (COPD)',
    'Chronic Pain Syndrome',
    'Cirrhosis',
    'Clostridium Difficile Colitis',
    'Coarctation of the Aorta',
    'Coccidioidomycosis',
    'Colitis (Ulcerative)',
    'Colon Cancer',
    'Compartment Syndrome',
    'Concussion',
    'Congenital Heart Disease',
    'Congestive Heart Failure',
    'Conjunctivitis',
    'Constipation (Chronic)',
    'Contact Dermatitis',
    'Coronary Artery Disease',
    'COVID-19',
    'Crohn\'s Disease',
    'Croup',
    'Cryptococcosis',
    'Cushing\'s Syndrome',
    'Cystic Fibrosis',
    'Cystitis',
    'Deep Vein Thrombosis (DVT)',
    'Delirium',
    'Dementia',
    'Depression (Major Depressive Disorder)',
    'Dermatitis (Atopic)',
    'Dermatomyositis',
    'Diabetes Insipidus',
    'Diabetes Mellitus Type 1',
    'Diabetes Mellitus Type 2',
    'Diabetic Ketoacidosis (DKA)',
    'Diabetic Neuropathy',
    'Diabetic Retinopathy',
    'Diarrhea (Chronic)',
    'Dilated Cardiomyopathy',
    'Discoid Lupus',
    'Diverticulitis',
    'Diverticulosis',
    'Down Syndrome',
    'Drug-Induced Liver Injury',
    'Duchenne Muscular Dystrophy',
    'Duodenal Ulcer',
    'Dysphagia',
    'Eczema (Atopic Dermatitis)',
    'Ehlers-Danlos Syndrome',
    'Emphysema',
    'Encephalitis',
    'Endocarditis',
    'Endometrial Cancer',
    'Endometriosis',
    'Epilepsy',
    'Erectile Dysfunction',
    'Esophageal Cancer',
    'Esophageal Varices',
    'Essential Tremor',
    'Fatty Liver Disease (NAFLD)',
    'Fibromyalgia',
    'Fracture (Bone)',
    'Friedreich\'s Ataxia',
    'Frostbite',
    'Gallstones (Cholelithiasis)',
    'Gastric Cancer',
    'Gastric Ulcer',
    'Gastritis',
    'Gastroenteritis',
    'Gastroesophageal Reflux Disease (GERD)',
    'Generalized Anxiety Disorder',
    'Genital Herpes',
    'Gestational Diabetes',
    'Giant Cell Arteritis',
    'Glaucoma',
    'Glomerulonephritis',
    'Gonorrhea',
    'Gout',
    'Graves\' Disease',
    'Guillain-Barré Syndrome',
    'Hashimoto\'s Thyroiditis',
    'Headache (Cluster)',
    'Headache (Migraine)',
    'Headache (Tension)',
    'Heart Block',
    'Heart Failure',
    'Heat Stroke',
    'Hemochromatosis',
    'Hemophilia',
    'Hemorrhoids',
    'Hepatic Encephalopathy',
    'Hepatitis A',
    'Hepatitis B',
    'Hepatitis C',
    'Hepatitis D',
    'Hepatitis E',
    'Hepatocellular Carcinoma',
    'Hepatorenal Syndrome',
    'Herniated Disc',
    'Herpes Simplex Virus (HSV)',
    'Herpes Zoster (Shingles)',
    'Hiatal Hernia',
    'Hidradenitis Suppurativa',
    'Hip Fracture',
    'Hirschsprung Disease',
    'HIV/AIDS',
    'Hodgkin Lymphoma',
    'Human Papillomavirus (HPV)',
    'Huntington\'s Disease',
    'Hydrocephalus',
    'Hydronephrosis',
    'Hyperaldosteronism',
    'Hypercalcemia',
    'Hypercholesterolemia',
    'Hyperglycemia',
    'Hyperkalemia',
    'Hyperlipidemia',
    'Hyperparathyroidism',
    'Hypertension',
    'Hypertensive Emergency',
    'Hyperthyroidism',
    'Hypertrophic Cardiomyopathy',
    'Hypocalcemia',
    'Hypoglycemia',
    'Hypokalemia',
    'Hyponatremia',
    'Hypoparathyroidism',
    'Hypotension',
    'Hypothermia',
    'Hypothyroidism',
    'Idiopathic Pulmonary Fibrosis',
    'IgA Nephropathy',
    'Immune Thrombocytopenia (ITP)',
    'Impetigo',
    'Inflammatory Bowel Disease (IBD)',
    'Influenza',
    'Insomnia',
    'Interstitial Cystitis',
    'Interstitial Lung Disease',
    'Intracranial Hemorrhage',
    'Intracerebral Hemorrhage',
    'Iron Deficiency Anemia',
    'Irritable Bowel Syndrome (IBS)',
    'Ischemic Heart Disease',
    'Kawasaki Disease',
    'Keratitis',
    'Kidney Stones (Nephrolithiasis)',
    'Klinefelter Syndrome',
    'Lactose Intolerance',
    'Laryngitis',
    'Lead Poisoning',
    'Legionnaires\' Disease',
    'Leukemia',
    'Lichen Planus',
    'Liver Cirrhosis',
    'Liver Failure',
    'Long QT Syndrome',
    'Lou Gehrig\'s Disease (ALS)',
    'Lung Cancer',
    'Lupus (Systemic Lupus Erythematosus)',
    'Lyme Disease',
    'Lymphedema',
    'Lymphoma',
    'Macular Degeneration',
    'Major Depressive Disorder',
    'Malaria',
    'Malignant Hypertension',
    'Malnutrition',
    'Marfan Syndrome',
    'Mastitis',
    'Measles',
    'Melanoma',
    'Ménière\'s Disease',
    'Meningitis',
    'Menopause',
    'Metabolic Syndrome',
    'Metastatic Cancer',
    'Migraine',
    'Mitral Regurgitation',
    'Mitral Stenosis',
    'Mitral Valve Prolapse',
    'Mononucleosis',
    'Motion Sickness',
    'Multiple Myeloma',
    'Multiple Sclerosis',
    'Mumps',
    'Muscular Dystrophy',
    'Myasthenia Gravis',
    'Mycobacterium Avium Complex (MAC)',
    'Myelodysplastic Syndrome',
    'Myelofibrosis',
    'Myocardial Infarction',
    'Myocarditis',
    'Narcolepsy',
    'Nephritic Syndrome',
    'Nephrolithiasis (Kidney Stones)',
    'Nephrotic Syndrome',
    'Neuroblastoma',
    'Neurofibromatosis',
    'Neuropathy (Peripheral)',
    'Non-Alcoholic Fatty Liver Disease (NAFLD)',
    'Non-Hodgkin Lymphoma',
    'Obesity',
    'Obsessive-Compulsive Disorder (OCD)',
    'Obstructive Sleep Apnea',
    'Optic Neuritis',
    'Oral Cancer',
    'Orthostatic Hypotension',
    'Osteomyelitis',
    'Osteoporosis',
    'Osteoarthritis',
    'Otitis Media',
    'Ovarian Cancer',
    'Ovarian Cyst',
    'Paget\'s Disease',
    'Pancreatic Cancer',
    'Pancreatitis (Acute)',
    'Pancreatitis (Chronic)',
    'Panic Disorder',
    'Parkinson\'s Disease',
    'Patent Ductus Arteriosus',
    'Pelvic Inflammatory Disease (PID)',
    'Pemphigus',
    'Peptic Ulcer Disease',
    'Pericardial Effusion',
    'Pericarditis',
    'Peripheral Arterial Disease',
    'Peripheral Neuropathy',
    'Peripheral Vascular Disease',
    'Peritonitis',
    'Pernicious Anemia',
    'Personality Disorder',
    'Pertussis (Whooping Cough)',
    'Pheochromocytoma',
    'Phlebitis',
    'Placenta Previa',
    'Pleural Effusion',
    'Pleurisy',
    'Pneumoconiosis',
    'Pneumonia',
    'Pneumothorax',
    'Polio',
    'Polycystic Kidney Disease',
    'Polycystic Ovary Syndrome (PCOS)',
    'Polycythemia Vera',
    'Polymyalgia Rheumatica',
    'Polymyositis',
    'Portal Hypertension',
    'Post-Traumatic Stress Disorder (PTSD)',
    'Preeclampsia',
    'Pregnancy',
    'Premature Ventricular Contractions (PVCs)',
    'Preterm Labor',
    'Primary Biliary Cholangitis',
    'Primary Sclerosing Cholangitis',
    'Prostate Cancer',
    'Prostatitis',
    'Pseudogout',
    'Psoriasis',
    'Psoriatic Arthritis',
    'Pulmonary Edema',
    'Pulmonary Embolism',
    'Pulmonary Fibrosis',
    'Pulmonary Hypertension',
    'Pyelonephritis',
    'Pyloric Stenosis',
    'Rabies',
    'Raynaud\'s Phenomenon',
    'Reactive Arthritis',
    'Rectal Cancer',
    'Renal Artery Stenosis',
    'Renal Cell Carcinoma',
    'Renal Failure (Acute)',
    'Renal Failure (Chronic)',
    'Respiratory Distress Syndrome',
    'Restless Legs Syndrome',
    'Retinal Detachment',
    'Retinopathy (Diabetic)',
    'Rhabdomyolysis',
    'Rheumatic Fever',
    'Rheumatoid Arthritis',
    'Rosacea',
    'Rotator Cuff Tear',
    'Rubella',
    'Salmonella Infection',
    'Sarcoidosis',
    'Scabies',
    'Schizophrenia',
    'Scleroderma',
    'Scoliosis',
    'Seasonal Affective Disorder',
    'Seborrheic Dermatitis',
    'Seizure Disorder',
    'Sepsis',
    'Septic Arthritis',
    'Septic Shock',
    'Severe Acute Respiratory Syndrome (SARS)',
    'Sexually Transmitted Infection (STI)',
    'Shingles (Herpes Zoster)',
    'Shock (Cardiogenic)',
    'Shock (Hypovolemic)',
    'Shock (Septic)',
    'Sickle Cell Disease',
    'Sinusitis',
    'Sjögren\'s Syndrome',
    'Sleep Apnea (Central)',
    'Sleep Apnea (Obstructive)',
    'Smallpox',
    'Spinal Cord Injury',
    'Spinal Stenosis',
    'Spontaneous Bacterial Peritonitis',
    'Squamous Cell Carcinoma',
    'Stevens-Johnson Syndrome',
    'Stomach Cancer',
    'Stroke (Hemorrhagic)',
    'Stroke (Ischemic)',
    'Subarachnoid Hemorrhage',
    'Subdural Hematoma',
    'Substance Use Disorder',
    'Sudden Cardiac Death',
    'Supraventricular Tachycardia (SVT)',
    'Syncope',
    'Syphilis',
    'Systemic Lupus Erythematosus (SLE)',
    'Takayasu Arteritis',
    'Temporal Arteritis',
    'Tendinitis',
    'Testicular Cancer',
    'Tetanus',
    'Tetralogy of Fallot',
    'Thalassemia',
    'Thoracic Outlet Syndrome',
    'Thrombocytopenia',
    'Thrombophilia',
    'Thrombosis',
    'Thyroid Cancer',
    'Thyroid Nodule',
    'Thyroiditis',
    'Tinnitus',
    'Tonsillitis',
    'Tourette Syndrome',
    'Toxic Shock Syndrome',
    'Toxoplasmosis',
    'Tracheomalacia',
    'Transient Ischemic Attack (TIA)',
    'Traumatic Brain Injury',
    'Trichinosis',
    'Tricuspid Regurgitation',
    'Trigeminal Neuralgia',
    'Tuberculosis',
    'Tuberous Sclerosis',
    'Turner Syndrome',
    'Typhoid Fever',
    'Ulcerative Colitis',
    'Urethritis',
    'Urinary Incontinence',
    'Urinary Retention',
    'Urinary Tract Infection (UTI)',
    'Urticaria (Hives)',
    'Uterine Cancer',
    'Uterine Fibroids',
    'Uveitis',
    'Vaginal Yeast Infection',
    'Valvular Heart Disease',
    'Varicose Veins',
    'Vasculitis',
    'Venous Insufficiency',
    'Venous Thromboembolism',
    'Ventricular Fibrillation',
    'Ventricular Septal Defect',
    'Ventricular Tachycardia',
    'Vertigo',
    'Viral Hepatitis',
    'Viral Meningitis',
    'Vitamin B12 Deficiency',
    'Vitamin D Deficiency',
    'Vitiligo',
    'Von Willebrand Disease',
    'Wegener\'s Granulomatosis',
    'West Nile Virus',
    'Whipple\'s Disease',
    'Whooping Cough (Pertussis)',
    'Wilson\'s Disease',
    'Wolff-Parkinson-White Syndrome',
    'Yellow Fever',
    'Zika Virus',
    'Zollinger-Ellison Syndrome'
  ]

  // Common medications (most frequently prescribed)
  const COMMON_MEDICATIONS = [
    'Albuterol',
    'Amlodipine',
    'Aspirin',
    'Atorvastatin',
    'Furosemide',
    'Gabapentin',
    'Hydrochlorothiazide',
    'Levothyroxine',
    'Lisinopril',
    'Metformin',
    'Metoprolol',
    'Omeprazole',
    'Prednisone',
    'Sertraline'
  ]

  // Comprehensive medication list (A-Z)
  const ALL_MEDICATIONS = [
    'Abacavir',
    'Abatacept',
    'Abiraterone',
    'Acamprosate',
    'Acarbose',
    'Acebutolol',
    'Acetaminophen',
    'Acetazolamide',
    'Acyclovir',
    'Adalimumab',
    'Adapalene',
    'Adefovir',
    'Adenosine',
    'Albuterol',
    'Alendronate',
    'Alfuzosin',
    'Allopurinol',
    'Almotriptan',
    'Alprazolam',
    'Alteplase',
    'Amantadine',
    'Amiodarone',
    'Amitriptyline',
    'Amlodipine',
    'Amoxicillin',
    'Amoxicillin-Clavulanate',
    'Amphotericin B',
    'Ampicillin',
    'Anastrozole',
    'Apixaban',
    'Aripiprazole',
    'Aspirin',
    'Atazanavir',
    'Atenolol',
    'Atomoxetine',
    'Atorvastatin',
    'Atovaquone',
    'Atropine',
    'Azathioprine',
    'Azithromycin',
    'Aztreonam',
    'Baclofen',
    'Beclomethasone',
    'Benazepril',
    'Benzonatate',
    'Benztropine',
    'Betamethasone',
    'Betaxolol',
    'Bevacizumab',
    'Bicalutamide',
    'Bisoprolol',
    'Bivalirudin',
    'Bleomycin',
    'Brimonidine',
    'Bromocriptine',
    'Budesonide',
    'Bumetanide',
    'Buprenorphine',
    'Bupropion',
    'Buspirone',
    'Busulfan',
    'Calcitonin',
    'Calcitriol',
    'Calcium Carbonate',
    'Canagliflozin',
    'Candesartan',
    'Capecitabine',
    'Captopril',
    'Carbamazepine',
    'Carbidopa-Levodopa',
    'Carboplatin',
    'Carvedilol',
    'Caspofungin',
    'Cefazolin',
    'Cefdinir',
    'Cefepime',
    'Cefotaxime',
    'Cefoxitin',
    'Ceftaroline',
    'Ceftazidime',
    'Ceftriaxone',
    'Cefuroxime',
    'Celecoxib',
    'Cephalexin',
    'Certolizumab',
    'Cetirizine',
    'Chlorambucil',
    'Chlorhexidine',
    'Chloroquine',
    'Chlorpheniramine',
    'Chlorpromazine',
    'Chlorthalidone',
    'Cholecalciferol (Vitamin D3)',
    'Cholestyramine',
    'Chondroitin',
    'Ciclesonide',
    'Cilastatin-Imipenem',
    'Cilostazol',
    'Cimetidine',
    'Cinacalcet',
    'Ciprofloxacin',
    'Cisplatin',
    'Citalopram',
    'Clarithromycin',
    'Clemastine',
    'Clindamycin',
    'Clobetasol',
    'Clomiphene',
    'Clomipramine',
    'Clonazepam',
    'Clonidine',
    'Clopidogrel',
    'Clotrimazole',
    'Clozapine',
    'Cocaine',
    'Codeine',
    'Colchicine',
    'Colesevelam',
    'Cortisone',
    'Cyclobenzaprine',
    'Cyclophosphamide',
    'Cyclosporine',
    'Cyproheptadine',
    'Cytarabine',
    'Dabigatran',
    'Dacarbazine',
    'Dactinomycin',
    'Dalteparin',
    'Dapagliflozin',
    'Dapsone',
    'Daptomycin',
    'Darifenacin',
    'Darunavir',
    'Dasatinib',
    'Daunorubicin',
    'Deferasirox',
    'Denosumab',
    'Desipramine',
    'Desloratadine',
    'Desmopressin',
    'Desvenlafaxine',
    'Dexamethasone',
    'Dexlansoprazole',
    'Dextroamphetamine',
    'Dextromethorphan',
    'Diazepam',
    'Diclofenac',
    'Dicyclomine',
    'Didanosine',
    'Digoxin',
    'Diltiazem',
    'Dimenhydrinate',
    'Diphenhydramine',
    'Dipyridamole',
    'Disulfiram',
    'Dobutamine',
    'Docetaxel',
    'Docusate',
    'Dofetilide',
    'Donepezil',
    'Dopamine',
    'Doxazosin',
    'Doxepin',
    'Doxorubicin',
    'Doxycycline',
    'Dronedarone',
    'Droperidol',
    'Duloxetine',
    'Dutasteride',
    'Edoxaban',
    'Efavirenz',
    'Eletriptan',
    'Eltrombopag',
    'Empagliflozin',
    'Emtricitabine',
    'Enalapril',
    'Enoxaparin',
    'Entacapone',
    'Entecavir',
    'Enzalutamide',
    'Ephedrine',
    'Epinephrine',
    'Eplerenone',
    'Epoetin Alfa',
    'Eptifibatide',
    'Erlotinib',
    'Ertapenem',
    'Erythromycin',
    'Escitalopram',
    'Esomeprazole',
    'Estradiol',
    'Eszopiclone',
    'Etanercept',
    'Ethambutol',
    'Ethosuximide',
    'Etoposide',
    'Ezetimibe',
    'Famciclovir',
    'Famotidine',
    'Febuxostat',
    'Felodipine',
    'Fenofibrate',
    'Fentanyl',
    'Ferrous Sulfate',
    'Fesoterodine',
    'Fexofenadine',
    'Finasteride',
    'Flecainide',
    'Fluconazole',
    'Fludrocortisone',
    'Flumazenil',
    'Flunisolide',
    'Fluorouracil (5-FU)',
    'Fluoxetine',
    'Fluphenazine',
    'Fluticasone',
    'Fluvastatin',
    'Fluvoxamine',
    'Folic Acid',
    'Fondaparinux',
    'Formoterol',
    'Fosamprenavir',
    'Foscarnet',
    'Fosinopril',
    'Fosphenytoin',
    'Frovatriptan',
    'Furosemide',
    'Gabapentin',
    'Galantamine',
    'Ganciclovir',
    'Gatifloxacin',
    'Gefitinib',
    'Gemcitabine',
    'Gemfibrozil',
    'Gentamicin',
    'Glimepiride',
    'Glipizide',
    'Glucagon',
    'Glyburide',
    'Glycopyrrolate',
    'Granisetron',
    'Griseofulvin',
    'Guaifenesin',
    'Guanfacine',
    'Haloperidol',
    'Heparin',
    'Hydralazine',
    'Hydrochlorothiazide',
    'Hydrocodone',
    'Hydrocortisone',
    'Hydromorphone',
    'Hydroxychloroquine',
    'Hydroxyurea',
    'Hydroxyzine',
    'Hyoscyamine',
    'Ibandronate',
    'Ibuprofen',
    'Ibutilide',
    'Idarubicin',
    'Ifosfamide',
    'Imatinib',
    'Imipenem-Cilastatin',
    'Imipramine',
    'Imiquimod',
    'Indapamide',
    'Indinavir',
    'Indomethacin',
    'Infliximab',
    'Insulin Aspart',
    'Insulin Detemir',
    'Insulin Glargine',
    'Insulin Glulisine',
    'Insulin Lispro',
    'Insulin NPH',
    'Insulin Regular',
    'Interferon Alfa',
    'Interferon Beta',
    'Ipratropium',
    'Irbesartan',
    'Irinotecan',
    'Iron Sucrose',
    'Isoniazid',
    'Isosorbide Dinitrate',
    'Isosorbide Mononitrate',
    'Isotretinoin',
    'Itraconazole',
    'Ivabradine',
    'Ivermectin',
    'Ketoconazole',
    'Ketoprofen',
    'Ketorolac',
    'Labetalol',
    'Lacosamide',
    'Lactulose',
    'Lamivudine',
    'Lamotrigine',
    'Lansoprazole',
    'Lanthanum',
    'Lapatinib',
    'Latanoprost',
    'Leflunomide',
    'Lenalidomide',
    'Letrozole',
    'Leucovorin',
    'Leuprolide',
    'Levalbuterol',
    'Levetiracetam',
    'Levocetirizine',
    'Levofloxacin',
    'Levothyroxine',
    'Lidocaine',
    'Linagliptin',
    'Linezolid',
    'Liothyronine',
    'Liraglutide',
    'Lisdexamfetamine',
    'Lisinopril',
    'Lithium',
    'Loperamide',
    'Loratadine',
    'Lorazepam',
    'Losartan',
    'Lovastatin',
    'Lubiprostone',
    'Lurasidone',
    'Magnesium Sulfate',
    'Mannitol',
    'Maraviroc',
    'Mebendazole',
    'Meclizine',
    'Medroxyprogesterone',
    'Mefloquine',
    'Megestrol',
    'Meloxicam',
    'Melphalan',
    'Memantine',
    'Meperidine',
    'Mercaptopurine',
    'Meropenem',
    'Mesalamine',
    'Metformin',
    'Methadone',
    'Methimazole',
    'Methocarbamol',
    'Methotrexate',
    'Methyldopa',
    'Methylnaltrexone',
    'Methylphenidate',
    'Methylprednisolone',
    'Metoclopramide',
    'Metolazone',
    'Metoprolol',
    'Metronidazole',
    'Mexiletine',
    'Micafungin',
    'Miconazole',
    'Midazolam',
    'Midodrine',
    'Milrinone',
    'Minocycline',
    'Minoxidil',
    'Mirtazapine',
    'Misoprostol',
    'Mitoxantrone',
    'Modafinil',
    'Moexipril',
    'Mometasone',
    'Montelukast',
    'Morphine',
    'Moxifloxacin',
    'Mupirocin',
    'Mycophenolate',
    'Nabumetone',
    'Nadolol',
    'Nafcillin',
    'Nalbuphine',
    'Naloxone',
    'Naltrexone',
    'Naproxen',
    'Naratriptan',
    'Nateglinide',
    'Nebivolol',
    'Nelfinavir',
    'Neomycin',
    'Neostigmine',
    'Nesiritide',
    'Nevirapine',
    'Niacin',
    'Nicardipine',
    'Nifedipine',
    'Nilotinib',
    'Nilutamide',
    'Nimodipine',
    'Nisoldipine',
    'Nitrofurantoin',
    'Nitroglycerin',
    'Nitroprusside',
    'Nizatidine',
    'Norepinephrine',
    'Norfloxacin',
    'Nortriptyline',
    'Nystatin',
    'Octreotide',
    'Ofloxacin',
    'Olanzapine',
    'Olmesartan',
    'Olopatadine',
    'Omalizumab',
    'Omeprazole',
    'Ondansetron',
    'Oseltamivir',
    'Oxaliplatin',
    'Oxazepam',
    'Oxcarbazepine',
    'Oxybutynin',
    'Oxycodone',
    'Oxymorphone',
    'Paclitaxel',
    'Paliperidone',
    'Pamidronate',
    'Pancrelipase',
    'Pantoprazole',
    'Paricalcitol',
    'Paroxetine',
    'Pazopanib',
    'Pegfilgrastim',
    'Peginterferon Alfa',
    'Penicillin G',
    'Penicillin V',
    'Pentamidine',
    'Pentazocine',
    'Pentoxifylline',
    'Perindopril',
    'Permethrin',
    'Perphenazine',
    'Phenazopyridine',
    'Phenobarbital',
    'Phenoxybenzamine',
    'Phentolamine',
    'Phenylephrine',
    'Phenytoin',
    'Pimecrolimus',
    'Pioglitazone',
    'Piperacillin-Tazobactam',
    'Piroxicam',
    'Pitavastatin',
    'Polymyxin B',
    'Posaconazole',
    'Potassium Chloride',
    'Pramipexole',
    'Prasugrel',
    'Pravastatin',
    'Prazosin',
    'Prednisolone',
    'Prednisone',
    'Pregabalin',
    'Primaquine',
    'Primidone',
    'Probenecid',
    'Procainamide',
    'Prochlorperazine',
    'Progesterone',
    'Promethazine',
    'Propafenone',
    'Propofol',
    'Propranolol',
    'Propylthiouracil',
    'Protamine',
    'Pseudoephedrine',
    'Pyrazinamide',
    'Pyridostigmine',
    'Pyridoxine (Vitamin B6)',
    'Quetiapine',
    'Quinapril',
    'Quinidine',
    'Quinine',
    'Rabeprazole',
    'Raloxifene',
    'Raltegravir',
    'Ramelteon',
    'Ramipril',
    'Ranitidine',
    'Ranolazine',
    'Rasagiline',
    'Rasburicase',
    'Remifentanil',
    'Repaglinide',
    'Reserpine',
    'Reteplase',
    'Ribavirin',
    'Rifabutin',
    'Rifampin',
    'Rifaximin',
    'Riluzole',
    'Risedronate',
    'Risperidone',
    'Ritonavir',
    'Rituximab',
    'Rivaroxaban',
    'Rivastigmine',
    'Rizatriptan',
    'Rocuronium',
    'Ropinirole',
    'Rosiglitazone',
    'Rosuvastatin',
    'Rotigotine',
    'Sacubitril-Valsartan',
    'Salicylic Acid',
    'Salmeterol',
    'Saquinavir',
    'Saxagliptin',
    'Scopolamine',
    'Secobarbital',
    'Selegiline',
    'Selenium Sulfide',
    'Senna',
    'Sertraline',
    'Sevelamer',
    'Sildenafil',
    'Simvastatin',
    'Sirolimus',
    'Sitagliptin',
    'Sodium Bicarbonate',
    'Sodium Polystyrene Sulfonate',
    'Solifenacin',
    'Sorafenib',
    'Sotalol',
    'Spironolactone',
    'Stavudine',
    'Streptomycin',
    'Sucralfate',
    'Sufentanil',
    'Sulfadiazine',
    'Sulfamethoxazole-Trimethoprim',
    'Sulfasalazine',
    'Sulindac',
    'Sumatriptan',
    'Sunitinib',
    'Tacrolimus',
    'Tadalafil',
    'Tamoxifen',
    'Tamsulosin',
    'Tapentadol',
    'Tazobactam',
    'Temazepam',
    'Temozolomide',
    'Tenecteplase',
    'Tenofovir',
    'Terazosin',
    'Terbinafine',
    'Terbutaline',
    'Teriparatide',
    'Testosterone',
    'Tetracycline',
    'Theophylline',
    'Thiamine (Vitamin B1)',
    'Thioridazine',
    'Tiagabine',
    'Ticagrelor',
    'Ticarcillin-Clavulanate',
    'Tigecycline',
    'Timolol',
    'Tinidazole',
    'Tioconazole',
    'Tiotropium',
    'Tipranavir',
    'Tirofiban',
    'Tizanidine',
    'Tobramycin',
    'Tocilizumab',
    'Tofacitinib',
    'Tolcapone',
    'Tolterodine',
    'Topiramate',
    'Topotecan',
    'Torsemide',
    'Tramadol',
    'Trandolapril',
    'Tranexamic Acid',
    'Trastuzumab',
    'Travoprost',
    'Trazodone',
    'Tretinoin',
    'Triamcinolone',
    'Triamterene',
    'Triazolam',
    'Trifluoperazine',
    'Trihexyphenidyl',
    'Trimethobenzamide',
    'Trimethoprim',
    'Trimipramine',
    'Tropicamide',
    'Trospium',
    'Umeclidinium',
    'Valacyclovir',
    'Valganciclovir',
    'Valproic Acid',
    'Valsartan',
    'Vancomycin',
    'Vardenafil',
    'Varenicline',
    'Vasopressin',
    'Vecuronium',
    'Venlafaxine',
    'Verapamil',
    'Vilazodone',
    'Vinblastine',
    'Vincristine',
    'Vinorelbine',
    'Vitamin A',
    'Vitamin B12 (Cyanocobalamin)',
    'Vitamin C (Ascorbic Acid)',
    'Vitamin D2 (Ergocalciferol)',
    'Vitamin D3 (Cholecalciferol)',
    'Vitamin E',
    'Vitamin K (Phytonadione)',
    'Voriconazole',
    'Vortioxetine',
    'Warfarin',
    'Zafirlukast',
    'Zaleplon',
    'Zanamivir',
    'Zidovudine',
    'Zileuton',
    'Ziprasidone',
    'Zoledronic Acid',
    'Zolmitriptan',
    'Zolpidem',
    'Zonisamide',
    'Zopiclone'
  ]

  // Common allergies (most frequently reported)
  const COMMON_ALLERGIES = [
    'Penicillin',
    'Sulfa drugs',
    'Aspirin',
    'NSAIDs',
    'Codeine',
    'Morphine',
    'Latex',
    'Contrast dye',
    'Shellfish',
    'Peanuts'
  ]

  // Comprehensive allergies list (A-Z)
  const ALL_ALLERGIES = [
    'Acetaminophen',
    'Almond',
    'Amoxicillin',
    'Ampicillin',
    'Anesthetics (Local)',
    'Animal Dander',
    'Aspirin',
    'Azithromycin',
    'Bananas',
    'Bee Venom',
    'Benzodiazepines',
    'Beta-Lactams',
    'Cashew',
    'Cat Dander',
    'Cephalosporins',
    'Chlorhexidine',
    'Ciprofloxacin',
    'Clindamycin',
    'Cocaine',
    'Codeine',
    'Contrast Dye (Iodinated)',
    'Corn',
    'Dairy/Milk',
    'Demerol',
    'Dog Dander',
    'Dust Mites',
    'Eggs',
    'Epinephrine',
    'Erythromycin',
    'Fentanyl',
    'Fish',
    'Fluoroquinolones',
    'Gelatin',
    'Gluten',
    'Hazelnut',
    'Hydrocodone',
    'Ibuprofen',
    'Iodine',
    'Ketorolac',
    'Lactose',
    'Latex',
    'Lidocaine',
    'Macrolides',
    'Meperidine',
    'Metformin',
    'Methadone',
    'Metronidazole',
    'Milk/Dairy',
    'Mold',
    'Morphine',
    'Naproxen',
    'Nickel',
    'NSAIDs',
    'Opioids',
    'Oxycodone',
    'Peanuts',
    'Pecan',
    'Penicillin',
    'Pineapple',
    'Pistachio',
    'Pollen',
    'Propofol',
    'Ragweed',
    'Rocuronium',
    'Seafood',
    'Sesame',
    'Shellfish',
    'Soy',
    'Strawberries',
    'Succinylcholine',
    'Sulfa Drugs',
    'Sulfamethoxazole',
    'Sulfites',
    'Tape Adhesive',
    'Tetracycline',
    'Tomatoes',
    'Tramadol',
    'Tree Nuts',
    'Vancomycin',
    'Walnut',
    'Wasp Venom',
    'Wheat'
  ]

  const ALLERGY_REACTIONS = [
    'Anaphylaxis',
    'Diarrhea',
    'Difficulty breathing',
    'Hives',
    'Itching',
    'Nausea/Vomiting',
    'Rash',
    'Swelling',
    'Unknown'
  ]

  // Helper function to filter options based on search term
  const filterOptions = (options, searchTerm) => {
    if (!searchTerm) return options
    const lowerSearch = searchTerm.toLowerCase()
    return options.filter(option => 
      option.toLowerCase().includes(lowerSearch)
    )
  }

  // Searchable Dropdown Component
  const SearchableDropdown = ({ 
    value, 
    onChange, 
    commonOptions, 
    allOptions, 
    placeholder = "Select or search...",
    fieldKey 
  }) => {
    const [isOpen, setIsOpen] = useState(false)
    const [searchTerm, setSearchTerm] = useState('')
    const dropdownRef = useRef(null)

    // Close dropdown when clicking outside
    useEffect(() => {
      const handleClickOutside = (event) => {
        if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
          setIsOpen(false)
        }
      }
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    const filteredCommon = filterOptions(commonOptions || [], searchTerm)
    const filteredAll = filterOptions(allOptions || [], searchTerm)

    const handleSelect = (selectedValue) => {
      onChange(selectedValue)
      setIsOpen(false)
      setSearchTerm('')
    }

    return (
      <div ref={dropdownRef} style={{ position: 'relative', width: '100%' }}>
        <input
          type="text"
          value={value || searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value)
            setIsOpen(true)
          }}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #ccc',
            borderRadius: '4px',
            fontSize: '14px'
          }}
        />
        {isOpen && (
          <div style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            maxHeight: '300px',
            overflowY: 'auto',
            backgroundColor: 'white',
            border: '1px solid #ccc',
            borderRadius: '4px',
            marginTop: '2px',
            zIndex: 1000,
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}>
            {filteredCommon.length > 0 && (
              <>
                <div style={{
                  padding: '8px 12px',
                  backgroundColor: '#f5f5f5',
                  fontWeight: 'bold',
                  fontSize: '12px',
                  color: '#666',
                  position: 'sticky',
                  top: 0,
                  zIndex: 1
                }}>
                  COMMON
                </div>
                {filteredCommon.map((option, idx) => (
                  <div
                    key={`common-${idx}`}
                    onClick={() => handleSelect(option)}
                    style={{
                      padding: '8px 12px',
                      cursor: 'pointer',
                      backgroundColor: value === option ? '#e3f2fd' : 'white',
                      borderBottom: '1px solid #f0f0f0'
                    }}
                    onMouseEnter={(e) => e.target.style.backgroundColor = '#f5f5f5'}
                    onMouseLeave={(e) => e.target.style.backgroundColor = value === option ? '#e3f2fd' : 'white'}
                  >
                    {option}
                  </div>
                ))}
              </>
            )}
            {filteredAll.length > 0 && (
              <>
                <div style={{
                  padding: '8px 12px',
                  backgroundColor: '#f5f5f5',
                  fontWeight: 'bold',
                  fontSize: '12px',
                  color: '#666',
                  position: 'sticky',
                  top: 0,
                  zIndex: 1
                }}>
                  ALL OPTIONS
                </div>
                {filteredAll.map((option, idx) => (
                  <div
                    key={`all-${idx}`}
                    onClick={() => handleSelect(option)}
                    style={{
                      padding: '8px 12px',
                      cursor: 'pointer',
                      backgroundColor: value === option ? '#e3f2fd' : 'white',
                      borderBottom: '1px solid #f0f0f0'
                    }}
                    onMouseEnter={(e) => e.target.style.backgroundColor = '#f5f5f5'}
                    onMouseLeave={(e) => e.target.style.backgroundColor = value === option ? '#e3f2fd' : 'white'}
                  >
                    {option}
                  </div>
                ))}
              </>
            )}
            {filteredCommon.length === 0 && filteredAll.length === 0 && (
              <div style={{
                padding: '12px',
                color: '#999',
                textAlign: 'center'
              }}>
                No results found
              </div>
            )}
            <div
              onClick={() => handleSelect('Other (custom)')}
              style={{
                padding: '8px 12px',
                cursor: 'pointer',
                backgroundColor: '#fff3cd',
                borderTop: '2px solid #ffc107',
                fontWeight: 'bold',
                color: '#856404'
              }}
              onMouseEnter={(e) => e.target.style.backgroundColor = '#ffeaa7'}
              onMouseLeave={(e) => e.target.style.backgroundColor = '#fff3cd'}
            >
              + Other (enter custom)
            </div>
          </div>
        )}
      </div>
    )
  }

  // Add new visit note
  const addVisitNote = () => {
    const newNote = {
      id: Date.now(),
      date: '',
      type: '',
      author: '',
      specialty: '',
      content: ''
    }
    setPatientData(prev => ({
      ...prev,
      visit_notes: [...prev.visit_notes, newNote]
    }))
  }

  const removeVisitNote = (id) => {
    setPatientData(prev => ({
      ...prev,
      visit_notes: prev.visit_notes.filter(note => note.id !== id)
    }))
  }

  const updateVisitNote = (id, field, value) => {
    setPatientData(prev => ({
      ...prev,
      visit_notes: prev.visit_notes.map(note =>
        note.id === id ? { ...note, [field]: value } : note
      )
    }))
  }

  // Add vital signs
  const addVitalSigns = () => {
    const newVitals = {
      id: Date.now(),
      date: '',
      time: '',
      temperature: '',
      temperature_unit: 'F',
      blood_pressure_systolic: '',
      blood_pressure_diastolic: '',
      heart_rate: '',
      respiratory_rate: '',
      oxygen_saturation: '',
      weight: '',
      weight_unit: 'lbs',
      height: '',
      height_unit: 'inches',
      bmi: '',
      pain_scale: '',
      notes: ''
    }
    setPatientData(prev => ({
      ...prev,
      vital_signs: [...prev.vital_signs, newVitals]
    }))
  }

  const removeVitalSigns = (id) => {
    setPatientData(prev => ({
      ...prev,
      vital_signs: prev.vital_signs.filter(vital => vital.id !== id)
    }))
  }

  const updateVitalSigns = (id, field, value) => {
    setPatientData(prev => ({
      ...prev,
      vital_signs: prev.vital_signs.map(vital =>
        vital.id === id ? { ...vital, [field]: value } : vital
      )
    }))
  }

  // Add diagnostic test
  const addDiagnosticTest = () => {
    const newTest = {
      id: Date.now(),
      date: '',
      test_name: '',
      test_type: '',
      result: '',
      abnormal: false,
      critical: false,
      interpretation: ''
    }
    setPatientData(prev => ({
      ...prev,
      diagnostic_tests: [...prev.diagnostic_tests, newTest]
    }))
  }

  const removeDiagnosticTest = (id) => {
    setPatientData(prev => ({
      ...prev,
      diagnostic_tests: prev.diagnostic_tests.filter(test => test.id !== id)
    }))
  }

  const updateDiagnosticTest = (id, field, value) => {
    setPatientData(prev => ({
      ...prev,
      diagnostic_tests: prev.diagnostic_tests.map(test =>
        test.id === id ? { ...test, [field]: value } : test
      )
    }))
  }

  // Add H&P
  const addHP = () => {
    const newHP = {
      id: Date.now(),
      date: '',
      author: '',
      chief_complaint: '',
      history_of_present_illness: '',
      past_medical_history: [],
      past_surgical_history: [],
      medications: [],
      allergies: [],
      family_history: '',
      social_history: '',
      review_of_systems: '',
      physical_exam: '',
      assessment: '',
      plan: ''
    }
    setPatientData(prev => ({
      ...prev,
      history_and_physicals: [...prev.history_and_physicals, newHP]
    }))
  }

  const removeHP = (id) => {
    setPatientData(prev => ({
      ...prev,
      history_and_physicals: prev.history_and_physicals.filter(hp => hp.id !== id)
    }))
  }

  const updateHP = (id, field, value) => {
    setPatientData(prev => ({
      ...prev,
      history_and_physicals: prev.history_and_physicals.map(hp =>
        hp.id === id ? { ...hp, [field]: value } : hp
      )
    }))
  }

  // Add procedure
  const addProcedure = () => {
    const newProc = {
      id: Date.now(),
      date: '',
      procedure_name: '',
      indication: '',
      outcome: '',
      complications: '',
      operator: ''
    }
    setPatientData(prev => ({
      ...prev,
      procedures: [...prev.procedures, newProc]
    }))
  }

  const removeProcedure = (id) => {
    setPatientData(prev => ({
      ...prev,
      procedures: prev.procedures.filter(proc => proc.id !== id)
    }))
  }

  const updateProcedure = (id, field, value) => {
    setPatientData(prev => ({
      ...prev,
      procedures: prev.procedures.map(proc =>
        proc.id === id ? { ...proc, [field]: value } : proc
      )
    }))
  }

  // Add imaging study
  const addImagingStudy = () => {
    const newImaging = {
      id: Date.now(),
      date: '',
      modality: '',
      body_site: '',
      indication: '',
      findings: '',
      impression: '',
      radiologist: ''
    }
    setPatientData(prev => ({
      ...prev,
      imaging_studies: [...prev.imaging_studies, newImaging]
    }))
  }

  const removeImagingStudy = (id) => {
    setPatientData(prev => ({
      ...prev,
      imaging_studies: prev.imaging_studies.filter(img => img.id !== id)
    }))
  }

  const updateImagingStudy = (id, field, value) => {
    setPatientData(prev => ({
      ...prev,
      imaging_studies: prev.imaging_studies.map(img =>
        img.id === id ? { ...img, [field]: value } : img
      )
    }))
  }

  // Add condition
  const addCondition = () => {
    const newCondition = {
      id: Date.now(),
      code: '',
      status: 'active',
      recorded_date: '',
      onset: ''
    }
    setPatientData(prev => ({
      ...prev,
      active_conditions: [...prev.active_conditions, newCondition]
    }))
  }

  const removeCondition = (id) => {
    setPatientData(prev => ({
      ...prev,
      active_conditions: prev.active_conditions.filter(cond => cond.id !== id)
    }))
  }

  const updateCondition = (id, field, value) => {
    setPatientData(prev => ({
      ...prev,
      active_conditions: prev.active_conditions.map(cond =>
        cond.id === id ? { ...cond, [field]: value } : cond
      )
    }))
  }

  // Add medication
  const addMedication = () => {
    const newMed = {
      id: Date.now(),
      name: '',
      status: 'active',
      dosage: '',
      date_prescribed: ''
    }
    setPatientData(prev => ({
      ...prev,
      current_medications: [...prev.current_medications, newMed]
    }))
  }

  const removeMedication = (id) => {
    setPatientData(prev => ({
      ...prev,
      current_medications: prev.current_medications.filter(med => med.id !== id)
    }))
  }

  const updateMedication = (id, field, value) => {
    setPatientData(prev => ({
      ...prev,
      current_medications: prev.current_medications.map(med =>
        med.id === id ? { ...med, [field]: value } : med
      )
    }))
  }

  // Add allergy
  const addAllergy = () => {
    const newAllergy = {
      id: Date.now(),
      allergen: '',
      reaction: ''
    }
    setPatientData(prev => ({
      ...prev,
      allergies: [...prev.allergies, newAllergy]
    }))
  }

  const removeAllergy = (id) => {
    setPatientData(prev => ({
      ...prev,
      allergies: prev.allergies.filter(allergy => allergy.id !== id)
    }))
  }

  const updateAllergy = (id, field, value) => {
    setPatientData(prev => ({
      ...prev,
      allergies: prev.allergies.map(allergy =>
        allergy.id === id ? { ...allergy, [field]: value } : allergy
      )
    }))
  }

  // Check medication safety
  const checkMedicationSafety = async () => {
    setCheckingSafety(true)
    try {
      const activeMeds = patientData.current_medications
        .filter(med => med.status === 'active' && med.name && med.name !== '')
        .map(med => med.name)
      
      if (activeMeds.length === 0) {
        alert('Please add at least one active medication to check safety.')
        setCheckingSafety(false)
        return
      }

      const conditions = patientData.active_conditions
        .filter(cond => cond.condition_name && cond.condition_name !== '')
        .map(cond => cond.condition_name)
      
      const allergies = patientData.allergies
        .filter(allergy => allergy.allergen && allergy.allergen !== '')
        .map(allergy => allergy.allergen)

      const response = await fetch(`${apiBase}/diagnostic/medication-safety-check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_medications: activeMeds,
          conditions: conditions,
          known_allergies: allergies
        })
      })

      if (response.ok) {
        const result = await response.json()
        setMedicationSafetyResult(result)
        setShowSafetyModal(true)
      } else {
        alert('Failed to check medication safety. Please try again.')
      }
    } catch (err) {
      console.error('Medication safety check failed:', err)
      alert('Error checking medication safety. Please check your connection.')
    } finally {
      setCheckingSafety(false)
    }
  }

  // Save data
  const handleSave = async () => {
    try {
      const response = await fetch(`${apiBase}/diagnostic/manual-history`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patientData)
      })
      
      if (response.ok) {
        setSavedMessage('✓ Patient history saved successfully!')
        setTimeout(() => setSavedMessage(''), 3000)
      } else {
        setSavedMessage('✗ Failed to save patient history')
      }
    } catch (err) {
      console.error('Save failed:', err)
      setSavedMessage('✗ Error saving patient history')
    }
  }

  const sections = [
    { id: 'demographics', label: 'Demographics', icon: '👤' },
    { id: 'vital_signs', label: 'Vital Signs', icon: '🩺' },
    { id: 'visit_notes', label: 'Visit Notes', icon: '📋' },
    { id: 'diagnostic_tests', label: 'Diagnostic Tests', icon: '🧪' },
    { id: 'history_physicals', label: 'H&P', icon: '📝' },
    { id: 'procedures', label: 'Procedures', icon: '🔬' },
    { id: 'imaging', label: 'Imaging', icon: '🏥' },
    { id: 'conditions', label: 'Conditions', icon: '📊' },
    { id: 'medications', label: 'Medications', icon: '💊' },
    { id: 'allergies', label: 'Allergies', icon: '⚠️' },
    { id: 'history', label: 'Family/Social History', icon: '👨‍👩‍👧' }
  ]

  return (
    <div className={styles.container}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto 1rem'
      }}>
        <RoleBasedNavigation />
      </div>

      <header className={styles.header}>
        <div className={styles.headerContent}>
          <PageHeader
            title="Manual Patient History Entry"
            subtitle="For non-EMR instances: Enter comprehensive patient history using dropdown lists"
          />
        </div>
      </header>

      <div className={styles.main}>
        {/* Section Navigation */}
        <nav className={styles.sectionNav}>
          {sections.map(section => (
            <button
              key={section.id}
              className={currentSection === section.id ? styles.activeSection : styles.inactiveSection}
              onClick={() => setCurrentSection(section.id)}
            >
              <span className={styles.sectionIcon}>{section.icon}</span>
              <span className={styles.sectionLabel}>{section.label}</span>
            </button>
          ))}
        </nav>

        <div className={styles.content}>
          {/* Demographics Section */}
          {currentSection === 'demographics' && (
            <div className={styles.section}>
              <h2>👤 Patient Demographics</h2>
              <div className={styles.formGrid}>
                <div className={styles.formGroup}>
                  <label>Patient ID / MRN</label>
                  <input
                    type="text"
                    value={patientData.patient_id}
                    onChange={(e) => setPatientData({...patientData, patient_id: e.target.value})}
                    placeholder="Enter patient ID"
                  />
                </div>
                <div className={styles.formGroup}>
                  <label>Patient Name</label>
                  <input
                    type="text"
                    value={patientData.patient_name}
                    onChange={(e) => setPatientData({...patientData, patient_name: e.target.value})}
                    placeholder="Enter patient name"
                  />
                </div>
                <div className={styles.formGroup}>
                  <label>Age</label>
                  <input
                    type="number"
                    value={patientData.age}
                    onChange={(e) => setPatientData({...patientData, age: e.target.value})}
                    placeholder="Patient age"
                  />
                </div>
                <div className={styles.formGroup}>
                  <label>Gender</label>
                  <select
                    value={patientData.gender}
                    onChange={(e) => setPatientData({...patientData, gender: e.target.value})}
                  >
                    <option value="">Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                    <option value="unknown">Unknown</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Visit Notes Section */}
          {currentSection === 'visit_notes' && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>📋 Visit Notes</h2>
                <button onClick={addVisitNote} className={styles.addButton}>+ Add Visit Note</button>
              </div>
              
              {patientData.visit_notes.length === 0 && (
                <p className={styles.emptyState}>No visit notes yet. Click "+ Add Visit Note" to begin.</p>
              )}

              {patientData.visit_notes.map(note => (
                <div key={note.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>Visit Note</h3>
                    <button onClick={() => removeVisitNote(note.id)} className={styles.removeButton}>✕</button>
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <label>Date</label>
                      <input
                        type="date"
                        value={note.date}
                        onChange={(e) => updateVisitNote(note.id, 'date', e.target.value)}
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Note Type</label>
                      <select
                        value={note.type}
                        onChange={(e) => updateVisitNote(note.id, 'type', e.target.value)}
                      >
                        <option value="">Select type</option>
                        {VISIT_NOTE_TYPES.map(type => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </select>
                    </div>
                    <div className={styles.formGroup}>
                      <label>Author / Provider</label>
                      <input
                        type="text"
                        value={note.author}
                        onChange={(e) => updateVisitNote(note.id, 'author', e.target.value)}
                        placeholder="Dr. Name"
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Specialty</label>
                      <select
                        value={note.specialty}
                        onChange={(e) => updateVisitNote(note.id, 'specialty', e.target.value)}
                      >
                        <option value="">Select specialty</option>
                        {SPECIALTIES.map(spec => (
                          <option key={spec} value={spec}>{spec}</option>
                        ))}
                      </select>
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Clinical Note Content</label>
                      <textarea
                        value={note.content}
                        onChange={(e) => updateVisitNote(note.id, 'content', e.target.value)}
                        rows={6}
                        placeholder="Enter clinical note..."
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Vital Signs Section */}
          {currentSection === 'vital_signs' && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>🩺 Vital Signs</h2>
                <button onClick={addVitalSigns} className={styles.addButton}>+ Add Vital Signs</button>
              </div>
              
              {patientData.vital_signs.length === 0 && (
                <p className={styles.emptyState}>No vital signs recorded yet. Click "+ Add Vital Signs" to begin.</p>
              )}

              {patientData.vital_signs.map(vital => (
                <div key={vital.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>Vital Signs Record</h3>
                    <button onClick={() => removeVitalSigns(vital.id)} className={styles.removeButton}>✕</button>
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <label>Date</label>
                      <input
                        type="date"
                        value={vital.date}
                        onChange={(e) => updateVitalSigns(vital.id, 'date', e.target.value)}
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Time</label>
                      <input
                        type="time"
                        value={vital.time}
                        onChange={(e) => updateVitalSigns(vital.id, 'time', e.target.value)}
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Temperature</label>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <input
                          type="number"
                          step="0.1"
                          value={vital.temperature}
                          onChange={(e) => updateVitalSigns(vital.id, 'temperature', e.target.value)}
                          placeholder="98.6"
                          style={{ flex: 1 }}
                        />
                        <select
                          value={vital.temperature_unit}
                          onChange={(e) => updateVitalSigns(vital.id, 'temperature_unit', e.target.value)}
                          style={{ width: '70px' }}
                        >
                          <option value="F">°F</option>
                          <option value="C">°C</option>
                        </select>
                      </div>
                    </div>
                    <div className={styles.formGroup}>
                      <label>Blood Pressure</label>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <input
                          type="number"
                          value={vital.blood_pressure_systolic}
                          onChange={(e) => updateVitalSigns(vital.id, 'blood_pressure_systolic', e.target.value)}
                          placeholder="120"
                          style={{ flex: 1 }}
                        />
                        <span>/</span>
                        <input
                          type="number"
                          value={vital.blood_pressure_diastolic}
                          onChange={(e) => updateVitalSigns(vital.id, 'blood_pressure_diastolic', e.target.value)}
                          placeholder="80"
                          style={{ flex: 1 }}
                        />
                        <span style={{ fontSize: '12px', color: '#666' }}>mmHg</span>
                      </div>
                    </div>
                    <div className={styles.formGroup}>
                      <label>Heart Rate (bpm)</label>
                      <input
                        type="number"
                        value={vital.heart_rate}
                        onChange={(e) => updateVitalSigns(vital.id, 'heart_rate', e.target.value)}
                        placeholder="72"
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Respiratory Rate (breaths/min)</label>
                      <input
                        type="number"
                        value={vital.respiratory_rate}
                        onChange={(e) => updateVitalSigns(vital.id, 'respiratory_rate', e.target.value)}
                        placeholder="16"
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Oxygen Saturation (%)</label>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={vital.oxygen_saturation}
                        onChange={(e) => updateVitalSigns(vital.id, 'oxygen_saturation', e.target.value)}
                        placeholder="98"
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Weight</label>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <input
                          type="number"
                          step="0.1"
                          value={vital.weight}
                          onChange={(e) => updateVitalSigns(vital.id, 'weight', e.target.value)}
                          placeholder="150"
                          style={{ flex: 1 }}
                        />
                        <select
                          value={vital.weight_unit}
                          onChange={(e) => updateVitalSigns(vital.id, 'weight_unit', e.target.value)}
                          style={{ width: '70px' }}
                        >
                          <option value="lbs">lbs</option>
                          <option value="kg">kg</option>
                        </select>
                      </div>
                    </div>
                    <div className={styles.formGroup}>
                      <label>Height</label>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <input
                          type="number"
                          step="0.1"
                          value={vital.height}
                          onChange={(e) => updateVitalSigns(vital.id, 'height', e.target.value)}
                          placeholder="68"
                          style={{ flex: 1 }}
                        />
                        <select
                          value={vital.height_unit}
                          onChange={(e) => updateVitalSigns(vital.id, 'height_unit', e.target.value)}
                          style={{ width: '90px' }}
                        >
                          <option value="inches">inches</option>
                          <option value="cm">cm</option>
                        </select>
                      </div>
                    </div>
                    <div className={styles.formGroup}>
                      <label>BMI</label>
                      <input
                        type="number"
                        step="0.1"
                        value={vital.bmi}
                        onChange={(e) => updateVitalSigns(vital.id, 'bmi', e.target.value)}
                        placeholder="Calculated or entered"
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Pain Scale (0-10)</label>
                      <input
                        type="number"
                        min="0"
                        max="10"
                        value={vital.pain_scale}
                        onChange={(e) => updateVitalSigns(vital.id, 'pain_scale', e.target.value)}
                        placeholder="0"
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Notes</label>
                      <textarea
                        value={vital.notes}
                        onChange={(e) => updateVitalSigns(vital.id, 'notes', e.target.value)}
                        rows={2}
                        placeholder="Additional notes about vital signs..."
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Diagnostic Tests Section */}
          {currentSection === 'diagnostic_tests' && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>🧪 Diagnostic Tests</h2>
                <button onClick={addDiagnosticTest} className={styles.addButton}>+ Add Test</button>
              </div>

              {patientData.diagnostic_tests.length === 0 && (
                <p className={styles.emptyState}>No diagnostic tests yet. Click "+ Add Test" to begin.</p>
              )}

              {patientData.diagnostic_tests.map(test => (
                <div key={test.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>Diagnostic Test</h3>
                    <button onClick={() => removeDiagnosticTest(test.id)} className={styles.removeButton}>✕</button>
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <label>Date</label>
                      <input
                        type="date"
                        value={test.date}
                        onChange={(e) => updateDiagnosticTest(test.id, 'date', e.target.value)}
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Test Name</label>
                      <SearchableDropdown
                        value={test.test_name}
                        onChange={(val) => updateDiagnosticTest(test.id, 'test_name', val)}
                        commonOptions={COMMON_LAB_TESTS}
                        allOptions={ALL_LAB_TESTS}
                        placeholder="Search or select test..."
                        fieldKey={`test-name-${test.id}`}
                      />
                    </div>
                    {test.test_name === 'Other (custom)' && (
                      <div className={styles.formGroup}>
                        <label>Custom Test Name</label>
                        <input
                          type="text"
                          placeholder="Enter test name"
                          onChange={(e) => updateDiagnosticTest(test.id, 'test_name', e.target.value)}
                        />
                      </div>
                    )}
                    <div className={styles.formGroup}>
                      <label>Test Type</label>
                      <select
                        value={test.test_type}
                        onChange={(e) => updateDiagnosticTest(test.id, 'test_type', e.target.value)}
                      >
                        <option value="">Select type</option>
                        {TEST_TYPES.map(type => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </select>
                    </div>
                    <div className={styles.formGroup}>
                      <label>Result</label>
                      <input
                        type="text"
                        value={test.result}
                        onChange={(e) => updateDiagnosticTest(test.id, 'result', e.target.value)}
                        placeholder="Enter result value"
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>
                        <input
                          type="checkbox"
                          checked={test.abnormal}
                          onChange={(e) => updateDiagnosticTest(test.id, 'abnormal', e.target.checked)}
                        />
                        {' '}Abnormal
                      </label>
                      <label>
                        <input
                          type="checkbox"
                          checked={test.critical}
                          onChange={(e) => updateDiagnosticTest(test.id, 'critical', e.target.checked)}
                        />
                        {' '}Critical
                      </label>
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Interpretation</label>
                      <textarea
                        value={test.interpretation}
                        onChange={(e) => updateDiagnosticTest(test.id, 'interpretation', e.target.value)}
                        rows={3}
                        placeholder="Clinical interpretation..."
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* H&P Section */}
          {currentSection === 'history_physicals' && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>📝 History & Physical Examinations</h2>
                <button onClick={addHP} className={styles.addButton}>+ Add H&P</button>
              </div>

              {patientData.history_and_physicals.length === 0 && (
                <p className={styles.emptyState}>No H&P documents yet. Click "+ Add H&P" to begin.</p>
              )}

              {patientData.history_and_physicals.map(hp => (
                <div key={hp.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>History & Physical</h3>
                    <button onClick={() => removeHP(hp.id)} className={styles.removeButton}>✕</button>
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <label>Date</label>
                      <input
                        type="date"
                        value={hp.date}
                        onChange={(e) => updateHP(hp.id, 'date', e.target.value)}
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Author / Provider</label>
                      <input
                        type="text"
                        value={hp.author}
                        onChange={(e) => updateHP(hp.id, 'author', e.target.value)}
                        placeholder="Dr. Name"
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Chief Complaint</label>
                      <input
                        type="text"
                        value={hp.chief_complaint}
                        onChange={(e) => updateHP(hp.id, 'chief_complaint', e.target.value)}
                        placeholder="e.g., Chest pain"
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>History of Present Illness (HPI)</label>
                      <textarea
                        value={hp.history_of_present_illness}
                        onChange={(e) => updateHP(hp.id, 'history_of_present_illness', e.target.value)}
                        rows={4}
                        placeholder="Describe the present illness..."
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Review of Systems (ROS)</label>
                      <textarea
                        value={hp.review_of_systems}
                        onChange={(e) => updateHP(hp.id, 'review_of_systems', e.target.value)}
                        rows={4}
                        placeholder="Systematic review..."
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Physical Exam</label>
                      <textarea
                        value={hp.physical_exam}
                        onChange={(e) => updateHP(hp.id, 'physical_exam', e.target.value)}
                        rows={4}
                        placeholder="Physical examination findings..."
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Assessment</label>
                      <textarea
                        value={hp.assessment}
                        onChange={(e) => updateHP(hp.id, 'assessment', e.target.value)}
                        rows={3}
                        placeholder="Clinical assessment..."
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Plan</label>
                      <textarea
                        value={hp.plan}
                        onChange={(e) => updateHP(hp.id, 'plan', e.target.value)}
                        rows={3}
                        placeholder="Treatment plan..."
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Procedures Section */}
          {currentSection === 'procedures' && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>🔬 Procedures</h2>
                <button onClick={addProcedure} className={styles.addButton}>+ Add Procedure</button>
              </div>

              {patientData.procedures.length === 0 && (
                <p className={styles.emptyState}>No procedures yet. Click "+ Add Procedure" to begin.</p>
              )}

              {patientData.procedures.map(proc => (
                <div key={proc.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>Procedure</h3>
                    <button onClick={() => removeProcedure(proc.id)} className={styles.removeButton}>✕</button>
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <label>Date</label>
                      <input
                        type="date"
                        value={proc.date}
                        onChange={(e) => updateProcedure(proc.id, 'date', e.target.value)}
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Procedure Name</label>
                      <input
                        type="text"
                        value={proc.procedure_name}
                        onChange={(e) => updateProcedure(proc.id, 'procedure_name', e.target.value)}
                        placeholder="e.g., Coronary angiography"
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Operator / Surgeon</label>
                      <input
                        type="text"
                        value={proc.operator}
                        onChange={(e) => updateProcedure(proc.id, 'operator', e.target.value)}
                        placeholder="Dr. Name"
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Indication</label>
                      <textarea
                        value={proc.indication}
                        onChange={(e) => updateProcedure(proc.id, 'indication', e.target.value)}
                        rows={2}
                        placeholder="Reason for procedure..."
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Outcome</label>
                      <textarea
                        value={proc.outcome}
                        onChange={(e) => updateProcedure(proc.id, 'outcome', e.target.value)}
                        rows={3}
                        placeholder="Procedure outcome..."
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Complications (if any)</label>
                      <textarea
                        value={proc.complications}
                        onChange={(e) => updateProcedure(proc.id, 'complications', e.target.value)}
                        rows={2}
                        placeholder="None or describe complications..."
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Imaging Section */}
          {currentSection === 'imaging' && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>🏥 Imaging Studies</h2>
                <button onClick={addImagingStudy} className={styles.addButton}>+ Add Imaging</button>
              </div>

              {patientData.imaging_studies.length === 0 && (
                <p className={styles.emptyState}>No imaging studies yet. Click "+ Add Imaging" to begin.</p>
              )}

              {patientData.imaging_studies.map(img => (
                <div key={img.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>Imaging Study</h3>
                    <button onClick={() => removeImagingStudy(img.id)} className={styles.removeButton}>✕</button>
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <label>Date</label>
                      <input
                        type="date"
                        value={img.date}
                        onChange={(e) => updateImagingStudy(img.id, 'date', e.target.value)}
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Modality</label>
                      <select
                        value={img.modality}
                        onChange={(e) => updateImagingStudy(img.id, 'modality', e.target.value)}
                      >
                        <option value="">Select modality</option>
                        {IMAGING_MODALITIES.map(mod => (
                          <option key={mod} value={mod}>{mod}</option>
                        ))}
                      </select>
                    </div>
                    <div className={styles.formGroup}>
                      <label>Body Site</label>
                      <select
                        value={img.body_site}
                        onChange={(e) => updateImagingStudy(img.id, 'body_site', e.target.value)}
                      >
                        <option value="">Select body site</option>
                        {BODY_SITES.map(site => (
                          <option key={site} value={site}>{site}</option>
                        ))}
                      </select>
                    </div>
                    <div className={styles.formGroup}>
                      <label>Radiologist</label>
                      <input
                        type="text"
                        value={img.radiologist}
                        onChange={(e) => updateImagingStudy(img.id, 'radiologist', e.target.value)}
                        placeholder="Dr. Name"
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Indication</label>
                      <textarea
                        value={img.indication}
                        onChange={(e) => updateImagingStudy(img.id, 'indication', e.target.value)}
                        rows={2}
                        placeholder="Reason for imaging..."
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Findings</label>
                      <textarea
                        value={img.findings}
                        onChange={(e) => updateImagingStudy(img.id, 'findings', e.target.value)}
                        rows={4}
                        placeholder="Detailed imaging findings..."
                      />
                    </div>
                    <div className={styles.formGroupFull}>
                      <label>Impression</label>
                      <textarea
                        value={img.impression}
                        onChange={(e) => updateImagingStudy(img.id, 'impression', e.target.value)}
                        rows={2}
                        placeholder="Radiologist impression..."
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Conditions Section */}
          {currentSection === 'conditions' && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>📊 Active Medical Conditions</h2>
                <button onClick={addCondition} className={styles.addButton}>+ Add Condition</button>
              </div>

              {patientData.active_conditions.length === 0 && (
                <p className={styles.emptyState}>No conditions yet. Click "+ Add Condition" to begin.</p>
              )}

              {patientData.active_conditions.map(cond => (
                <div key={cond.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>Medical Condition</h3>
                    <button onClick={() => removeCondition(cond.id)} className={styles.removeButton}>✕</button>
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <label>Condition</label>
                      <SearchableDropdown
                        value={cond.code}
                        onChange={(val) => updateCondition(cond.id, 'code', val)}
                        commonOptions={COMMON_CONDITIONS}
                        allOptions={ALL_CONDITIONS}
                        placeholder="Search or select condition..."
                        fieldKey={`condition-${cond.id}`}
                      />
                    </div>
                    {cond.code === 'Other (custom)' && (
                      <div className={styles.formGroup}>
                        <label>Custom Condition</label>
                        <input
                          type="text"
                          placeholder="Enter condition name"
                          onChange={(e) => updateCondition(cond.id, 'code', e.target.value)}
                        />
                      </div>
                    )}
                    <div className={styles.formGroup}>
                      <label>Status</label>
                      <select
                        value={cond.status}
                        onChange={(e) => updateCondition(cond.id, 'status', e.target.value)}
                      >
                        <option value="active">Active</option>
                        <option value="resolved">Resolved</option>
                        <option value="inactive">Inactive</option>
                      </select>
                    </div>
                    <div className={styles.formGroup}>
                      <label>Recorded Date</label>
                      <input
                        type="date"
                        value={cond.recorded_date}
                        onChange={(e) => updateCondition(cond.id, 'recorded_date', e.target.value)}
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Onset Date</label>
                      <input
                        type="date"
                        value={cond.onset}
                        onChange={(e) => updateCondition(cond.id, 'onset', e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Medications Section */}
          {currentSection === 'medications' && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>💊 Current Medications</h2>
                <div>
                  <button 
                    onClick={checkMedicationSafety} 
                    className={styles.safetyButton}
                    disabled={checkingSafety}
                    style={{ marginRight: '10px' }}
                  >
                    {checkingSafety ? '⏳ Checking...' : '🛡️ Check Safety'}
                  </button>
                  <button onClick={addMedication} className={styles.addButton}>+ Add Medication</button>
                </div>
              </div>

              {patientData.current_medications.length === 0 && (
                <p className={styles.emptyState}>No medications yet. Click "+ Add Medication" to begin.</p>
              )}

              {patientData.current_medications.map(med => (
                <div key={med.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>Medication</h3>
                    <button onClick={() => removeMedication(med.id)} className={styles.removeButton}>✕</button>
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <label>Medication Name</label>
                      <SearchableDropdown
                        value={med.name}
                        onChange={(val) => updateMedication(med.id, 'name', val)}
                        commonOptions={COMMON_MEDICATIONS}
                        allOptions={ALL_MEDICATIONS}
                        placeholder="Search or select medication..."
                        fieldKey={`medication-${med.id}`}
                      />
                    </div>
                    {med.name === 'Other (custom)' && (
                      <div className={styles.formGroup}>
                        <label>Custom Medication</label>
                        <input
                          type="text"
                          placeholder="Enter medication name"
                          onChange={(e) => updateMedication(med.id, 'name', e.target.value)}
                        />
                      </div>
                    )}
                    <div className={styles.formGroup}>
                      <label>Dosage</label>
                      <input
                        type="text"
                        value={med.dosage}
                        onChange={(e) => updateMedication(med.id, 'dosage', e.target.value)}
                        placeholder="e.g., 20mg once daily"
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label>Status</label>
                      <select
                        value={med.status}
                        onChange={(e) => updateMedication(med.id, 'status', e.target.value)}
                      >
                        <option value="active">Active</option>
                        <option value="stopped">Stopped</option>
                        <option value="completed">Completed</option>
                      </select>
                    </div>
                    <div className={styles.formGroup}>
                      <label>Date Prescribed</label>
                      <input
                        type="date"
                        value={med.date_prescribed}
                        onChange={(e) => updateMedication(med.id, 'date_prescribed', e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Allergies Section */}
          {currentSection === 'allergies' && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>⚠️ Allergies & Intolerances</h2>
                <button onClick={addAllergy} className={styles.addButton}>+ Add Allergy</button>
              </div>

              {patientData.allergies.length === 0 && (
                <p className={styles.emptyState}>No allergies yet. Click "+ Add Allergy" to begin.</p>
              )}

              {patientData.allergies.map(allergy => (
                <div key={allergy.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>Allergy</h3>
                    <button onClick={() => removeAllergy(allergy.id)} className={styles.removeButton}>✕</button>
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <label>Allergen</label>
                      <SearchableDropdown
                        value={allergy.allergen}
                        onChange={(val) => updateAllergy(allergy.id, 'allergen', val)}
                        commonOptions={COMMON_ALLERGIES}
                        allOptions={ALL_ALLERGIES}
                        placeholder="Search or select allergen..."
                        fieldKey={`allergen-${allergy.id}`}
                      />
                    </div>
                    {allergy.allergen === 'Other (custom)' && (
                      <div className={styles.formGroup}>
                        <label>Custom Allergen</label>
                        <input
                          type="text"
                          placeholder="Enter allergen"
                          onChange={(e) => updateAllergy(allergy.id, 'allergen', e.target.value)}
                        />
                      </div>
                    )}
                    <div className={styles.formGroup}>
                      <label>Reaction</label>
                      <select
                        value={allergy.reaction}
                        onChange={(e) => updateAllergy(allergy.id, 'reaction', e.target.value)}
                      >
                        <option value="">Select reaction</option>
                        {ALLERGY_REACTIONS.map(reaction => (
                          <option key={reaction} value={reaction}>{reaction}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Family/Social History Section */}
          {currentSection === 'history' && (
            <div className={styles.section}>
              <h2>👨‍👩‍👧 Family & Social History</h2>
              <div className={styles.formGrid}>
                <div className={styles.formGroupFull}>
                  <label>Family History</label>
                  <textarea
                    value={patientData.family_history}
                    onChange={(e) => setPatientData({...patientData, family_history: e.target.value})}
                    rows={6}
                    placeholder="e.g., Father: MI at age 62; Mother: Type 2 diabetes, hypertension; Sister: breast cancer at age 50"
                  />
                </div>
                <div className={styles.formGroupFull}>
                  <label>Social History</label>
                  <textarea
                    value={patientData.social_history}
                    onChange={(e) => setPatientData({...patientData, social_history: e.target.value})}
                    rows={6}
                    placeholder="e.g., Former smoker (quit 2020, 20 pack-year history); Occasional alcohol use (2-3 drinks/week); Works as accountant; Married with 2 children"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Save Button */}
        <div className={styles.saveSection}>
          <button onClick={handleSave} className={styles.saveButton}>
            💾 Save Patient History
          </button>
          {savedMessage && (
            <div className={savedMessage.includes('✓') ? styles.successMessage : styles.errorMessage}>
              {savedMessage}
            </div>
          )}
        </div>
      </div>

      {/* Medication Safety Modal */}
      {showSafetyModal && medicationSafetyResult && (
        <div className={styles.modalOverlay} onClick={() => setShowSafetyModal(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>🛡️ Medication Safety Report</h2>
              <button className={styles.closeButton} onClick={() => setShowSafetyModal(false)}>✕</button>
            </div>
            
            <div className={styles.modalBody}>
              {/* Safety Score */}
              <div className={styles.safetyScore}>
                <div className={styles.scoreCircle} style={{
                  borderColor: medicationSafetyResult.safety_score >= 90 ? '#10b981' :
                               medicationSafetyResult.safety_score >= 70 ? '#f59e0b' : '#ef4444'
                }}>
                  <span className={styles.scoreNumber}>{medicationSafetyResult.safety_score}</span>
                  <span className={styles.scoreLabel}>Safety Score</span>
                </div>
                <p className={styles.scoreSummary}>{medicationSafetyResult.summary}</p>
              </div>

              {/* Alerts */}
              {medicationSafetyResult.alerts && medicationSafetyResult.alerts.length > 0 && (
                <div className={styles.alertsSection}>
                  <h3>⚠️ Safety Alerts ({medicationSafetyResult.alerts.length})</h3>
                  {medicationSafetyResult.alerts.map((alert, index) => (
                    <div key={index} className={`${styles.alertCard} ${styles[alert.severity]}`}>
                      <div className={styles.alertHeader}>
                        <span className={styles.alertType}>
                          {alert.alert_type === 'drug_interaction' ? '💊' :
                           alert.alert_type === 'contraindication' ? '🚫' :
                           alert.alert_type === 'allergen_cross_reactivity' ? '⚠️' :
                           alert.alert_type === 'dose_concern' ? '📊' :
                           alert.alert_type === 'pregnancy_risk' ? '🤰' :
                           alert.alert_type === 'renal_adjustment' ? '🩺' :
                           alert.alert_type === 'hepatic_adjustment' ? '🩺' : '⚠️'}
                          {' '}
                          {alert.alert_type.replace(/_/g, ' ').toUpperCase()}
                        </span>
                        <span className={styles.severityBadge}>{alert.severity}</span>
                      </div>
                      
                      <p className={styles.alertMedication}>
                        <strong>Medication:</strong> {alert.medication}
                        {alert.interacting_medication && (
                          <span> + {alert.interacting_medication}</span>
                        )}
                        {alert.condition && (
                          <span> with {alert.condition}</span>
                        )}
                        {alert.allergen && alert.cross_reactive_drug && (
                          <span> ({alert.allergen} → {alert.cross_reactive_drug})</span>
                        )}
                      </p>

                      {alert.clinical_effect && (
                        <p className={styles.alertEffect}>
                          <strong>Clinical Effect:</strong> {alert.clinical_effect}
                        </p>
                      )}

                      {alert.recommendation && (
                        <p className={styles.alertRecommendation}>
                          <strong>Recommendation:</strong> {alert.recommendation}
                        </p>
                      )}

                      {alert.monitoring && (
                        <p className={styles.alertMonitoring}>
                          <strong>Monitoring:</strong> {alert.monitoring}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* No Alerts */}
              {(!medicationSafetyResult.alerts || medicationSafetyResult.alerts.length === 0) && (
                <div className={styles.noAlerts}>
                  <p>✅ No safety concerns detected with current medication regimen.</p>
                </div>
              )}

              {/* Additional Info */}
              {medicationSafetyResult.requires_monitoring && medicationSafetyResult.requires_monitoring.length > 0 && (
                <div className={styles.infoSection}>
                  <h4>📋 Requires Monitoring</h4>
                  <ul>
                    {medicationSafetyResult.requires_monitoring.map((med, index) => (
                      <li key={index}>{med}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className={styles.modalFooter}>
              <button className={styles.primaryButton} onClick={() => setShowSafetyModal(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
