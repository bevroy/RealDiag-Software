"""Pydantic schemas for the modular diagnostic engine."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CodeBundle(BaseModel):
    icd10: list[str] = Field(default_factory=list)
    snomed: list[str] = Field(default_factory=list)
    cpt: list[str] = Field(default_factory=list)


class DifferentialDiagnosis(BaseModel):
    name: str
    confidence: int
    summary: str


class AnalyzeRequest(BaseModel):
    patient_age: int
    patient_sex: str
    symptoms: list[str] = Field(default_factory=list)
    history: list[str] = Field(default_factory=list)
    include_variations: bool = True
    codes: CodeBundle = Field(default_factory=CodeBundle)


class AnalyzeResponse(BaseModel):
    differential: list[DifferentialDiagnosis]
    workup: list[str]
    referral: list[str]
    codes: CodeBundle
    rationale: str
