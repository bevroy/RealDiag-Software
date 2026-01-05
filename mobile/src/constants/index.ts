/**
 * App Constants
 */

// API Configuration
export const API_BASE_URL = __DEV__
  ? 'http://localhost:8000'
  : 'https://realdiag-software.onrender.com';

export const API_TIMEOUT = 10000; // 10 seconds

// Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: '@realdiag:auth_token',
  USER_DATA: '@realdiag:user_data',
  OFFLINE_RULES: '@realdiag:offline_rules',
  SEARCH_HISTORY: '@realdiag:search_history',
  SETTINGS: '@realdiag:settings',
} as const;

// Session Configuration
export const SESSION_TIMEOUT = 15 * 60 * 1000; // 15 minutes
export const MAX_OFFLINE_RULES = 1000;
export const CACHE_EXPIRY = 24 * 60 * 60 * 1000; // 24 hours

// Medical Specialties
export const SPECIALTIES = [
  'Cardiology',
  'Dermatology',
  'Emergency Medicine',
  'Endocrinology',
  'Gastroenterology',
  'Geriatrics',
  'Hematology',
  'Immunology',
  'Infectious Disease',
  'Nephrology',
  'Neurology',
  'Obstetrics',
  'Oncology',
  'Ophthalmology',
  'Orthopedics',
  'Pediatrics',
  'Psychiatry',
  'Pulmonology',
  'Radiology',
  'Rheumatology',
  'Surgery',
  'Urology',
] as const;

// Urgency Levels
export const URGENCY_LEVELS = {
  LOW: {
    label: 'Low',
    color: '#10b981',
    icon: 'information-outline',
  },
  MEDIUM: {
    label: 'Medium',
    color: '#f59e0b',
    icon: 'alert-circle-outline',
  },
  HIGH: {
    label: 'High',
    color: '#ef4444',
    icon: 'alert-outline',
  },
  CRITICAL: {
    label: 'Critical',
    color: '#dc2626',
    icon: 'alert-octagon-outline',
  },
} as const;

// Validation Rules
export const VALIDATION = {
  EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PASSWORD_MIN_LENGTH: 8,
  NAME_MIN_LENGTH: 2,
  QUERY_MIN_LENGTH: 2,
} as const;

// Feature Flags
export const FEATURES = {
  VOICE_INPUT: true,
  BIOMETRIC_AUTH: true,
  OFFLINE_MODE: true,
  EHR_INTEGRATION: false, // Coming soon
  PDF_REPORTS: false, // Coming soon
  PUSH_NOTIFICATIONS: false, // Coming soon
} as const;
