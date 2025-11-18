/**
 * Time-Sensitive Alerts System
 * Flags diagnoses requiring immediate action with time windows
 */

// Urgency classifications
export const urgencyLevels = {
  IMMEDIATE: {
    level: 'immediate',
    label: 'IMMEDIATE',
    timeWindow: '< 15 minutes',
    color: '#dc2626',
    bgColor: '#fee2e2',
    icon: '🚨',
    description: 'Life-threatening, requires immediate intervention'
  },
  EMERGENT: {
    level: 'emergent',
    label: 'EMERGENT',
    timeWindow: '< 1 hour',
    color: '#ea580c',
    bgColor: '#ffedd5',
    icon: '⚡',
    description: 'Urgent, significant morbidity/mortality if delayed'
  },
  URGENT: {
    level: 'urgent',
    label: 'URGENT',
    timeWindow: '< 6 hours',
    color: '#f59e0b',
    bgColor: '#fef3c7',
    icon: '⏰',
    description: 'Time-sensitive, best outcomes with prompt treatment'
  },
  SEMI_URGENT: {
    level: 'semi-urgent',
    label: 'SEMI-URGENT',
    timeWindow: '< 24 hours',
    color: '#eab308',
    bgColor: '#fef9c3',
    icon: '⏱️',
    description: 'Should be evaluated within 24 hours'
  },
  NON_URGENT: {
    level: 'non-urgent',
    label: 'ROUTINE',
    timeWindow: '< 1 week',
    color: '#14b8a6',
    bgColor: '#ccfbf1',
    icon: '📋',
    description: 'Routine evaluation appropriate'
  }
};

