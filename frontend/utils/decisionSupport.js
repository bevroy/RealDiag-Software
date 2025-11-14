/**
 * Task 3.3: Advanced Decision Support Functions
 * Bayesian Likelihood & Confidence Calculations
 */

/**
 * Calculate Bayesian likelihood score for a diagnostic result
 * @param {Object} result - Result object with sensitivity, specificity, match_score
 * @returns {number|null} - Likelihood percentage (0-99) or null if insufficient data
 */
export const calculateLikelihood = (result) => {
  if (!result || !result.sensitivity || !result.specificity) return null;
  
  // Normalize match score to 0-1 range
  const matchRatio = result.match_score / 10;
  
  const sensitivity = result.sensitivity;
  const specificity = result.specificity;
  
  // Positive likelihood ratio: sensitivity / (1 - specificity)
  // Add small epsilon to avoid division by zero
  const likelihoodRatio = sensitivity / (1 - specificity + 0.001);
  
  // Base probability (prevalence assumption)
  // In clinical practice, this would be disease-specific
  const baseProbability = 0.1;
  
  // Bayesian posterior probability calculation
  // P(Disease|Test+) = (LR+ * P(Disease)) / ((LR+ * P(Disease)) + P(~Disease))
  const numerator = likelihoodRatio * baseProbability * matchRatio;
  const denominator = numerator + (1 - baseProbability);
  const posterior = numerator / denominator;
  
  // Return as percentage, capped at 99%
  return Math.min(posterior * 100, 99);
};

/**
 * Get confidence level text based on likelihood score
 * @param {number} likelihood - Likelihood percentage
 * @returns {string} - Confidence level description
 */
export const getConfidenceLevel = (likelihood) => {
  if (likelihood == null || isNaN(likelihood)) return 'Unknown';
  if (likelihood >= 80) return 'Very High';
  if (likelihood >= 60) return 'High';
  if (likelihood >= 40) return 'Moderate';
  if (likelihood >= 20) return 'Low';
  return 'Very Low';
};

/**
 * Get confidence color based on likelihood score
 * @param {number} likelihood - Likelihood percentage
 * @returns {string} - Hex color code
 */
export const getConfidenceColor = (likelihood) => {
  if (likelihood == null || isNaN(likelihood)) return '#9ca3af'; // Gray
  if (likelihood >= 80) return '#10b981'; // Green
  if (likelihood >= 60) return '#34d399'; // Light green
  if (likelihood >= 40) return '#fbbf24'; // Amber
  if (likelihood >= 20) return '#fb923c'; // Orange
  return '#ef4444'; // Red
};

/**
 * Calculate impact of removing a finding on likelihood
 * @param {number} currentLikelihood - Current likelihood percentage
 * @param {number} numberOfFindings - Total number of matched findings
 * @param {number} findingsToRemove - Number of findings being removed
 * @returns {number} - Estimated likelihood decrease percentage
 */
export const calculateWhatIfImpact = (currentLikelihood, numberOfFindings, findingsToRemove) => {
  if (!currentLikelihood || numberOfFindings === 0) return 0;
  
  // Simplified impact model: each finding contributes proportionally
  const impactPerFinding = currentLikelihood / numberOfFindings;
  const totalImpact = impactPerFinding * findingsToRemove;
  
  // Return decrease percentage, capped at current likelihood
  return Math.min(totalImpact, currentLikelihood);
};

/**
 * Generate decision trace explanation
 * @param {Object} result - Diagnostic result object
 * @param {number} likelihood - Calculated likelihood
 * @returns {Array<string>} - Step-by-step reasoning trace
 */
export const generateDecisionTrace = (result, likelihood) => {
  const trace = [];
  
  if (!result) return trace;
  
  trace.push(`Initial match score: ${result.match_score.toFixed(1)}/10`);
  
  if (result.matched_presentations && result.matched_presentations.length > 0) {
    trace.push(`Matched ${result.matched_presentations.length} clinical presentation(s)`);
    result.matched_presentations.forEach((p, i) => {
      trace.push(`  ${i + 1}. ${p}`);
    });
  }
  
  if (result.sensitivity && result.specificity) {
    trace.push(`Test characteristics: Sensitivity ${(result.sensitivity * 100).toFixed(0)}%, Specificity ${(result.specificity * 100).toFixed(0)}%`);
    
    const likelihoodRatio = result.sensitivity / (1 - result.specificity + 0.001);
    trace.push(`Positive likelihood ratio: ${likelihoodRatio.toFixed(2)}`);
  }
  
  if (likelihood != null) {
    trace.push(`Calculated probability: ${likelihood.toFixed(1)}% (${getConfidenceLevel(likelihood)} confidence)`);
  }
  
  if (result.clinical_pearls && result.clinical_pearls.length > 0) {
    trace.push(`Clinical pearls support diagnosis`);
  }
  
  return trace;
};

/**
 * Compare two diagnostic results and rank them
 * @param {Object} result1 - First diagnostic result
 * @param {Object} result2 - Second diagnostic result
 * @returns {number} - Comparison value for sorting
 */
export const compareByLikelihood = (result1, result2) => {
  const likelihood1 = calculateLikelihood(result1) || result1.match_score;
  const likelihood2 = calculateLikelihood(result2) || result2.match_score;
  return likelihood2 - likelihood1; // Descending order
};

export default {
  calculateLikelihood,
  getConfidenceLevel,
  getConfidenceColor,
  calculateWhatIfImpact,
  generateDecisionTrace,
  compareByLikelihood
};
