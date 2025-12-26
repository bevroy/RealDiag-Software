#!/usr/bin/env python3
"""
Script to add missing SNOMED codes to diagnostic trees based on ICD-10 codes.
"""
import yaml
import os
import sys

# Comprehensive ICD-10 to SNOMED mapping
ICD10_TO_SNOMED = {
    # Cardiology
    'I24.9': '394659003', 'R07.9': '29857009', 'I10': '38341003',
    'I21.3': '401303003', 'I21.9': '57054005', 'I49.9': '698247007',
    'I73.9': '399957001', 'I30.9': '3238004', 'I35.1': '60234000',
    'I48.91': '49436004', 'I48.92': '5370000', 'I44.0': '27885002',
    'I44.1': '28189009', 'I44.2': '27885002', 'I50.9': '84114007',
    'I42.9': '85898001', 'I05.0': '79619009', 'I34.0': '48724000',
    'I34.1': '79619009', 'I47.1': '6456007', 'I47.2': '25569003',
    'I49.01': '17366009',
    # Dermatology  
    'L70.0': '88616000', 'C44.91': '254701007', 'L23.9': '40275004',
    'L20.9': '24079001', 'L30.1': '238865004', 'L30.9': '43116000',
    'L52': '238838007', 'L73.2': '201101007', 'L60.0': '74430001',
    'L91.0': '40791000', 'B35.1': '414941008', 'L43.9': '4307007',
    'L42': '200791005', 'R21': '271807003', 'B86': '128869009',
    # Gastroenterology
    'R10.9': '21522001', 'K22.0': '80774007', 'K81.0': '65275009',
    'K22.70': '196611002', 'K90.0': '396331005', 'K83.0': '82403002',
    'C18.9': '363406005', 'R19.7': '62315008', 'I85.9': '14457001',
    'A09': '25374005', 'K64.9': '90458008', 'K75.9': '40468003',
    'K50.90': '34000006', 'K58.9': '10743008', 'E73.9': '267425008',
    # Hematology
    'D64.9': '271737000', 'D61.9': '306058006', 'D69.3': '32273002',
    'D50.9': '87522002', 'D57.1': '417357006', 'D69.6': '415116008',
    # Infectious Disease
    'R50.9': '386661006', 'B00.1': '10629181000119109', 'B37.0': '78048006',
    'G06.0': '44403003', 'B16.9': '66071002', 'B17.10': '50711007',
    'J11.1': '6142004', 'B50.9': '61462000', 'A15.0': '56717001',
    # Nephrology/Urology
    'N18.9': '709044004', 'N05.9': '36171008', 'M31.0': '50581000',
    'N04.9': '52254009', 'N40.0': '266569009', 'N30.10': '197834003',
    'C67.9': '399068003', 'N32.81': '442972004', 'N52.9': '397803000',
    'N20.0': '95570007', 'C61': '399068003',
    # Neurology
    'G81.9': '26544005', 'R40.20': '419284004', 'G30.9': '26929004',
    'F03.90': '52448006', 'G43.909': '37796009', 'G72.9': '129565002',
    'G40.909': '313307000', 'R56.9': '91175000',
    # OB/GYN
    'O24.419': '11687002', 'O14.90': '398254007', 'O60.10X0': '64550006',
    'D25.9': '95315005', 'N80.9': '129103003', 'N95.1': '161712005',
    'E28.2': '69878068', 'O26.9': '609496007', 'N93.9': '289530006',
    # Ophthalmology
    'H53.2': '699739006', 'H40.9': '23986001', 'H35.30': '422338006',
    'H01.009': '47180009', 'H00.19': '1482004', 'H00.019': '1489008',
    # Orthopedics
    'S83.511A': '444121005', 'M54.5': '279039007', 'M79.9': '22253000',
    'M77.10': '202855006', 'M48.06': '76107001', 'S83.209A': '239720000',
    'M17.9': '239873007', 'M75.10': '428971000124102', 'M65.30': '367566005',
    'M05.9': '69896004',
    # ENT
    'H92.09': '16001004', 'H91.90': '15188001', 'J32.9': '36971009',
    'J02.9': '162397003', 'R42': '399153001',
    # Pulmonology
    'J21.9': '4120002', 'J47.9': '12295008', 'J20.9': '10509002',
    'J42': '63480004', 'R05': '49727002', 'R06.00': '267036007',
    # Rheumatology
    'M45.9': '9631008', 'M35.2': '31996006', 'M10.9': '90560007',
    'M35.3': '55819004', 'M33.20': '203061004', 'L40.50': '33339009',
    'I73.00': '266261006', 'M02.9': '129133007', 'M31.6': '400130008',
    # Surgery/Emergency
    'K35.80': '74400008', 'T30.0': '125666000', 'T78.2': '39579001',
    'S06.9X0A': '82271004',
    # Dentistry
    'K04.7': '300488002', 'M26.60': '298231005', 'S03.2XXA': '35029008',
    # General Medicine
    'E66.9': '414916001', 'R60.9': '267038008', 'R53.83': '84229001',
    # Oncology
    'N63.0': '274153004',
}

def add_snomed_to_file(filepath):
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
    snomed_code = ICD10_TO_SNOMED.get(icd10_code)
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
    """Main function to process all files."""
    updated = []
    skipped = []
    no_mapping = []
    
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
            if icd10_code not in ICD10_TO_SNOMED:
                no_mapping.append(f"{filename} (ICD: {icd10_code})")
                continue
            
            if add_snomed_to_file(filepath):
                updated.append(f"{filename} -> {ICD10_TO_SNOMED[icd10_code]}")
            else:
                skipped.append(filename)
                
        except Exception as e:
            print(f"Error processing {filename}: {e}", file=sys.stderr)
    
    print(f"\n{'='*80}")
    print(f"SNOMED CODE UPDATE SUMMARY")
    print(f"{'='*80}\n")
    print(f"✅ Successfully updated: {len(updated)} files")
    if updated:
        for f in updated[:20]:
            print(f"   {f}")
        if len(updated) > 20:
            print(f"   ... and {len(updated) - 20} more")
    
    print(f"\n⚠️  No mapping available: {len(no_mapping)} files")
    if no_mapping:
        for f in no_mapping[:10]:
            print(f"   {f}")
        if len(no_mapping) > 10:
            print(f"   ... and {len(no_mapping) - 10} more")
    
    print(f"\n⏭️  Skipped (already processed): {len(skipped)} files")
    print(f"\n{'='*80}")

if __name__ == '__main__':
    main()