// Time-sensitive conditions database
export const timeSensitiveConditions = {
  // IMMEDIATE (< 15 minutes)
  'cardiac-arrest': {
    urgency: urgencyLevels.IMMEDIATE,
    timeToTreatment: '< 5 minutes',
    outcomeWithDelay: 'Brain damage after 4-6 minutes, death after 10 minutes',
    criticalActions: [
      'CPR immediately',
      'Defibrillation if shockable rhythm',
      'Epinephrine q3-5min',
      'Advanced airway',
      'Treat reversible causes (H\'s and T\'s)'
    ],
    keywords: ['cardiac arrest', 'pulseless', 'vfib', 'ventricular fibrillation']
  },
  'anaphylaxis': {
    urgency: urgencyLevels.IMMEDIATE,
    timeToTreatment: '< 5 minutes',
    outcomeWithDelay: 'Airway compromise, cardiovascular collapse, death',
    criticalActions: [
      'Epinephrine 0.3-0.5mg IM immediately',
      'Repeat q5-15min as needed',
      'Airway management',
      'IV fluids',
      'Antihistamines and steroids'
    ],
    keywords: ['anaphylaxis', 'anaphylactic shock']
  },
  'tension-pneumothorax': {
    urgency: urgencyLevels.IMMEDIATE,
    timeToTreatment: '< 5 minutes',
    outcomeWithDelay: 'Cardiovascular collapse, death',
    criticalActions: [
      'Needle decompression immediately',
      'Do NOT wait for imaging',
      'Chest tube placement',
      'High-flow oxygen'
    ],
    keywords: ['tension pneumothorax']
  },

  // EMERGENT (< 1 hour)
  'stemi': {
    urgency: urgencyLevels.EMERGENT,
    timeToTreatment: '< 90 minutes (door-to-balloon)',
    outcomeWithDelay: 'Every 30-minute delay increases 1-year mortality by 7.5%',
    criticalActions: [
      'Activate cath lab',
      'Aspirin 325mg immediately',
      'Dual antiplatelet therapy',
      'Anticoagulation',
      'Primary PCI < 90 minutes'
    ],
    milestones: [
      { time: '10 min', action: 'ECG obtained' },
      { time: '30 min', action: 'Cath lab activated' },
      { time: '90 min', action: 'Balloon inflation' }
    ],
    keywords: ['stemi', 'st elevation', 'acute mi', 'myocardial infarction']
  },
  'ischemic-stroke': {
    urgency: urgencyLevels.EMERGENT,
    timeToTreatment: '< 4.5 hours for tPA, < 24 hours for thrombectomy',
    outcomeWithDelay: '1.9 million neurons die per minute without treatment',
    criticalActions: [
      'Activate stroke team',
      'CT head within 25 minutes',
      'tPA if within 4.5 hours',
      'Thrombectomy evaluation',
      'Blood pressure management'
    ],
    milestones: [
      { time: '10 min', action: 'Stroke team activated' },
      { time: '25 min', action: 'CT completed' },
      { time: '45 min', action: 'tPA bolus if indicated' },
      { time: '6 hours', action: 'Thrombectomy window (can extend to 24h)' }
    ],
    keywords: ['stroke', 'cva', 'ischemic stroke', 'cerebrovascular accident']
  },
  'septic-shock': {
    urgency: urgencyLevels.EMERGENT,
    timeToTreatment: '< 1 hour for antibiotics',
    outcomeWithDelay: 'Each hour delay increases mortality by 7.6%',
    criticalActions: [
      'Blood cultures before antibiotics',
      'Broad-spectrum antibiotics within 1 hour',
      '30mL/kg crystalloid bolus',
      'Lactate level',
      'Vasopressors if needed',
      'Source control'
    ],
    milestones: [
      { time: '15 min', action: 'Blood cultures obtained' },
      { time: '30 min', action: 'Fluid bolus started' },
      { time: '45 min', action: 'Antibiotics administered' },
      { time: '6 hours', action: 'Reassess lactate and vitals' }
    ],
    keywords: ['septic shock', 'severe sepsis']
  },
  'bacterial-meningitis': {
    urgency: urgencyLevels.EMERGENT,
    timeToTreatment: '< 1 hour for antibiotics',
    outcomeWithDelay: 'Mortality increases significantly with delay',
    criticalActions: [
      'Blood cultures immediately',
      'Antibiotics within 1 hour (do NOT wait for LP)',
      'Dexamethasone before or with antibiotics',
      'LP when safe',
      'Airway protection'
    ],
    keywords: ['bacterial meningitis', 'meningitis']
  },
  'aortic-dissection': {
    urgency: urgencyLevels.EMERGENT,
    timeToTreatment: '< 1 hour',
    outcomeWithDelay: '1-2% mortality per hour',
    criticalActions: [
      'Blood pressure control (SBP 100-120)',
      'Beta blocker first',
      'CTA chest/abdomen/pelvis',
      'Cardiothoracic surgery STAT',
      'Type and cross'
    ],
    keywords: ['aortic dissection']
  },

  // URGENT (< 6 hours)
  'testicular-torsion': {
    urgency: urgencyLevels.URGENT,
    timeToTreatment: '< 6 hours',
    outcomeWithDelay: 'Testicle salvage: >90% if <6h, <10% if >24h',
    criticalActions: [
      'Urology consult immediately',
      'Manual detorsion attempt',
      'Emergent surgical exploration',
      'Do not delay for imaging if high suspicion'
    ],
    keywords: ['testicular torsion', 'acute scrotum']
  },
  'retinal-artery-occlusion': {
    urgency: urgencyLevels.URGENT,
    timeToTreatment: '< 4 hours',
    outcomeWithDelay: 'Permanent vision loss, "stroke of the eye"',
    criticalActions: [
      'Ophthalmology consult STAT',
      'Ocular massage',
      'Lower intraocular pressure',
      'Hyperbaric oxygen if available',
      'Workup for embolic source'
    ],
    keywords: ['retinal artery occlusion', 'central retinal artery']
  },
  'ruptured-ectopic': {
    urgency: urgencyLevels.URGENT,
    timeToTreatment: '< 2 hours',
    outcomeWithDelay: 'Hemorrhagic shock, death',
    criticalActions: [
      'Two large bore IVs',
      'Type and cross',
      'OB/GYN consult STAT',
      'Emergent OR',
      'Aggressive resuscitation'
    ],
    keywords: ['ruptured ectopic', 'ectopic pregnancy']
  },
  'necrotizing-fasciitis': {
    urgency: urgencyLevels.URGENT,
    timeToTreatment: '< 6 hours',
    outcomeWithDelay: 'Each hour delay increases mortality',
    criticalActions: [
      'Surgical debridement STAT',
      'Broad-spectrum antibiotics + clindamycin',
      'Aggressive fluid resuscitation',
      'ICU admission',
      'Serial debridements'
    ],
    keywords: ['necrotizing fasciitis', 'necrotizing soft tissue']
  },
  'compartment-syndrome': {
    urgency: urgencyLevels.URGENT,
    timeToTreatment: '< 6 hours',
    outcomeWithDelay: 'Muscle necrosis, permanent disability',
    criticalActions: [
      'Orthopedic surgery consult',
      'Compartment pressure measurement',
      'Emergent fasciotomy if pressure >30mmHg',
      'Remove constricting dressings',
      'Elevate to heart level only'
    ],
    keywords: ['compartment syndrome', 'acute compartment syndrome']
  },

  // SEMI-URGENT (< 24 hours)
  'acute-angle-closure-glaucoma': {
    urgency: urgencyLevels.SEMI_URGENT,
    timeToTreatment: '< 24 hours',
    outcomeWithDelay: 'Permanent vision loss',
    criticalActions: [
      'Ophthalmology consult',
      'IOP-lowering medications',
      'Acetazolamide',
      'Topical beta-blocker and pilocarpine',
      'Laser iridotomy within 24 hours'
    ],
    keywords: ['angle closure glaucoma', 'acute angle closure']
  },
  'appendicitis': {
    urgency: urgencyLevels.SEMI_URGENT,
    timeToTreatment: '< 24 hours',
    outcomeWithDelay: 'Perforation risk increases after 24-36 hours',
    criticalActions: [
      'Surgery consult',
      'NPO, IV fluids',
      'Antibiotics if complicated',
      'CT if diagnosis uncertain',
      'Appendectomy'
    ],
    keywords: ['appendicitis', 'acute appendicitis']
  },
  'bowel-obstruction': {
    urgency: urgencyLevels.SEMI_URGENT,
    timeToTreatment: '< 24 hours',
    outcomeWithDelay: 'Ischemia, perforation, sepsis',
    criticalActions: [
      'NPO, NGT decompression',
      'IV fluids',
      'Surgery consult',
      'CT abdomen/pelvis',
      'Monitor for peritonitis'
    ],
    keywords: ['bowel obstruction', 'small bowel obstruction', 'sbo']
  },
  'cholelithiasis': {
    urgency: urgencyLevels.SEMI_URGENT,
    timeToTreatment: '< 24-72 hours if complicated',
    outcomeWithDelay: 'Cholangitis, pancreatitis, sepsis',
    criticalActions: [
      'NPO, IV fluids',
      'Antibiotics if cholecystitis',
      'Surgery consult',
      'Ultrasound or CT',
      'Cholecystectomy within 72 hours if acute'
    ],
    keywords: ['acute cholecystitis', 'cholangitis', 'gallstone']
  }
};

