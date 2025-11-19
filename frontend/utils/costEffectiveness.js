/**
 * Cost-Effectiveness Analysis Engine
 * Compares diagnostic pathways by cost and time-to-diagnosis
 */

// Diagnostic test costs (approximate US dollars)
const testCosts = {
  // Lab tests
  'cbc': { cost: 50, time: '2-4 hours', description: 'Complete blood count' },
  'cmp': { cost: 75, time: '2-4 hours', description: 'Comprehensive metabolic panel' },
  'bmp': { cost: 50, time: '2-4 hours', description: 'Basic metabolic panel' },
  'troponin': { cost: 100, time: '1-2 hours', description: 'Troponin I/T' },
  'bnp': { cost: 150, time: '2-4 hours', description: 'BNP/NT-proBNP' },
  'd-dimer': { cost: 75, time: '1-2 hours', description: 'D-dimer' },
  'inr': { cost: 40, time: '1-2 hours', description: 'INR/PT' },
  'esr': { cost: 30, time: '2-4 hours', description: 'ESR' },
  'crp': { cost: 50, time: '2-4 hours', description: 'C-reactive protein' },
  'lipase': { cost: 80, time: '2-4 hours', description: 'Lipase' },
  'liver-function': { cost: 75, time: '2-4 hours', description: 'Liver function tests' },
  'tsh': { cost: 60, time: '4-8 hours', description: 'Thyroid stimulating hormone' },
  'hba1c': { cost: 45, time: '1-2 hours', description: 'Hemoglobin A1c' },
  'urinalysis': { cost: 40, time: '1 hour', description: 'Urinalysis with microscopy' },
  'urine-culture': { cost: 75, time: '24-48 hours', description: 'Urine culture' },
  'blood-culture': { cost: 150, time: '24-72 hours', description: 'Blood culture (x2)' },
  'rapid-strep': { cost: 25, time: '15 minutes', description: 'Rapid strep test' },
  'flu-test': { cost: 40, time: '30 minutes', description: 'Rapid influenza test' },
  'covid-test': { cost: 50, time: '30 minutes', description: 'COVID-19 rapid antigen' },
  'covid-pcr': { cost: 100, time: '4-24 hours', description: 'COVID-19 PCR' },

  // Imaging
  'chest-xray': { cost: 200, time: '30-60 minutes', description: 'Chest X-ray (2 views)' },
  'abdominal-xray': { cost: 200, time: '30-60 minutes', description: 'Abdominal X-ray' },
  'extremity-xray': { cost: 150, time: '30 minutes', description: 'Extremity X-ray' },
  'ct-head': { cost: 1200, time: '1-2 hours', description: 'CT head without contrast' },
  'ct-chest': { cost: 1500, time: '1-2 hours', description: 'CT chest with contrast (PE protocol)' },
  'ct-abdomen': { cost: 1800, time: '1-2 hours', description: 'CT abdomen/pelvis with contrast' },
  'ultrasound-doppler': { cost: 500, time: '30-60 minutes', description: 'Venous doppler ultrasound' },
  'echocardiogram': { cost: 800, time: '1-2 hours', description: 'Transthoracic echo' },
  'ultrasound-abdomen': { cost: 600, time: '30-60 minutes', description: 'Abdominal ultrasound' },
  'mri-brain': { cost: 2500, time: '2-4 hours', description: 'MRI brain with/without contrast' },
  'vq-scan': { cost: 1400, time: '2-3 hours', description: 'V/Q scan' },

  // Procedures
  'ecg': { cost: 100, time: '15 minutes', description: '12-lead ECG' },
  'lumbar-puncture': { cost: 500, time: '1-2 hours', description: 'Lumbar puncture with CSF analysis' },
  'stress-test': { cost: 800, time: '2-3 hours', description: 'Exercise stress test' },
  'holter-monitor': { cost: 600, time: '24-48 hours', description: '24-48 hour Holter monitor' },
  'endoscopy': { cost: 2000, time: '4-6 hours', description: 'Upper endoscopy' },
  'colonoscopy': { cost: 2500, time: '4-6 hours', description: 'Colonoscopy' },

  // Specialty consultations
  'cardiology-consult': { cost: 400, time: '4-24 hours', description: 'Cardiology consultation' },
  'neurology-consult': { cost: 400, time: '4-24 hours', description: 'Neurology consultation' },
  'surgery-consult': { cost: 400, time: '2-12 hours', description: 'Surgical consultation' },
  'gi-consult': { cost: 400, time: '4-24 hours', description: 'GI consultation' }
};

