import React, { useState, useEffect } from 'react';
import Head from 'next/head';

export default function EducationPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [quizQuestions, setQuizQuestions] = useState([]);
  const [quizActive, setQuizActive] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [quizResults, setQuizResults] = useState([]);
  const [showExplanation, setShowExplanation] = useState(false);
  const [flashcards, setFlashcards] = useState([]);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showCardBack, setShowCardBack] = useState(false);
  const [progress, setProgress] = useState(null);
  const [learningObjectives, setLearningObjectives] = useState([]);
  const [filters, setFilters] = useState({
    specialty: '',
    difficulty: '',
    yearLevel: ''
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [studyStreak, setStudyStreak] = useState(0);
  const [achievements, setAchievements] = useState([]);
  const [weakAreas, setWeakAreas] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [studyPlan, setStudyPlan] = useState(null);
  const [expandedCaseId, setExpandedCaseId] = useState(null);
  const [availableSpecialties, setAvailableSpecialties] = useState([]);

  // Use runtime config for API base, with fallback to env var or Render URL
  const runtimeConfig = (typeof window !== 'undefined' && window.__RUNTIME_CONFIG) ? window.__RUNTIME_CONFIG : null;
  const API_BASE = runtimeConfig?.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com';
  const userId = 'student_001';

  const loadCases = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.specialty) params.append('specialty', filters.specialty);
      if (filters.difficulty) params.append('difficulty', filters.difficulty);
      
      const response = await fetch(`${API_BASE}/education/cases?${params}`);
      const data = await response.json();
      setCases(data);
    } catch (error) {
      console.error('Error loading cases:', error);
    }
    setLoading(false);
  };

  const loadAvailableSpecialties = async () => {
    try {
      // Load all cases without filters to get unique specialties
      const response = await fetch(`${API_BASE}/education/cases`);
      const allCases = await response.json();
      
      // Extract unique specialties and sort them
      const specialties = [...new Set(allCases.map(c => c.specialty))].sort();
      setAvailableSpecialties(specialties);
    } catch (error) {
      console.error('Error loading specialties:', error);
    }
  };

  const searchCases = async () => {
    if (!searchQuery.trim()) {
      loadCases();
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/education/cases/search/${encodeURIComponent(searchQuery)}`);
      const data = await response.json();
      setCases(data.results);
    } catch (error) {
      console.error('Error searching cases:', error);
    }
    setLoading(false);
  };

  const startQuiz = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ count: '10' });
      if (filters.difficulty) params.append('difficulty', filters.difficulty);
      
      const response = await fetch(`${API_BASE}/education/quiz/questions?${params}`);
      const data = await response.json();
      setQuizQuestions(data.questions);
      setQuizActive(true);
      setCurrentQuestionIndex(0);
      setQuizResults([]);
      setSelectedAnswer(null);
      setShowExplanation(false);
    } catch (error) {
      console.error('Error loading quiz:', error);
    }
    setLoading(false);
  };

  const submitQuizAnswer = async () => {
    if (!selectedAnswer) return;
    
    const startTime = Date.now();
    const question = quizQuestions[currentQuestionIndex];
    
    try {
      const response = await fetch(`${API_BASE}/education/quiz/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          attempt_id: `attempt_${Date.now()}`,
          user_id: userId,
          question_id: question.question_id,
          selected_answers: [selectedAnswer],
          correct: false,
          time_taken: Math.floor((Date.now() - startTime) / 1000),
          timestamp: new Date().toISOString()
        })
      });
      
      const result = await response.json();
      setQuizResults([...quizResults, result]);
      setShowExplanation(true);
    } catch (error) {
      console.error('Error submitting answer:', error);
    }
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < quizQuestions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setSelectedAnswer(null);
      setShowExplanation(false);
    } else {
      setQuizActive(false);
      loadProgress();
    }
  };

  const loadFlashcards = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/education/flashcards/due?user_id=${userId}&limit=20`);
      const data = await response.json();
      setFlashcards(data.flashcards);
      setCurrentCardIndex(0);
      setShowCardBack(false);
    } catch (error) {
      console.error('Error loading flashcards:', error);
    }
    setLoading(false);
  };

  const reviewFlashcard = async (quality) => {
    const card = flashcards[currentCardIndex];
    
    try {
      await fetch(`${API_BASE}/education/flashcards/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          card_id: card.card_id,
          quality: quality,
          timestamp: new Date().toISOString()
        })
      });
      
      if (currentCardIndex < flashcards.length - 1) {
        setCurrentCardIndex(currentCardIndex + 1);
        setShowCardBack(false);
      } else {
        loadFlashcards();
      }
    } catch (error) {
      console.error('Error reviewing flashcard:', error);
    }
  };

  const loadProgress = async () => {
    try {
      const response = await fetch(`${API_BASE}/education/progress/${userId}`);
      const data = await response.json();
      setProgress(data);
    } catch (error) {
      console.error('Error loading progress:', error);
    }
  };

  const loadLearningObjectives = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.specialty) params.append('specialty', filters.specialty);
      if (filters.yearLevel) params.append('year_level', filters.yearLevel);
      
      const response = await fetch(`${API_BASE}/education/learning-objectives?${params}`);
      const data = await response.json();
      setLearningObjectives(data.objectives);
    } catch (error) {
      console.error('Error loading objectives:', error);
    }
    setLoading(false);
  };

  const loadStudyAnalytics = async () => {
    try {
      // Simulate analytics data (in production, fetch from API)
      setStudyStreak(7);
      setAchievements([
        { id: 1, title: 'Week Warrior', description: '7 days study streak', icon: '🔥', earned: true },
        { id: 2, title: 'Quiz Master', description: '50 quiz questions answered', icon: '🎯', earned: true },
        { id: 3, title: 'Case Closer', description: 'Completed 10 cases', icon: '📋', earned: false },
        { id: 4, title: 'Perfect Score', description: '100% on a quiz', icon: '💯', earned: false }
      ]);
      setWeakAreas([
        { specialty: 'Cardiology', accuracy: 65, questionsAttempted: 20 },
        { specialty: 'Neurology', accuracy: 72, questionsAttempted: 18 },
        { specialty: 'Emergency', accuracy: 88, questionsAttempted: 25 }
      ]);
      setRecentActivity([
        { type: 'quiz', title: 'Completed Cardiology Quiz', score: 85, time: '2 hours ago' },
        { type: 'case', title: 'Reviewed Acute MI Case', specialty: 'Cardiology', time: '5 hours ago' },
        { type: 'flashcards', title: 'Studied 15 Flashcards', time: '1 day ago' }
      ]);
      setStudyPlan({
        todayGoal: 'Complete 2 cases and 10 flashcards',
        weeklyGoal: 'Study 5 days, complete 3 quizzes',
        recommendedTopics: ['Acute Coronary Syndrome', 'Stroke Recognition', 'Sepsis Management']
      });
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  useEffect(() => {
    loadCases();
    loadProgress();
    loadStudyAnalytics();
    loadAvailableSpecialties();
  }, []);

  useEffect(() => {
    if (activeTab === 'cases') loadCases();
    if (activeTab === 'flashcards') loadFlashcards();
    if (activeTab === 'objectives') loadLearningObjectives();
  }, [activeTab, filters]);

  return (
    <>
      <Head>
        <title>Medical Training Center - RealDiag</title>
      </Head>
      
      <style jsx>{`
        body {
          background: linear-gradient(135deg, #f0fdfa 0%, #e7f5f3 100%);
          min-height: 100vh;
        }

        .education-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }

        .nav-dropdown {
          margin-bottom: 1rem;
        }

        .nav-dropdown details {
          background: white;
          padding: 0.75rem 1.25rem;
          border-radius: 10px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          border: 1px solid #e2e8f0;
          cursor: pointer;
        }

        .nav-dropdown summary {
          color: #0f766e;
          font-size: 1rem;
          font-weight: 600;
          list-style: none;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .nav-links {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
          gap: 0.75rem;
          margin-top: 1rem;
          padding-top: 1rem;
          border-top: 1px solid #e2e8f0;
        }

        .nav-links a {
          padding: 0.75rem;
          background: #f0fdfa;
          border: 1px solid #ccfbf1;
          border-radius: 8px;
          text-decoration: none;
          text-align: center;
          color: #0f766e;
          font-weight: 600;
          font-size: 0.9rem;
        }

        .education-header {
          margin-bottom: 20px;
          padding: 1.5rem;
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 16px;
        }

        .header-content {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .header-content img {
          height: 50px;
        }

        .education-header h1 {
          margin: 0;
          font-size: 1.75em;
          color: #92400e; /* brown */
        }

        .home-button {
          padding: 8px 16px;
          background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);
          color: white;
          text-decoration: none;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 6px;
          white-space: nowrap;
        }

        .education-header p {
          margin: 0;
          opacity: 0.9;
          font-size: 1.1em;
        }

        .education-tabs {
          display: flex;
          gap: 10px;
          margin-bottom: 25px;
          border-bottom: 2px solid #e0e0e0;
          flex-wrap: wrap;
        }

        .education-tabs button {
          padding: 12px 24px;
          border: none;
          background: transparent;
          cursor: pointer;
          font-size: 16px;
          color: #666;
          border-bottom: 3px solid transparent;
          transition: all 0.3s;
        }

        .education-tabs button:hover {
          color: #14b8a6;
          background: #f5f5f5;
        }

        .education-tabs button.tab-active {
          color: #009688; /* teal */
          border-bottom-color: #009688;
          font-weight: 600;
        }

        .education-filters {
          display: flex;
          gap: 15px;
          margin-bottom: 25px;
          flex-wrap: wrap;
        }

        .education-filters select {
          padding: 10px 15px;
          border: 2px solid #e0e0e0;
          border-radius: 8px;
          font-size: 14px;
          cursor: pointer;
        }

        .loading {
          text-align: center;
          padding: 60px;
          font-size: 18px;
          color: #666;
        }

        .badge {
          display: inline-block;
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
          text-transform: uppercase;
        }

        .badge.beginner {
          background: #ccfbf1;
          color: #0f766e;
        }

        .badge.intermediate {
          background: #fef3c7;
          color: #78350f;
        }

        .badge.advanced {
          background: #ccfbf1;
          color: #0d9488;
        }

        .search-bar {
          display: flex;
          gap: 10px;
          margin-bottom: 25px;
        }

        .search-bar input {
          flex: 1;
          padding: 12px 20px;
          border: 2px solid #e0e0e0;
          border-radius: 8px;
          font-size: 16px;
        }

        .search-bar button {
          padding: 12px 30px;
          background: #14b8a6;
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
        }

        .cases-list {
          background: white;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .case-list-item {
          padding: 16px 24px;
          cursor: pointer;
          transition: all 0.2s;
          border-left: 4px solid transparent;
        }

        .case-list-item:not(:last-child) {
          border-bottom: 1px solid #f0f0f0;
        }

        .case-list-item.difficulty-beginner {
          border-left-color: #10b981;
          background: linear-gradient(90deg, rgba(16, 185, 129, 0.05) 0%, white 100%);
        }

        .case-list-item.difficulty-intermediate {
          border-left-color: #f59e0b;
          background: linear-gradient(90deg, rgba(245, 158, 11, 0.05) 0%, white 100%);
        }

        .case-list-item.difficulty-advanced {
          border-left-color: #ef4444;
          background: linear-gradient(90deg, rgba(239, 68, 68, 0.05) 0%, white 100%);
        }

        .case-list-item:hover {
          background: #f8fafc;
          transform: translateX(4px);
        }

        .case-list-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 16px;
        }

        .case-title {
          font-size: 16px;
          font-weight: 500;
          color: #1f2937;
          flex: 1;
        }

        .difficulty-badge {
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .difficulty-badge.beginner {
          background: #d1fae5;
          color: #065f46;
        }

        .difficulty-badge.intermediate {
          background: #fef3c7;
          color: #92400e;
        }

        .difficulty-badge.advanced {
          background: #fee2e2;
          color: #991b1b;
        }

        .case-list-item.expanded {
          background: white !important;
        }

        .case-details {
          padding: 24px;
          margin-top: 16px;
          background: #fafafa;
          border-radius: 8px;
          border-top: 2px solid #e5e7eb;
        }

        .case-section {
          margin-bottom: 20px;
        }

        .case-section h4 {
          color: #14b8a6;
          font-size: 16px;
          font-weight: 600;
          margin-bottom: 10px;
          border-bottom: 2px solid #14b8a6;
          padding-bottom: 4px;
        }

        .case-section p {
          color: #374151;
          line-height: 1.6;
          margin: 8px 0;
        }

        .case-section ul {
          margin: 8px 0;
          padding-left: 20px;
        }

        .case-section li {
          color: #374151;
          line-height: 1.8;
          margin: 6px 0;
        }

        .history-item, .exam-item, .lab-item, .imaging-item {
          padding: 8px;
          margin: 4px 0;
          background: white;
          border-radius: 4px;
          font-size: 14px;
          line-height: 1.6;
        }

        .history-item strong, .exam-item strong, .lab-item strong, .imaging-item strong {
          color: #14b8a6;
          display: inline-block;
          min-width: 150px;
          text-transform: capitalize;
        }

        .diagnosis-section {
          background: #f0fdfa;
          padding: 16px;
          border-radius: 8px;
          border-left: 4px solid #14b8a6;
        }

        .diagnosis {
          font-size: 18px;
          font-weight: 600;
          color: #0f766e;
        }

        .tags {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .tag {
          background: #e0f2fe;
          color: #075985;
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
        }

        .no-progress {
          text-align: center;
          padding: 60px;
          background: white;
          border-radius: 12px;
        }

        /* Quiz Styles */
        .quiz-start {
          text-align: center;
          padding: 3rem;
          background: white;
          border-radius: 12px;
          max-width: 600px;
          margin: 0 auto;
        }

        .quiz-start h2 {
          color: #0f766e;
          margin-bottom: 1rem;
        }

        .quiz-start button {
          margin-top: 1.5rem;
          padding: 1rem 2rem;
          background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 1.125rem;
          font-weight: 600;
          cursor: pointer;
          transition: transform 0.2s;
        }

        .quiz-start button:hover:not(:disabled) {
          transform: translateY(-2px);
        }

        .quiz-start button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .quiz-container {
          background: white;
          border-radius: 12px;
          padding: 2rem;
          max-width: 800px;
          margin: 0 auto;
        }

        .quiz-progress {
          background: #f3f4f6;
          padding: 0.75rem;
          border-radius: 8px;
          text-align: center;
          font-weight: 600;
          color: #0f766e;
          margin-bottom: 1.5rem;
        }

        .quiz-options {
          display: flex;
          flex-direction: column;
          gap: 1rem;
          margin: 1.5rem 0;
        }

        .quiz-option {
          padding: 1rem;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .quiz-option:hover {
          border-color: #14b8a6;
          background: #f0fdfa;
        }

        .quiz-option.selected {
          border-color: #14b8a6;
          background: #ccfbf1;
        }

        .explanation {
          background: #fef3c7;
          border-left: 4px solid #f59e0b;
          padding: 1.5rem;
          border-radius: 8px;
          margin: 1.5rem 0;
        }

        .quiz-actions {
          display: flex;
          justify-content: center;
          margin-top: 1.5rem;
        }

        .quiz-actions button {
          padding: 0.75rem 2rem;
          background: #14b8a6;
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
        }

        .quiz-actions button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        /* Flashcard Styles */
        .flashcard-container {
          max-width: 600px;
          margin: 0 auto;
        }

        .flashcard-progress {
          background: #f3f4f6;
          padding: 0.75rem;
          border-radius: 8px;
          text-align: center;
          font-weight: 600;
          color: #0f766e;
          margin-bottom: 1.5rem;
        }

        .flashcard {
          background: white;
          border: 2px solid #14b8a6;
          border-radius: 12px;
          padding: 3rem 2rem;
          min-height: 300px;
          display: flex;
          flex-direction: column;
          justify-content: center;
          cursor: pointer;
          transition: all 0.3s;
        }

        .flashcard:hover {
          box-shadow: 0 8px 24px rgba(20, 184, 166, 0.2);
        }

        .flashcard-front h3,
        .flashcard-back h4 {
          color: #0f766e;
          margin-top: 0;
        }

        .flashcard-meta {
          margin-top: 1rem;
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .flashcard-review {
          margin-top: 1.5rem;
          text-align: center;
        }

        .review-buttons {
          display: flex;
          gap: 0.75rem;
          justify-content: center;
          margin-top: 1rem;
        }

        .review-buttons button {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          transition: transform 0.2s;
        }

        .review-buttons button:hover {
          transform: translateY(-2px);
        }

        .review-again { background: #ef4444; color: white; }
        .review-hard { background: #f59e0b; color: white; }
        .review-good { background: #10b981; color: white; }
        .review-easy { background: #3b82f6; color: white; }

        .no-flashcards {
          text-align: center;
          padding: 3rem;
          background: white;
          border-radius: 12px;
        }

        /* Learning Objectives Styles */
        .objectives-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 1.5rem;
        }

        .objective-card {
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          padding: 1.5rem;
        }

        .objective-header {
          display: flex;
          justify-content: space-between;
          align-items: start;
          margin-bottom: 1rem;
        }

        .objective-header h3 {
          color: #0f766e;
          margin: 0;
          font-size: 1.125rem;
        }

        .objective-header div {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .objective-links {
          margin-top: 1rem;
          padding-top: 1rem;
          border-top: 1px solid #e5e7eb;
          font-size: 0.875rem;
          color: #6b7280;
        }

        .no-objectives {
          text-align: center;
          padding: 3rem;
          background: white;
          border-radius: 12px;
        }

        /* Overview Tab Styles */
        .overview-container {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .welcome-section {
          background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);
          color: white;
          padding: 2rem;
          border-radius: 12px;
          text-align: center;
        }

        .welcome-section h2 {
          margin: 0 0 0.5rem 0;
          font-size: 2rem;
        }

        .welcome-section p {
          margin: 0;
          font-size: 1.1rem;
          opacity: 0.95;
        }

        .stats-dashboard {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1.5rem;
        }

        .stat-card {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          display: flex;
          align-items: center;
          gap: 1rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          transition: transform 0.2s;
        }

        .stat-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .stat-icon {
          font-size: 2.5rem;
        }

        .stat-content h3 {
          margin: 0;
          font-size: 2rem;
          color: #0f766e;
        }

        .stat-content p {
          margin: 0.25rem 0 0 0;
          color: #6b7280;
          font-size: 0.9rem;
        }

        .today-goals {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .today-goals h3 {
          margin: 0 0 1rem 0;
          color: #0f766e;
        }

        .goal-card {
          background: #f0fdfa;
          padding: 1.5rem;
          border-radius: 8px;
          border-left: 4px solid #14b8a6;
        }

        .goal-card p {
          margin: 0.5rem 0;
          color: #374151;
        }

        .progress-bar {
          height: 8px;
          background: #e5e7eb;
          border-radius: 4px;
          overflow: hidden;
          margin: 1rem 0 0.5rem 0;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #14b8a6 0%, #0d9488 100%);
          transition: width 0.3s ease;
        }

        .progress-text {
          font-size: 0.875rem;
          color: #6b7280;
          margin: 0.5rem 0 0 0;
        }

        .achievements-section {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .achievements-section h3 {
          margin: 0 0 1.5rem 0;
          color: #0f766e;
        }

        .achievements-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1rem;
        }

        .achievement-card {
          background: #f9fafb;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          padding: 1.5rem;
          text-align: center;
          transition: all 0.2s;
        }

        .achievement-card.earned {
          background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
          border-color: #f59e0b;
        }

        .achievement-card.locked {
          opacity: 0.6;
          filter: grayscale(1);
        }

        .achievement-icon {
          font-size: 3rem;
          margin-bottom: 0.5rem;
        }

        .achievement-card h4 {
          margin: 0.5rem 0;
          font-size: 1rem;
          color: #374151;
        }

        .achievement-card p {
          margin: 0.25rem 0 0 0;
          font-size: 0.875rem;
          color: #6b7280;
        }

        .locked-badge {
          margin-top: 0.5rem;
          font-size: 0.875rem;
          color: #9ca3af;
        }

        .weak-areas-section {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .weak-areas-section h3 {
          margin: 0 0 1.5rem 0;
          color: #0f766e;
        }

        .weak-areas-list {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1.5rem;
        }

        .weak-area-card {
          background: #fef2f2;
          border: 2px solid #fecaca;
          border-radius: 8px;
          padding: 1.5rem;
        }

        .area-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .area-header h4 {
          margin: 0;
          color: #374151;
        }

        .accuracy-badge {
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.875rem;
          font-weight: 600;
        }

        .study-button {
          margin-top: 1rem;
          padding: 0.5rem 1rem;
          background: #14b8a6;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 600;
          width: 100%;
          transition: background 0.2s;
        }

        .study-button:hover {
          background: #0d9488;
        }

        .recent-activity-section {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .recent-activity-section h3 {
          margin: 0 0 1.5rem 0;
          color: #0f766e;
        }

        .activity-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .activity-item {
          display: flex;
          gap: 1rem;
          padding: 1rem;
          background: #f9fafb;
          border-radius: 8px;
          border-left: 4px solid #14b8a6;
        }

        .activity-icon {
          font-size: 2rem;
        }

        .activity-content h4 {
          margin: 0 0 0.25rem 0;
          color: #374151;
          font-size: 1rem;
        }

        .activity-content p {
          margin: 0.25rem 0 0 0;
          font-size: 0.875rem;
          color: #6b7280;
        }

        .activity-score {
          color: #0f766e;
          font-weight: 600;
        }

        .activity-time {
          font-style: italic;
        }

        .recommended-topics-section {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .recommended-topics-section h3 {
          margin: 0 0 1.5rem 0;
          color: #0f766e;
        }

        .topics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 1rem;
        }

        .topic-card {
          background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
          border: 2px solid #a7f3d0;
          border-radius: 8px;
          padding: 1.5rem;
          text-align: center;
        }

        .topic-card h4 {
          margin: 0 0 1rem 0;
          color: #065f46;
        }

        .start-learning-btn {
          padding: 0.5rem 1.5rem;
          background: #10b981;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 600;
          transition: background 0.2s;
        }

        .start-learning-btn:hover {
          background: #059669;
        }

        /* Study Plan Styles */
        .study-plan-container {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .plan-header {
          background: white;
          border-radius: 12px;
          padding: 2rem;
          text-align: center;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .plan-header h2 {
          margin: 0 0 0.5rem 0;
          color: #0f766e;
        }

        .plan-header p {
          margin: 0;
          color: #6b7280;
        }

        .study-schedule {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .study-schedule h3 {
          margin: 0 0 1.5rem 0;
          color: #0f766e;
        }

        .schedule-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1rem;
        }

        .schedule-day {
          background: #f9fafb;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          padding: 1rem;
        }

        .schedule-day.active {
          background: #ecfdf5;
          border-color: #10b981;
        }

        .schedule-day.weekend {
          background: #fef3c7;
          border-color: #fde68a;
        }

        .day-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.75rem;
          padding-bottom: 0.5rem;
          border-bottom: 1px solid #e5e7eb;
        }

        .day-header strong {
          color: #374151;
        }

        .day-status {
          font-size: 1.25rem;
        }

        .day-status.completed {
          color: #10b981;
        }

        .day-status.active {
          color: #f59e0b;
        }

        .schedule-day ul {
          margin: 0;
          padding-left: 1.5rem;
          font-size: 0.875rem;
          color: #6b7280;
        }

        .schedule-day li {
          margin: 0.25rem 0;
        }

        .focus-areas {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .focus-areas h3 {
          margin: 0 0 1.5rem 0;
          color: #0f766e;
        }

        .focus-cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1.5rem;
        }

        .focus-card {
          border-radius: 8px;
          padding: 1.5rem;
          position: relative;
        }

        .focus-card.high-priority {
          background: #fef2f2;
          border: 2px solid #fca5a5;
        }

        .focus-card.medium-priority {
          background: #fff7ed;
          border: 2px solid #fdba74;
        }

        .focus-card.low-priority {
          background: #f0fdf4;
          border: 2px solid #86efac;
        }

        .priority-badge {
          position: absolute;
          top: 1rem;
          right: 1rem;
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 600;
          background: #dc2626;
          color: white;
        }

        .priority-badge.medium {
          background: #f59e0b;
        }

        .priority-badge.low {
          background: #10b981;
        }

        .focus-card h4 {
          margin: 0 0 0.5rem 0;
          color: #374151;
          padding-right: 6rem;
        }

        .focus-card p {
          margin: 0.5rem 0;
          font-size: 0.875rem;
          color: #6b7280;
        }

        .focus-reason {
          font-style: italic;
          color: #9ca3af;
        }

        .focus-actions {
          display: flex;
          gap: 0.5rem;
          margin-top: 1rem;
        }

        .focus-actions button {
          padding: 0.5rem 1rem;
          background: #14b8a6;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.875rem;
          font-weight: 600;
          transition: background 0.2s;
        }

        .focus-actions button:hover {
          background: #0d9488;
        }

        .study-tips {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .study-tips h3 {
          margin: 0 0 1.5rem 0;
          color: #0f766e;
        }

        .tips-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1rem;
        }

        .tip-card {
          background: #f0fdfa;
          border: 2px solid #99f6e4;
          border-radius: 8px;
          padding: 1.5rem;
          text-align: center;
        }

        .tip-icon {
          font-size: 2.5rem;
          margin-bottom: 0.5rem;
        }

        .tip-card h4 {
          margin: 0.5rem 0;
          color: #0f766e;
        }

        .tip-card p {
          margin: 0.5rem 0 0 0;
          font-size: 0.875rem;
          color: #6b7280;
          line-height: 1.5;
        }

        .learning-path {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .learning-path h3 {
          margin: 0 0 1.5rem 0;
          color: #0f766e;
        }

        .path-timeline {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .path-item {
          display: flex;
          gap: 1rem;
          padding-left: 1rem;
          border-left: 3px solid #e5e7eb;
          position: relative;
        }

        .path-item.completed {
          border-left-color: #10b981;
        }

        .path-item.active {
          border-left-color: #f59e0b;
        }

        .path-marker {
          position: absolute;
          left: -11px;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #10b981;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.75rem;
        }

        .path-marker.active {
          background: #f59e0b;
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }

        .path-content {
          flex: 1;
          padding-bottom: 0.5rem;
        }

        .path-content h4 {
          margin: 0 0 0.25rem 0;
          color: #374151;
        }

        .path-content p {
          margin: 0.25rem 0;
          font-size: 0.875rem;
          color: #6b7280;
        }

        .path-progress {
          height: 6px;
          background: #e5e7eb;
          border-radius: 3px;
          overflow: hidden;
          margin-top: 0.5rem;
        }

        .path-progress-fill {
          height: 100%;
          background: #f59e0b;
          transition: width 0.3s ease;
        }

        .study-resources {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .study-resources h3 {
          margin: 0 0 1.5rem 0;
          color: #0f766e;
        }

        .resources-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .resource-item {
          display: flex;
          gap: 1rem;
          padding: 1.5rem;
          background: #f9fafb;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          transition: all 0.2s;
        }

        .resource-item:hover {
          border-color: #14b8a6;
          transform: translateX(4px);
        }

        .resource-icon {
          font-size: 2rem;
        }

        .resource-content {
          flex: 1;
        }

        .resource-content h4 {
          margin: 0 0 0.25rem 0;
          color: #374151;
        }

        .resource-content p {
          margin: 0.25rem 0 0.75rem 0;
          font-size: 0.875rem;
          color: #6b7280;
        }

        .resource-link {
          color: #14b8a6;
          text-decoration: none;
          font-weight: 600;
          font-size: 0.875rem;
          background: none;
          border: none;
          cursor: pointer;
          padding: 0;
        }

        .resource-link:hover {
          color: #0d9488;
          text-decoration: underline;
        }
      `}</style>

      <div className="education-container">
        {/* Navigation Dropdown */}
        <div className="nav-dropdown">
          <details>
            <summary>
              <span>☰ Navigation</span>
            </summary>
            <div className="nav-links">
              <a href="/">🏠 Home</a>
              <a href="/symptom-search">🔬 Symptom Search</a>
              <a href="/search">🔍 Diagnosis Search</a>
              <a href="/rules">📋 Browse Rules</a>
              <a href="/integration">🔌 API</a>
              <a href="/features-demo">✨ Features</a>
              <a href="/education">📚 Training</a>
              <a href="/sources">📖 Sources</a>
              <a href="/patient-history">📋 Patient History</a>
              <a href="/account">👤 Account</a>
            </div>
          </details>
        </div>

        <header className="education-header">
          <div className="header-content">
            <img src="/logo.png" alt="RealDiag Logo" />
            <h1>Medical Training Center</h1>
          </div>
        </header>

        <div className="education-tabs">
          <button 
            className={activeTab === 'overview' ? 'tab-active' : ''}
            onClick={() => { setActiveTab('overview'); loadStudyAnalytics(); }}
          >
            📊 Overview
          </button>
          <button 
            className={activeTab === 'cases' ? 'tab-active' : ''}
            onClick={() => setActiveTab('cases')}
          >
            📋 Case Library
          </button>
          <button 
            className={activeTab === 'quiz' ? 'tab-active' : ''}
            onClick={() => setActiveTab('quiz')}
          >
            🎯 Quiz Mode
          </button>
          <button 
            className={activeTab === 'flashcards' ? 'tab-active' : ''}
            onClick={() => setActiveTab('flashcards')}
          >
            🗂️ Flashcards
          </button>
          <button 
            className={activeTab === 'progress' ? 'tab-active' : ''}
            onClick={() => { setActiveTab('progress'); loadProgress(); }}
          >
            📈 Progress
          </button>
          <button 
            className={activeTab === 'objectives' ? 'tab-active' : ''}
            onClick={() => setActiveTab('objectives')}
          >
            🎓 Learning Objectives
          </button>
          <button 
            className={activeTab === 'study-plan' ? 'tab-active' : ''}
            onClick={() => setActiveTab('study-plan')}
          >
            📅 Study Plan
          </button>
        </div>

        <div className="education-filters">
          <select 
            value={filters.specialty} 
            onChange={(e) => setFilters({...filters, specialty: e.target.value})}
          >
            <option value="">All Specialties</option>
            {availableSpecialties.map(specialty => (
              <option key={specialty} value={specialty}>
                {specialty.charAt(0).toUpperCase() + specialty.slice(1).replace(/_/g, ' ')}
              </option>
            ))}
          </select>

          <select 
            value={filters.difficulty} 
            onChange={(e) => setFilters({...filters, difficulty: e.target.value})}
          >
            <option value="">All Levels</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>

          {activeTab === 'objectives' && (
            <select 
              value={filters.yearLevel} 
              onChange={(e) => setFilters({...filters, yearLevel: e.target.value})}
            >
              <option value="">All Years</option>
              <option value="MS1">MS1</option>
              <option value="MS2">MS2</option>
              <option value="MS3">MS3</option>
              <option value="MS4">MS4</option>
              <option value="resident">Resident</option>
            </select>
          )}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="overview-container">
            {/* Welcome Section */}
            <div className="welcome-section">
              <h2>Welcome to Your Medical Training Center</h2>
              <p>Track your progress, identify weak areas, and follow personalized study recommendations.</p>
            </div>

            {/* Stats Dashboard */}
            <div className="stats-dashboard">
              <div className="stat-card">
                <div className="stat-icon">🔥</div>
                <div className="stat-content">
                  <h3>{studyStreak} Days</h3>
                  <p>Study Streak</p>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">📋</div>
                <div className="stat-content">
                  <h3>{progress?.total_cases_attempted || 0}</h3>
                  <p>Cases Completed</p>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">🎯</div>
                <div className="stat-content">
                  <h3>{progress?.total_quiz_questions || 0}</h3>
                  <p>Questions Answered</p>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">📈</div>
                <div className="stat-content">
                  <h3>{progress?.accuracy_rate || 0}%</h3>
                  <p>Overall Accuracy</p>
                </div>
              </div>
            </div>

            {/* Today's Goals */}
            {studyPlan && (
              <div className="today-goals">
                <h3>📅 Today's Study Goals</h3>
                <div className="goal-card">
                  <p><strong>Daily Goal:</strong> {studyPlan.todayGoal}</p>
                  <p><strong>Weekly Goal:</strong> {studyPlan.weeklyGoal}</p>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: '60%' }}></div>
                  </div>
                  <p className="progress-text">60% Complete</p>
                </div>
              </div>
            )}

            {/* Achievements */}
            <div className="achievements-section">
              <h3>🏆 Achievements</h3>
              <div className="achievements-grid">
                {achievements.map((achievement) => (
                  <div 
                    key={achievement.id} 
                    className={`achievement-card ${achievement.earned ? 'earned' : 'locked'}`}
                  >
                    <div className="achievement-icon">{achievement.icon}</div>
                    <h4>{achievement.title}</h4>
                    <p>{achievement.description}</p>
                    {!achievement.earned && <div className="locked-badge">🔒 Locked</div>}
                  </div>
                ))}
              </div>
            </div>

            {/* Weak Areas */}
            <div className="weak-areas-section">
              <h3>🎯 Areas for Improvement</h3>
              <div className="weak-areas-list">
                {weakAreas.map((area, index) => (
                  <div key={index} className="weak-area-card">
                    <div className="area-header">
                      <h4>{area.specialty}</h4>
                      <span className="accuracy-badge" style={{
                        background: area.accuracy >= 80 ? '#10b981' : area.accuracy >= 60 ? '#f59e0b' : '#ef4444',
                        color: 'white'
                      }}>
                        {area.accuracy}% Accuracy
                      </span>
                    </div>
                    <p>{area.questionsAttempted} questions attempted</p>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ 
                          width: `${area.accuracy}%`,
                          background: area.accuracy >= 80 ? '#10b981' : area.accuracy >= 60 ? '#f59e0b' : '#ef4444'
                        }}
                      ></div>
                    </div>
                    <button 
                      className="study-button"
                      onClick={() => {
                        setFilters({...filters, specialty: area.specialty.toLowerCase()});
                        setActiveTab('cases');
                      }}
                    >
                      Study {area.specialty}
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="recent-activity-section">
              <h3>📝 Recent Activity</h3>
              <div className="activity-list">
                {recentActivity.map((activity, index) => (
                  <div key={index} className="activity-item">
                    <div className="activity-icon">
                      {activity.type === 'quiz' && '🎯'}
                      {activity.type === 'case' && '📋'}
                      {activity.type === 'flashcards' && '🗂️'}
                    </div>
                    <div className="activity-content">
                      <h4>{activity.title}</h4>
                      {activity.score && <p className="activity-score">Score: {activity.score}%</p>}
                      {activity.specialty && <p className="activity-specialty">{activity.specialty}</p>}
                      <p className="activity-time">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommended Topics */}
            {studyPlan && studyPlan.recommendedTopics && (
              <div className="recommended-topics-section">
                <h3>💡 Recommended Study Topics</h3>
                <div className="topics-grid">
                  {studyPlan.recommendedTopics.map((topic, index) => (
                    <div key={index} className="topic-card">
                      <h4>{topic}</h4>
                      <button 
                        className="start-learning-btn"
                        onClick={() => {
                          setSearchQuery(topic);
                          setActiveTab('cases');
                          searchCases();
                        }}
                      >
                        Start Learning →
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'cases' && (
          <div>
            <div className="search-bar">
              <input
                type="text"
                placeholder="Search cases by keywords..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && searchCases()}
              />
              <button onClick={searchCases}>🔍 Search</button>
            </div>

            {loading ? (
              <div className="loading">Loading cases...</div>
            ) : (
              <div className="cases-list">
                {cases
                  .sort((a, b) => {
                    const difficultyOrder = { 'beginner': 1, 'intermediate': 2, 'advanced': 3 };
                    return difficultyOrder[a.difficulty] - difficultyOrder[b.difficulty];
                  })
                  .map((caseItem) => {
                    const isExpanded = expandedCaseId === caseItem.case_id;
                    return (
                      <div 
                        key={caseItem.case_id} 
                        className={`case-list-item difficulty-${caseItem.difficulty} ${isExpanded ? 'expanded' : ''}`}
                      >
                        <div 
                          className="case-list-content"
                          onClick={() => setExpandedCaseId(isExpanded ? null : caseItem.case_id)}
                        >
                          <span className="case-title">
                            {isExpanded ? '▼' : '▶'} {caseItem.title}
                          </span>
                          <span className={`difficulty-badge ${caseItem.difficulty}`}>{caseItem.difficulty}</span>
                        </div>
                        {isExpanded && (
                          <div className="case-details">
                            <div className="case-section">
                              <h4>Presentation</h4>
                              <p>{caseItem.presentation}</p>
                            </div>
                            {caseItem.learning_objectives && (
                              <div className="case-section">
                                <h4>Learning Objectives</h4>
                                <ul>
                                  {caseItem.learning_objectives.map((obj, i) => (
                                    <li key={i}>{obj}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            <div className="case-section">
                              <h4>History</h4>
                              {caseItem.history && Object.entries(caseItem.history).map(([key, value]) => (
                                <div key={key} className="history-item">
                                  <strong>{key.replace(/_/g, ' ').toUpperCase()}:</strong> {value}
                                </div>
                              ))}
                            </div>
                            <div className="case-section">
                              <h4>Physical Exam</h4>
                              {caseItem.physical_exam && Object.entries(caseItem.physical_exam).map(([key, value]) => (
                                <div key={key} className="exam-item">
                                  <strong>{key.replace(/_/g, ' ').toUpperCase()}:</strong> {value}
                                </div>
                              ))}
                            </div>
                            {caseItem.labs && (
                              <div className="case-section">
                                <h4>Laboratory Results</h4>
                                {Object.entries(caseItem.labs).map(([key, value]) => (
                                  <div key={key} className="lab-item">
                                    <strong>{key.replace(/_/g, ' ').toUpperCase()}:</strong> {value}
                                  </div>
                                ))}
                              </div>
                            )}
                            {caseItem.imaging && (
                              <div className="case-section">
                                <h4>Imaging</h4>
                                {Object.entries(caseItem.imaging).map(([key, value]) => (
                                  <div key={key} className="imaging-item">
                                    <strong>{key.replace(/_/g, ' ').toUpperCase()}:</strong> {value}
                                  </div>
                                ))}
                              </div>
                            )}
                            <div className="case-section diagnosis-section">
                              <h4>Correct Diagnosis</h4>
                              <p className="diagnosis">{caseItem.correct_diagnosis}</p>
                            </div>
                            {caseItem.differential && (
                              <div className="case-section">
                                <h4>Differential Diagnosis</h4>
                                <ul>
                                  {caseItem.differential.map((dx, i) => (
                                    <li key={i}>{dx}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            <div className="case-section">
                              <h4>Explanation</h4>
                              <p>{caseItem.explanation}</p>
                            </div>
                            {caseItem.management_pearls && (
                              <div className="case-section">
                                <h4>Management Pearls</h4>
                                <ul>
                                  {caseItem.management_pearls.map((pearl, i) => (
                                    <li key={i}>{pearl}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {caseItem.pitfalls && (
                              <div className="case-section">
                                <h4>Common Pitfalls</h4>
                                <ul>
                                  {caseItem.pitfalls.map((pitfall, i) => (
                                    <li key={i}>{pitfall}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {caseItem.tags && (
                              <div className="case-section">
                                <h4>Tags</h4>
                                <div className="tags">
                                  {caseItem.tags.map((tag, i) => (
                                    <span key={i} className="tag">{tag}</span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
              </div>
            )}
          </div>
        )}

        {activeTab === 'progress' && (
          <div>
            {progress && progress.user_id ? (
              <div>
                <h2>Your Progress</h2>
                <p>Accuracy: {progress.accuracy_rate}%</p>
                <p>Cases: {progress.total_cases_attempted}</p>
                <p>Quiz: {progress.total_quiz_questions}</p>
              </div>
            ) : (
              <div className="no-progress">
                <h3>Start Learning to Track Progress</h3>
                <p>Complete cases and quizzes to see your statistics here!</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'quiz' && (
          <div>
            {!quizActive ? (
              <div className="quiz-start">
                <h2>Start Quiz</h2>
                <p>Test your knowledge with multiple-choice questions based on clinical cases.</p>
                <button onClick={startQuiz} disabled={loading}>
                  {loading ? 'Loading...' : '🎯 Start Quiz (10 Questions)'}
                </button>
              </div>
            ) : (
              <div className="quiz-container">
                <div className="quiz-progress">
                  Question {currentQuestionIndex + 1} of {quizQuestions.length}
                </div>
                {quizQuestions[currentQuestionIndex] && (
                  <div>
                    <h3>{quizQuestions[currentQuestionIndex].question_text}</h3>
                    <div className="quiz-options">
                      {quizQuestions[currentQuestionIndex].options.map((option) => (
                        <div 
                          key={option.id}
                          className={`quiz-option ${selectedAnswer === option.id ? 'selected' : ''}`}
                          onClick={() => !showExplanation && setSelectedAnswer(option.id)}
                        >
                          <strong>{option.id}.</strong> {option.text}
                        </div>
                      ))}
                    </div>
                    {showExplanation && (
                      <div className="explanation">
                        <h4>Explanation:</h4>
                        <p>{quizQuestions[currentQuestionIndex].explanation}</p>
                        <p><strong>Correct Answer:</strong> {quizQuestions[currentQuestionIndex].correct_answer.join(', ')}</p>
                      </div>
                    )}
                    <div className="quiz-actions">
                      {!showExplanation ? (
                        <button onClick={submitQuizAnswer} disabled={!selectedAnswer}>
                          Submit Answer
                        </button>
                      ) : (
                        <button onClick={nextQuestion}>
                          {currentQuestionIndex < quizQuestions.length - 1 ? 'Next Question' : 'Finish Quiz'}
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'flashcards' && (
          <div>
            {loading ? (
              <div className="loading">Loading flashcards...</div>
            ) : flashcards.length === 0 ? (
              <div className="no-flashcards">
                <h3>No Flashcards Due</h3>
                <p>You're all caught up! Check back later or start a quiz to add more cards.</p>
                <button onClick={loadFlashcards}>Refresh</button>
              </div>
            ) : (
              <div className="flashcard-container">
                <div className="flashcard-progress">
                  Card {currentCardIndex + 1} of {flashcards.length}
                </div>
                <div 
                  className={`flashcard ${showCardBack ? 'flipped' : ''}`}
                  onClick={() => setShowCardBack(!showCardBack)}
                >
                  <div className="flashcard-front">
                    <h3>{flashcards[currentCardIndex].front}</h3>
                    <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '1rem' }}>
                      Click to reveal answer
                    </p>
                  </div>
                  {showCardBack && (
                    <div className="flashcard-back">
                      <h4>Answer:</h4>
                      <p>{flashcards[currentCardIndex].back}</p>
                      <div className="flashcard-meta">
                        <span className="badge">{flashcards[currentCardIndex].specialty}</span>
                        <span className={`badge ${flashcards[currentCardIndex].difficulty}`}>
                          {flashcards[currentCardIndex].difficulty}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
                {showCardBack && (
                  <div className="flashcard-review">
                    <p>How well did you know this?</p>
                    <div className="review-buttons">
                      <button onClick={() => reviewFlashcard(1)} className="review-again">
                        Again
                      </button>
                      <button onClick={() => reviewFlashcard(3)} className="review-hard">
                        Hard
                      </button>
                      <button onClick={() => reviewFlashcard(4)} className="review-good">
                        Good
                      </button>
                      <button onClick={() => reviewFlashcard(5)} className="review-easy">
                        Easy
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'objectives' && (
          <div>
            {loading ? (
              <div className="loading">Loading objectives...</div>
            ) : (
              <div className="objectives-grid">
                {learningObjectives.map((objective) => (
                  <div key={objective.objective_id} className="objective-card">
                    <div className="objective-header">
                      <h3>{objective.title}</h3>
                      <div>
                        <span className="badge">{objective.year_level}</span>
                        <span className="badge">{objective.specialty}</span>
                      </div>
                    </div>
                    <p>{objective.description}</p>
                    {objective.related_cases && objective.related_cases.length > 0 && (
                      <div className="objective-links">
                        <strong>Related Cases:</strong> {objective.related_cases.join(', ')}
                      </div>
                    )}
                  </div>
                ))}
                {learningObjectives.length === 0 && (
                  <div className="no-objectives">
                    <p>No learning objectives found for the selected filters.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Study Plan Tab */}
        {activeTab === 'study-plan' && (
          <div className="study-plan-container">
            <div className="plan-header">
              <h2>📅 Personalized Study Plan</h2>
              <p>AI-generated study recommendations based on your progress and weak areas</p>
            </div>

            {/* Study Schedule */}
            <div className="study-schedule">
              <h3>This Week's Schedule</h3>
              <div className="schedule-grid">
                <div className="schedule-day">
                  <div className="day-header">
                    <strong>Monday</strong>
                    <span className="day-status completed">✓</span>
                  </div>
                  <ul>
                    <li>✅ 2 Cardiology Cases</li>
                    <li>✅ 10 Flashcards</li>
                  </ul>
                </div>
                <div className="schedule-day">
                  <div className="day-header">
                    <strong>Tuesday</strong>
                    <span className="day-status completed">✓</span>
                  </div>
                  <ul>
                    <li>✅ Neurology Quiz (10 Q)</li>
                    <li>✅ Review weak areas</li>
                  </ul>
                </div>
                <div className="schedule-day active">
                  <div className="day-header">
                    <strong>Wednesday</strong>
                    <span className="day-status active">📍</span>
                  </div>
                  <ul>
                    <li>⏳ 1 Emergency Case</li>
                    <li>⏳ 15 Flashcards</li>
                    <li>⏳ Practice Quiz</li>
                  </ul>
                </div>
                <div className="schedule-day">
                  <div className="day-header">
                    <strong>Thursday</strong>
                    <span className="day-status">○</span>
                  </div>
                  <ul>
                    <li>Pulmonology Review</li>
                    <li>10 Questions</li>
                  </ul>
                </div>
                <div className="schedule-day">
                  <div className="day-header">
                    <strong>Friday</strong>
                    <span className="day-status">○</span>
                  </div>
                  <ul>
                    <li>GI Cases (2)</li>
                    <li>Flashcard Review</li>
                  </ul>
                </div>
                <div className="schedule-day weekend">
                  <div className="day-header">
                    <strong>Saturday</strong>
                    <span className="day-status">○</span>
                  </div>
                  <ul>
                    <li>Comprehensive Quiz</li>
                    <li>Review all specialties</li>
                  </ul>
                </div>
                <div className="schedule-day weekend">
                  <div className="day-header">
                    <strong>Sunday</strong>
                    <span className="day-status">○</span>
                  </div>
                  <ul>
                    <li>Rest Day / Light Review</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Focus Areas */}
            <div className="focus-areas">
              <h3>🎯 Priority Focus Areas</h3>
              <div className="focus-cards">
                <div className="focus-card high-priority">
                  <div className="priority-badge">High Priority</div>
                  <h4>Cardiology - Acute Coronary Syndrome</h4>
                  <p>Current Accuracy: 65% | Target: 85%</p>
                  <p className="focus-reason">Based on recent quiz performance and upcoming objectives</p>
                  <div className="focus-actions">
                    <button onClick={() => { setSearchQuery('Acute Coronary Syndrome'); setActiveTab('cases'); }}>
                      📋 Study Cases
                    </button>
                    <button onClick={() => { setFilters({...filters, specialty: 'cardiology'}); setActiveTab('quiz'); }}>
                      🎯 Take Quiz
                    </button>
                  </div>
                </div>
                <div className="focus-card medium-priority">
                  <div className="priority-badge medium">Medium Priority</div>
                  <h4>Neurology - Stroke Recognition</h4>
                  <p>Current Accuracy: 72% | Target: 90%</p>
                  <p className="focus-reason">Important for emergency medicine rotation</p>
                  <div className="focus-actions">
                    <button onClick={() => { setSearchQuery('Stroke'); setActiveTab('cases'); }}>
                      📋 Study Cases
                    </button>
                    <button onClick={() => { setFilters({...filters, specialty: 'neurology'}); setActiveTab('flashcards'); }}>
                      🗂️ Flashcards
                    </button>
                  </div>
                </div>
                <div className="focus-card low-priority">
                  <div className="priority-badge low">Maintenance</div>
                  <h4>Emergency Medicine - Sepsis</h4>
                  <p>Current Accuracy: 88% | Target: 90%</p>
                  <p className="focus-reason">Strong performance, maintain with periodic review</p>
                  <div className="focus-actions">
                    <button onClick={() => { setSearchQuery('Sepsis'); setActiveTab('cases'); }}>
                      📋 Review
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Study Tips */}
            <div className="study-tips">
              <h3>💡 Personalized Study Tips</h3>
              <div className="tips-grid">
                <div className="tip-card">
                  <div className="tip-icon">⏰</div>
                  <h4>Optimal Study Time</h4>
                  <p>Your best performance is in the morning (9-11 AM). Schedule complex topics during this time.</p>
                </div>
                <div className="tip-card">
                  <div className="tip-icon">🔄</div>
                  <h4>Spaced Repetition</h4>
                  <p>Review Cardiology cases again in 3 days for optimal retention (last studied 4 days ago).</p>
                </div>
                <div className="tip-card">
                  <div className="tip-icon">📊</div>
                  <h4>Progress Insight</h4>
                  <p>You've improved 15% in Neurology over the past 2 weeks. Keep up the momentum!</p>
                </div>
                <div className="tip-card">
                  <div className="tip-icon">🎯</div>
                  <h4>Goal Setting</h4>
                  <p>Complete 3 more cases this week to maintain your 5-day study streak.</p>
                </div>
              </div>
            </div>

            {/* Learning Path */}
            <div className="learning-path">
              <h3>🛤️ Recommended Learning Path</h3>
              <div className="path-timeline">
                <div className="path-item completed">
                  <div className="path-marker">✓</div>
                  <div className="path-content">
                    <h4>Week 1-2: Cardiology Basics</h4>
                    <p>Completed with 85% average</p>
                  </div>
                </div>
                <div className="path-item active">
                  <div className="path-marker active">⬤</div>
                  <div className="path-content">
                    <h4>Week 3-4: Advanced Cardiology</h4>
                    <p>Currently: Acute Coronary Syndrome</p>
                    <div className="path-progress">
                      <div className="path-progress-fill" style={{ width: '60%' }}></div>
                    </div>
                  </div>
                </div>
                <div className="path-item">
                  <div className="path-marker">○</div>
                  <div className="path-content">
                    <h4>Week 5-6: Neurology Foundation</h4>
                    <p>Unlocks after completing Cardiology</p>
                  </div>
                </div>
                <div className="path-item">
                  <div className="path-marker">○</div>
                  <div className="path-content">
                    <h4>Week 7-8: Emergency Medicine</h4>
                    <p>Integration of all specialties</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Study Resources */}
            <div className="study-resources">
              <h3>📚 Additional Resources</h3>
              <div className="resources-list">
                <div className="resource-item">
                  <span className="resource-icon">📖</span>
                  <div className="resource-content">
                    <h4>Cardiology Reference Guide</h4>
                    <p>Comprehensive review of ACS, Heart Failure, and Arrhythmias</p>
                    <a href="/sources" className="resource-link">View Resource →</a>
                  </div>
                </div>
                <div className="resource-item">
                  <span className="resource-icon">🎥</span>
                  <div className="resource-content">
                    <h4>Clinical Skills Videos</h4>
                    <p>Physical exam techniques and diagnostic procedures</p>
                    <a href="#" className="resource-link">Coming Soon</a>
                  </div>
                </div>
                <div className="resource-item">
                  <span className="resource-icon">📝</span>
                  <div className="resource-content">
                    <h4>Practice Exams</h4>
                    <p>USMLE-style questions for comprehensive review</p>
                    <button 
                      className="resource-link"
                      onClick={() => setActiveTab('quiz')}
                    >
                      Start Exam →
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
