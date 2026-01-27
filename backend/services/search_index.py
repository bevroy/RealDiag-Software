"""
Search Index Builder for RealDiag
Pre-computes symptom → diagnosis mappings for faster search
"""

import logging
from typing import Dict, List, Set
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class SearchIndex:
    """
    Pre-computed inverted index for symptom-based search.
    Maps normalized symptoms to lists of diagnosis IDs for O(1) lookup.
    """
    
    def __init__(self):
        self.symptom_to_diagnoses: Dict[str, Set[str]] = defaultdict(set)
        self.diagnosis_metadata: Dict[str, Dict] = {}
        self.indexed = False
    
    def build_index(self, families: Dict[str, List[Dict]]) -> None:
        """
        Build inverted index from all diagnostic trees.
        
        Args:
            families: Dict of family_name → list of diagnostic rules
        """
        logger.info("🔨 Building search index...")
        total_symptoms = 0
        total_diagnoses = 0
        
        for family_name, rules in families.items():
            for rule in rules:
                diagnosis_id = rule.get('id', '')
                presentations = rule.get('presentations', [])
                
                if not diagnosis_id:
                    continue
                
                # Store diagnosis metadata
                self.diagnosis_metadata[diagnosis_id] = {
                    'id': diagnosis_id,
                    'label': rule.get('label', ''),
                    'family': family_name,
                    'icd10': rule.get('icd10', []),
                    'presentations': presentations
                }
                
                total_diagnoses += 1
                
                # Index each presentation
                for presentation in presentations:
                    if not isinstance(presentation, str):
                        continue
                    
                    # Normalize and tokenize
                    normalized = self._normalize_text(presentation)
                    words = normalized.split()
                    
                    # Index individual words
                    for word in words:
                        if len(word) >= 3:  # Skip very short words
                            self.symptom_to_diagnoses[word].add(diagnosis_id)
                            total_symptoms += 1
                    
                    # Index bigrams for multi-word symptoms
                    for i in range(len(words) - 1):
                        bigram = f"{words[i]} {words[i+1]}"
                        self.symptom_to_diagnoses[bigram].add(diagnosis_id)
                    
                    # Index full phrase
                    if len(normalized) > 0:
                        self.symptom_to_diagnoses[normalized].add(diagnosis_id)
        
        self.indexed = True
        logger.info(f"✅ Search index built: {total_diagnoses} diagnoses, {len(self.symptom_to_diagnoses)} symptom keys")
    
    def search(self, symptoms: List[str]) -> Set[str]:
        """
        Fast lookup of diagnoses matching any of the symptoms.
        
        Args:
            symptoms: List of symptom strings
            
        Returns:
            Set of diagnosis IDs that match
        """
        if not self.indexed:
            return set()
        
        matching_diagnoses = set()
        
        for symptom in symptoms:
            normalized = self._normalize_text(symptom)
            
            # Look up full symptom
            if normalized in self.symptom_to_diagnoses:
                matching_diagnoses.update(self.symptom_to_diagnoses[normalized])
            
            # Look up individual words
            words = normalized.split()
            for word in words:
                if word in self.symptom_to_diagnoses:
                    matching_diagnoses.update(self.symptom_to_diagnoses[word])
        
        return matching_diagnoses
    
    def get_diagnosis_metadata(self, diagnosis_id: str) -> Dict:
        """Get metadata for a diagnosis by ID."""
        return self.diagnosis_metadata.get(diagnosis_id, {})
    
    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text for indexing (lowercase, remove punctuation)."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


# Global search index
search_index = SearchIndex()


def build_search_index_from_families(families: Dict[str, List[Dict]]) -> SearchIndex:
    """Build and return search index from families data."""
    index = SearchIndex()
    index.build_index(families)
    return index