// Calculate pathway cost and time
const calculatePathwayMetrics = (tests) => {
  let totalCost = 0;
  let maxTimeHours = 0;
  const testDetails = [];

  tests.forEach(testName => {
    if (!testName || typeof testName !== 'string') return;
    const test = testCosts[testName.toLowerCase()];
    if (test) {
      totalCost += test.cost;
      
      // Parse time to hours (take maximum of range)
      const timeStr = test.time;
      let hours = 0;
      if (timeStr.includes('minutes')) {
        hours = parseFloat(timeStr) / 60;
      } else if (timeStr.includes('hours')) {
        const match = timeStr.match(/(\d+)-?(\d+)?/);
        hours = match[2] ? parseFloat(match[2]) : parseFloat(match[1]);
      } else if (timeStr.includes('days')) {
        const match = timeStr.match(/(\d+)-?(\d+)?/);
        hours = (match[2] ? parseFloat(match[2]) : parseFloat(match[1])) * 24;
      }
      
      maxTimeHours = Math.max(maxTimeHours, hours);
      
      testDetails.push({
        name: testName,
        cost: test.cost,
        time: test.time,
        description: test.description
      });
    }
  });

  return {
    totalCost,
    timeHours: maxTimeHours,
    timeDescription: formatTime(maxTimeHours),
    tests: testDetails
  };
};

// Format time in human-readable form
const formatTime = (hours) => {
  if (hours < 1) {
    return `${Math.round(hours * 60)} minutes`;
  } else if (hours < 24) {
    return `${Math.round(hours)} hours`;
  } else {
    const days = Math.floor(hours / 24);
    const remainingHours = Math.round(hours % 24);
    return remainingHours > 0 ? `${days} days ${remainingHours} hours` : `${days} days`;
  }
};

// Define diagnostic pathways for common conditions
export const diagnosticPathways = {
  'pulmonary-embolism': {
    pathways: [
      {
        name: 'Standard Workup',
        tests: ['d-dimer', 'ct-chest', 'ecg', 'troponin'],
        sensitivity: 95,
        specificity: 90,
        notes: 'Gold standard for PE diagnosis'
      },
      {
        name: 'Low-Risk Pathway (PERC negative)',
        tests: ['ecg'],
        sensitivity: 98,
        specificity: 15,
        notes: 'Rule-out only if PERC negative and low clinical suspicion'
      },
      {
        name: 'V/Q Scan Alternative',
        tests: ['d-dimer', 'vq-scan', 'ecg'],
        sensitivity: 90,
        specificity: 85,
        notes: 'Use when contrast contraindicated'
      }
    ]
  },
  'deep-vein-thrombosis': {
    pathways: [
      {
        name: 'Standard Workup',
        tests: ['d-dimer', 'ultrasound-doppler'],
        sensitivity: 95,
        specificity: 95,
        notes: 'First-line diagnostic approach'
      },
      {
        name: 'High Probability (Wells >2)',
        tests: ['ultrasound-doppler'],
        sensitivity: 95,
        specificity: 95,
        notes: 'Skip D-dimer if high clinical probability'
      },
      {
        name: 'Low Probability (Wells ≤0)',
        tests: ['d-dimer'],
        sensitivity: 98,
        specificity: 40,
        notes: 'Negative D-dimer rules out DVT'
      }
    ]
  },
  'acute-coronary-syndrome': {
    pathways: [
      {
        name: 'Standard ED Workup',
        tests: ['ecg', 'troponin', 'cbc', 'bmp', 'chest-xray'],
        sensitivity: 95,
        specificity: 85,
        notes: 'Serial troponins at 0 and 3-6 hours'
      },
      {
        name: 'Low-Risk Chest Pain (HEART ≤3)',
        tests: ['ecg', 'troponin'],
        sensitivity: 99,
        specificity: 40,
        notes: 'May allow early discharge'
      },
      {
        name: 'High-Risk Protocol',
        tests: ['ecg', 'troponin', 'cbc', 'bmp', 'chest-xray', 'echocardiogram', 'cardiology-consult'],
        sensitivity: 98,
        specificity: 90,
        notes: 'For STEMI or high HEART score'
      }
    ]
  },
  'stroke': {
    pathways: [
      {
        name: 'Acute Stroke Protocol',
        tests: ['ct-head', 'ecg', 'cbc', 'bmp', 'inr', 'blood-glucose'],
        sensitivity: 95,
        specificity: 98,
        notes: 'Non-contrast CT to rule out hemorrhage'
      },
      {
        name: 'Comprehensive Stroke Workup',
        tests: ['ct-head', 'mri-brain', 'ecg', 'echocardiogram', 'carotid-doppler', 'lipid-panel', 'neurology-consult'],
        sensitivity: 98,
        specificity: 95,
        notes: 'Full workup for stroke mechanism'
      },
      {
        name: 'TIA Workup',
        tests: ['ct-head', 'ecg', 'carotid-doppler', 'echocardiogram'],
        sensitivity: 90,
        specificity: 90,
        notes: 'Outpatient workup acceptable if low risk'
      }
    ]
  },
  'pneumonia': {
    pathways: [
      {
        name: 'Standard Workup',
        tests: ['chest-xray', 'cbc', 'cmp', 'blood-culture'],
        sensitivity: 85,
        specificity: 80,
        notes: 'Outpatient if CURB-65 ≤1'
      },
      {
        name: 'Severe Pneumonia',
        tests: ['chest-xray', 'ct-chest', 'cbc', 'cmp', 'blood-culture', 'sputum-culture', 'abg'],
        sensitivity: 95,
        specificity: 85,
        notes: 'For ICU-level care or complicated pneumonia'
      },
      {
        name: 'Outpatient Low-Risk',
        tests: ['chest-xray'],
        sensitivity: 75,
        specificity: 75,
        notes: 'Young, healthy patients with clear clinical diagnosis'
      }
    ]
  },
  'appendicitis': {
    pathways: [
      {
        name: 'Standard Workup',
        tests: ['ct-abdomen', 'cbc', 'urinalysis'],
        sensitivity: 95,
        specificity: 94,
        notes: 'Gold standard diagnostic approach'
      },
      {
        name: 'Ultrasound First (Pediatric/Pregnant)',
        tests: ['ultrasound-abdomen', 'cbc', 'urinalysis'],
        sensitivity: 85,
        specificity: 92,
        notes: 'Avoid radiation in young patients'
      },
      {
        name: 'Clinical Diagnosis',
        tests: ['cbc', 'urinalysis', 'surgery-consult'],
        sensitivity: 80,
        specificity: 85,
        notes: 'High clinical suspicion, proceed to OR'
      }
    ]
  }
};

