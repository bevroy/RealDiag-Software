/**
 * Type definitions for RealDiag Mobile App
 */

// User & Authentication
export interface User {
  user_id: string;
  email: string;
  full_name: string;
  specialty?: string;
  institution?: string;
  role: 'admin' | 'provider' | 'user' | 'guest';
  created_at: string;
  last_login?: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  token: string | null;
  error: string | null;
}

// Diagnostic Data
export interface DiagnosticTree {
  id: string;
  title: string;
  name: string;
  specialty: string;
  family: string;
  icd10: string[];
  snomed: string[];
  presentations: string[];
  description?: string;
  urgency?: 'Low' | 'Medium' | 'High' | 'Critical';
}

export interface SearchResult {
  id: string;
  label: string;
  family: string;
  presentations: string[];
  icd10: string[];
  snomed: string[];
  match_score?: number;
}

export interface SymptomSearchParams {
  query: string;
  age?: number;
  sex?: 'M' | 'F' | 'Other';
  family?: string;
}

// Patient Data (FHIR-compatible)
export interface Patient {
  id: string;
  name: string;
  dateOfBirth: string;
  gender: string;
  mrn?: string;
  allergies: Allergy[];
  medications: Medication[];
  conditions: Condition[];
  vitals?: Vitals[];
  labs?: LabResult[];
}

export interface Allergy {
  id: string;
  substance: string;
  severity: 'mild' | 'moderate' | 'severe';
  reaction?: string;
  status: 'active' | 'resolved';
}

export interface Medication {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
  route: string;
  status: 'active' | 'stopped' | 'completed';
  startDate?: string;
}

export interface Condition {
  id: string;
  name: string;
  code?: string;
  status: 'active' | 'resolved' | 'inactive';
  onsetDate?: string;
  severity?: string;
}

export interface Vitals {
  id: string;
  timestamp: string;
  bloodPressure?: {systolic: number; diastolic: number};
  heartRate?: number;
  temperature?: number;
  respiratoryRate?: number;
  oxygenSaturation?: number;
  weight?: number;
  height?: number;
}

export interface LabResult {
  id: string;
  name: string;
  value: string;
  unit: string;
  referenceRange: string;
  status: 'normal' | 'abnormal' | 'critical';
  timestamp: string;
}

// App Navigation
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
  DiagnosticDetail: {diagnosisId: string};
  PatientDetail: {patientId: string};
  WorkupPlan: {diagnosisId: string; patientId?: string};
};

export type MainTabParamList = {
  Home: undefined;
  Search: undefined;
  Patient: undefined;
  Settings: undefined;
};

// API Responses
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface SearchResponse {
  query: string;
  count: number;
  results: SearchResult[];
}

// Offline Storage
export interface OfflineRule {
  id: string;
  data: DiagnosticTree;
  cachedAt: number;
}

export interface OfflineSearch {
  id: string;
  query: string;
  results: SearchResult[];
  timestamp: number;
  synced: boolean;
}

// App Configuration
export interface AppConfig {
  apiBaseUrl: string;
  apiTimeout: number;
  offlineEnabled: boolean;
  biometricEnabled: boolean;
  sessionTimeout: number;
  maxOfflineRules: number;
}

// Redux State
export interface RootState {
  auth: AuthState;
  diagnostics: DiagnosticsState;
  patient: PatientState;
  settings: SettingsState;
}

export interface DiagnosticsState {
  searchResults: SearchResult[];
  selectedDiagnosis: DiagnosticTree | null;
  isSearching: boolean;
  error: string | null;
  offlineRules: OfflineRule[];
}

export interface PatientState {
  currentPatient: Patient | null;
  isLoading: boolean;
  error: string | null;
}

export interface SettingsState {
  config: AppConfig;
  theme: 'light' | 'dark' | 'auto';
  notifications: {
    enabled: boolean;
    types: string[];
  };
}
