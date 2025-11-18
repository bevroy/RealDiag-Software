/**
 * Drug Interactions Checker
 * Cross-references medications with management recommendations
 */

// Drug interaction database
const drugInteractions = {
  // Anticoagulants
  'warfarin': {
    interactions: [
      { drug: 'aspirin', severity: 'major', effect: 'Increased bleeding risk', alternative: 'Consider clopidogrel or reduce aspirin dose' },
      { drug: 'nsaids', severity: 'major', effect: 'Increased bleeding risk', alternative: 'Use acetaminophen for pain' },
      { drug: 'antibiotics', severity: 'moderate', effect: 'INR fluctuation', alternative: 'Monitor INR closely, adjust dose' },
      { drug: 'amiodarone', severity: 'major', effect: 'Increased warfarin effect', alternative: 'Reduce warfarin dose by 30-50%' },
      { drug: 'clarithromycin', severity: 'major', effect: 'Increased bleeding risk', alternative: 'Use azithromycin instead' },
      { drug: 'fluconazole', severity: 'major', effect: 'Increased INR', alternative: 'Use alternative antifungal or reduce warfarin dose' }
    ],
    monitoring: 'Check INR frequently when starting/stopping interacting medications'
  },
  'apixaban': {
    interactions: [
      { drug: 'aspirin', severity: 'moderate', effect: 'Increased bleeding risk', alternative: 'Use lowest effective aspirin dose' },
      { drug: 'nsaids', severity: 'moderate', effect: 'Increased bleeding risk', alternative: 'Use acetaminophen' },
      { drug: 'ketoconazole', severity: 'major', effect: 'Increased apixaban levels', alternative: 'Reduce apixaban dose by 50%' },
      { drug: 'rifampin', severity: 'major', effect: 'Decreased apixaban efficacy', alternative: 'Avoid combination or use alternative anticoagulant' }
    ],
    monitoring: 'Monitor for signs of bleeding'
  },
  'rivaroxaban': {
    interactions: [
      { drug: 'aspirin', severity: 'moderate', effect: 'Increased bleeding risk', alternative: 'Use lowest effective aspirin dose' },
      { drug: 'nsaids', severity: 'moderate', effect: 'Increased bleeding risk', alternative: 'Use acetaminophen' },
      { drug: 'ketoconazole', severity: 'major', effect: 'Increased rivaroxaban levels', alternative: 'Avoid combination' },
      { drug: 'carbamazepine', severity: 'major', effect: 'Decreased rivaroxaban efficacy', alternative: 'Avoid combination' }
    ],
    monitoring: 'Monitor for bleeding and thromboembolic events'
  },

  // Antiplatelets
  'aspirin': {
    interactions: [
      { drug: 'warfarin', severity: 'major', effect: 'Increased bleeding risk', alternative: 'Consider alternative antiplatelet' },
      { drug: 'nsaids', severity: 'moderate', effect: 'Increased GI bleeding', alternative: 'Use acetaminophen or add PPI' },
      { drug: 'ssri', severity: 'moderate', effect: 'Increased bleeding risk', alternative: 'Monitor closely, consider PPI' },
      { drug: 'corticosteroids', severity: 'moderate', effect: 'Increased GI bleeding', alternative: 'Add PPI prophylaxis' }
    ],
    monitoring: 'Monitor for signs of bleeding, especially GI'
  },
  'clopidogrel': {
    interactions: [
      { drug: 'omeprazole', severity: 'moderate', effect: 'Decreased clopidogrel efficacy', alternative: 'Use pantoprazole instead' },
      { drug: 'esomeprazole', severity: 'moderate', effect: 'Decreased clopidogrel efficacy', alternative: 'Use pantoprazole or ranitidine' },
      { drug: 'aspirin', severity: 'moderate', effect: 'Increased bleeding risk', alternative: 'Benefits often outweigh risks in dual therapy' },
      { drug: 'nsaids', severity: 'moderate', effect: 'Increased bleeding risk', alternative: 'Use acetaminophen' }
    ],
    monitoring: 'Monitor for cardiovascular events and bleeding'
  },

  // Antibiotics
  'azithromycin': {
    interactions: [
      { drug: 'amiodarone', severity: 'major', effect: 'QT prolongation', alternative: 'Use doxycycline or avoid if possible' },
      { drug: 'antipsychotics', severity: 'major', effect: 'QT prolongation', alternative: 'Use alternative antibiotic' },
      { drug: 'warfarin', severity: 'moderate', effect: 'Increased INR', alternative: 'Monitor INR closely' }
    ],
    monitoring: 'ECG if risk factors for QT prolongation'
  },
  'ciprofloxacin': {
    interactions: [
      { drug: 'antacids', severity: 'moderate', effect: 'Decreased absorption', alternative: 'Separate administration by 2-6 hours' },
      { drug: 'warfarin', severity: 'major', effect: 'Increased INR', alternative: 'Monitor INR closely or use alternative' },
      { drug: 'nsaids', severity: 'moderate', effect: 'Increased seizure risk', alternative: 'Avoid combination in elderly' },
      { drug: 'theophylline', severity: 'major', effect: 'Theophylline toxicity', alternative: 'Monitor levels, reduce dose' }
    ],
    monitoring: 'Monitor for CNS effects and tendon problems'
  },

  // Cardiovascular
  'amlodipine': {
    interactions: [
      { drug: 'simvastatin', severity: 'moderate', effect: 'Increased statin levels', alternative: 'Limit simvastatin to 20mg or use alternative statin' },
      { drug: 'grapefruit juice', severity: 'moderate', effect: 'Increased amlodipine levels', alternative: 'Avoid grapefruit products' },
      { drug: 'diltiazem', severity: 'moderate', effect: 'Additive hypotension', alternative: 'Monitor BP closely' }
    ],
    monitoring: 'Monitor blood pressure and heart rate'
  },
  'metoprolol': {
    interactions: [
      { drug: 'diltiazem', severity: 'major', effect: 'Bradycardia, heart block', alternative: 'Avoid combination or monitor closely' },
      { drug: 'verapamil', severity: 'major', effect: 'Bradycardia, hypotension', alternative: 'Avoid combination' },
      { drug: 'insulin', severity: 'moderate', effect: 'Masks hypoglycemia symptoms', alternative: 'Monitor glucose closely' },
      { drug: 'clonidine', severity: 'moderate', effect: 'Rebound hypertension', alternative: 'Taper both medications together' }
    ],
    monitoring: 'Monitor heart rate and blood pressure'
  },

  // Statins
  'simvastatin': {
    interactions: [
      { drug: 'amlodipine', severity: 'moderate', effect: 'Increased rhabdomyolysis risk', alternative: 'Limit to 20mg simvastatin or switch statin' },
      { drug: 'clarithromycin', severity: 'major', effect: 'Severe rhabdomyolysis risk', alternative: 'Hold statin during antibiotic course' },
      { drug: 'gemfibrozil', severity: 'major', effect: 'Severe rhabdomyolysis risk', alternative: 'Use fenofibrate or alternative statin' },
      { drug: 'grapefruit juice', severity: 'major', effect: 'Increased statin levels', alternative: 'Avoid grapefruit or switch to pravastatin' }
    ],
    monitoring: 'Monitor for muscle pain, weakness, CK levels'
  },
  'atorvastatin': {
    interactions: [
      { drug: 'clarithromycin', severity: 'moderate', effect: 'Increased rhabdomyolysis risk', alternative: 'Use azithromycin or hold statin' },
      { drug: 'gemfibrozil', severity: 'major', effect: 'Increased rhabdomyolysis risk', alternative: 'Use fenofibrate instead' },
      { drug: 'grapefruit juice', severity: 'moderate', effect: 'Increased statin levels', alternative: 'Limit grapefruit consumption' }
    ],
    monitoring: 'Monitor for muscle symptoms and liver function'
  },

  // Diabetes medications
  'metformin': {
    interactions: [
      { drug: 'contrast dye', severity: 'major', effect: 'Lactic acidosis risk', alternative: 'Hold 48h before and after contrast' },
      { drug: 'alcohol', severity: 'moderate', effect: 'Increased lactic acidosis risk', alternative: 'Limit alcohol consumption' },
      { drug: 'topiramate', severity: 'moderate', effect: 'Increased metformin levels', alternative: 'Monitor for lactic acidosis' }
    ],
    monitoring: 'Monitor renal function, hold if eGFR <30'
  },

  // PPIs
  'omeprazole': {
    interactions: [
      { drug: 'clopidogrel', severity: 'moderate', effect: 'Decreased antiplatelet effect', alternative: 'Use pantoprazole or H2 blocker' },
      { drug: 'warfarin', severity: 'moderate', effect: 'Increased INR', alternative: 'Monitor INR when starting/stopping' },
      { drug: 'methotrexate', severity: 'major', effect: 'Methotrexate toxicity', alternative: 'Use H2 blocker instead' }
    ],
    monitoring: 'Consider long-term risks (fractures, infections)'
  },

  // Antidepressants
  'ssri': {
    interactions: [
      { drug: 'aspirin', severity: 'moderate', effect: 'Increased bleeding risk', alternative: 'Consider PPI prophylaxis' },
      { drug: 'nsaids', severity: 'moderate', effect: 'Increased bleeding risk', alternative: 'Use acetaminophen' },
      { drug: 'tramadol', severity: 'major', effect: 'Serotonin syndrome risk', alternative: 'Use alternative analgesic' },
      { drug: 'triptans', severity: 'major', effect: 'Serotonin syndrome', alternative: 'Monitor closely or avoid' }
    ],
    monitoring: 'Monitor for bleeding and serotonin syndrome'
  }
};