// Analyze cost-effectiveness of pathways
export const analyzePathways = (condition) => {
  if (!condition || typeof condition !== 'string') {
    return null;
  }
  const conditionKey = condition.toLowerCase().replace(/\s+/g, '-');
  const pathwayData = diagnosticPathways[conditionKey];
  
  if (!pathwayData) {
    return null;
  }

  const analyzedPathways = pathwayData.pathways.map(pathway => {
    const metrics = calculatePathwayMetrics(pathway.tests);
    
    // Calculate cost per % sensitivity
    const efficiency = metrics.totalCost / pathway.sensitivity;
    
    return {
      ...pathway,
      ...metrics,
      efficiency,
      costEfficiency: efficiency < 50 ? 'Excellent' : efficiency < 100 ? 'Good' : 'Fair'
    };
  });

  // Sort by cost
  const sortedByCost = [...analyzedPathways].sort((a, b) => a.totalCost - b.totalCost);
  
  // Sort by time
  const sortedByTime = [...analyzedPathways].sort((a, b) => a.timeHours - b.timeHours);
  
  // Sort by efficiency (cost per sensitivity)
  const sortedByEfficiency = [...analyzedPathways].sort((a, b) => a.efficiency - b.efficiency);

  return {
    condition,
    pathways: analyzedPathways,
    cheapest: sortedByCost[0],
    fastest: sortedByTime[0],
    mostEfficient: sortedByEfficiency[0],
    recommendations: generateRecommendations(analyzedPathways)
  };
};

// Generate recommendations based on pathway analysis
const generateRecommendations = (pathways) => {
  const recommendations = [];
  
  const cheapest = pathways.reduce((min, p) => p.totalCost < min.totalCost ? p : min);
  const fastest = pathways.reduce((min, p) => p.timeHours < min.timeHours ? p : min);
  const mostSensitive = pathways.reduce((max, p) => p.sensitivity > max.sensitivity ? p : max);
  
  recommendations.push({
    type: 'cost',
    title: 'Most Cost-Effective',
    pathway: cheapest.name,
    reason: `Lowest cost at $${cheapest.totalCost} with ${cheapest.sensitivity}% sensitivity`
  });
  
  recommendations.push({
    type: 'time',
    title: 'Fastest Diagnosis',
    pathway: fastest.name,
    reason: `Results in ${fastest.timeDescription} with ${fastest.sensitivity}% sensitivity`
  });
  
  recommendations.push({
    type: 'accuracy',
    title: 'Most Accurate',
    pathway: mostSensitive.name,
    reason: `${mostSensitive.sensitivity}% sensitivity, ${mostSensitive.specificity}% specificity`
  });
  
  return recommendations;
};

// Compare two diagnostic pathways
export const comparePathways = (condition, pathway1Name, pathway2Name) => {
  const analysis = analyzePathways(condition);
  if (!analysis) return null;
  
  const p1 = analysis.pathways.find(p => p.name === pathway1Name);
  const p2 = analysis.pathways.find(p => p.name === pathway2Name);
  
  if (!p1 || !p2) return null;
  
  return {
    pathway1: p1,
    pathway2: p2,
    comparison: {
      costDifference: Math.abs(p1.totalCost - p2.totalCost),
      cheaperPathway: p1.totalCost < p2.totalCost ? p1.name : p2.name,
      timeDifference: Math.abs(p1.timeHours - p2.timeHours),
      fasterPathway: p1.timeHours < p2.timeHours ? p1.name : p2.name,
      sensitivityDifference: Math.abs(p1.sensitivity - p2.sensitivity),
      moreAccurate: p1.sensitivity > p2.sensitivity ? p1.name : p2.name
    }
  };
};

// Get test information
export const getTestInfo = (testName) => {
  if (!testName || typeof testName !== 'string') {
    return null;
  }
  return testCosts[testName.toLowerCase()] || null;
};

// Calculate custom pathway
export const calculateCustomPathway = (tests) => {
  return calculatePathwayMetrics(tests);
};

export default {
  analyzePathways,
  comparePathways,
  getTestInfo,
  calculateCustomPathway,
  testCosts,
  diagnosticPathways
};
