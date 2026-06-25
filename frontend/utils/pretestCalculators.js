/**
 * Pretest Probability Calculators
 * Clinical decision support scores for various conditions
 */

// Wells Score for DVT
export const calculateWellsDVT = (criteria) => {
  let score = 0;
  const {
    activeCancer,
    paralysisOrImmobilization,
    recentlyBedridden,
    localizedTenderness,
    entireLegSwollen,
    calfSwelling3cm,
    pittingEdema,
    collateralVeins,
    previousDVT,
    alternativeDiagnosis
  } = criteria;

  if (activeCancer) score += 1;
  if (paralysisOrImmobilization) score += 1;
  if (recentlyBedridden) score += 1;
  if (localizedTenderness) score += 1;
  if (entireLegSwollen) score += 1;
  if (calfSwelling3cm) score += 1;
  if (pittingEdema) score += 1;
  if (collateralVeins) score += 1;
  if (previousDVT) score += 1;
  if (alternativeDiagnosis) score -= 2;

  let risk, probability, interpretation;
  if (score <= 0) {
    risk = 'Low';
    probability = '5%';
    interpretation = 'Low probability of DVT. Consider D-dimer testing.';
  } else if (score <= 2) {
    risk = 'Moderate';
    probability = '17%';
    interpretation = 'Moderate probability of DVT. Recommend D-dimer or ultrasound.';
  } else {
    risk = 'High';
    probability = '53%';
    interpretation = 'High probability of DVT. Proceed directly to ultrasound imaging.';
  }

  return { score, risk, probability, interpretation };
};

// Wells Score for Pulmonary Embolism
export const calculateWellsPE = (criteria) => {
  let score = 0;
  const {
    clinicalDVTSigns,
    alternativeDiagnosisLessLikely,
    heartRateOver100,
    immobilizationOrSurgery,
    previousDVTPE,
    hemoptysis,
    malignancy
  } = criteria;

  if (clinicalDVTSigns) score += 3;
  if (alternativeDiagnosisLessLikely) score += 3;
  if (heartRateOver100) score += 1.5;
  if (immobilizationOrSurgery) score += 1.5;
  if (previousDVTPE) score += 1.5;
  if (hemoptysis) score += 1;
  if (malignancy) score += 1;

  let risk, probability, interpretation;
  if (score < 2) {
    risk = 'Low';
    probability = '1.3%';
    interpretation = 'Low probability of PE. Consider D-dimer testing.';
  } else if (score <= 6) {
    risk = 'Moderate';
    probability = '16.2%';
    interpretation = 'Moderate probability of PE. Recommend D-dimer or CTPA.';
  } else {
    risk = 'High';
    probability = '40.6%';
    interpretation = 'High probability of PE. Proceed to CTPA or V/Q scan.';
  }

  return { score, risk, probability, interpretation };
};

// PERC Rule (Pulmonary Embolism Rule-out Criteria)
export const calculatePERC = (criteria) => {
  let positiveCount = 0;
  const {
    ageOver50,
    heartRateOver100,
    oxygenSatBelow95,
    unilateralLegSwelling,
    hemoptysis,
    recentSurgeryOrTrauma,
    priorDVTPE,
    hormonalUse
  } = criteria;

  if (ageOver50) positiveCount += 1;
  if (heartRateOver100) positiveCount += 1;
  if (oxygenSatBelow95) positiveCount += 1;
  if (unilateralLegSwelling) positiveCount += 1;
  if (hemoptysis) positiveCount += 1;
  if (recentSurgeryOrTrauma) positiveCount += 1;
  if (priorDVTPE) positiveCount += 1;
  if (hormonalUse) positiveCount += 1;

  const passed = positiveCount === 0;
  const interpretation = passed
    ? 'PERC rule negative: PE risk <2%. No further testing needed if clinical suspicion is low.'
    : `PERC rule positive (${positiveCount}/8 criteria met): Cannot rule out PE. Proceed with risk stratification and testing.`;

  return { 
    positiveCount, 
    passed, 
    interpretation,
    recommendation: passed ? 'No further workup needed' : 'Proceed with Wells score and D-dimer/imaging'
  };
};

