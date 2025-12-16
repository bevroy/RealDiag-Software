"""
Comprehensive ICD-10 Code Database
Maps ICD-10 codes to diagnosis names for search functionality
"""

ICD10_DATABASE = {
    # Infectious Diseases (A00-B99)
    "A00.0": "Cholera due to Vibrio cholerae 01, biovar cholerae",
    "A00.1": "Cholera due to Vibrio cholerae 01, biovar eltor",
    "A00.9": "Cholera, unspecified",
    "A01.0": "Typhoid fever",
    "A02.0": "Salmonella enteritis",
    "A09": "Infectious gastroenteritis and colitis, unspecified",
    "A15.0": "Tuberculosis of lung",
    "A15.9": "Respiratory tuberculosis unspecified",
    "A40.0": "Sepsis due to streptococcus, group A",
    "A40.1": "Sepsis due to streptococcus, group B",
    "A40.9": "Streptococcal sepsis, unspecified",
    "A41.0": "Sepsis due to Staphylococcus aureus",
    "A41.9": "Sepsis, unspecified organism",
    "B00.9": "Herpesviral infection, unspecified",
    "B01.9": "Varicella without complication",
    "B02.9": "Zoster without complications",
    "B15.9": "Hepatitis A without hepatic coma",
    "B16.9": "Acute hepatitis B without delta-agent and without hepatic coma",
    "B17.1": "Acute hepatitis C",
    "B18.1": "Chronic viral hepatitis B without delta-agent",
    "B18.2": "Chronic viral hepatitis C",
    "B19.9": "Unspecified viral hepatitis without hepatic coma",
    "B20": "Human immunodeficiency virus [HIV] disease",
    
    # Neoplasms (C00-D49)
    "C34.90": "Malignant neoplasm of unspecified part of unspecified bronchus or lung",
    "C50.919": "Malignant neoplasm of unspecified site of unspecified female breast",
    "C61": "Malignant neoplasm of prostate",
    "C18.9": "Malignant neoplasm of colon, unspecified",
    "C20": "Malignant neoplasm of rectum",
    "C25.9": "Malignant neoplasm of pancreas, unspecified",
    "C73": "Malignant neoplasm of thyroid gland",
    "C91.10": "Chronic lymphocytic leukemia of B-cell type not having achieved remission",
    "D50.9": "Iron deficiency anemia, unspecified",
    "D64.9": "Anemia, unspecified",
    
    # Endocrine (E00-E89)
    "E03.9": "Hypothyroidism, unspecified",
    "E05.90": "Thyrotoxicosis, unspecified without thyrotoxic crisis or storm",
    "E10.9": "Type 1 diabetes mellitus without complications",
    "E10.65": "Type 1 diabetes mellitus with hyperglycemia",
    "E11.9": "Type 2 diabetes mellitus without complications",
    "E11.65": "Type 2 diabetes mellitus with hyperglycemia",
    "E11.22": "Type 2 diabetes mellitus with diabetic chronic kidney disease",
    "E11.36": "Type 2 diabetes mellitus with diabetic cataract",
    "E66.9": "Obesity, unspecified",
    "E78.5": "Hyperlipidemia, unspecified",
    "E87.6": "Hypokalemia",
    "E87.5": "Hyperkalemia",
    "E86.0": "Dehydration",
    
    # Mental and Behavioral (F01-F99)
    "F10.20": "Alcohol dependence, uncomplicated",
    "F17.210": "Nicotine dependence, cigarettes, uncomplicated",
    "F20.9": "Schizophrenia, unspecified",
    "F31.9": "Bipolar disorder, unspecified",
    "F32.9": "Major depressive disorder, single episode, unspecified",
    "F33.9": "Major depressive disorder, recurrent, unspecified",
    "F41.0": "Panic disorder [episodic paroxysmal anxiety]",
    "F41.1": "Generalized anxiety disorder",
    "F41.9": "Anxiety disorder, unspecified",
    "F43.10": "Post-traumatic stress disorder, unspecified",
    
    # Nervous System (G00-G99)
    "G40.909": "Epilepsy, unspecified, not intractable, without status epilepticus",
    "G43.909": "Migraine, unspecified, not intractable, without status migrainosus",
    "G45.9": "Transient cerebral ischemic attack, unspecified",
    "G47.00": "Insomnia, unspecified",
    "G62.9": "Polyneuropathy, unspecified",
    "G89.29": "Other chronic pain",
    
    # Eye and Adnexa (H00-H59)
    "H10.9": "Conjunctivitis, unspecified",
    "H40.9": "Unspecified glaucoma",
    "H52.4": "Presbyopia",
    
    # Ear and Mastoid (H60-H95)
    "H60.90": "Unspecified otitis externa, unspecified ear",
    "H65.90": "Unspecified nonsuppurative otitis media, unspecified ear",
    "H66.90": "Otitis media, unspecified, unspecified ear",
    "H81.49": "Vertigo of central origin, unspecified ear",
    "H91.90": "Unspecified hearing loss, unspecified ear",
    
    # Circulatory System (I00-I99)
    "I10": "Essential (primary) hypertension",
    "I11.9": "Hypertensive heart disease without heart failure",
    "I20.0": "Unstable angina",
    "I20.9": "Angina pectoris, unspecified",
    "I21.3": "ST elevation (STEMI) myocardial infarction of unspecified site",
    "I21.4": "Non-ST elevation (NSTEMI) myocardial infarction",
    "I21.9": "Acute myocardial infarction, unspecified",
    "I25.10": "Atherosclerotic heart disease of native coronary artery without angina pectoris",
    "I48.91": "Unspecified atrial fibrillation",
    "I49.9": "Cardiac arrhythmia, unspecified",
    "I50.9": "Heart failure, unspecified",
    "I50.23": "Acute on chronic systolic (congestive) heart failure",
    "I50.33": "Acute on chronic diastolic (congestive) heart failure",
    "I50.43": "Acute on chronic combined systolic (congestive) and diastolic (congestive) heart failure",
    "I63.9": "Cerebral infarction, unspecified",
    "I64": "Stroke, not specified as hemorrhage or infarction",
    "I73.9": "Peripheral vascular disease, unspecified",
    "I80.3": "Phlebitis and thrombophlebitis of lower extremities, unspecified",
    "I82.409": "Acute embolism and thrombosis of unspecified deep veins of unspecified lower extremity",
    
    # Respiratory System (J00-J99)
    "J00": "Acute nasopharyngitis [common cold]",
    "J01.90": "Acute sinusitis, unspecified",
    "J02.9": "Acute pharyngitis, unspecified",
    "J03.90": "Acute tonsillitis, unspecified",
    "J06.9": "Acute upper respiratory infection, unspecified",
    "J18.9": "Pneumonia, unspecified organism",
    "J20.9": "Acute bronchitis, unspecified",
    "J42": "Unspecified chronic bronchitis",
    "J44.0": "Chronic obstructive pulmonary disease with acute lower respiratory infection",
    "J44.1": "Chronic obstructive pulmonary disease with (acute) exacerbation",
    "J44.9": "Chronic obstructive pulmonary disease, unspecified",
    "J45.909": "Unspecified asthma, uncomplicated",
    "J45.40": "Moderate persistent asthma, uncomplicated",
    "J45.41": "Moderate persistent asthma with (acute) exacerbation",
    "J81.0": "Acute pulmonary edema",
    "J90": "Pleural effusion, not elsewhere classified",
    "J96.00": "Acute respiratory failure, unspecified whether with hypoxia or hypercapnia",
    
    # Digestive System (K00-K95)
    "K21.9": "Gastro-esophageal reflux disease without esophagitis",
    "K25.9": "Gastric ulcer, unspecified as acute or chronic, without hemorrhage or perforation",
    "K29.70": "Gastritis, unspecified, without bleeding",
    "K30": "Functional dyspepsia",
    "K35.80": "Unspecified acute appendicitis",
    "K40.90": "Unilateral inguinal hernia, without obstruction or gangrene, not specified as recurrent",
    "K50.90": "Crohn's disease, unspecified, without complications",
    "K51.90": "Ulcerative colitis, unspecified, without complications",
    "K52.9": "Noninfective gastroenteritis and colitis, unspecified",
    "K56.60": "Unspecified intestinal obstruction",
    "K57.90": "Diverticulosis of intestine, part unspecified, without perforation or abscess without bleeding",
    "K58.9": "Irritable bowel syndrome without diarrhea",
    "K59.00": "Constipation, unspecified",
    "K70.30": "Alcoholic cirrhosis of liver without ascites",
    "K74.60": "Unspecified cirrhosis of liver",
    "K76.0": "Fatty (change of) liver, not elsewhere classified",
    "K80.20": "Calculus of gallbladder without cholecystitis without obstruction",
    "K85.90": "Acute pancreatitis, unspecified",
    "K86.1": "Other chronic pancreatitis",
    "K92.2": "Gastrointestinal hemorrhage, unspecified",
    
    # Skin (L00-L99)
    "L02.91": "Cutaneous abscess, unspecified",
    "L03.90": "Cellulitis, unspecified",
    "L20.9": "Atopic dermatitis, unspecified",
    "L30.9": "Dermatitis, unspecified",
    "L40.9": "Psoriasis, unspecified",
    "L50.9": "Urticaria, unspecified",
    "L89.159": "Pressure ulcer of sacral region, unspecified stage",
    "L97.909": "Non-pressure chronic ulcer of unspecified part of unspecified lower leg with unspecified severity",
    
    # Musculoskeletal (M00-M99)
    "M05.9": "Rheumatoid arthritis with rheumatoid factor, unspecified",
    "M06.9": "Rheumatoid arthritis, unspecified",
    "M10.9": "Gout, unspecified",
    "M15.9": "Polyosteoarthritis, unspecified",
    "M19.90": "Unspecified osteoarthritis, unspecified site",
    "M25.50": "Pain in unspecified joint",
    "M54.5": "Low back pain",
    "M54.2": "Cervicalgia",
    "M79.3": "Panniculitis, unspecified",
    "M81.0": "Age-related osteoporosis without current pathological fracture",
    
    # Genitourinary (N00-N99)
    "N18.3": "Chronic kidney disease, stage 3 (moderate)",
    "N18.5": "Chronic kidney disease, stage 5",
    "N18.9": "Chronic kidney disease, unspecified",
    "N20.0": "Calculus of kidney",
    "N20.1": "Calculus of ureter",
    "N20.2": "Calculus of kidney with calculus of ureter",
    "N30.00": "Acute cystitis without hematuria",
    "N39.0": "Urinary tract infection, site not specified",
    "N40.0": "Benign prostatic hyperplasia without lower urinary tract symptoms",
    
    # Pregnancy (O00-O9A)
    "O00.9": "Ectopic pregnancy, unspecified",
    "O03.9": "Complete or unspecified spontaneous abortion without complication",
    "O24.419": "Gestational diabetes mellitus in pregnancy, unspecified control",
    "O80": "Encounter for full-term uncomplicated delivery",
    
    # Injury and Poisoning (S00-T88)
    "S06.0X0A": "Concussion without loss of consciousness, initial encounter",
    "S06.9X9A": "Unspecified intracranial injury with loss of consciousness of unspecified duration, initial encounter",
    "S22.32XA": "Fracture of one rib, left side, initial encounter for closed fracture",
    "S42.001A": "Fracture of unspecified part of right clavicle, initial encounter for closed fracture",
    "S52.501A": "Unspecified fracture of the lower end of right radius, initial encounter for closed fracture",
    "S72.001A": "Fracture of unspecified part of neck of right femur, initial encounter for closed fracture",
    "S82.001A": "Unspecified fracture of right patella, initial encounter for closed fracture",
    "T14.90XA": "Injury, unspecified, initial encounter",
    "T78.40XA": "Allergy, unspecified, initial encounter",
    
    # External Causes (V00-Y99)
    "Z00.00": "Encounter for general adult medical examination without abnormal findings",
    "Z23": "Encounter for immunization",
    "Z79.4": "Long term (current) use of insulin",
    "Z79.899": "Other long term (current) drug therapy",
}

def get_diagnosis_from_icd10(code: str) -> str:
    """
    Get diagnosis name from ICD-10 code
    Returns the diagnosis name or None if not found
    """
    code_upper = code.upper().strip()
    
    # Try exact match first
    if code_upper in ICD10_DATABASE:
        return ICD10_DATABASE[code_upper]
    
    # Try without trailing characters (e.g., "I21" from "I21.9")
    if "." in code_upper:
        base_code = code_upper.split(".")[0]
        for icd_code, diagnosis in ICD10_DATABASE.items():
            if icd_code.startswith(base_code):
                return diagnosis
    
    return None

def search_icd10_by_diagnosis(query: str) -> list:
    """
    Search ICD-10 codes by diagnosis name
    Returns list of (code, diagnosis_name) tuples
    """
    query_upper = query.upper()
    results = []
    
    for code, diagnosis in ICD10_DATABASE.items():
        if query_upper in diagnosis.upper():
            results.append((code, diagnosis))
    
    return results
