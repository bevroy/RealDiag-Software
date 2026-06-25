#!/usr/bin/env python3
"""
Final batch of SNOMED mappings for remaining files.
"""
import yaml
import os

FINAL_MAPPINGS = {
    # Cardiology - specific subtypes
    'I50.33': '418304008',    # Heart failure diastolic
    'I50.23': '441530006',    # Heart failure systolic
    'I45.81': '111975006',    # Long QT syndrome
    'I40.9': '50920009',      # Myocarditis
    'I49.1': '251198005',     # Premature atrial contractions (PACs)
    'I20.1': '371806007',     # Prinzmetal angina
    'I49.3': '164884008',     # Premature ventricular contractions (PVCs)
    'I51.81': '71772001',     # Takotsubo cardiomyopathy
    'I07.1': '111287006',     # Tricuspid regurgitation
    'I20.0': '25106000',      # Unstable angina
    'I45.6': '74390002',      # WPW syndrome
    
    # Dermatology - specific subtypes
    'L25.9': '40275004',      # Contact dermatitis (irritant)
    'L21.9': '86708008',      # Seborrheic dermatitis
    'C44.90': '372130007',    # Skin infection/cancer
    'L50.8': '402408005',     # Chronic urticaria
    'L85.3': '16386004',      # Xerosis
    
    # ENT - specific codes
    'H92.00': '16001004',     # Ear pain (otalgia)
    'J01.90': '36971009',     # Acute sinusitis
    'R07.0': '162397003',     # Sore throat (throat pain)
    
    # GI - specific subtypes
    'K52.9': '25374005',      # Acute gastroenteritis
    'K51.90': '64766004',     # IBD (ulcerative colitis)
    'K27.9': '13200003',      # Peptic ulcer disease
    'K74.3': '31712002',      # Primary biliary cholangitis
    
    # Infectious Disease - chronic hepatitis
    'B18.1': '76795007',      # Chronic hepatitis B
    'B18.2': '50711007',      # Chronic hepatitis C
    'B54': '248427009',       # Malaria unspecified
    
    # Neurology
    'M62.81': '26544005',     # Muscle weakness
    'R40.4': '419284004',     # Altered mental status (transient)
    
    # OB/GYN
    'O60.00': '79586000',     # Preterm labor
    'R58': '289530006',       # Vaginal bleeding
    
    # Oncology
    'C25.9': '363418001',     # Pancreatic cancer
    
    # Ophthalmology
    'A64': '246636008',       # Diplopia
    'H40.11': '392288008',    # Primary open-angle glaucoma
    
    # Orthopedics
    'M54.9': '161891005',     # Back pain unspecified
    'S82.90XA': '16114001',   # Fracture unspecified
    'M25.50': '57676002',     # Joint pain
    
    # Pulmonology
    'J44.0': '63480004',      # Chronic bronchitis with COPD
    
    # Rheumatology
    'M1A.9': '90560007',      # Chronic gout
    
    # Urology
    'N40.1': '253875009',     # BPH with lower urinary tract symptoms
}

def add_snomed_to_file(filepath, mappings):
    """Add SNOMED code to a file if missing."""
    with open(filepath, 'r') as f:
        content = f.read()
        data = yaml.safe_load(content)
    
    # Check if SNOMED is missing
    snomed = data.get('snomed')
    if snomed and snomed != '' and not (isinstance(snomed, list) and len(snomed) == 0):
        return False
    
    # Get ICD-10 code
    icd10 = data.get('icd10')
    if not icd10:
        return False
    
    icd10_code = icd10[0] if isinstance(icd10, list) else icd10
    
    # Look up SNOMED
    snomed_code = mappings.get(icd10_code)
    if not snomed_code:
        return False
    
    # Find where to insert SNOMED
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('icd10:'):
            j = i + 1
            while j < len(lines) and (lines[j].startswith('- ') or lines[j].startswith(' ')):
                j += 1
            if j < len(lines) and lines[j].startswith('snomed:'):
                if 'snomed: []' in lines[j] or lines[j] == 'snomed:':
                    lines[j] = f'snomed: {snomed_code}'
                else:
                    return False
            else:
                lines.insert(j, f'snomed: {snomed_code}')
            
            with open(filepath, 'w') as f:
                f.write('\n'.join(lines))
            return True
    
    return False

def main():
    updated = []
    still_missing = []
    
    for filename in sorted(os.listdir('.')):
        if not filename.endswith('.yml'):
            continue
        
        filepath = os.path.join('.', filename)
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            snomed = data.get('snomed')
            if snomed and snomed != '' and not (isinstance(snomed, list) and len(snomed) == 0):
                continue
            
            icd10 = data.get('icd10')
            if not icd10:
                continue
            
            icd10_code = icd10[0] if isinstance(icd10, list) else icd10
            
            if icd10_code in FINAL_MAPPINGS:
                if add_snomed_to_file(filepath, FINAL_MAPPINGS):
                    updated.append(f"{filename} -> {FINAL_MAPPINGS[icd10_code]}")
            else:
                still_missing.append(f"{filename} (ICD: {icd10_code})")
                
        except Exception as e:
            print(f"Error: {filename}: {e}")
    
    print(f"\n{'='*80}")
    print(f"FINAL SNOMED CODE UPDATE")
    print(f"{'='*80}\n")
    print(f"✅ Successfully updated: {len(updated)} files")
    for f in updated:
        print(f"   {f}")
    
    if still_missing:
        print(f"\n⚠️  Still missing: {len(still_missing)} files")
        for f in still_missing:
            print(f"   {f}")
    else:
        print(f"\n🎉 ALL FILES NOW HAVE SNOMED CODES!")
    
    print(f"\n{'='*80}")

if __name__ == '__main__':
    main()
