/**
 * Red Flag Alert System
 * Automatically detects and highlights life-threatening conditions
 */

// Red flag conditions database
export const redFlagConditions = {
  // Cardiovascular
  'stemi': {
    severity: 'critical',
    category: 'Cardiovascular',
    alert: '🚨 STEMI - ACTIVATE CATH LAB',
    timeWindow: '90 minutes',
    actions: [
      'Activate STEMI protocol immediately',
      'Aspirin 325mg chewed',
      'Dual antiplatelet therapy (clopidogrel/ticagrelor)',
      'Anticoagulation (heparin or enoxaparin)',
      'Door-to-balloon time <90 minutes',
      'Cardiology consult STAT'
    ],
    mortality: '5-10% (untreated >20%)',
    keywords: ['st elevation', 'stemi', 'acute mi', 'inferior mi', 'anterior mi']
  },
  'aortic-dissection': {
    severity: 'critical',
    category: 'Cardiovascular',
    alert: '🚨 SUSPECTED AORTIC DISSECTION',
    timeWindow: 'Immediate',
    actions: [
      'NPO, IV access x2',
      'Blood pressure control (SBP 100-120)',
      'Beta blocker first (esmolol or labetalol)',
      'CTA chest/abdomen/pelvis STAT',
      'Cardiothoracic surgery consult immediately',
      'Type and crossmatch 6 units'
    ],
    mortality: '1-2% per hour if untreated',
    keywords: ['aortic dissection', 'tearing chest pain', 'mediastinal widening']
  },
  'cardiac-tamponade': {
    severity: 'critical',
    category: 'Cardiovascular',
    alert: '🚨 CARDIAC TAMPONADE',
    timeWindow: 'Immediate',
    actions: [
      'Pericardiocentesis STAT',
      'IV fluids - aggressive resuscitation',
      'Echo to confirm diagnosis',
      'Cardiology/cardiothoracic surgery STAT',
      'Prepare for OR/cath lab'
    ],
    mortality: 'Fatal if untreated',
    keywords: ['cardiac tamponade', "beck's triad", 'pulsus paradoxus']
  },
  'ventricular-tachycardia': {
    severity: 'critical',
    category: 'Cardiovascular',
    alert: '🚨 UNSTABLE V-TACH',
    timeWindow: 'Immediate',
    actions: [
      'If pulseless: CPR and defibrillation',
      'If unstable: Synchronized cardioversion',
      'If stable: Amiodarone or lidocaine',
      'Cardiology consult',
      'Continuous telemetry'
    ],
    mortality: 'High if unstable',
    keywords: ['ventricular tachycardia', 'v-tach', 'wide complex tachycardia']
  },

  // Neurological
  'ischemic-stroke': {
    severity: 'critical',
    category: 'Neurological',
    alert: '🚨 ACUTE STROKE - ACTIVATE STROKE TEAM',
    timeWindow: '4.5 hours for tPA, 24 hours for thrombectomy',
    actions: [
      'CT head STAT (non-contrast)',
      'Stroke team activation',
      'NIH Stroke Scale assessment',
      'tPA if within 4.5 hours and no contraindications',
      'Thrombectomy evaluation if large vessel occlusion',
      'Blood pressure management per protocol'
    ],
    mortality: 'Time-dependent',
    keywords: ['stroke', 'cva', 'hemiparesis', 'aphasia', 'facial droop']
  },
  'hemorrhagic-stroke': {
    severity: 'critical',
    category: 'Neurological',
    alert: '🚨 INTRACRANIAL HEMORRHAGE',
    timeWindow: 'Immediate',
    actions: [
      'Neurosurgery consult STAT',
      'Reverse anticoagulation immediately',
      'Blood pressure control (SBP <140)',
      'Repeat CT in 6 hours',
      'ICU admission',
      'Consider EVD if hydrocephalus'
    ],
    mortality: '40-50% overall',
    keywords: ['intracranial hemorrhage', 'ich', 'subarachnoid hemorrhage', 'sah']
  },
  'bacterial-meningitis': {
    severity: 'critical',
    category: 'Neurological',
    alert: '🚨 BACTERIAL MENINGITIS',
    timeWindow: '< 1 hour for antibiotics',
    actions: [
      'Blood cultures x2 STAT',
      'Empiric antibiotics within 1 hour (do NOT wait for LP)',
      'Ceftriaxone 2g IV + vancomycin 15-20mg/kg',
      'Add ampicillin if >50yo or immunocompromised',
      'Dexamethasone 10mg IV before or with antibiotics',
      'LP when safe (check for elevated ICP)'
    ],
    mortality: '15-30% if delayed treatment',
    keywords: ['meningitis', 'nuchal rigidity', 'kernig sign', 'brudzinski']
  },
  'status-epilepticus': {
    severity: 'critical',
    category: 'Neurological',
    alert: '🚨 STATUS EPILEPTICUS',
    timeWindow: '< 30 minutes',
    actions: [
      'Benzodiazepines immediately (lorazepam 0.1mg/kg)',
      'If continues: Fosphenytoin 20 PE/kg',
      'If refractory: ICU, intubation, propofol/midazolam',
      'Check glucose, correct electrolytes',
      'EEG monitoring',
      'Neurology consult'
    ],
    mortality: 'Increases with duration >30min',
    keywords: ['status epilepticus', 'prolonged seizure', 'continuous seizure']
  },

  // Pulmonary
  'tension-pneumothorax': {
    severity: 'critical',
    category: 'Pulmonary',
    alert: '🚨 TENSION PNEUMOTHORAX',
    timeWindow: 'Immediate',
    actions: [
      'Needle decompression immediately (2nd ICS, midclavicular)',
      'Do NOT wait for imaging',
      'Chest tube placement',
      'Surgery consult if traumatic',
      '100% oxygen'
    ],
    mortality: 'Fatal if untreated',
    keywords: ['tension pneumothorax', 'absent breath sounds', 'tracheal deviation']
  },
  'massive-pulmonary-embolism': {
    severity: 'critical',
    category: 'Pulmonary',
    alert: '🚨 MASSIVE PE - HEMODYNAMICALLY UNSTABLE',
    timeWindow: 'Immediate',
    actions: [
      'Aggressive resuscitation',
      'Thrombolytics (tPA) if no contraindications',
      'Anticoagulation (heparin bolus + infusion)',
      'Consider ECMO if available',
      'Thrombectomy evaluation',
      'ICU admission'
    ],
    mortality: '25-30% if massive PE',
    keywords: ['massive pe', 'hemodynamically unstable', 'right heart strain']
  },

  // Gastrointestinal
  'ruptured-aaa': {
    severity: 'critical',
    category: 'Gastrointestinal',
    alert: '🚨 RUPTURED AAA',
    timeWindow: 'Immediate',
    actions: [
      'Vascular surgery STAT - DO NOT DELAY',
      'NPO',
      'Type and cross 10 units PRBC',
      'Permissive hypotension (SBP 90-100)',
      'Large bore IV x2',
      'Direct to OR - imaging only if stable'
    ],
    mortality: '80-90% if ruptured',
    keywords: ['ruptured aaa', 'abdominal aortic aneurysm', 'pulsatile mass']
  },
  'perforated-viscus': {
    severity: 'critical',
    category: 'Gastrointestinal',
    alert: '⚠️ PERFORATED VISCUS',
    timeWindow: '< 6 hours',
    actions: [
      'NPO, NGT decompression',
      'IV fluids, broad spectrum antibiotics',
      'CT abdomen/pelvis with PO contrast',
      'Surgery consult STAT',
      'Prepare for OR'
    ],
    mortality: 'Increases with delay >24 hours',
    keywords: ['perforated viscus', 'free air', 'peritonitis', 'rigid abdomen']
  },
  'upper-gi-bleed': {
    severity: 'high',
    category: 'Gastrointestinal',
    alert: '⚠️ SEVERE UPPER GI BLEED',
    timeWindow: '< 12 hours',
    actions: [
      'Two large bore IVs',
      'Type and cross 4 units',
      'Aggressive resuscitation (crystalloid, PRBCs)',
      'PPI bolus + infusion',
      'GI consult for urgent endoscopy',
      'Correct coagulopathy'
    ],
    mortality: '5-10% overall',
    keywords: ['upper gi bleed', 'hematemesis', 'melena', 'coffee ground']
  },

  // Infectious
  'septic-shock': {
    severity: 'critical',
    category: 'Infectious',
    alert: '🚨 SEPTIC SHOCK',
    timeWindow: '< 1 hour',
    actions: [
      'Blood cultures x2 before antibiotics',
      'Broad spectrum antibiotics within 1 hour',
      'Lactate level',
      '30mL/kg IV crystalloid bolus',
      'Vasopressors if hypotension persists',
      'Source control'
    ],
    mortality: '25-40% with septic shock',
    keywords: ['septic shock', 'sepsis', 'hypotension', 'lactate >4']
  },
  'necrotizing-fasciitis': {
    severity: 'critical',
    category: 'Infectious',
    alert: '🚨 NECROTIZING FASCIITIS',
    timeWindow: '< 6 hours',
    actions: [
      'Surgical debridement STAT',
      'Broad spectrum antibiotics + clindamycin',
      'Aggressive fluid resuscitation',
      'ICU admission',
      'Consider IVIG',
      'Serial debridements often needed'
    ],
    mortality: '20-40%',
    keywords: ['necrotizing fasciitis', 'necrotizing soft tissue', 'crepitus', 'dishwater fluid']
  },

  // Other
  'anaphylaxis': {
    severity: 'critical',
    category: 'Allergy',
    alert: '🚨 ANAPHYLAXIS',
    timeWindow: 'Immediate',
    actions: [
      'Epinephrine 0.3-0.5mg IM (anterolateral thigh)',
      'Repeat epinephrine q5-15min if needed',
      'IV fluids 1-2L bolus',
      'H1 blocker (diphenhydramine)',
      'H2 blocker (ranitidine/famotidine)',
      'Corticosteroids',
      'Observe 4-6 hours for biphasic reaction'
    ],
    mortality: 'Rare with prompt treatment',
    keywords: ['anaphylaxis', 'angioedema', 'stridor', 'urticaria', 'hypotension']
  },
  'acute-angle-closure-glaucoma': {
    severity: 'high',
    category: 'Ophthalmology',
    alert: '⚠️ ACUTE ANGLE-CLOSURE GLAUCOMA',
    timeWindow: '< 24 hours',
    actions: [
      'Ophthalmology consult STAT',
      'IOP-lowering medications immediately',
      'Acetazolamide 500mg IV',
      'Timolol 0.5% eye drops',
      'Pilocarpine 2% eye drops',
      'Definitive treatment: Laser iridotomy'
    ],
    mortality: 'Permanent vision loss if delayed',
    keywords: ['angle closure glaucoma', 'elevated iop', 'mid-dilated pupil', 'hazy cornea']
  },
  'testicular-torsion': {
    severity: 'high',
    category: 'Urology',
    alert: '⚠️ TESTICULAR TORSION',
    timeWindow: '< 6 hours',
    actions: [
      'Urology consult STAT',
      'Manual detorsion attempt',
      'Ultrasound if diagnosis uncertain',
      'Emergent surgical exploration',
      'NPO, prepare for OR'
    ],
    mortality: 'Testicle salvage decreases after 6 hours',
    keywords: ['testicular torsion', 'acute scrotum', 'absent cremasteric reflex']
  }
};

