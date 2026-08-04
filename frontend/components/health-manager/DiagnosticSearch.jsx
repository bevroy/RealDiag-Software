'use client';

import { useState } from 'react';
import { authenticatedFetch } from '../../utils/auth';

export default function DiagnosticSearch({ patientData, onDiagnosisComplete }) {
  const [symptoms, setSymptoms] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [diagnosticResults, setDiagnosticResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchMode, setSearchMode] = useState('simple'); // 'simple' or 'advanced'

  const commonSymptoms = [
    'Headache', 'Fever', 'Cough', 'Fatigue', 'Nausea',
    'Dizziness', 'Chest Pain', 'Shortness of Breath',
    'Abdominal Pain', 'Back Pain', 'Joint Pain', 'Rash'
  ];

  const handleSymptomToggle = (symptom) => {
    if (selectedSymptoms.includes(symptom)) {
      setSelectedSymptoms(selectedSymptoms.filter(s => s !== symptom));
    } else {
      setSelectedSymptoms([...selectedSymptoms, symptom]);
    }
  };

  const handleSearch = async () => {
    if (selectedSymptoms.length === 0 && !searchQuery) {
      alert('Please select symptoms or enter a search query');
      return;
    }

    setLoading(true);
    try {
      const response = await authenticatedFetch('/api/diagnostic/search', {
        method: 'POST',
        body: JSON.stringify({
          symptoms: selectedSymptoms,
          query: searchQuery,
          patientContext: {
            age: patientData?.ehrData?.age,
            sex: patientData?.ehrData?.sex,
            medications: patientData?.ehrData?.medications,
            allergies: patientData?.ehrData?.allergies,
            vitals: patientData?.wearableData
          }
        })
      });

      if (response.ok) {
        const results = await response.json();
        setDiagnosticResults(results);
        
        // Save to history
        if (onDiagnosisComplete) {
          onDiagnosisComplete({
            timestamp: new Date().toISOString(),
            symptoms: selectedSymptoms,
            results: results
          });
        }
      } else {
        alert('Failed to perform diagnostic search');
      }
    } catch (error) {
      console.error('Diagnostic search error:', error);
      alert('An error occurred during the search');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSelectedSymptoms([]);
    setSearchQuery('');
    setDiagnosticResults(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Diagnostic Search</h2>
          <div className="flex space-x-2">
            <button
              onClick={() => setSearchMode('simple')}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                searchMode === 'simple'
                  ? 'bg-teal-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Simple
            </button>
            <button
              onClick={() => setSearchMode('advanced')}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                searchMode === 'advanced'
                  ? 'bg-teal-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Advanced
            </button>
          </div>
        </div>
        <p className="text-gray-600">
          Select symptoms or describe your condition to find possible diagnoses using the same diagnostic engine as healthcare providers.
        </p>
      </div>

      {/* Search Interface */}
      <div className="bg-white rounded-lg shadow-md p-6">
        {searchMode === 'simple' ? (
          <>
            {/* Quick Symptom Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Common Symptoms
              </label>
              <div className="flex flex-wrap gap-2">
                {commonSymptoms.map((symptom) => (
                  <button
                    key={symptom}
                    onClick={() => handleSymptomToggle(symptom)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                      selectedSymptoms.includes(symptom)
                        ? 'bg-teal-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {symptom}
                    {selectedSymptoms.includes(symptom) && (
                      <span className="ml-2">✓</span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Symptom Input */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Or describe your symptoms
              </label>
              <textarea
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="e.g., I have a severe headache with nausea and sensitivity to light..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                rows="4"
              />
            </div>
          </>
        ) : (
          <>
            {/* Advanced Search with Context */}
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Chief Complaint
                </label>
                <input
                  type="text"
                  placeholder="Main reason for visit"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Duration
                  </label>
                  <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500">
                    <option>Less than 1 day</option>
                    <option>1-3 days</option>
                    <option>3-7 days</option>
                    <option>1-2 weeks</option>
                    <option>More than 2 weeks</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Severity
                  </label>
                  <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500">
                    <option>Mild</option>
                    <option>Moderate</option>
                    <option>Severe</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Associated Symptoms
                </label>
                <textarea
                  placeholder="Any additional symptoms..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
                  rows="3"
                />
              </div>
            </div>
          </>
        )}

        {/* Selected Symptoms Display */}
        {selectedSymptoms.length > 0 && (
          <div className="mb-6 p-4 bg-teal-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-teal-800">
                Selected Symptoms ({selectedSymptoms.length})
              </span>
              <button
                onClick={() => setSelectedSymptoms([])}
                className="text-sm text-teal-600 hover:text-teal-700"
              >
                Clear all
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {selectedSymptoms.map((symptom) => (
                <span
                  key={symptom}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-teal-100 text-teal-800"
                >
                  {symptom}
                  <button
                    onClick={() => handleSymptomToggle(symptom)}
                    className="ml-2 hover:text-teal-900"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-4">
          <button
            onClick={handleSearch}
            disabled={loading || (selectedSymptoms.length === 0 && !searchQuery)}
            className="flex-1 bg-teal-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-teal-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Searching...
              </span>
            ) : (
              '🔍 Search Diagnoses'
            )}
          </button>
          <button
            onClick={handleClear}
            className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Clear
          </button>
        </div>
      </div>

      {/* Diagnostic Results */}
      {diagnosticResults && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Possible Diagnoses</h3>
          
          {diagnosticResults.diagnoses?.length > 0 ? (
            <div className="space-y-4">
              {diagnosticResults.diagnoses.map((diagnosis, index) => (
                <div
                  key={index}
                  className="border border-gray-200 rounded-lg p-4 hover:border-teal-500 transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h4 className="text-lg font-semibold text-gray-900">{diagnosis.name}</h4>
                      <p className="text-sm text-gray-500 mt-1">{diagnosis.description}</p>
                    </div>
                    <div className="ml-4">
                      <div className="flex items-center">
                        <span className="text-2xl font-bold text-teal-600">
                          {diagnosis.confidence}%
                        </span>
                        <span className="text-sm text-gray-500 ml-2">match</span>
                      </div>
                    </div>
                  </div>

                  {/* Matching Symptoms */}
                  {diagnosis.matchingSymptoms && (
                    <div className="mt-3">
                      <span className="text-sm font-medium text-gray-700">Matching symptoms: </span>
                      <span className="text-sm text-gray-600">
                        {diagnosis.matchingSymptoms.join(', ')}
                      </span>
                    </div>
                  )}

                  {/* Recommended Tests */}
                  {diagnosis.recommendedTests && (
                    <div className="mt-3">
                      <span className="text-sm font-medium text-gray-700">Recommended tests: </span>
                      <span className="text-sm text-gray-600">
                        {diagnosis.recommendedTests.join(', ')}
                      </span>
                    </div>
                  )}

                  {/* View Details Button */}
                  <button className="mt-4 text-teal-600 hover:text-teal-700 text-sm font-medium">
                    View full details →
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              No matching diagnoses found. Try adjusting your symptoms or search query.
            </p>
          )}

          {/* Disclaimer */}
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              <strong>⚠️ Important:</strong> These results are for informational purposes only and should not replace professional medical advice. Please consult with a healthcare provider for accurate diagnosis and treatment.
            </p>
          </div>
        </div>
      )}

      {/* Patient Context Card */}
      {patientData && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Health Context</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {patientData.ehrData?.age && (
              <div className="flex items-center text-sm">
                <span className="text-gray-600 mr-2">Age:</span>
                <span className="font-medium">{patientData.ehrData.age}</span>
              </div>
            )}
            {patientData.ehrData?.sex && (
              <div className="flex items-center text-sm">
                <span className="text-gray-600 mr-2">Sex:</span>
                <span className="font-medium">{patientData.ehrData.sex}</span>
              </div>
            )}
            {patientData.wearableData?.heartRate && (
              <div className="flex items-center text-sm">
                <span className="text-gray-600 mr-2">Heart Rate:</span>
                <span className="font-medium">{patientData.wearableData.heartRate} bpm</span>
              </div>
            )}
            {patientData.ehrData?.medications?.length > 0 && (
              <div className="flex items-center text-sm">
                <span className="text-gray-600 mr-2">Medications:</span>
                <span className="font-medium">{patientData.ehrData.medications.length} active</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
