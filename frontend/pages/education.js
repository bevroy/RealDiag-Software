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
        .education-container {
          max-width: 1400px;
          margin: 0 auto;
          padding: 20px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }

        .education-header {
          text-align: center;
          margin-bottom: 30px;
          padding: 30px;
          background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);
          color: white;
          border-radius: 12px;
          position: relative;
        }

        .home-button {
          position: absolute;
          top: 20px;
          right: 20px;
          padding: 8px 16px;
          background: rgba(255, 255, 255, 0.2);
          color: white;
          text-decoration: none;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .education-header h1 {
          margin: 0 0 10px 0;
          font-size: 2.5em;
          color: #78350f;
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
          color: #14b8a6;
          border-bottom-color: #14b8a6;
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
          background: #e3f2fd;
          color: #1976d2;
        }

        .badge.intermediate {
          background: #fff3e0;
          color: #f57c00;
        }

        .badge.advanced {
          background: #fce4ec;
          color: #c2185b;
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
      `}</style>

      <div className="education-container">
        <header className="education-header">
          <a href="/" className="home-button">🏠 Home</a>
          <h1>📚 Medical Training Center</h1>
          <p>Enhance your clinical reasoning skills with cases, quizzes, and flashcards</p>
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

        {(activeTab === 'quiz' || activeTab === 'flashcards' || activeTab === 'objectives') && (
          <div className="loading">
            {activeTab === 'quiz' && 'Quiz mode coming soon...'}
            {activeTab === 'flashcards' && 'Flashcards coming soon...'}
            {activeTab === 'objectives' && 'Learning objectives coming soon...'}
          </div>
        )}
      </div>
    </>
  );
}