// Scan diagnosis for red flags
export const detectRedFlags = (diagnosis) => {
  // Handle undefined, null, or non-string diagnosis
  if (!diagnosis || typeof diagnosis !== 'string') {
    return [];
  }
  
  const diagnosisLower = diagnosis.toLowerCase();
  const detectedFlags = [];
  
  Object.entries(redFlagConditions).forEach(([key, condition]) => {
    // Check if diagnosis matches red flag keywords
    const matched = condition.keywords.some(keyword => 
      diagnosisLower.includes(keyword.toLowerCase())
    );
    
    if (matched) {
      detectedFlags.push({
        key,
        ...condition,
        priority: getSeverityPriority(condition.severity)
      });
    }
  });
  
  // Sort by priority (critical first)
  detectedFlags.sort((a, b) => a.priority - b.priority);
  
  return detectedFlags;
};

// Get numerical priority for sorting
const getSeverityPriority = (severity) => {
  switch (severity) {
    case 'critical': return 1;
    case 'high': return 2;
    case 'moderate': return 3;
    default: return 4;
  }
};

// Get severity styling
export const getSeverityStyle = (severity) => {
  switch (severity) {
    case 'critical':
      return {
        bg: '#fecaca',
        border: '#dc2626',
        text: '#7f1d1d',
        icon: '🚨',
        pulse: true
      };
    case 'high':
      return {
        bg: '#fed7aa',
        border: '#ea580c',
        text: '#7c2d12',
        icon: '⚠️',
        pulse: false
      };
    case 'moderate':
      return {
        bg: '#fef08a',
        border: '#ca8a04',
        text: '#713f12',
        icon: '⚡',
        pulse: false
      };
    default:
      return {
        bg: '#e5e7eb',
        border: '#6b7280',
        text: '#1f2937',
        icon: 'ℹ️',
        pulse: false
      };
  }
};