// Check interactions for a medication list
export const checkDrugInteractions = (medications) => {
  const interactions = [];
  const medicationList = medications.map(m => m.toLowerCase());

  medicationList.forEach((med, index) => {
    if (drugInteractions[med]) {
      const drugInfo = drugInteractions[med];
      
      // Check against other medications in list
      medicationList.slice(index + 1).forEach(otherMed => {
        const interaction = drugInfo.interactions.find(i => 
          otherMed.includes(i.drug) || i.drug.includes(otherMed)
        );
        
        if (interaction) {
          interactions.push({
            drug1: med,
            drug2: otherMed,
            severity: interaction.severity,
            effect: interaction.effect,
            alternative: interaction.alternative,
            monitoring: drugInfo.monitoring
          });
        }
      });
    }
  });

  return interactions;
};

// Get interactions for a specific drug
export const getDrugInfo = (medication) => {
  const med = medication.toLowerCase();
  return drugInteractions[med] || null;
};

// Check if medication is in database
export const hasDrugInfo = (medication) => {
  return medication.toLowerCase() in drugInteractions;
};

// Get severity color
export const getSeverityColor = (severity) => {
  switch (severity) {
    case 'major':
      return { bg: '#fee2e2', text: '#991b1b', border: '#fca5a5' };
    case 'moderate':
      return { bg: '#fef3c7', text: '#92400e', border: '#fcd34d' };
    case 'minor':
      return { bg: '#dbeafe', text: '#1e40af', border: '#93c5fd' };
    default:
      return { bg: '#f3f4f6', text: '#374151', border: '#d1d5db' };
  }
};

