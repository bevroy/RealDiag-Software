#!/usr/bin/env python3
"""
Add ICD-10 codes to decision tree files based on their condition names.
"""

import yaml
from pathlib import Path
import re

# Comprehensive ICD-10 mapping for common medical conditions
ICD10_MAPPING = {
    # Cardiology
    "CHEST-PAIN": "R07.9",
    "ACS": "I21.9",
    "MI": "I21.9",
    "STEMI": "I21.3",
    "NSTEMI": "I21.4",
    "ANGINA": "I20.9",
    "PERICARDITIS": "I30.9",
    "MYOCARDITIS": "I40.9",
    "CHF": "I50.9",
    "HEART-FAILURE": "I50.9",
    "HF-SYSTOLIC": "I50.20",
    "HF-DIASTOLIC": "I50.30",
    "AFIB": "I48.91",
    "ATRIAL-FIB": "I48.91",
    "PALPITATIONS": "R00.2",
    "SVT": "I47.1",
    "VTACH": "I47.2",
    "SYNCOPE": "R55",
    "HTN": "I10",
    "HYPERTENSION": "I10",
    "HTN-EMERGENCY": "I16.9",
    "AORTIC-DISSECTION": "I71.00",
    "PE": "I26.9",
    "PULMONARY-EMBOLISM": "I26.9",
    "DVT": "I82.9",
    "ENDOCARDITIS": "I33.0",
    "TAMPONADE": "I31.4",
    "CARDIOMYOPATHY": "I42.9",
    "VALVULAR": "I38",
    "AORTIC-STENOSIS": "I35.0",
    "MITRAL-REGURG": "I34.0",
    
    # Neurology
    "HEADACHE": "R51",
    "MIGRAINE": "G43.909",
    "TENSION-HEADACHE": "G44.209",
    "CLUSTER-HEADACHE": "G44.009",
    "SEIZURE": "R56.9",
    "EPILEPSY": "G40.909",
    "STATUS-EPILEPTICUS": "G41.9",
    "STROKE": "I63.9",
    "CVA": "I63.9",
    "ISCHEMIC-STROKE": "I63.9",
    "HEMORRHAGIC-STROKE": "I61.9",
    "TIA": "G45.9",
    "SAH": "I60.9",
    "ICH": "I61.9",
    "VERTIGO": "R42",
    "BPPV": "H81.1",
    "MENIERES": "H81.0",
    "CONFUSION": "R41.0",
    "ALTERED-MS": "R40.4",
    "ALTERED-MENTAL-STATUS": "R40.4",
    "DELIRIUM": "F05",
    "DEMENTIA": "F03.90",
    "ALZHEIMERS": "G30.9",
    "PARKINSONS": "G20",
    "MS": "G35",
    "MULTIPLE-SCLEROSIS": "G35",
    "GBS": "G61.0",
    "GUILLAIN-BARRE": "G61.0",
    "MYASTHENIA-GRAVIS": "G70.00",
    "ALS": "G12.21",
    "MENINGITIS": "G03.9",
    "ENCEPHALITIS": "G04.90",
    "BELLS-PALSY": "G51.0",
    "TRIGEMINAL-NEURALGIA": "G50.0",
    "NEUROPATHY": "G62.9",
    "PERIPHERAL-NEUROPATHY": "G62.9",
    "CARPAL-TUNNEL": "G56.00",
    "RADICULOPATHY": "M54.10",
    "SCIATICA": "M54.30",
    "WEAKNESS": "M62.81",
    "TREMOR": "R25.1",
    
    # Gastroenterology
    "ABD-PAIN": "R10.9",
    "ABDOMINAL-PAIN": "R10.9",
    "NAUSEA": "R11.0",
    "VOMITING": "R11.10",
    "DIARRHEA": "R19.7",
    "CONSTIPATION": "K59.00",
    "GI-BLEED": "K92.2",
    "UPPER-GI-BLEED": "K92.2",
    "LOWER-GI-BLEED": "K62.5",
    "HEMATEMESIS": "K92.0",
    "MELENA": "K92.1",
    "HEMATOCHEZIA": "K92.1",
    "GERD": "K21.9",
    "PUD": "K27.9",
    "PEPTIC-ULCER": "K27.9",
    "GASTRITIS": "K29.70",
    "PANCREATITIS": "K85.9",
    "ACUTE-PANCREATITIS": "K85.9",
    "CHRONIC-PANCREATITIS": "K86.1",
    "CHOLECYSTITIS": "K81.9",
    "CHOLELITHIASIS": "K80.20",
    "GALLSTONES": "K80.20",
    "CHOLANGITIS": "K83.0",
    "HEPATITIS": "K75.9",
    "CIRRHOSIS": "K74.60",
    "ASCITES": "R18.8",
    "IBD": "K50.90",
    "CROHNS": "K50.90",
    "ULCERATIVE-COLITIS": "K51.90",
    "IBS": "K58.9",
    "DIVERTICULITIS": "K57.92",
    "APPENDICITIS": "K37",
    "BOWEL-OBSTRUCTION": "K56.60",
    "ILEUS": "K56.7",
    "ISCHEMIC-COLITIS": "K55.9",
    "C-DIFF": "A04.7",
    "ESOPHAGITIS": "K20.9",
    "BARRETT-ESOPHAGUS": "K22.70",
    
    # Pulmonology
    "SOB": "R06.00",
    "DYSPNEA": "R06.00",
    "COUGH": "R05",
    "HEMOPTYSIS": "R04.2",
    "WHEEZING": "R06.2",
    "ASTHMA": "J45.909",
    "COPD": "J44.9",
    "PNEUMONIA": "J18.9",
    "CAP": "J18.9",
    "HAP": "J18.9",
    "ASPIRATION-PNEUMONIA": "J69.0",
    "BRONCHITIS": "J20.9",
    "ACUTE-BRONCHITIS": "J20.9",
    "CHRONIC-BRONCHITIS": "J42",
    "PLEURISY": "R09.1",
    "PLEURAL-EFFUSION": "J90",
    "EMPYEMA": "J86.9",
    "PTX": "J93.9",
    "PNEUMOTHORAX": "J93.9",
    "ARDS": "J80",
    "RESPIRATORY-FAILURE": "J96.90",
    "PULM-FIBROSIS": "J84.10",
    "SARCOIDOSIS": "D86.9",
    "SLEEP-APNEA": "G47.30",
    "OSA": "G47.33",
    
    # Endocrinology
    "DIABETES": "E11.9",
    "DM": "E11.9",
    "TYPE1-DM": "E10.9",
    "TYPE2-DM": "E11.9",
    "DKA": "E10.10",
    "HHS": "E11.01",
    "HYPOGLYCEMIA": "E16.2",
    "THYROID": "E07.9",
    "HYPOTHYROID": "E03.9",
    "HYPERTHYROID": "E05.90",
    "THYROIDITIS": "E06.9",
    "HASHIMOTOS": "E06.3",
    "GRAVES": "E05.00",
    "THYROID-NODULE": "E04.1",
    "GOITER": "E04.9",
    "ADRENAL": "E27.9",
    "ADDISONS": "E27.1",
    "CUSHINGS": "E24.9",
    "PHEOCHROMOCYTOMA": "D35.00",
    "HYPERALDOSTERONISM": "E26.9",
    "HYPERPARA": "E21.0",
    "HYPOPARA": "E20.9",
    "HYPERCALCEMIA": "E83.52",
    "HYPOCALCEMIA": "E83.51",
    "HYPERKALEMIA": "E87.5",
    "HYPOKALEMIA": "E87.6",
    "HYPONATREMIA": "E87.1",
    "HYPERNATREMIA": "E87.0",
    "METABOLIC-SYNDROME": "E88.81",
    "OBESITY": "E66.9",
    "MALNUTRITION": "E46",
    
    # Nephrology
    "AKI": "N17.9",
    "ACUTE-KIDNEY-INJURY": "N17.9",
    "CKD": "N18.9",
    "CHRONIC-KIDNEY-DISEASE": "N18.9",
    "ESRD": "N18.6",
    "GLOMERULONEPHRITIS": "N05.9",
    "NEPHROTIC-SYNDROME": "N04.9",
    "NEPHRITIC-SYNDROME": "N00.9",
    "PYELONEPHRITIS": "N12",
    "KIDNEY-STONE": "N20.0",
    "NEPHROLITHIASIS": "N20.0",
    "HYDRONEPHROSIS": "N13.30",
    "HEMATURIA": "R31.9",
    "PROTEINURIA": "R80.9",
    "UREMIA": "N19",
    
    # Infectious Disease
    "FEVER": "R50.9",
    "SEPSIS": "A41.9",
    "SEPTIC-SHOCK": "R65.21",
    "UTI": "N39.0",
    "CYSTITIS": "N30.90",
    "PROSTATITIS": "N41.9",
    "CELLULITIS": "L03.90",
    "ABSCESS": "L02.91",
    "OSTEOMYELITIS": "M86.9",
    "SEPTIC-ARTHRITIS": "M00.9",
    "ENDOCARDITIS": "I33.0",
    "INFLUENZA": "J11.1",
    "FLU": "J11.1",
    "COVID": "U07.1",
    "TUBERCULOSIS": "A16.9",
    "TB": "A16.9",
    "HIV": "B20",
    "AIDS": "B20",
    "HEPATITIS-A": "B15.9",
    "HEPATITIS-B": "B16.9",
    "HEPATITIS-C": "B17.10",
    "MONONUCLEOSIS": "B27.90",
    "EBV": "B27.90",
    "CMV": "B25.9",
    "HERPES-ZOSTER": "B02.9",
    "SHINGLES": "B02.9",
    "LYME": "A69.20",
    "MALARIA": "B54",
    
    # Hematology/Oncology
    "ANEMIA": "D64.9",
    "IRON-DEFICIENCY": "D50.9",
    "B12-DEFICIENCY": "D51.0",
    "FOLATE-DEFICIENCY": "D52.9",
    "HEMOLYTIC-ANEMIA": "D59.9",
    "APLASTIC-ANEMIA": "D61.9",
    "SICKLE-CELL": "D57.1",
    "THALASSEMIA": "D56.9",
    "BLEEDING": "R58",
    "THROMBOCYTOPENIA": "D69.6",
    "ITP": "D69.3",
    "TTP": "M31.1",
    "DIC": "D65",
    "HEMOPHILIA": "D66",
    "VWD": "D68.0",
    "LEUKEMIA": "C95.90",
    "ALL": "C91.00",
    "AML": "C92.00",
    "CLL": "C91.10",
    "CML": "C92.10",
    "LYMPHOMA": "C85.90",
    "HODGKINS": "C81.90",
    "NHL": "C85.90",
    "MULTIPLE-MYELOMA": "C90.00",
    "POLYCYTHEMIA": "D45",
    
    # Dermatology
    "RASH": "R21",
    "ECZEMA": "L30.9",
    "ATOPIC-DERMATITIS": "L20.9",
    "PSORIASIS": "L40.9",
    "CELLULITIS": "L03.90",
    "ABSCESS": "L02.91",
    "IMPETIGO": "L01.00",
    "FOLLICULITIS": "L73.9",
    "ACNE": "L70.0",
    "ROSACEA": "L71.9",
    "URTICARIA": "L50.9",
    "HIVES": "L50.9",
    "ANGIOEDEMA": "T78.3",
    "CONTACT-DERMATITIS": "L25.9",
    "SEBORRHEIC-DERMATITIS": "L21.9",
    "DERMATITIS": "L30.9",
    "TINEA": "B35.9",
    "RINGWORM": "B35.4",
    "CANDIDIASIS": "B37.9",
    "SCABIES": "B86",
    "HERPES-SIMPLEX": "B00.9",
    "SHINGLES": "B02.9",
    "WARTS": "B07.9",
    "SKIN-CANCER": "C44.90",
    "MELANOMA": "C43.9",
    "BASAL-CELL": "C44.91",
    "SQUAMOUS-CELL": "C44.92",
    
    # ENT
    "EAR-PAIN": "H92.00",
    "OTALGIA": "H92.00",
    "OTITIS-MEDIA": "H66.90",
    "OTITIS-EXTERNA": "H60.90",
    "SORE-THROAT": "R07.0",
    "PHARYNGITIS": "J02.9",
    "TONSILLITIS": "J03.90",
    "STREP-THROAT": "J02.0",
    "LARYNGITIS": "J04.0",
    "SINUSITIS": "J32.9",
    "RHINITIS": "J31.0",
    "ALLERGIC-RHINITIS": "J30.9",
    "EPISTAXIS": "R04.0",
    "NOSEBLEED": "R04.0",
    "HEARING-LOSS": "H91.90",
    "TINNITUS": "H93.1",
    "MENIERE": "H81.0",
    "VERTIGO": "R42",
    "BPPV": "H81.1",
    "VESTIBULAR-NEURITIS": "H81.2",
    "LABYRINTHITIS": "H83.0",
    
    # Orthopedics
    "BACK-PAIN": "M54.9",
    "LOW-BACK-PAIN": "M54.5",
    "NECK-PAIN": "M54.2",
    "JOINT-PAIN": "M25.50",
    "ARTHRALGIA": "M25.50",
    "OSTEOARTHRITIS": "M19.90",
    "RHEUMATOID-ARTHRITIS": "M06.9",
    "GOUT": "M10.9",
    "PSEUDOGOUT": "M11.9",
    "FRACTURE": "S82.90XA",
    "ANKLE-FRACTURE": "S82.899A",
    "HIP-FRACTURE": "S72.009A",
    "SPRAIN": "S93.40XA",
    "STRAIN": "S86.919A",
    "TENDONITIS": "M77.9",
    "BURSITIS": "M71.9",
    "ROTATOR-CUFF": "M75.10",
    "CARPAL-TUNNEL": "G56.00",
    "PLANTAR-FASCIITIS": "M72.2",
    "OSTEOPOROSIS": "M81.0",
    "SCOLIOSIS": "M41.9",
    "DISC-HERNIATION": "M51.9",
    "SPINAL-STENOSIS": "M48.00",
    
    # OB/GYN
    "PREGNANCY": "Z34.90",
    "ECTOPIC-PREGNANCY": "O00.9",
    "MISCARRIAGE": "O03.9",
    "PREECLAMPSIA": "O14.90",
    "ECLAMPSIA": "O15.9",
    "GESTATIONAL-DM": "O24.419",
    "LABOR": "O80",
    "POSTPARTUM-HEMORRHAGE": "O72.1",
    "MENSTRUAL-DISORDER": "N92.6",
    "DYSMENORRHEA": "N94.6",
    "AMENORRHEA": "N91.2",
    "MENORRHAGIA": "N92.0",
    "PMS": "N94.3",
    "PMDD": "N94.3",
    "PCOS": "E28.2",
    "ENDOMETRIOSIS": "N80.9",
    "FIBROIDS": "D25.9",
    "OVARIAN-CYST": "N83.20",
    "PID": "N73.9",
    "VAGINITIS": "N76.0",
    "CANDIDIASIS": "B37.3",
    "BV": "N76.0",
    "STI": "A64",
    "CHLAMYDIA": "A56.9",
    "GONORRHEA": "A54.9",
    "SYPHILIS": "A53.9",
    "HPV": "B97.7",
    "CERVICAL-CANCER": "C53.9",
    "OVARIAN-CANCER": "C56.9",
    "BREAST-CANCER": "C50.919",
    
    # Pediatrics
    "FEVER-INFANT": "R50.9",
    "CROUP": "J05.0",
    "BRONCHIOLITIS": "J21.9",
    "RSV": "J21.0",
    "KAWASAKI": "M30.3",
    "FAILURE-TO-THRIVE": "R62.51",
    
    # Psychiatry
    "DEPRESSION": "F32.9",
    "MDD": "F32.9",
    "BIPOLAR": "F31.9",
    "ANXIETY": "F41.9",
    "GAD": "F41.1",
    "PANIC-DISORDER": "F41.0",
    "PTSD": "F43.10",
    "OCD": "F42.9",
    "SCHIZOPHRENIA": "F20.9",
    "PSYCHOSIS": "F29",
    "MANIA": "F30.9",
    "ADHD": "F90.9",
    "AUTISM": "F84.0",
    "EATING-DISORDER": "F50.9",
    "ANOREXIA": "F50.00",
    "BULIMIA": "F50.2",
    "SUBSTANCE-ABUSE": "F19.10",
    "ALCOHOL-USE": "F10.10",
    "OPIOID-USE": "F11.10",
    "SUICIDAL-IDEATION": "R45.851",
    
    # Rheumatology
    "RA": "M06.9",
    "SLE": "M32.9",
    "LUPUS": "M32.9",
    "SJOGRENS": "M35.00",
    "SCLERODERMA": "M34.9",
    "POLYMYOSITIS": "M33.20",
    "DERMATOMYOSITIS": "M33.90",
    "VASCULITIS": "M31.9",
    "GIANT-CELL-ARTERITIS": "M31.6",
    "POLYMYALGIA-RHEUMATICA": "M35.3",
    "ANKYLOSING-SPONDYLITIS": "M45.9",
    "REACTIVE-ARTHRITIS": "M02.9",
    "FIBROMYALGIA": "M79.7",
    
    # Urology
    "URINARY-RETENTION": "R33.9",
    "INCONTINENCE": "N39.3",
    "BPH": "N40.0",
    "PROSTATE-CANCER": "C61",
    "BLADDER-CANCER": "C67.9",
    "KIDNEY-CANCER": "C64.9",
    "TESTICULAR-CANCER": "C62.90",
    "ERECTILE-DYSFUNCTION": "N52.9",
    "EPIDIDYMITIS": "N45.1",
    "ORCHITIS": "N45.2",
    "TESTICULAR-TORSION": "N44.00",
    "VARICOCELE": "I86.1",
    
    # Trauma
    "HEAD-INJURY": "S09.90XA",
    "TBI": "S06.9X0A",
    "CONCUSSION": "S06.0X0A",
    "CHEST-TRAUMA": "S29.9XXA",
    "ABD-TRAUMA": "S39.91XA",
    "TRAUMA": "T14.90XA",
    
    # Ophthalmology
    "CONJUNCTIVITIS": "H10.9",
    "PINK-EYE": "H10.9",
    "GLAUCOMA": "H40.9",
    "CATARACT": "H26.9",
    "MACULAR-DEGENERATION": "H35.30",
    "DIABETIC-RETINOPATHY": "E11.319",
    "RETINAL-DETACHMENT": "H33.0",
    "UVEITIS": "H20.9",
    "OPTIC-NEURITIS": "H46.9",
}


