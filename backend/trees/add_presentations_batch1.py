#!/usr/bin/env python3
"""
Add clinical presentations to all diagnostic trees missing them.
Batch 1: Cardiology, Allergy, Dentistry
"""
import yaml
import re
import os

# Clinical presentations by condition
PRESENTATIONS = {
    # Allergy
    'ALLERGY-DRUG-ALLERGY': [
        'Cutaneous reactions: maculopapular rash, urticaria, angioedema (most common)',
        'Systemic reactions: fever, lymphadenopathy, arthralgias',
        'Anaphylaxis: acute onset dyspnea, hypotension, throat swelling',
        'Delayed reactions: serum sickness-like syndrome (7-14 days after exposure)',
        'Organ-specific: hepatitis, nephritis, pneumonitis',
    ],
    
    # Cardiology
    'CARD-ACUTE-CORONARY-SYNDROME': [
        'Chest pain: substernal, pressure-like, radiating to left arm/jaw/back',
        'Associated symptoms: dyspnea, diaphoresis, nausea, lightheadedness',
        'Pain lasting >20 minutes, not fully relieved by rest or nitroglycerin',
        'May present atypically in elderly, diabetics, women (epigastric pain, fatigue)',
        'Cardiogenic shock: hypotension, cool extremities, altered mental status',
    ],
    'CARD-CHEST-PAIN': [
        'Location: substernal, left-sided, or right-sided chest discomfort',
        'Quality: sharp, dull, pressure, burning, or stabbing',
        'Radiation: to arms, jaw, back, or abdomen',
        'Associated symptoms: dyspnea, palpitations, diaphoresis, nausea',
        'Timing: acute onset, chronic/recurrent, positional, or exertional',
        'Red flags: severe pain, hemodynamic instability, syncope',
    ],
    'CARD-HYPERTENSION': [
        'Often asymptomatic (discovered on routine screening)',
        'Headache (typically occipital, worse in morning)',
        'Dizziness, lightheadedness, or vertigo',
        'Visual changes or blurred vision',
        'Epistaxis (nosebleeds)',
        'Hypertensive emergency: severe BP elevation with end-organ damage (chest pain, dyspnea, altered mental status, acute kidney injury)',
    ],
    'CARD-MYOCARDIAL-INFARCTION-STEMI': [
        'Severe substernal chest pain: crushing, pressure-like, >20 minutes duration',
        'Radiation to left arm, jaw, neck, or back',
        'Diaphoresis, nausea, vomiting, dyspnea',
        'Sense of impending doom, anxiety',
        'May have syncope, palpitations, or cardiogenic shock',
        'Atypical in elderly/diabetics: epigastric pain, dyspnea without chest pain',
    ],
    'CARD-MYOCARDIAL-INFARCTION': [
        'Substernal chest pain or pressure lasting >20 minutes',
        'Pain radiating to left arm, jaw, neck, back, or epigastrium',
        'Associated dyspnea, diaphoresis, nausea, vomiting',
        'Lightheadedness, palpitations, or syncope',
        'May be asymptomatic (silent MI in elderly or diabetics)',
        'Cardiogenic shock: hypotension, cool/clammy skin, altered mental status',
    ],
    'CARD-PALPITATIONS': [
        'Sensation of rapid, irregular, or forceful heartbeat',
        'Fluttering or pounding sensation in chest or neck',
        'May be paroxysmal (sudden onset/offset) or sustained',
        'Associated lightheadedness, dyspnea, or chest discomfort',
        'Syncope or near-syncope with palpitations (concerning)',
        'Triggers: caffeine, alcohol, stress, exercise, or medications',
    ],
    'CARD-PERIPHERAL-ARTERY-DISEASE': [
        'Intermittent claudication: leg pain with walking, relieved by rest',
        'Pain typically in calf, thigh, or buttock (depends on lesion location)',
        'Cool, pale extremities with diminished pulses',
        'Hair loss, shiny skin, brittle nails on affected limb',
        'Chronic wounds or ulcers (especially on toes/heels)',
        'Critical limb ischemia: rest pain, non-healing wounds, gangrene',
    ],
    'CARDS-ACUTE-PERICARDITIS': [
        'Sharp, pleuritic chest pain worse with inspiration and lying flat',
        'Pain improved by sitting up and leaning forward',
        'Pain may radiate to trapezius ridge (highly specific)',
        'Fever, malaise, myalgias',
        'Pericardial friction rub (pathognomonic but not always present)',
        'Dyspnea if associated pericardial effusion',
    ],
    'CARDS-AORTIC-REGURGITATION': [
        'Often asymptomatic for years (chronic AR)',
        'Exertional dyspnea and fatigue (early symptoms)',
        'Orthopnea, paroxysmal nocturnal dyspnea (heart failure)',
        'Palpitations (awareness of forceful heartbeat)',
        'Chest pain (atypical angina from reduced coronary perfusion)',
        'Acute AR: sudden dyspnea, pulmonary edema, cardiogenic shock',
        'Wide pulse pressure, bounding pulses, head bobbing with pulse',
    ],
}

def add_presentations(filename, presentations):
    """Add presentations to a YAML file."""
    with open(filename, 'r') as f:
        content = f.read()
    
    # Check if already has presentations
    if re.search(r'^presentations?:', content, re.MULTILINE):
        return False
    
    # Find where to insert (after snomed or icd10)
    lines = content.split('\n')
    insert_pos = -1
    
    for i, line in enumerate(lines):
        if line.startswith('snomed:'):
            insert_pos = i + 1
            break
        elif line.startswith('icd10:') and insert_pos == -1:
            # Skip to end of icd10 list if it's a list
            j = i + 1
            while j < len(lines) and (lines[j].startswith('  -') or lines[j].startswith('- ')):
                j += 1
            insert_pos = j
    
    if insert_pos == -1:
        return False
    
    # Build presentations section
    pres_lines = ['presentations:']
    for p in presentations:
        pres_lines.append(f'  - {p}')
    
    # Insert
    lines = lines[:insert_pos] + pres_lines + lines[insert_pos:]
    
    with open(filename, 'w') as f:
        f.write('\n'.join(lines))
    
    return True

# Process files
updated = []
skipped = []

for filename, presentations in PRESENTATIONS.items():
    filepath = f"{filename}.yml"
    if os.path.exists(filepath):
        if add_presentations(filepath, presentations):
            updated.append(filename)
        else:
            skipped.append(filename)

print(f"✅ Updated: {len(updated)} files")
for f in updated:
    print(f"   {f}")

if skipped:
    print(f"\n⏭️ Skipped: {len(skipped)} files")
    for f in skipped:
        print(f"   {f}")
EOF
