/**
 * Differential Diagnosis Comparison Tool
 * Side-by-side comparison of test characteristics for competing diagnoses
 */

// Calculate likelihood ratios
export const calculateLikelihoodRatios = (sensitivity, specificity) => {
  const sens = sensitivity / 100;
  const spec = specificity / 100;
  
  const lrPositive = sens / (1 - spec);
  const lrNegative = (1 - sens) / spec;
  
  return {
    lrPositive: lrPositive.toFixed(2),
    lrNegative: lrNegative.toFixed(2)
  };
};

// Interpret likelihood ratio
export const interpretLR = (lr) => {
  const value = parseFloat(lr);
  
  if (value > 10) return { strength: 'Large', effect: 'Significantly increases probability', color: '#10b981' };
  if (value > 5) return { strength: 'Moderate', effect: 'Moderately increases probability', color: '#6ee7b7' };
  if (value > 2) return { strength: 'Small', effect: 'Slightly increases probability', color: '#a7f3d0' };
  if (value > 1) return { strength: 'Minimal', effect: 'Minimal change', color: '#d1fae5' };
  if (value === 1) return { strength: 'None', effect: 'No change in probability', color: '#e5e7eb' };
  if (value > 0.5) return { strength: 'Minimal', effect: 'Minimal change', color: '#fce7f3' };
  if (value > 0.2) return { strength: 'Small', effect: 'Slightly decreases probability', color: '#fbcfe8' };
  if (value > 0.1) return { strength: 'Moderate', effect: 'Moderately decreases probability', color: '#f9a8d4' };
  return { strength: 'Large', effect: 'Significantly decreases probability', color: '#f472b6' };
};

// Calculate post-test probability using Bayesian approach
export const calculatePostTestProbability = (pretestProb, likelihoodRatio) => {
  const pretest = pretestProb / 100;
  const pretestOdds = pretest / (1 - pretest);
  const posttestOdds = pretestOdds * likelihoodRatio;
  const posttestProb = posttestOdds / (1 + posttestOdds);
  
  return (posttestProb * 100).toFixed(1);
};

// Compare diagnostic tests for a single condition
export const compareTests = (diagnosis, tests) => {
  const comparisons = tests.map(test => {
    const { lrPositive, lrNegative } = calculateLikelihoodRatios(test.sensitivity, test.specificity);
    
    return {
      ...test,
      lrPositive,
      lrNegative,
      lrPosInterpretation: interpretLR(lrPositive),
      lrNegInterpretation: interpretLR(lrNegative),
      accuracy: ((test.sensitivity + test.specificity) / 2).toFixed(1),
      youdensIndex: ((test.sensitivity + test.specificity - 100) / 100).toFixed(2)
    };
  });
  
  return {
    diagnosis,
    tests: comparisons,
    bestSensitivity: comparisons.reduce((max, t) => t.sensitivity > max.sensitivity ? t : max),
    bestSpecificity: comparisons.reduce((max, t) => t.specificity > max.specificity ? t : max),
    bestAccuracy: comparisons.reduce((max, t) => parseFloat(t.accuracy) > parseFloat(max.accuracy) ? t : max)
  };
};

// Compare multiple diagnoses for the same clinical presentation
export const compareDifferentialDiagnoses = (diagnoses) => {
  // Calculate comparison metrics
  const comparison = diagnoses.map(dx => {
    let avgSensitivity = 0;
    let avgSpecificity = 0;
    let testCount = 0;
    
    if (dx.diagnostic_tests && dx.diagnostic_tests.length > 0) {
      dx.diagnostic_tests.forEach(test => {
        if (test.sensitivity && test.specificity) {
          avgSensitivity += test.sensitivity;
          avgSpecificity += test.specificity;
          testCount++;
        }
      });
      
      if (testCount > 0) {
        avgSensitivity /= testCount;
        avgSpecificity /= testCount;
      }
    }
    
    // Calculate overall diagnostic difficulty score
    const diagnosticDifficulty = calculateDiagnosticDifficulty(dx);
    
    return {
      ...dx,
      avgSensitivity: avgSensitivity.toFixed(1),
      avgSpecificity: avgSpecificity.toFixed(1),
      diagnosticDifficulty,
      hasGoldStandard: dx.diagnostic_tests?.some(t => t.sensitivity > 95 && t.specificity > 95)
    };
  });
  
  return {
    diagnoses: comparison,
    easiestToDiagnose: comparison.reduce((min, dx) => 
      dx.diagnosticDifficulty < min.diagnosticDifficulty ? dx : min
    ),
    hardestToDiagnose: comparison.reduce((max, dx) => 
      dx.diagnosticDifficulty > max.diagnosticDifficulty ? dx : max
    )
  };
};