def extract_condition_from_tree_id(tree_id: str) -> str:
    """Extract the primary condition name from a tree ID like CARD-CHEST-PAIN"""
    parts = tree_id.split("-", 1)  # Split once to remove prefix
    if len(parts) > 1:
        return parts[1]  # Return everything after first dash
    return tree_id


def find_icd10_code(tree_id: str, tree_name: str) -> str:
    """Find the most appropriate ICD-10 code for a tree"""
    # Try exact match on tree_id suffix
    suffix = tree_id.split("-", 1)[1] if "-" in tree_id else tree_id
    if suffix in ICD10_MAPPING:
        return ICD10_MAPPING[suffix]
    
    # Try partial matches in tree name
    name_upper = tree_name.upper().replace(" ", "-")
    for key in ICD10_MAPPING:
        if key in suffix or key in name_upper:
            return ICD10_MAPPING[key]
    
    # Look for key terms in tree name
    for term, code in ICD10_MAPPING.items():
        term_words = term.split("-")
        if any(word in name_upper for word in term_words if len(word) > 3):
            return ICD10_MAPPING[term]
    
    return None


def add_icd10_to_tree_file(tree_path: Path):
    """Add ICD-10 code to a single tree file"""
    try:
        with tree_path.open("r", encoding="utf-8") as f:
            content = f.read()
            tree_data = yaml.safe_load(content)
        
        if not tree_data:
            print(f"  ⚠️  Skipping {tree_path.name}: Empty file")
            return False
        
        # Skip if already has ICD-10
        if tree_data.get("icd10"):
            print(f"  ✓ Skipping {tree_path.name}: Already has ICD-10")
            return False
        
        # Get tree ID and name
        tree_id = tree_data.get("tree_id") or tree_data.get("id") or tree_path.stem
        tree_name = tree_data.get("name") or tree_data.get("title") or ""
        
        # Find appropriate ICD-10 code
        icd10_code = find_icd10_code(tree_id, tree_name)
        
        if not icd10_code:
            print(f"  ⚠️  No ICD-10 match for {tree_path.name} ({tree_name})")
            return False
        
        # Insert ICD-10 after version line
        lines = content.split("\n")
        new_lines = []
        inserted = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            # Insert after version line, before nodes
            if not inserted and line.startswith("version:") and i + 1 < len(lines):
                new_lines.append(f"icd10: {icd10_code}")
                inserted = True
        
        if inserted:
            # Write back to file
            with tree_path.open("w", encoding="utf-8") as f:
                f.write("\n".join(new_lines))
            print(f"  ✅ Added {icd10_code} to {tree_path.name}")
            return True
        else:
            print(f"  ⚠️  Could not insert ICD-10 for {tree_path.name}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error processing {tree_path.name}: {e}")
        return False


def main():
    trees_dir = Path(__file__).parent.parent / "backend" / "trees"
    
    if not trees_dir.exists():
        print(f"❌ Trees directory not found: {trees_dir}")
        return
    
    print(f"📁 Processing tree files in {trees_dir}\n")
    
    tree_files = list(trees_dir.glob("*.yml"))
    total = len(tree_files)
    updated = 0
    skipped = 0
    errors = 0
    
    for tree_file in sorted(tree_files):
        result = add_icd10_to_tree_file(tree_file)
        if result:
            updated += 1
        elif result is False:
            skipped += 1
        else:
            errors += 1
    
    print(f"\n📊 Summary:")
    print(f"  Total files: {total}")
    print(f"  ✅ Updated: {updated}")
    print(f"  ⏭️  Skipped: {skipped}")
    print(f"  ❌ Errors: {errors}")


if __name__ == "__main__":
    main()
