"""
Comprehensive SNOMED CT Code Database
Maps SNOMED CT codes to diagnosis/condition names for search functionality
"""

SNOMED_DATABASE = {
    # Infectious Diseases
    "63650001": "Cholera",
    "4834000": "Typhoid fever",
    "302231008": "Salmonella gastroenteritis",
    "95891005": "Influenza",
    "6142004": "Influenza A",
    "442438000": "Influenza due to influenza A virus subtype H1N1",
    "40733004": "Infectious disease",
    "409822003": "Sepsis",
    "91302008": "Sepsis syndrome",
    "10001005": "Bacterial sepsis",
    "56819008": "Tuberculosis",
    "154283005": "Pulmonary tuberculosis",
    "240532009": "Human immunodeficiency virus infection",
    "86406008": "Human immunodeficiency virus infection",
    "38362002": "Herpes simplex",
    "38907003": "Varicella",
    "4740000": "Herpes zoster",
    "40468003": "Viral hepatitis A",
    "66071002": "Viral hepatitis B",
    "50711007": "Viral hepatitis C",
    "235869004": "Chronic viral hepatitis C",
    
    # Cardiovascular
    "38341003": "Hypertensive disorder",
    "59621000": "Essential hypertension",
    "429457004": "Systolic heart failure",
    "48447003": "Chronic heart failure",
    "56265001": "Heart disease",
    "414545008": "Ischemic heart disease",
    "413838009": "Chronic ischemic heart disease",
    "53741008": "Coronary arteriosclerosis",
    "194828000": "Angina pectoris",
    "25106000": "Unstable angina",
    "57054005": "Acute myocardial infarction",
    "401314000": "Acute ST segment elevation myocardial infarction",
    "401303003": "Acute non-ST segment elevation myocardial infarction",
    "233970002": "Coronary artery thrombosis",
    "49436004": "Atrial fibrillation",
    "5370000": "Atrial flutter",
    "698247007": "Cardiac arrhythmia",
    "230690007": "Cerebrovascular accident",
    "422504002": "Ischemic stroke",
    "432504007": "Cerebral infarction",
    "266257000": "Transient ischemic attack",
    "37796009": "Migraine",
    "56097005": "Migraine without aura",
    "4473006": "Migraine with aura",
    "52702003": "Chronic obstructive lung disease",
    "312453006": "Chronic obstructive lung disease with acute exacerbation",
    
    # Respiratory
    "10509002": "Acute bronchitis",
    "195967001": "Asthma",
    "370218001": "Mild persistent asthma",
    "370219009": "Moderate persistent asthma",
    "370220003": "Severe persistent asthma",
    "233604007": "Pneumonia",
    "385093006": "Community acquired pneumonia",
    "53084003": "Bacterial pneumonia",
    "233607000": "Aspiration pneumonia",
    "444814009": "Viral pneumonia",
    "82272006": "Common cold",
    "54398005": "Upper respiratory infection",
    "363746003": "Acute sinusitis",
    "40055000": "Chronic sinusitis",
    "126485001": "Acute pharyngitis",
    "90176007": "Tonsillitis",
    "195708003": "Acute pulmonary edema",
    "60046008": "Pleural effusion",
    "409622000": "Respiratory failure",
    "65710008": "Acute respiratory failure",
    
    # Gastrointestinal
    "235595009": "Gastroesophageal reflux disease",
    "13645005": "Chronic gastroesophageal reflux disease",
    "397825006": "Gastric ulcer",
    "312359006": "Duodenal ulcer",
    "4556007": "Gastritis",
    "266503006": "Functional dyspepsia",
    "74400008": "Appendicitis",
    "85189001": "Acute appendicitis",
    "34000006": "Crohn disease",
    "64766004": "Ulcerative colitis",
    "24526004": "Inflammatory bowel disease",
    "235595009": "Gastroesophageal reflux disease",
    "235796007": "Irritable bowel syndrome",
    "62315008": "Diarrhea",
    "14760008": "Constipation",
    "197321007": "Stomatitis",
    "235919008": "Cholecystitis",
    "266474003": "Cholelithiasis",
    "197456007": "Acute pancreatitis",
    "197465000": "Chronic pancreatitis",
    "197321007": "Stomatitis",
    "235494005": "Chronic liver disease",
    "19943007": "Cirrhosis of liver",
    "197279005": "Alcoholic cirrhosis",
    "10761003": "Hepatic encephalopathy",
    "128241005": "Inflammatory disease of liver",
    
    # Endocrine and Metabolic
    "73211009": "Diabetes mellitus",
    "46635009": "Type 1 diabetes mellitus",
    "44054006": "Type 2 diabetes mellitus",
    "11687002": "Gestational diabetes mellitus",
    "190416003": "Type 1 diabetes mellitus with ketoacidosis",
    "421725003": "Diabetes mellitus due to pancreatic insufficiency",
    "81531005": "Diabetic neuropathy",
    "390834004": "Diabetic nephropathy",
    "4855003": "Diabetic retinopathy",
    "40930008": "Hypothyroidism",
    "66893009": "Primary hypothyroidism",
    "34486009": "Hyperthyroidism",
    "353295004": "Graves disease",
    "190905008": "Cushing syndrome",
    "14304000": "Addison disease",
    "237599002": "Hyperlipidemia",
    "267432004": "Hypercholesterolemia",
    "55822004": "Hyperlipidemia",
    "238131007": "Obesity",
    "414916001": "Morbid obesity",
    "414915002": "Overweight",
    "272036006": "Dehydration",
    "43381005": "Hyponatremia",
    "14140009": "Hypernatremia",
    "43339004": "Hypokalemia",
    "14140009": "Hyperkalemia",
    
    # Neurological
    "84757009": "Epilepsy",
    "313307000": "Epileptic seizure",
    "91175000": "Seizure disorder",
    "230456007": "Status epilepticus",
    "193462001": "Insomnia",
    "271782001": "Sleep disorder",
    "193462001": "Insomnia",
    "128188000": "Paralysis",
    "29ひびひ64006": "Multiple sclerosis",
    "49049000": "Parkinson disease",
    "26929004": "Alzheimer disease",
    "52448006": "Dementia",
    "52052004": "Bell palsy",
    "427139004": "Facial nerve palsy",
    "367391008": "Peripheral neuropathy",
    "302226006": "Diabetic peripheral neuropathy",
    
    # Psychiatric
    "35489007": "Depression",
    "370143000": "Major depressive disorder",
    "36923009": "Major depression single episode",
    "191610000": "Panic disorder",
    "21897009": "Gender dysphoria",
    "48694002": "Anxiety",
    "197480006": "Anxiety disorder",
    "13746004": "Bipolar disorder",
    "191461001": "Manic disorder",
    "36923009": "Major depression single episode",
    "191736004": "Obsessive-compulsive disorder",
    "47505003": "Posttraumatic stress disorder",
    "58214004": "Schizophrenia",
    "191542003": "Schizophrenia and related disorders",
    "191816009": "Attention deficit hyperactivity disorder",
    "7200002": "Alcoholism",
    "66590003": "Alcohol dependence",
    "191816009": "Attention deficit hyperactivity disorder",
    
    # Musculoskeletal
    "3723001": "Arthritis",
    "69896004": "Rheumatoid arthritis",
    "239873007": "Osteoarthritis",
    "396275006": "Osteoarthritis of knee",
    "201834006": "Localized osteoarthritis",
    "90560007": "Gout",
    "239872002": "Osteopenia",
    "64859006": "Osteoporosis",
    "16114001": "Fracture",
    "125605004": "Fracture of bone",
    "161891005": "Back pain",
    "279039007": "Low back pain",
    "81680005": "Neck pain",
    "123946008": "Thoracic back pain",
    "22253000": "Pain",
    "82423001": "Chronic pain",
    "274664007": "Joint pain",
    "68962001": "Muscle pain",
    
    # Genitourinary
    "709044004": "Chronic kidney disease",
    "46177005": "End-stage renal disease",
    "90688005": "Chronic renal failure",
    "68566005": "Urinary tract infection",
    "38822007": "Cystitis",
    "236664009": "Acute cystitis",
    "237754008": "Chronic cystitis",
    "95570007": "Kidney stone",
    "95570007": "Urolithiasis",
    "65074000": "Ureterolithiasis",
    "233903004": "Vesical calculus",
    "236636009": "Acute kidney injury",
    "73211009": "Diabetes mellitus",
    "90708001": "Kidney disease",
    "199225007": "Chronic kidney disease stage 3",
    "433144002": "Chronic kidney disease stage 4",
    "433146000": "Chronic kidney disease stage 5",
    "236636009": "Acute kidney injury",
    
    # Dermatological
    "3013004": "Cellulitis",
    "128045006": "Cellulitis",
    "409498004": "Abscess",
    "47665007": "Dermatitis",
    "24079001": "Atopic dermatitis",
    "238575004": "Allergic contact dermatitis",
    "9014002": "Psoriasis",
    "126485001": "Acute pharyngitis",
    "126417005": "Cellulitis and abscess of leg",
    "402588000": "Stasis dermatitis",
    "422000003": "Venous stasis ulcer",
    "399912005": "Pressure ulcer",
    "26298008": "Urticaria",
    "402408009": "Acute urticaria",
    "427419006": "Chronic urticaria",
    
    # Hematological
    "271737000": "Anemia",
    "87522002": "Iron deficiency anemia",
    "83414005": "Vitamin B12 deficiency anemia",
    "41841004": "Folate deficiency anemia",
    "417357006": "Sickle cell disease",
    "74474003": "Gastrointestinal hemorrhage",
    "307164000": "Gastrointestinal bleeding",
    "27177004": "Deep vein thrombosis",
    "233935004": "Acute deep vein thrombosis",
    "59282003": "Pulmonary embolism",
    "233937007": "Acute pulmonary embolism",
    
    # Oncological
    "363346000": "Malignant neoplastic disease",
    "93870000": "Primary malignant neoplasm",
    "254637007": "Non-small cell lung cancer",
    "254632001": "Small cell carcinoma of lung",
    "363443007": "Malignant tumor of prostate",
    "399068003": "Malignant tumor of breast",
    "93761005": "Primary malignant neoplasm of colon",
    "363510005": "Malignant tumor of pancreas",
    "353431000119107": "Acute myeloid leukemia",
    "92814006": "Chronic lymphocytic leukemia",
    "413448007": "Chronic myeloid leukemia",
    "414029004": "Disorder of brain",
    
    # Eye and Ear
    "1491003": "Conjunctivitis",
    "9826008": "Conjunctivitis due to bacteria",
    "193570009": "Cataract",
    "77075001": "Senile cataract",
    "23986001": "Glaucoma",
    "392288008": "Primary open-angle glaucoma",
    "193638007": "Age-related macular degeneration",
    "65363002": "Otitis media",
    "3110003": "Acute otitis media",
    "155287003": "Chronic otitis media",
    "70394003": "Otitis externa",
    "39004005": "Tinnitus",
    "15188001": "Hearing loss",
    "60700002": "Sensorineural hearing loss",
    "44057004": "Conductive hearing loss",
    
    # Pregnancy and Perinatal
    "34801009": "Ectopic pregnancy",
    "79586000": "Tubal pregnancy",
    "17369002": "Miscarriage",
    "11687002": "Gestational diabetes mellitus",
    "48194001": "Pregnancy-induced hypertension",
    "398254007": "Preeclampsia",
    "15938005": "Eclampsia",
    "237238006": "Pregnancy",
    "289908002": "Pregnancy in third trimester",
    
    # Trauma and Injury
    "125670008": "Concussion with loss of consciousness",
    "110030002": "Concussion injury of brain",
    "125605004": "Fracture of bone",
    "82271004": "Injury of head",
    "417746004": "Traumatic injury",
    "125670008": "Concussion with loss of consciousness",
    "242786009": "Sprain",
    "3157004": "Strain",
    "125593007": "Open wound",
    "125667009": "Contusion",
    "125665001": "Crushing injury",
    "283545005": "Laceration",
    
    # Allergic and Immunologic
    "419076005": "Allergic rhinitis",
    "232346004": "Allergic bronchopulmonary aspergillosis",
    "91935009": "Allergy to peanuts",
    "300913006": "Penicillin allergy",
    "419263009": "Allergy to bee venom",
    "232347008": "Drug hypersensitivity",
    "609328004": "Allergic disposition",
    "14304000": "Addison disease",
    
    # Preventive Care and Health Maintenance
    "310611001": "Immunization given",
    "710824005": "Long-term care",
    "413712001": "Primary prevention",
    "310611001": "Immunization given",
}

def get_diagnosis_from_snomed(code: str) -> str:
    """
    Get diagnosis name from SNOMED CT code
    Returns the diagnosis name or None if not found
    """
    code_clean = code.strip()
    
    # Try exact match
    if code_clean in SNOMED_DATABASE:
        return SNOMED_DATABASE[code_clean]
    
    return None

def search_snomed_by_diagnosis(query: str) -> list:
    """
    Search SNOMED CT codes by diagnosis name
    Returns list of (code, diagnosis_name) tuples
    """
    query_upper = query.upper()
    results = []
    
    for code, diagnosis in SNOMED_DATABASE.items():
        if query_upper in diagnosis.upper():
            results.append((code, diagnosis))
    
    return results

def get_snomed_codes_for_diagnosis(diagnosis_name: str) -> list:
    """
    Get all SNOMED codes that match a diagnosis name
    Returns list of codes
    """
    diagnosis_upper = diagnosis_name.upper()
    codes = []
    
    for code, name in SNOMED_DATABASE.items():
        if diagnosis_upper in name.upper() or name.upper() in diagnosis_upper:
            codes.append(code)
    
    return codes
