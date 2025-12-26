#!/usr/bin/env python3
"""
Script to add remaining missing SNOMED codes with expanded mapping.
"""
import yaml
import os
import sys

# Expanded ICD-10 to SNOMED mapping for remaining files
ADDITIONAL_MAPPINGS = {
    # Cardiology expanded
    'I42.8': '85898001',      # Arrhythmogenic RV cardiomyopathy
    'I47.9': '195080001',     # Brugada syndrome
    'I31.4': '35304003',      # Cardiac tamponade
    'R57.0': '27942005',      # Cardiogenic shock
    'N17.9': '14669001',      # Cardiorenal syndrome (AKI)
    'I31.1': '51615001',      # Constrictive pericarditis
    'I25.10': '53741008',     # Coronary artery disease
    'I42.0': '399020009',     # Dilated cardiomyopathy
    'I71.4': '233985008',     # Abdominal aortic aneurysm
    'I05.9': '79619009',      # Mitral valve disease
    'I42.1': '426263006',     # Hypertrophic cardiomyopathy
    'I71.00': '233970002',    # Thoracic aortic aneurysm/dissection
    'I51.4': '409622000',     # Myocarditis
    'I27.81': '70995007',     # Pulmonary hypertension
    'I42.5': '44088000',      # Restrictive cardiomyopathy
    'I21.4': '307598008',     # STEMI inferior
    'I35.0': '60573004',      # Aortic stenosis
    'I49.5': '11092001',      # Sick sinus syndrome
    'I45.9': '698252002',     # Conduction disorder
    'I01.9': '58718002',      # Acute rheumatic fever
    'R00.2': '80313002',      # Palpitations
    'I20.9': '194828000',     # Angina pectoris
    
    # Dermatology expanded
    'L98.9': '95320005',      # Skin disorder
    'C43.9': '372244006',     # Melanoma
    'L02.91': '128045006',    # Skin abscess
    'L89.90': '399912005',    # Pressure ulcer
    'L98.4': '47596007',      # Chronic ulcer of skin
    
    # Emergency/Trauma
    'T14.90XA': '417746004',  # Injury unspecified
    'S09.90XA': '82271004',   # Head injury
    'T75.1XXA': '242396005',  # Drowning/submersion
    
    # ENT
    'H81.09': '399153001',    # Vertigo
    'R05.9': '49727002',      # Cough
    
    # GI expanded
    'K21.9': '235595009',     # GERD
    'K92.2': '74474003',      # GI bleeding
    'K29.70': '235595009',    # Gastritis
    'K80.20': '235919008',    # Cholelithiasis
    'K56.60': '81060008',     # Bowel obstruction
    
    # Hematology expanded
    'D68.9': '64779008',      # Coagulation defect
    'D61.818': '58800005',    # Pancytopenia
    
    # Infectious Disease expanded
    'A41.9': '91302008',      # Sepsis
    'B34.9': '34014006',      # Viral infection
    
    # Nephrology/Urology expanded
    'N17.9': '14669001',      # Acute kidney injury
    'N39.0': '68566005',      # UTI
    'C64.9': '126926005',     # Kidney cancer
    
    # Neurology expanded
    'G35': '24700007',        # Multiple sclerosis
    'G20': '49049000',        # Parkinson's disease
    'G47.00': '73430006',     # Insomnia
    
    # OB/GYN expanded
    'Z34.90': '77386006',     # Normal pregnancy
    'O80': '199612007',       # Labor and delivery
    
    # Oncology
    'C91.00': '91861009',     # Leukemia (acute lymphoblastic)
    
    # Ophthalmology expanded
    'H52.13': '38101003',     # Myopia
    'H16.9': '9826008',       # Keratitis
    
    # Orthopedics expanded
    'M19.90': '396275006',    # Osteoarthritis
    'M81.0': '64859006',      # Osteoporosis
    'M80.00XA': '443165006',  # Osteoporotic fracture
    'S82.109A': '16114001',   # Tibia fracture
    'S52.509A': '16114001',   # Radius fracture
    
    # Pulmonology expanded
    'J18.9': '233604007',     # Pneumonia
    'J44.9': '13645005',      # COPD
    'J96.00': '409622000',    # Respiratory failure
    'J81.0': '19242006',      # Pulmonary edema
    
    # Rheumatology expanded
    'M79.3': '24693007',      # Panniculitis
    'M13.9': '3723001',       # Arthritis unspecified
    'M06.9': '69896004',      # Rheumatoid arthritis
    
    # Surgery
    'K43.9': '52731004',      # Ventral hernia
}

def add_snomed_to_file(filepath, mappings):
    """Add SNOMED code to a file if missing."""
    with open(filepath, 'r') as f:
        content = f.read()
        data = yaml.safe_load(content)
    
    # Check if SNOMED is missing
    snomed = data.get('snomed')
    if snomed and snomed != '' and not (isinstance(snomed, list) and len(snomed) == 0):
        return False  # Already has SNOMED
    
    # Get ICD-10 code
    icd10 = data.get('icd10')
    if not icd10:
        return False  # No ICD-10 to map from
    
    # Handle list or single ICD-10
    icd10_code = icd10[0] if isinstance(icd10, list) else icd10
    
    # Look up SNOMED
    snomed_code = mappings.get(icd10_code)
    if not snomed_code:
        return False  # No mapping available
    
    # Find where to insert SNOMED in the file
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('icd10:'):
            # Find end of icd10 block
            j = i + 1
            while j < len(lines) and (lines[j].startswith('- ') or lines[j].startswith(' ')):
                j += 1
            # Check if snomed line already exists
            if j < len(lines) and lines[j].startswith('snomed:'):
                # Replace empty snomed
                if 'snomed: []' in lines[j] or lines[j] == 'snomed:':
                    lines[j] = f'snomed: {snomed_code}'
                else:
                    return False
            else:
                # Insert snomed after icd10
                lines.insert(j, f'snomed: {snomed_code}')
            
            # Write back
            with open(filepath, 'w') as f:
                f.write('\n'.join(lines))
            return True
    
    return False

def main():
    """Main function to process remaining files."""
    updated = []
    still_missing = []
    
    for filename in sorted(os.listdir('.')):
        if not filename.endswith('.yml'):
            continue
        
        filepath = os.path.join('.', filename)
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            # Check if needs SNOMED
            snomed = data.get('snomed')
            if snomed and snomed != '' and not (isinstance(snomed, list) and len(snomed) == 0):
                continue  # Has SNOMED
            
            icd10 = data.get('icd10')
            if not icd10:
                continue  # No ICD-10
            
            icd10_code = icd10[0] if isinstance(icd10, list) else icd10
            
            if icd10_code in ADDITIONAL_MAPPINGS:
                if add_snomed_to_file(filepath, ADDITIONAL_MAPPINGS):
                    updated.append(f"{filename} -> {ADDITIONAL_MAPPINGS[icd10_code]}")
            else:
                still_missing.append(f"{filename} (ICD: {icd10_code})")
                
        except Exception as e:
            print(f"Error processing {filename}: {e}", file=sys.stderr)
    
    print(f"\n{'='*80}")
    print(f"ADDITIONAL SNOMED CODE UPDATE")
    print(f"{'='*80}\n")
    print(f"✅ Successfully updated: {len(updated)} files")
    for f in updated:
        print(f"   {f}")
    
    print(f"\n⚠️  Still missing mapping: {len(still_missing)} files")
    for f in still_missing:
        print(f"   {f}")
    
    print(f"\n{'='*80}")

if __name__ == '__main__':
    main()