// Determine urgency level for a diagnosis
export const assessUrgency = (diagnosis) => {
  const diagnosisLower = diagnosis.toLowerCase();
  
  for (const [key, condition] of Object.entries(timeSensitiveConditions)) {
    const matched = condition.keywords.some(keyword => 
      diagnosisLower.includes(keyword.toLowerCase())
    );
    
    if (matched) {
      return {
        key,
        ...condition,
        hasTimeWindow: true
      };
    }
  }
  
  // Default to routine if no match
  return {
    urgency: urgencyLevels.NON_URGENT,
    hasTimeWindow: false
  };
};

// Generate urgency report for multiple diagnoses
export const generateUrgencyReport = (diagnoses) => {
  const assessments = diagnoses.map(dx => ({
    diagnosis: dx.diagnosis || dx,
    ...assessUrgency(dx.diagnosis || dx)
  }));
  
  // Sort by urgency level
  const urgencyOrder = ['immediate', 'emergent', 'urgent', 'semi-urgent', 'non-urgent'];
  assessments.sort((a, b) => {
    const aIndex = urgencyOrder.indexOf(a.urgency.level);
    const bIndex = urgencyOrder.indexOf(b.urgency.level);
    return aIndex - bIndex;
  });
  
  const immediate = assessments.filter(a => a.urgency.level === 'immediate');
  const emergent = assessments.filter(a => a.urgency.level === 'emergent');
  const urgent = assessments.filter(a => a.urgency.level === 'urgent');
  
  return {
    assessments,
    immediate,
    emergent,
    urgent,
    highestUrgency: assessments[0]?.urgency.level || 'non-urgent',
    needsImmediateAction: immediate.length > 0 || emergent.length > 0,
    timeCriticalCount: immediate.length + emergent.length + urgent.length
  };
};