// Calculate diagnostic difficulty score (higher = harder to diagnose)
const calculateDiagnosticDifficulty = (diagnosis) => {
  let score = 0;
  
  // Factor 1: Test availability
  const testCount = diagnosis.diagnostic_tests?.length || 0;
  if (testCount === 0) score += 50;
  else if (testCount < 3) score += 30;
  else score += 10;
  
  // Factor 2: Test accuracy
  let hasHighAccuracyTest = false;
  if (diagnosis.diagnostic_tests) {
    diagnosis.diagnostic_tests.forEach(test => {
      if (test.sensitivity > 90 && test.specificity > 90) {
        hasHighAccuracyTest = true;
      }
    });
  }
  if (!hasHighAccuracyTest) score += 30;
  
  // Factor 3: Clinical presentation clarity
  const symptomCount = diagnosis.symptoms?.length || 0;
  if (symptomCount < 3) score += 20;
  
  return score;
};

// Generate comparison table data
export const generateComparisonTable = (diagnoses) => {
  const features = [];
  const featureMap = new Map();
  
  // Collect all unique clinical features
  diagnoses.forEach(dx => {
    // Add symptoms
    dx.symptoms?.forEach(symptom => {
      if (!featureMap.has(symptom)) {
        featureMap.set(symptom, { type: 'symptom', values: {} });
      }
      featureMap.get(symptom).values[dx.diagnosis] = 'present';
    });
    
    // Add physical exam findings
    dx.physical_exam?.forEach(finding => {
      if (!featureMap.has(finding)) {
        featureMap.set(finding, { type: 'physical', values: {} });
      }
      featureMap.get(finding).values[dx.diagnosis] = 'present';
    });
    
    // Add tests
    dx.diagnostic_tests?.forEach(test => {
      const key = test.test_name;
      if (!featureMap.has(key)) {
        featureMap.set(key, { type: 'test', values: {} });
      }
      featureMap.get(key).values[dx.diagnosis] = {
        sensitivity: test.sensitivity,
        specificity: test.specificity,
        finding: test.expected_finding
      };
    });
  });
  
  // Convert to array format
  featureMap.forEach((data, feature) => {
    const row = {
      feature,
      type: data.type,
      ...data.values
    };
    features.push(row);
  });
  
  return {
    features,
    diagnoses: diagnoses.map(dx => dx.diagnosis)
  };
};

