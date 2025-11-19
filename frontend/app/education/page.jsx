'use client';

import React, { useState, useEffect } from 'react';
import './education.css';

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

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const userId = 'student_001'; // In production, get from auth

  // Load cases
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

  // Search cases
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

  // Load quiz questions
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

  // Submit quiz answer
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
          correct: false, // Server will determine
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

  // Next question
  const nextQuestion = () => {
    if (currentQuestionIndex < quizQuestions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setSelectedAnswer(null);
      setShowExplanation(false);
    } else {
      // Quiz complete
      setQuizActive(false);
      loadProgress();
    }
  };

  // Load flashcards
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

  // Review flashcard
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
      
      // Next card
      if (currentCardIndex < flashcards.length - 1) {
        setCurrentCardIndex(currentCardIndex + 1);
        setShowCardBack(false);
      } else {
        // All cards reviewed
        loadFlashcards();
      }
    } catch (error) {
      console.error('Error reviewing flashcard:', error);
    }
  };

  // Load progress
  const loadProgress = async () => {
    try {
      const response = await fetch(`${API_BASE}/education/progress/${userId}`);
      const data = await response.json();
      setProgress(data);
    } catch (error) {
      console.error('Error loading progress:', error);
    }
  };

  // Load learning objectives
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

  // Load initial data
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
    <div className="education-container">
      <header className="education-header">
        <h1>📚 Medical Training Center</h1>
        <p>Enhance your clinical reasoning skills with cases, quizzes, and flashcards</p>
      </header>

      {/* Navigation Tabs */}
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

      {/* Filters */}
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

      {/* Case Library Tab */}
      {activeTab === 'cases' && (
        <div className="cases-section">
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
            <div className="case-detail">
              <button onClick={() => setSelectedCase(null)} className="back-btn">← Back to Cases</button>
              
              <div className="case-header">
                <h2>{selectedCase.title}</h2>
                <div className="case-meta">
                  <span className={`badge ${selectedCase.difficulty}`}>{selectedCase.difficulty}</span>
                  <span className="badge">{selectedCase.specialty}</span>
                </div>
              </div>

              <div className="case-content">
                <section>
                  <h3>📝 Presentation</h3>
                  <p>{selectedCase.presentation}</p>
                </section>

                <section>
                  <h3>📖 History</h3>
                  <div className="history-details">
                    <p><strong>Chief Complaint:</strong> {selectedCase.history.chief_complaint}</p>
                    <p><strong>HPI:</strong> {selectedCase.history.hpi}</p>
                    <p><strong>PMH:</strong> {selectedCase.history.pmh}</p>
                    <p><strong>Medications:</strong> {selectedCase.history.medications}</p>
                    <p><strong>Social:</strong> {selectedCase.history.social}</p>
                    <p><strong>Family:</strong> {selectedCase.history.family}</p>
                  </div>
                </section>

                <section>
                  <h3>🔍 Physical Exam</h3>
                  <div className="exam-details">
                    <p><strong>Vitals:</strong> {selectedCase.physical_exam.vitals}</p>
                    <p><strong>General:</strong> {selectedCase.physical_exam.general}</p>
                    <p><strong>Cardiac:</strong> {selectedCase.physical_exam.cardiac}</p>
                    <p><strong>Lungs:</strong> {selectedCase.physical_exam.lungs}</p>
                  </div>
                </section>

                {selectedCase.labs && (
                  <section>
                    <h3>🧪 Labs & Imaging</h3>
                    <div className="labs-details">
                      {Object.entries(selectedCase.labs).map(([key, value]) => (
                        <p key={key}><strong>{key.replace(/_/g, ' ').toUpperCase()}:</strong> {value}</p>
                      ))}
                    </div>
                  </section>
                )}

                <section className="diagnosis-section">
                  <h3>✅ Diagnosis</h3>
                  <p className="correct-diagnosis">{selectedCase.correct_diagnosis}</p>
                  
                  <h4>Differential Diagnosis:</h4>
                  <ul>
                    {selectedCase.differential.map((dx, idx) => (
                      <li key={idx}>{dx}</li>
                    ))}
                  </ul>
                </section>

                <section className="explanation-section">
                  <h3>💡 Explanation</h3>
                  <p>{selectedCase.explanation}</p>
                </section>

                <section>
                  <h3>💊 Management Pearls</h3>
                  <ul className="pearls-list">
                    {selectedCase.management_pearls.map((pearl, idx) => (
                      <li key={idx}>{pearl}</li>
                    ))}
                  </ul>
                </section>

                <section>
                  <h3>🎯 Learning Objectives</h3>
                  <ul>
                    {selectedCase.learning_objectives.map((obj, idx) => (
                      <li key={idx}>{obj}</li>
                    ))}
                  </ul>
                </section>

                <section>
                  <h3>📚 References</h3>
                  <ul>
                    {selectedCase.references.map((ref, idx) => (
                      <li key={idx}>{ref}</li>
                    ))}
                  </ul>
                </section>
              </div>
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
                  <p className="case-preview">{caseItem.presentation.substring(0, 150)}...</p>
                  <div className="case-footer">
                    <span className={`badge ${caseItem.difficulty}`}>{caseItem.difficulty}</span>
                    <span className="badge">{caseItem.specialty}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Quiz Mode Tab */}
      {activeTab === 'quiz' && (
        <div className="quiz-section">
          {!quizActive ? (
            <div className="quiz-start">
              <h2>🎯 Test Your Diagnostic Reasoning</h2>
              <p>Answer multiple-choice questions based on clinical cases</p>
              <button onClick={startQuiz} className="start-quiz-btn">Start Quiz (10 Questions)</button>
            </div>
          ) : (
            <div className="quiz-active">
              <div className="quiz-header">
                <span>Question {currentQuestionIndex + 1} of {quizQuestions.length}</span>
                <span>Score: {quizResults.filter(r => r.correct).length}/{quizResults.length}</span>
              </div>

              {quizQuestions[currentQuestionIndex] && (
                <div className="quiz-question">
                  <h3>{quizQuestions[currentQuestionIndex].question_text}</h3>
                  
                  <div className="quiz-options">
                    {quizQuestions[currentQuestionIndex].options.map((option) => (
                      <div 
                        key={option.id}
                        className={`quiz-option ${selectedAnswer === option.id ? 'selected' : ''} ${
                          showExplanation ? (
                            quizQuestions[currentQuestionIndex].correct_answer.includes(option.id) ? 'correct' : 
                            selectedAnswer === option.id ? 'incorrect' : ''
                          ) : ''
                        }`}
                        onClick={() => !showExplanation && setSelectedAnswer(option.id)}
                      >
                        <span className="option-id">{option.id}</span>
                        <span className="option-text">{option.text}</span>
                      </div>
                    ))}
                  </div>

                  {showExplanation && (
                    <div className="explanation-box">
                      <h4>💡 Explanation:</h4>
                      <p>{quizQuestions[currentQuestionIndex].explanation}</p>
                      <button onClick={nextQuestion} className="next-btn">
                        {currentQuestionIndex < quizQuestions.length - 1 ? 'Next Question →' : 'Finish Quiz'}
                      </button>
                    </div>
                  )}

                  {!showExplanation && (
                    <button 
                      onClick={submitQuizAnswer} 
                      disabled={!selectedAnswer}
                      className="submit-btn"
                    >
                      Submit Answer
                    </button>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Flashcards Tab */}
      {activeTab === 'flashcards' && (
        <div className="flashcards-section">
          {loading ? (
            <div className="loading">Loading flashcards...</div>
          ) : flashcards.length === 0 ? (
            <div className="no-cards">
              <h3>🎉 All caught up!</h3>
              <p>No flashcards due for review right now.</p>
            </div>
          ) : (
            <div className="flashcard-container">
              <div className="flashcard-header">
                <span>Card {currentCardIndex + 1} of {flashcards.length}</span>
                <span className={`badge ${flashcards[currentCardIndex].difficulty}`}>
                  {flashcards[currentCardIndex].difficulty}
                </span>
              </div>

              <div 
                className={`flashcard ${showCardBack ? 'flipped' : ''}`}
                onClick={() => setShowCardBack(!showCardBack)}
              >
                <div className="flashcard-content">
                  {!showCardBack ? (
                    <div className="flashcard-front">
                      <h3>❓ Question</h3>
                      <p>{flashcards[currentCardIndex].front}</p>
                      <span className="flip-hint">Click to reveal answer</span>
                    </div>
                  ) : (
                    <div className="flashcard-back">
                      <h3>✅ Answer</h3>
                      <p>{flashcards[currentCardIndex].back}</p>
                    </div>
                  )}
                </div>
              </div>

              {showCardBack && (
                <div className="flashcard-rating">
                  <p>How well did you know this?</p>
                  <div className="rating-buttons">
                    <button onClick={() => reviewFlashcard(0)} className="rating-again">
                      Again (0)
                    </button>
                    <button onClick={() => reviewFlashcard(3)} className="rating-hard">
                      Hard (3)
                    </button>
                    <button onClick={() => reviewFlashcard(4)} className="rating-good">
                      Good (4)
                    </button>
                    <button onClick={() => reviewFlashcard(5)} className="rating-easy">
                      Easy (5)
                    </button>
                  </div>
                </div>
              )}

              <div className="flashcard-meta">
                <span>Type: {flashcards[currentCardIndex].card_type}</span>
                <span>Specialty: {flashcards[currentCardIndex].specialty}</span>
                <span>Reviews: {flashcards[currentCardIndex].review_count}</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Progress Tab */}
      {activeTab === 'progress' && (
        <div className="progress-section">
          {progress && progress.user_id ? (
            <>
              <div className="stats-grid">
                <div className="stat-card">
                  <h3>📊 Overall Accuracy</h3>
                  <div className="stat-value">{progress.accuracy_rate}%</div>
                </div>
                
                <div className="stat-card">
                  <h3>📋 Cases Completed</h3>
                  <div className="stat-value">{progress.total_cases_attempted}</div>
                  <div className="stat-detail">{progress.total_cases_correct} correct</div>
                </div>
                
                <div className="stat-card">
                  <h3>🎯 Quiz Questions</h3>
                  <div className="stat-value">{progress.total_quiz_questions}</div>
                  <div className="stat-detail">{progress.total_quiz_correct} correct</div>
                </div>
                
                <div className="stat-card">
                  <h3>⏱️ Avg Time per Case</h3>
                  <div className="stat-value">{Math.round(progress.average_time_per_case)}s</div>
                </div>
              </div>

              <div className="level-progress">
                <h3>🎓 Progress by Level</h3>
                <div className="level-bars">
                  <div className="level-bar">
                    <span>Beginner</span>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill beginner" 
                        style={{width: `${Math.min((progress.level_progress.beginner / 50) * 100, 100)}%`}}
                      />
                    </div>
                    <span>{progress.level_progress.beginner}</span>
                  </div>
                  
                  <div className="level-bar">
                    <span>Intermediate</span>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill intermediate" 
                        style={{width: `${Math.min((progress.level_progress.intermediate / 30) * 100, 100)}%`}}
                      />
                    </div>
                    <span>{progress.level_progress.intermediate}</span>
                  </div>
                  
                  <div className="level-bar">
                    <span>Advanced</span>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill advanced" 
                        style={{width: `${Math.min((progress.level_progress.advanced / 20) * 100, 100)}%`}}
                      />
                    </div>
                    <span>{progress.level_progress.advanced}</span>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="no-progress">
              <h3>📊 Start Learning to Track Progress</h3>
              <p>Complete cases and quizzes to see your statistics here!</p>
            </div>
          )}
        </div>
      )}

      {/* Learning Objectives Tab */}
      {activeTab === 'objectives' && (
        <div className="objectives-section">
          {loading ? (
            <div className="loading">Loading objectives...</div>
          ) : (
            <div className="objectives-list">
              {learningObjectives.map((obj) => (
                <div key={obj.objective_id} className="objective-card">
                  <div className="objective-header">
                    <h3>{obj.title}</h3>
                    <div className="objective-meta">
                      <span className="badge">{obj.year_level}</span>
                      <span className="badge">{obj.specialty}</span>
                      <span className="badge">{obj.category}</span>
                    </div>
                  </div>
                  <p>{obj.description}</p>
                  <div className="objective-footer">
                    <span>📋 {obj.related_cases.length} cases</span>
                    <span>🏥 {obj.related_diagnoses.length} diagnoses</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