// HEART Score (chest pain)
export const calculateHEART = (criteria) => {
  let score = 0;
  const {
    historyRisk, // 'slightly-suspicious' | 'moderately-suspicious' | 'highly-suspicious'
    ecgFindings, // 'normal' | 'non-specific' | 'significant'
    age,
    riskFactors, // count of risk factors (0-2, 3-4, 5+)
    troponin // 'normal' | '1-3x' | '>3x'
  } = criteria;

  // History (0-2 points)
  if (historyRisk === 'slightly-suspicious') score += 0;
  else if (historyRisk === 'moderately-suspicious') score += 1;
  else if (historyRisk === 'highly-suspicious') score += 2;

  // ECG (0-2 points)
  if (ecgFindings === 'normal') score += 0;
  else if (ecgFindings === 'non-specific') score += 1;
  else if (ecgFindings === 'significant') score += 2;

  // Age (0-2 points)
  if (age < 45) score += 0;
  else if (age >= 45 && age <= 64) score += 1;
  else if (age >= 65) score += 2;

  // Risk factors (0-2 points)
  if (riskFactors <= 2) score += 0;
  else if (riskFactors <= 4) score += 1;
  else score += 2;

  // Troponin (0-2 points)
  if (troponin === 'normal') score += 0;
  else if (troponin === '1-3x') score += 1;
  else if (troponin === '>3x') score += 2;

  let risk, probability, interpretation;
  if (score <= 3) {
    risk = 'Low';
    probability = '1.7%';
    interpretation = 'Low risk for MACE at 6 weeks. Consider early discharge with outpatient follow-up.';
  } else if (score <= 6) {
    risk = 'Moderate';
    probability = '12-17%';
    interpretation = 'Moderate risk for MACE. Admit for observation and further testing.';
  } else {
    risk = 'High';
    probability = '50-65%';
    interpretation = 'High risk for MACE. Admit for aggressive management and early invasive strategy.';
  }

  return { score, risk, probability, interpretation };
};

// CHA2DS2-VASc Score (stroke risk in AFib)
export const calculateCHA2DS2VASc = (criteria) => {
  let score = 0;
  const {
    chf,
    hypertension,
    age,
    diabetes,
    strokeTIAEmbolism,
    vascularDisease,
    sex
  } = criteria;

  if (chf) score += 1;
  if (hypertension) score += 1;
  if (age >= 75) score += 2;
  else if (age >= 65) score += 1;
  if (diabetes) score += 1;
  if (strokeTIAEmbolism) score += 2;
  if (vascularDisease) score += 1;
  if (sex === 'female') score += 1;

  let risk, annualStrokeRisk, interpretation;
  if (score === 0) {
    risk = 'Low';
    annualStrokeRisk = '0%';
    interpretation = 'Low risk. No anticoagulation recommended (males only).';
  } else if (score === 1) {
    risk = 'Low';
    annualStrokeRisk = '1.3%';
    interpretation = 'Low risk. Consider anticoagulation vs no treatment.';
  } else if (score === 2) {
    risk = 'Moderate';
    annualStrokeRisk = '2.2%';
    interpretation = 'Moderate risk. Oral anticoagulation recommended.';
  } else {
    risk = 'High';
    annualStrokeRisk = `${Math.min(score * 2.2, 15.2)}%`;
    interpretation = 'High risk. Oral anticoagulation strongly recommended.';
  }

  return { score, risk, annualStrokeRisk, interpretation };
};

// HAS-BLED Score (bleeding risk with anticoagulation)
export const calculateHASBLED = (criteria) => {
  let score = 0;
  const {
    hypertension,
    abnormalRenalLiverFunction,
    stroke,
    bleedingHistory,
    labileINR,
    elderly,
    drugsAlcohol
  } = criteria;

  if (hypertension) score += 1;
  if (abnormalRenalLiverFunction) score += 1; // 1 point each or 2 if both
  if (stroke) score += 1;
  if (bleedingHistory) score += 1;
  if (labileINR) score += 1;
  if (elderly) score += 1;
  if (drugsAlcohol) score += 1; // 1 point each or 2 if both

  let risk, interpretation;
  if (score <= 1) {
    risk = 'Low';
    interpretation = 'Low bleeding risk (1-2% per year). Anticoagulation benefits likely outweigh risks.';
  } else if (score === 2) {
    risk = 'Moderate';
    interpretation = 'Moderate bleeding risk (3-4% per year). Caution and regular review recommended.';
  } else {
    risk = 'High';
    interpretation = 'High bleeding risk (>5% per year). Consider alternatives or very close monitoring.';
  }

  return { score, risk, interpretation };
};

// CHADS2 Score (simplified stroke risk in AFib)
export const calculateCHADS2 = (criteria) => {
  let score = 0;
  const {
    chf,
    hypertension,
    age75orOlder,
    diabetes,
    strokeTIA
  } = criteria;

  if (chf) score += 1;
  if (hypertension) score += 1;
  if (age75orOlder) score += 1;
  if (diabetes) score += 1;
  if (strokeTIA) score += 2;

  let risk, annualStrokeRisk, interpretation;
  if (score === 0) {
    risk = 'Low';
    annualStrokeRisk = '1.9%';
    interpretation = 'Low risk. Aspirin or no treatment.';
  } else if (score === 1) {
    risk = 'Moderate';
    annualStrokeRisk = '2.8%';
    interpretation = 'Moderate risk. Consider anticoagulation vs aspirin.';
  } else {
    risk = 'High';
    annualStrokeRisk = `${Math.min(2.8 + (score - 1) * 2, 18.2)}%`;
    interpretation = 'High risk. Anticoagulation recommended.';
  }

  return { score, risk, annualStrokeRisk, interpretation };
};