// Find distinguishing features between diagnoses
export const findDistinguishingFeatures = (diagnosis1, diagnosis2) => {
  const unique1 = [];
  const unique2 = [];
  const common = [];
  
  // Compare symptoms
  const symptoms1 = new Set(diagnosis1.symptoms || []);
  const symptoms2 = new Set(diagnosis2.symptoms || []);
  
  symptoms1.forEach(s => {
    if (!symptoms2.has(s)) unique1.push({ type: 'symptom', feature: s });
    else common.push({ type: 'symptom', feature: s });
  });
  
  symptoms2.forEach(s => {
    if (!symptoms1.has(s)) unique2.push({ type: 'symptom', feature: s });
  });
  
  // Compare physical exam
  const exam1 = new Set(diagnosis1.physical_exam || []);
  const exam2 = new Set(diagnosis2.physical_exam || []);
  
  exam1.forEach(e => {
    if (!exam2.has(e)) unique1.push({ type: 'physical', feature: e });
    else common.push({ type: 'physical', feature: e });
  });
  
  exam2.forEach(e => {
    if (!exam1.has(e)) unique2.push({ type: 'physical', feature: e });
  });
  
  // Compare test characteristics
  const tests1 = diagnosis1.diagnostic_tests || [];
  const tests2 = diagnosis2.diagnostic_tests || [];
  
  tests1.forEach(test1 => {
    const test2 = tests2.find(t => t.test_name === test1.test_name);
    if (test2) {
      if (test1.expected_finding !== test2.expected_finding) {
        unique1.push({ 
          type: 'test', 
          feature: `${test1.test_name}: ${test1.expected_finding}`,
          test: test1
        });
        unique2.push({ 
          type: 'test', 
          feature: `${test2.test_name}: ${test2.expected_finding}`,
          test: test2
        });
      }
    } else {
      unique1.push({ 
        type: 'test', 
        feature: `${test1.test_name} (specific to this diagnosis)`,
        test: test1
      });
    }
  });
  
  tests2.forEach(test2 => {
    if (!tests1.find(t => t.test_name === test2.test_name)) {
      unique2.push({ 
        type: 'test', 
        feature: `${test2.test_name} (specific to this diagnosis)`,
        test: test2
      });
    }
  });
  
  return {
    diagnosis1: {
      name: diagnosis1.diagnosis,
      uniqueFeatures: unique1,
      featureCount: unique1.length
    },
    diagnosis2: {
      name: diagnosis2.diagnosis,
      uniqueFeatures: unique2,
      featureCount: unique2.length
    },
    commonFeatures: common,
    discriminatingPower: (unique1.length + unique2.length) / (unique1.length + unique2.length + common.length)
  };
};

// Calculate confidence in diagnosis based on test characteristics
export const calculateDiagnosticConfidence = (diagnosis, availableTests = []) => {
  let confidence = 0;
  let reasoning = [];
  
  const diagnosticTests = diagnosis.diagnostic_tests || [];
  
  // Check if gold standard test is available
  const goldStandard = diagnosticTests.find(t => t.sensitivity >= 95 && t.specificity >= 95);
  if (goldStandard && availableTests.includes(goldStandard.test_name)) {
    confidence = 95;
    reasoning.push(`Gold standard test (${goldStandard.test_name}) available with ${goldStandard.sensitivity}% sensitivity`);
  }
  
  // Check for highly specific tests
  const highlySpecific = diagnosticTests.filter(t => t.specificity >= 90);
  if (highlySpecific.length > 0 && highlySpecific.some(t => availableTests.includes(t.test_name))) {
    confidence = Math.max(confidence, 85);
    reasoning.push(`Highly specific test available (>90% specificity)`);
  }
  
  // Check for sensitive tests
  const highlySensitive = diagnosticTests.filter(t => t.sensitivity >= 90);
  if (highlySensitive.length > 0 && highlySensitive.some(t => availableTests.includes(t.test_name))) {
    confidence = Math.max(confidence, 80);
    reasoning.push(`Highly sensitive test available (>90% sensitivity)`);
  }
  
  // Factor in number of confirming tests
  const availableDiagnosticTests = diagnosticTests.filter(t => availableTests.includes(t.test_name));
  if (availableDiagnosticTests.length > 2) {
    confidence += 10;
    reasoning.push(`Multiple confirmatory tests available (${availableDiagnosticTests.length})`);
  }
  
  // Cap at 99%
  confidence = Math.min(confidence, 99);
  
  if (confidence === 0) {
    confidence = 50;
    reasoning.push('Clinical diagnosis based on presentation');
  }
  
  return {
    confidence,
    reasoning,
    level: confidence >= 90 ? 'Very High' : confidence >= 75 ? 'High' : confidence >= 60 ? 'Moderate' : 'Low'
  };
};

export default {
  calculateLikelihoodRatios,
  interpretLR,
  calculatePostTestProbability,
  compareTests,
  compareDifferentialDiagnoses,
  generateComparisonTable,
  findDistinguishingFeatures,
  calculateDiagnosticConfidence
};
