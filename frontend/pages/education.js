import React, { useState, useEffect } from 'react';
import Head from 'next/head';

export default function EducationPage() {
  const [activeTab, setActiveTab] = useState('cases');
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

  useEffect(() => {
    loadCases();
    loadProgress();
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

        .cases-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 20px;
        }

        .case-card {
          background: white;
          border: 2px solid #e0e0e0;
          border-radius: 12px;
          padding: 20px;
          cursor: pointer;
          transition: all 0.3s;
        }

        .case-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 24px rgba(0,0,0,0.1);
          border-color: #14b8a6;
        }

        .case-card h3 {
          margin: 0 0 12px 0;
          color: #333;
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
            📊 Progress
          </button>
          <button 
            className={activeTab === 'objectives' ? 'tab-active' : ''}
            onClick={() => setActiveTab('objectives')}
          >
            🎓 Learning Objectives
          </button>
        </div>

        <div className="education-filters">
          <select 
            value={filters.specialty} 
            onChange={(e) => setFilters({...filters, specialty: e.target.value})}
          >
            <option value="">All Specialties</option>
            <option value="cardiology">Cardiology</option>
            <option value="neurology">Neurology</option>
            <option value="gastroenterology">Gastroenterology</option>
            <option value="pulmonology">Pulmonology</option>
            <option value="emergency">Emergency Medicine</option>
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
            ) : selectedCase ? (
              <div>
                <button onClick={() => setSelectedCase(null)}>← Back to Cases</button>
                <h2>{selectedCase.title}</h2>
                <div>
                  <span className={`badge ${selectedCase.difficulty}`}>{selectedCase.difficulty}</span>
                  <span className="badge">{selectedCase.specialty}</span>
                </div>
                <p>{selectedCase.presentation}</p>
                <h3>Diagnosis: {selectedCase.correct_diagnosis}</h3>
              </div>
            ) : (
              <div className="cases-grid">
                {cases.map((caseItem) => (
                  <div 
                    key={caseItem.case_id} 
                    className="case-card"
                    onClick={() => setSelectedCase(caseItem)}
                  >
                    <h3>{caseItem.title}</h3>
                    <p>{caseItem.presentation.substring(0, 150)}...</p>
                    <div>
                      <span className={`badge ${caseItem.difficulty}`}>{caseItem.difficulty}</span>
                      <span className="badge">{caseItem.specialty}</span>
                    </div>
                  </div>
                ))}
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
      </div>
    </>
  );
}