// CURB-65 (pneumonia severity)
export const calculateCURB65 = (criteria) => {
  let score = 0;
  const {
    confusion,
    urea,
    respiratoryRate,
    bloodPressure,
    age65orOlder
  } = criteria;

  if (confusion) score += 1;
  if (urea) score += 1;
  if (respiratoryRate) score += 1;
  if (bloodPressure) score += 1;
  if (age65orOlder) score += 1;

  let risk, mortality, interpretation;
  if (score <= 1) {
    risk = 'Low';
    mortality = '<3%';
    interpretation = 'Low severity. Consider outpatient treatment.';
  } else if (score === 2) {
    risk = 'Moderate';
    mortality = '9%';
    interpretation = 'Moderate severity. Consider short hospitalization or close outpatient monitoring.';
  } else {
    risk = 'High';
    mortality = '15-40%';
    interpretation = 'High severity. Hospitalization recommended, consider ICU assessment.';
  }

  return { score, risk, mortality, interpretation };
};

// Centor Score (strep pharyngitis)
export const calculateCentor = (criteria) => {
  let score = 0;
  const {
    tonsillarExudates,
    tenderAnteriorCervicalNodes,
    feverHistory,
    absenceOfCough,
    age
  } = criteria;

  if (tonsillarExudates) score += 1;
  if (tenderAnteriorCervicalNodes) score += 1;
  if (feverHistory) score += 1;
  if (absenceOfCough) score += 1;

  // Modified Centor adds age
  if (age >= 3 && age <= 14) score += 1;
  else if (age >= 15 && age <= 44) score += 0;
  else if (age >= 45) score -= 1;

  let probability, interpretation;
  if (score <= 0) {
    probability = '1-2.5%';
    interpretation = 'Very low probability of strep. No testing or antibiotics needed.';
  } else if (score === 1) {
    probability = '5-10%';
    interpretation = 'Low probability of strep. No testing or antibiotics typically needed.';
  } else if (score === 2) {
    probability = '11-17%';
    interpretation = 'Moderate probability. Consider rapid strep test.';
  } else if (score === 3) {
    probability = '28-35%';
    interpretation = 'High probability. Rapid strep test recommended.';
  } else {
    probability = '51-53%';
    interpretation = 'Very high probability. Consider empiric antibiotics or rapid strep test.';
  }

  return { score, probability, interpretation };
};

// Ottawa Ankle Rules
export const evaluateOttawaAnkle = (criteria) => {
  const {
    boneProminenceTenderness,
    unableToWeightBear
  } = criteria;

  const imagingNeeded = boneProminenceTenderness || unableToWeightBear;
  
  const interpretation = imagingNeeded
    ? 'Ottawa Ankle Rules positive: X-ray indicated to rule out fracture.'
    : 'Ottawa Ankle Rules negative: Fracture unlikely (<1%). X-ray not needed.';

  return { imagingNeeded, interpretation };
};

// List of all available calculators
export const availableCalculators = [
  {
    id: 'wells-dvt',
    name: 'Wells Score (DVT)',
    category: 'Vascular',
    description: 'Predicts probability of deep vein thrombosis',
    calculate: calculateWellsDVT
  },
  {
    id: 'wells-pe',
    name: 'Wells Score (PE)',
    category: 'Vascular',
    description: 'Predicts probability of pulmonary embolism',
    calculate: calculateWellsPE
  },
  {
    id: 'perc',
    name: 'PERC Rule',
    category: 'Vascular',
    description: 'Rules out PE in low-risk patients',
    calculate: calculatePERC
  },
  {
    id: 'heart',
    name: 'HEART Score',
    category: 'Cardiology',
    description: 'Chest pain risk stratification',
    calculate: calculateHEART
  },
  {
    id: 'cha2ds2-vasc',
    name: 'CHA₂DS₂-VASc',
    category: 'Cardiology',
    description: 'Stroke risk in atrial fibrillation',
    calculate: calculateCHA2DS2VASc
  },
  {
    id: 'has-bled',
    name: 'HAS-BLED',
    category: 'Cardiology',
    description: 'Bleeding risk with anticoagulation',
    calculate: calculateHASBLED
  },
  {
    id: 'chads2',
    name: 'CHADS₂',
    category: 'Cardiology',
    description: 'Simplified stroke risk in AFib',
    calculate: calculateCHADS2
  },
  {
    id: 'curb65',
    name: 'CURB-65',
    category: 'Pulmonology',
    description: 'Pneumonia severity assessment',
    calculate: calculateCURB65
  },
  {
    id: 'centor',
    name: 'Centor/McIsaac Score',
    category: 'Infectious Disease',
    description: 'Strep pharyngitis probability',
    calculate: calculateCentor
  },
  {
    id: 'ottawa-ankle',
    name: 'Ottawa Ankle Rules',
    category: 'Orthopedics',
    description: 'Determine need for ankle X-ray',
    calculate: evaluateOttawaAnkle
  }
];