// Get severity icon
export const getSeverityIcon = (severity) => {
  switch (severity) {
    case 'major':
      return '⚠️';
    case 'moderate':
      return '⚡';
    case 'minor':
      return 'ℹ️';
    default:
      return '•';
  }
};

// Common drug categories for quick reference
export const drugCategories = {
  anticoagulants: ['warfarin', 'apixaban', 'rivaroxaban', 'dabigatran', 'edoxaban'],
  antiplatelets: ['aspirin', 'clopidogrel', 'ticagrelor', 'prasugrel'],
  antibiotics: ['azithromycin', 'ciprofloxacin', 'levofloxacin', 'clarithromycin', 'doxycycline'],
  betaBlockers: ['metoprolol', 'atenolol', 'carvedilol', 'bisoprolol'],
  calciumChannelBlockers: ['amlodipine', 'diltiazem', 'verapamil', 'nifedipine'],
  statins: ['simvastatin', 'atorvastatin', 'rosuvastatin', 'pravastatin'],
  diabetesMeds: ['metformin', 'glipizide', 'insulin'],
  ppis: ['omeprazole', 'pantoprazole', 'esomeprazole', 'lansoprazole'],
  ssris: ['sertraline', 'fluoxetine', 'citalopram', 'escitalopram']
};

// Parse medication text from management recommendations
export const extractMedications = (text) => {
  if (!text) return [];
  
  const medications = [];
  const lowerText = text.toLowerCase();
  
  // Check each drug in database
  Object.keys(drugInteractions).forEach(drug => {
    if (lowerText.includes(drug)) {
      medications.push(drug);
    }
  });
  
  // Check categories
  Object.values(drugCategories).flat().forEach(drug => {
    if (lowerText.includes(drug) && !medications.includes(drug)) {
      medications.push(drug);
    }
  });
  
  return [...new Set(medications)]; // Remove duplicates
};

// Analyze management plan for drug interactions
export const analyzeManagementInteractions = (managementText, patientMedications = []) => {
  const recommendedMeds = extractMedications(managementText);
  const allMeds = [...recommendedMeds, ...patientMedications];
  const interactions = checkDrugInteractions(allMeds);
  
  return {
    recommendedMedications: recommendedMeds,
    patientMedications,
    interactions,
    hasInteractions: interactions.length > 0,
    hasMajorInteractions: interactions.some(i => i.severity === 'major')
  };
};

export default {
  checkDrugInteractions,
  getDrugInfo,
  hasDrugInfo,
  getSeverityColor,
  getSeverityIcon,
  drugCategories,
  extractMedications,
  analyzeManagementInteractions
};
