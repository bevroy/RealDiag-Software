export type CodeBundle = {
  icd10: string[];
  snomed: string[];
  cpt: string[];
};

export type AnalyzeRequest = {
  patient_age: number;
  patient_sex: string;
  symptoms: string[];
  history: string[];
  include_variations: boolean;
  codes: CodeBundle;
};

export type DifferentialDiagnosis = {
  name: string;
  confidence: number;
  summary: string;
};

export type AnalyzeResponse = {
  differential: DifferentialDiagnosis[];
  workup: string[];
  referral: string[];
  codes: CodeBundle;
  rationale: string;
};