// Check if diagnosis list contains any red flags
export const hasRedFlags = (diagnoses) => {
  if (!Array.isArray(diagnoses) || diagnoses.length === 0) {
    return false;
  }
  return diagnoses.some(dx => {
    if (!dx) return false;
    const flags = detectRedFlags(dx.diagnosis || dx);
    return flags.length > 0;
  });
};

// Get highest severity red flag from diagnosis list
export const getHighestSeverityFlag = (diagnoses) => {
  if (!Array.isArray(diagnoses) || diagnoses.length === 0) {
    return null;
  }
  
  let highestSeverity = null;
  let highestPriority = 999;
  
  diagnoses.forEach(dx => {
    if (!dx) return;
    const flags = detectRedFlags(dx.diagnosis || dx);
    flags.forEach(flag => {
      if (flag.priority < highestPriority) {
        highestPriority = flag.priority;
        highestSeverity = flag;
      }
    });
  });
  
  return highestSeverity;
};

// Generate red flag summary for multiple diagnoses
export const generateRedFlagSummary = (diagnoses) => {
  const allFlags = [];
  const criticalFlags = [];
  const highFlags = [];
  
  if (!Array.isArray(diagnoses)) {
    return {
      totalFlags: 0,
      criticalCount: 0,
      highCount: 0,
      allFlags: [],
      criticalFlags: [],
      highFlags: [],
      hasCritical: false,
      needsImmediateAction: false
    };
  }
  
  diagnoses.forEach(dx => {
    if (!dx) return;
    const flags = detectRedFlags(dx.diagnosis || dx);
    flags.forEach(flag => {
      const flagWithDx = {
        ...flag,
        diagnosis: dx.diagnosis || dx
      };
      
      allFlags.push(flagWithDx);
      
      if (flag.severity === 'critical') {
        criticalFlags.push(flagWithDx);
      } else if (flag.severity === 'high') {
        highFlags.push(flagWithDx);
      }
    });
  });
  
  return {
    totalFlags: allFlags.length,
    criticalCount: criticalFlags.length,
    highCount: highFlags.length,
    allFlags,
    criticalFlags,
    highFlags,
    hasCritical: criticalFlags.length > 0,
    needsImmediateAction: criticalFlags.length > 0
  };
};

// Format time window for display
export const formatTimeWindow = (timeWindow) => {
  if (!timeWindow) return 'Immediate action required';
  return `Time-critical: ${timeWindow}`;
};

// Get recommended actions as formatted list
export const getActionList = (flag) => {
  return flag.actions.map((action, idx) => ({
    order: idx + 1,
    action,
    completed: false
  }));
};

export default {
  redFlagConditions,
  detectRedFlags,
  getSeverityStyle,
  hasRedFlags,
  getHighestSeverityFlag,
  generateRedFlagSummary,
  formatTimeWindow,
  getActionList
};