// Calculate time elapsed and remaining
export const calculateTimeMetrics = (symptomOnsetTime, diagnosisTime = new Date()) => {
  const onset = new Date(symptomOnsetTime);
  const now = new Date(diagnosisTime);
  const elapsedMs = now - onset;
  const elapsedHours = elapsedMs / (1000 * 60 * 60);
  
  return {
    elapsedMs,
    elapsedHours: elapsedHours.toFixed(1),
    elapsedDisplay: formatElapsedTime(elapsedHours)
  };
};

// Format elapsed time
const formatElapsedTime = (hours) => {
  if (hours < 1) {
    return `${Math.round(hours * 60)} minutes`;
  } else if (hours < 24) {
    return `${hours.toFixed(1)} hours`;
  } else {
    const days = Math.floor(hours / 24);
    const remainingHours = Math.round(hours % 24);
    return `${days} days ${remainingHours} hours`;
  }
};

// Check if time window exceeded
export const isTimeWindowExceeded = (condition, elapsedHours) => {
  if (!condition.timeToTreatment) return false;
  
  // Parse time window
  const timeStr = condition.timeToTreatment;
  let windowHours = 0;
  
  if (timeStr.includes('minutes')) {
    windowHours = parseFloat(timeStr) / 60;
  } else if (timeStr.includes('hour')) {
    windowHours = parseFloat(timeStr);
  } else if (timeStr.includes('day')) {
    windowHours = parseFloat(timeStr) * 24;
  }
  
  return elapsedHours > windowHours;
};

// Generate treatment timeline
export const generateTimeline = (condition) => {
  if (!condition.milestones) return null;
  
  return {
    condition: condition.keywords[0],
    urgency: condition.urgency.label,
    milestones: condition.milestones,
    totalTimeWindow: condition.timeToTreatment
  };
};

// Get urgency badge styling
export const getUrgencyBadge = (urgencyLevel) => {
  const level = urgencyLevel.level || urgencyLevel;
  const urgency = Object.values(urgencyLevels).find(u => u.level === level) || urgencyLevels.NON_URGENT;
  
  return {
    ...urgency,
    styles: {
      backgroundColor: urgency.bgColor,
      color: urgency.color,
      borderColor: urgency.color,
      borderWidth: '2px',
      borderStyle: 'solid',
      padding: '8px 16px',
      borderRadius: '8px',
      fontWeight: 'bold'
    }
  };
};

// Priority score for sorting (lower = higher priority)
export const getUrgencyPriority = (urgencyLevel) => {
  const priorities = {
    'immediate': 1,
    'emergent': 2,
    'urgent': 3,
    'semi-urgent': 4,
    'non-urgent': 5
  };
  return priorities[urgencyLevel] || 5;
};

export default {
  urgencyLevels,
  timeSensitiveConditions,
  assessUrgency,
  generateUrgencyReport,
  calculateTimeMetrics,
  isTimeWindowExceeded,
  generateTimeline,
  getUrgencyBadge,
  getUrgencyPriority
};
