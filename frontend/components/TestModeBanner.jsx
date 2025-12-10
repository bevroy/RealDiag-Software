"use client";

import { useState, useEffect } from 'react';
import { AlertTriangle, TestTube, CheckCircle } from 'lucide-react';

/**
 * Test Mode Banner Component
 * 
 * Displays a prominent banner when the application is running in test mode.
 * Shows test environment status and unlimited access information.
 */
export default function TestModeBanner() {
  const [testMode, setTestMode] = useState(false);
  const [healthData, setHealthData] = useState(null);
  const [showBanner, setShowBanner] = useState(true);

  useEffect(() => {
    // Check if we're in test environment
    const envMode = process.env.NEXT_PUBLIC_ENVIRONMENT;
    const isTest = envMode === 'test';
    setTestMode(isTest);

    // Fetch health endpoint to confirm test mode
    if (isTest) {
      fetchHealthStatus();
    }
  }, []);

  const fetchHealthStatus = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/health`);
      const data = await response.json();
      setHealthData(data);
    } catch (error) {
      console.error('Failed to fetch health status:', error);
    }
  };

  if (!testMode || !showBanner) {
    return null;
  }

  return (
    <div className="bg-gradient-to-r from-yellow-400 via-amber-500 to-yellow-600 border-b-4 border-yellow-700 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex items-center justify-between flex-wrap">
          <div className="flex items-center flex-1">
            <div className="flex items-center">
              <TestTube className="h-6 w-6 text-white mr-3 animate-pulse" />
              <div className="ml-2">
                <h3 className="text-white font-bold text-lg flex items-center">
                  🧪 TEST ENVIRONMENT
                  <span className="ml-2 px-2 py-1 bg-white/20 rounded text-sm">
                    Beta Testing
                  </span>
                </h3>
                <p className="text-white/90 text-sm mt-1">
                  <CheckCircle className="inline h-4 w-4 mr-1" />
                  All features unlocked • Unlimited access • No payment required
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 mt-2 sm:mt-0">
            {healthData?.test_mode && (
              <div className="bg-white/20 px-3 py-1 rounded-lg backdrop-blur-sm">
                <span className="text-white text-xs font-semibold">
                  Status: {healthData.test_info?.subscription_checks === 'bypassed' ? '✓ Active' : 'Unknown'}
                </span>
              </div>
            )}
            
            <button
              onClick={() => setShowBanner(false)}
              className="text-white hover:text-yellow-100 transition-colors"
              aria-label="Dismiss banner"
            >
              <svg className="h-5 w-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>
        
        {/* Additional info row */}
        <div className="mt-2 flex items-center space-x-4 text-xs text-white/80">
          <span>🔓 Subscription checks: bypassed</span>
          <span>⚡ Rate limits: disabled</span>
          <span>💳 Payment: not required</span>
          {healthData?.environment && (
            <span className="ml-auto font-mono bg-white/10 px-2 py-1 rounded">
              ENV: {healthData.environment}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
