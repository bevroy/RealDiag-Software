/**
 * Voice Input Manager
 * Web Speech API integration for hands-free symptom entry
 */

// Check browser support
export function isVoiceInputSupported() {
  return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
}

// Create recognition instance
export function createVoiceRecognition(options = {}) {
  if (!isVoiceInputSupported()) {
    console.warn('Speech recognition not supported in this browser');
    return null;
  }
  
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  
  // Configuration
  recognition.continuous = options.continuous !== undefined ? options.continuous : false;
  recognition.interimResults = options.interimResults !== undefined ? options.interimResults : true;
  recognition.lang = options.lang || 'en-US';
  recognition.maxAlternatives = options.maxAlternatives || 3;
  
  return recognition;
}

// Medical term recognition improvements
const medicalTerms = {
  // Common replacements
  'heading': 'headache',
  'head egg': 'headache',
  'head ache': 'headache',
  'fever': 'fever',
  'coughing': 'cough',
  'cuffing': 'cough',
  'nausea': 'nausea',
  'vomiting': 'vomiting',
  'dizziness': 'dizziness',
  'dizzy': 'dizziness',
  'shortness of breath': 'shortness of breath',
  'sob': 'shortness of breath',
  'chest pain': 'chest pain',
  'abdominal pain': 'abdominal pain',
  'belly pain': 'abdominal pain',
  'stomach pain': 'abdominal pain',
  'fatigue': 'fatigue',
  'tired': 'fatigue',
  'weakness': 'weakness',
  'rash': 'rash',
  'swelling': 'swelling'
};

// Clean and normalize medical terms
export function normalizeMedicalText(text) {
  let normalized = text.toLowerCase().trim();
  
  // Replace common misrecognitions
  for (const [misheard, correct] of Object.entries(medicalTerms)) {
    const regex = new RegExp(`\\b${misheard}\\b`, 'gi');
    normalized = normalized.replace(regex, correct);
  }
  
  return normalized;
}

// Voice command recognition
const voiceCommands = {
  'add symptom': 'ADD_SYMPTOM',
  'remove symptom': 'REMOVE_SYMPTOM',
  'delete symptom': 'REMOVE_SYMPTOM',
  'clear all': 'CLEAR_ALL',
  'search': 'SEARCH',
  'diagnose': 'SEARCH',
  'find diagnosis': 'SEARCH',
  'show results': 'SHOW_RESULTS',
  'show favorites': 'SHOW_FAVORITES',
  'go back': 'GO_BACK',
  'help': 'HELP'
};

// Detect voice commands
export function detectVoiceCommand(text) {
  const normalized = text.toLowerCase().trim();
  
  for (const [command, action] of Object.entries(voiceCommands)) {
    if (normalized.includes(command)) {
      return {
        detected: true,
        action,
        command,
        original: text
      };
    }
  }
  
  return {
    detected: false,
    original: text
  };
}

// Start listening
export function startListening(recognition, callbacks = {}) {
  if (!recognition) return;
  
  recognition.onstart = () => {
    console.log('[Voice] Listening started');
    if (callbacks.onStart) callbacks.onStart();
  };
  
  recognition.onresult = (event) => {
    const result = event.results[event.results.length - 1];
    const transcript = result[0].transcript;
    const isFinal = result.isFinal;
    const confidence = result[0].confidence;
    
    console.log('[Voice] Transcript:', transcript, 'Final:', isFinal, 'Confidence:', confidence);
    
    // Normalize medical terms
    const normalized = normalizeMedicalText(transcript);
    
    // Check for commands
    const commandCheck = detectVoiceCommand(normalized);
    
    if (callbacks.onResult) {
      callbacks.onResult({
        transcript,
        normalized,
        isFinal,
        confidence,
        command: commandCheck.detected ? commandCheck : null
      });
    }
  };
  
  recognition.onerror = (event) => {
    console.error('[Voice] Recognition error:', event.error);
    if (callbacks.onError) {
      callbacks.onError({
        error: event.error,
        message: getErrorMessage(event.error)
      });
    }
  };
  
  recognition.onend = () => {
    console.log('[Voice] Listening ended');
    if (callbacks.onEnd) callbacks.onEnd();
  };
  
  try {
    recognition.start();
  } catch (error) {
    console.error('[Voice] Failed to start:', error);
    if (callbacks.onError) {
      callbacks.onError({
        error: 'start-failed',
        message: 'Failed to start voice recognition'
      });
    }
  }
}

// Stop listening
export function stopListening(recognition) {
  if (recognition) {
    try {
      recognition.stop();
    } catch (error) {
      console.error('[Voice] Failed to stop:', error);
    }
  }
}

// Get error message
function getErrorMessage(error) {
  const messages = {
    'no-speech': 'No speech detected. Please try again.',
    'audio-capture': 'Microphone not accessible. Please check permissions.',
    'not-allowed': 'Microphone permission denied. Please allow access in settings.',
    'network': 'Network error. Speech recognition requires internet connection.',
    'aborted': 'Speech recognition aborted.',
    'language-not-supported': 'Language not supported.'
  };
  
  return messages[error] || 'An error occurred with voice recognition.';
}

// Request microphone permission
export async function requestMicrophonePermission() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach(track => track.stop());
    return { granted: true };
  } catch (error) {
    console.error('[Voice] Microphone permission denied:', error);
    return { 
      granted: false, 
      error: error.name,
      message: 'Microphone permission denied'
    };
  }
}

// Check microphone permission
export async function checkMicrophonePermission() {
  if (!navigator.permissions) {
    return { state: 'unknown' };
  }
  
  try {
    const result = await navigator.permissions.query({ name: 'microphone' });
    return { state: result.state };
  } catch (error) {
    return { state: 'unknown', error: error.message };
  }
}

// Speech synthesis (text-to-speech)
export function speak(text, options = {}) {
  if (!('speechSynthesis' in window)) {
    console.warn('Speech synthesis not supported');
    return;
  }
  
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = options.lang || 'en-US';
  utterance.rate = options.rate || 1.0;
  utterance.pitch = options.pitch || 1.0;
  utterance.volume = options.volume || 1.0;
  
  if (options.onEnd) {
    utterance.onend = options.onEnd;
  }
  
  window.speechSynthesis.speak(utterance);
}

// Stop speech
export function stopSpeaking() {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
}

// Get available voices
export function getAvailableVoices() {
  if (!('speechSynthesis' in window)) {
    return [];
  }
  
  return window.speechSynthesis.getVoices();
}

export default {
  isVoiceInputSupported,
  createVoiceRecognition,
  normalizeMedicalText,
  detectVoiceCommand,
  startListening,
  stopListening,
  requestMicrophonePermission,
  checkMicrophonePermission,
  speak,
  stopSpeaking,
  getAvailableVoices
};
