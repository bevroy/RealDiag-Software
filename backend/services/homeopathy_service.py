"""
Homeopathy Remedy Service
==========================

Provides complementary homeopathic remedy suggestions based on symptoms.
Based on classical homeopathic materia medica and repertory references.

IMPORTANT DISCLAIMER: Homeopathic remedies are complementary and should not 
replace conventional medical diagnosis and treatment. Always consult with a 
licensed healthcare provider for medical conditions.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class HomeopathicRemedy(BaseModel):
    """Homeopathic remedy suggestion."""
    name: str
    common_name: Optional[str] = None
    potency: str = "30C"  # Common potency
    indications: List[str] = []
    modalities: Optional[str] = None  # Better/worse with
    constitution: Optional[str] = None  # Constitutional type
    source: str = "Classical Homeopathic Materia Medica"


class HomeopathyService:
    """Service for homeopathic remedy suggestions."""
    
    def __init__(self):
        self.remedy_database = self._initialize_remedy_database()
        self.condition_aliases = self._initialize_condition_aliases()
    
    def _initialize_condition_aliases(self) -> Dict[str, str]:
        """
        Map disease diagnosis names to symptom keys in the remedy database.
        This allows the API to accept both symptom descriptions and diagnostic names.
        """
        return {
            # Cardiac conditions → chest_pain
            "acute_coronary_syndrome": "chest_pain",
            "myocardial_infarction": "chest_pain",
            "angina": "chest_pain",
            "heart_attack": "chest_pain",
            "cardiac_ischemia": "chest_pain",
            "unstable_angina": "chest_pain",
            
            # Neurological conditions → headache
            "migraine": "headache",
            "tension_headache": "headache",
            "cluster_headache": "headache",
            "cephalalgia": "headache",
            
            # Vertigo/dizziness → vertigo
            "dizziness": "vertigo",
            "benign_positional_vertigo": "vertigo",
            "bppv": "vertigo",
            
            # Respiratory conditions → cough
            "bronchitis": "cough",
            "acute_bronchitis": "cough",
            "chronic_bronchitis": "cough",
            "pneumonia": "cough",
            "community_acquired_pneumonia": "cough",
            "upper_respiratory_infection": "cough",
            "uri": "cough",
            "common_cold": "cough",
            "influenza": "cough",
            "flu": "cough",
            "tracheitis": "cough",
            
            # Respiratory conditions → dyspnea
            "shortness_of_breath": "dyspnea",
            "asthma": "dyspnea",
            "copd": "dyspnea",
            "chronic_obstructive_pulmonary_disease": "dyspnea",
            "wheezing": "dyspnea",
            "respiratory_distress": "dyspnea",
            
            # GI conditions → nausea_vomiting
            "gastritis": "nausea_vomiting",
            "gastroenteritis": "nausea_vomiting",
            "food_poisoning": "nausea_vomiting",
            "morning_sickness": "nausea_vomiting",
            "hyperemesis": "nausea_vomiting",
            
            # GI conditions → diarrhea
            "acute_diarrhea": "diarrhea",
            "travelers_diarrhea": "diarrhea",
            "infectious_diarrhea": "diarrhea",
            
            # GI conditions → abdominal_pain
            "colitis": "abdominal_pain",
            "ibs": "abdominal_pain",
            "irritable_bowel_syndrome": "abdominal_pain",
            "gerd": "abdominal_pain",
            "acid_reflux": "abdominal_pain",
            "stomach_pain": "abdominal_pain",
            "gastric_pain": "abdominal_pain",
            
            # Fever conditions
            "pyrexia": "fever",
            "febrile_illness": "fever",
            "high_fever": "fever",
            
            # Musculoskeletal → joint_pain
            "arthritis": "joint_pain",
            "osteoarthritis": "joint_pain",
            "rheumatoid_arthritis": "joint_pain",
            "arthralgia": "joint_pain",
            "joint_stiffness": "joint_pain",
            "polyarthralgia": "joint_pain",
            
            # Musculoskeletal → back_pain
            "low_back_pain": "back_pain",
            "lumbago": "back_pain",
            "sciatica": "back_pain",
            "spinal_pain": "back_pain",
            "dorsalgia": "back_pain",
            
            # Mental health → anxiety
            "anxiety_disorder": "anxiety",
            "panic_disorder": "anxiety",
            "panic_attack": "anxiety",
            "generalized_anxiety_disorder": "anxiety",
            "gad": "anxiety",
            "stress": "anxiety",
            "nervousness": "anxiety",
            
            # Endocrine/metabolic (map to most relevant symptom)
            "diabetes": "nausea_vomiting",  # GI symptoms common in DM
            "diabetes_mellitus": "nausea_vomiting",
            "type_1_diabetes": "nausea_vomiting",
            "type_2_diabetes": "nausea_vomiting",
            "type_2_diabetes_mellitus": "nausea_vomiting",
            "hypoglycemia": "anxiety",  # Anxiety/tremor common
            "hypothyroidism": "fever",  # Fatigue/lethargy
            "hyperthyroidism": "anxiety",  # Anxiety/palpitations
            "thyroid_disorder": "anxiety",
            
            # More respiratory
            "pneumonia_community_acquired": "cough",
            "acute_bronchiolitis": "cough",
            "croup": "cough",
            "pertussis": "cough",
            "whooping_cough": "cough",
            "tuberculosis": "cough",
            "tb": "cough",
            "pleural_effusion": "dyspnea",
            "pulmonary_edema": "dyspnea",
            "congestive_heart_failure": "dyspnea",
            "chf": "dyspnea",
            "heart_failure": "dyspnea",
            
            # More GI
            "peptic_ulcer": "abdominal_pain",
            "duodenal_ulcer": "abdominal_pain",
            "gastric_ulcer": "abdominal_pain",
            "pancreatitis": "abdominal_pain",
            "appendicitis": "abdominal_pain",
            "cholecystitis": "abdominal_pain",
            "gallstones": "abdominal_pain",
            "inflammatory_bowel_disease": "abdominal_pain",
            "crohns_disease": "abdominal_pain",
            "ulcerative_colitis": "abdominal_pain",
            
            # Neurological
            "stroke": "headache",
            "cva": "headache",
            "cerebrovascular_accident": "headache",
            "tia": "headache",
            "transient_ischemic_attack": "headache",
            "seizure": "headache",
            "epilepsy": "headache",
            "meningitis": "headache",
            "encephalitis": "headache",
        }
    
    def _initialize_remedy_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize remedy database based on Boericke's Materia Medica and Kent's Repertory.
        Organized by symptom patterns and clinical conditions.
        """
        return {
            # Cardiovascular conditions
            "chest_pain": {
                "remedies": [
                    {
                        "name": "Aconitum napellus",
                        "common_name": "Monkshood",
                        "potency": "30C",
                        "indications": ["Sudden onset chest pain", "Anxiety with chest pain", "Fear of death", "Palpitations"],
                        "modalities": "Worse: Evening, night, warm room. Better: Open air",
                        "constitution": "Acute, sudden onset conditions with anxiety"
                    },
                    {
                        "name": "Cactus grandiflorus",
                        "common_name": "Night-blooming Cereus",
                        "potency": "30C",
                        "indications": ["Constriction around chest", "Heart feels gripped", "Angina-like symptoms"],
                        "modalities": "Worse: Lying on left side, 11am and 11pm",
                        "constitution": "Cardiac affections with constriction"
                    },
                    {
                        "name": "Arnica montana",
                        "common_name": "Leopard's Bane",
                        "potency": "30C",
                        "indications": ["Chest pain after injury or exertion", "Bruised feeling", "Fear of being touched"],
                        "modalities": "Worse: Touch, motion. Better: Lying down",
                        "constitution": "Trauma, overexertion"
                    }
                ]
            },
            
            # Neurological conditions
            "headache": {
                "remedies": [
                    {
                        "name": "Belladonna",
                        "common_name": "Deadly Nightshade",
                        "potency": "30C",
                        "indications": ["Throbbing headache", "Sudden violent onset", "Red face", "Photophobia"],
                        "modalities": "Worse: Light, noise, jarring. Better: Dark room, pressure",
                        "constitution": "Acute inflammatory conditions"
                    },
                    {
                        "name": "Gelsemium sempervirens",
                        "common_name": "Yellow Jasmine",
                        "potency": "30C",
                        "indications": ["Occipital headache", "Heavy eyelids", "Drowsiness", "Visual disturbances"],
                        "modalities": "Worse: Heat, humidity, anticipation. Better: Urination",
                        "constitution": "Nervous exhaustion, anticipatory anxiety"
                    },
                    {
                        "name": "Natrum muriaticum",
                        "common_name": "Table Salt",
                        "potency": "30C",
                        "indications": ["Blinding headache", "Worse from sun", "Migraine with visual aura", "Numbness"],
                        "modalities": "Worse: 10-11am, sun, consolation. Better: Open air, cold applications",
                        "constitution": "Introverted, sensitive to criticism"
                    }
                ]
            },
            
            "vertigo": {
                "remedies": [
                    {
                        "name": "Conium maculatum",
                        "common_name": "Poison Hemlock",
                        "potency": "30C",
                        "indications": ["Vertigo on turning in bed", "Worse lying down", "Objects seem to move"],
                        "modalities": "Worse: Turning head, lying down, light. Better: Motion, pressure",
                        "constitution": "Elderly, debility, trembling"
                    },
                    {
                        "name": "Cocculus indicus",
                        "common_name": "Indian Cockle",
                        "potency": "30C",
                        "indications": ["Vertigo with nausea", "Motion sickness", "Worse rising from lying"],
                        "modalities": "Worse: Loss of sleep, motion, open air. Better: Lying quietly",
                        "constitution": "Travel sickness, sleep deprivation"
                    }
                ]
            },
            
            # Respiratory conditions
            "cough": {
                "remedies": [
                    {
                        "name": "Bryonia alba",
                        "common_name": "White Bryony",
                        "potency": "30C",
                        "indications": ["Dry painful cough", "Worse with movement", "Holds chest when coughing"],
                        "modalities": "Worse: Motion, deep breath, heat. Better: Pressure, rest, cool air",
                        "constitution": "Slow onset, wants to be left alone"
                    },
                    {
                        "name": "Drosera rotundifolia",
                        "common_name": "Sundew",
                        "potency": "30C",
                        "indications": ["Spasmodic cough", "Whooping cough", "Worse after midnight", "Choking sensation"],
                        "modalities": "Worse: After midnight, lying down, warmth. Better: Open air, pressure",
                        "constitution": "Violent spasmodic cough"
                    },
                    {
                        "name": "Phosphorus",
                        "common_name": "Phosphorus",
                        "potency": "30C",
                        "indications": ["Dry tickling cough", "Hoarseness", "Burning in chest", "Thirst for cold drinks"],
                        "modalities": "Worse: Evening, lying left side, cold air. Better: Sleep, massage",
                        "constitution": "Tall, slender, sensitive, anxious"
                    }
                ]
            },
            
            "dyspnea": {
                "remedies": [
                    {
                        "name": "Arsenicum album",
                        "common_name": "White Arsenic",
                        "potency": "30C",
                        "indications": ["Wheezing worse after midnight", "Anxiety with dyspnea", "Restlessness", "Burning pains"],
                        "modalities": "Worse: After midnight (1-2am), cold. Better: Warmth, sitting up",
                        "constitution": "Anxious, restless, fastidious"
                    },
                    {
                        "name": "Antimonium tartaricum",
                        "common_name": "Tartar Emetic",
                        "potency": "30C",
                        "indications": ["Rattling cough with dyspnea", "Cannot expectorate", "Drowsiness"],
                        "modalities": "Worse: Lying down, warmth, damp. Better: Sitting up, expectoration",
                        "constitution": "Weakness, rattling mucus"
                    }
                ]
            },
            
            # Gastrointestinal conditions
            "nausea_vomiting": {
                "remedies": [
                    {
                        "name": "Ipecacuanha",
                        "common_name": "Ipecac Root",
                        "potency": "30C",
                        "indications": ["Persistent nausea", "Clean tongue", "Nausea not relieved by vomiting"],
                        "modalities": "Worse: Warm moist weather, motion. Better: Open air, rest",
                        "constitution": "Nausea predominates"
                    },
                    {
                        "name": "Nux vomica",
                        "common_name": "Poison Nut",
                        "potency": "30C",
                        "indications": ["Nausea from overindulgence", "Irritability", "Wants to vomit but cannot"],
                        "modalities": "Worse: Morning, stimulants, anger. Better: Evening, rest, warmth",
                        "constitution": "Type A personality, overworked, stimulant abuse"
                    }
                ]
            },
            
            "diarrhea": {
                "remedies": [
                    {
                        "name": "Podophyllum peltatum",
                        "common_name": "May Apple",
                        "potency": "30C",
                        "indications": ["Profuse watery diarrhea", "Gushing", "Worse in morning", "Painless"],
                        "modalities": "Worse: Early morning (4-5am), hot weather. Better: Lying on abdomen",
                        "constitution": "Summer diarrhea, teething children"
                    },
                    {
                        "name": "Aloe socotrina",
                        "common_name": "Socotrine Aloes",
                        "potency": "30C",
                        "indications": ["Sudden urging", "Insecurity of rectum", "Worse immediately after eating"],
                        "modalities": "Worse: Early morning, after eating. Better: Cold applications",
                        "constitution": "Urgent, explosive diarrhea"
                    }
                ]
            },
            
            "abdominal_pain": {
                "remedies": [
                    {
                        "name": "Colocynthis",
                        "common_name": "Bitter Cucumber",
                        "potency": "30C",
                        "indications": ["Cutting, cramping pain", "Better bending double", "Better pressure", "Colic"],
                        "modalities": "Worse: Eating, anger. Better: Doubling up, hard pressure, warmth",
                        "constitution": "Cramping, colicky pains"
                    },
                    {
                        "name": "Magnesia phosphorica",
                        "common_name": "Magnesium Phosphate",
                        "potency": "30C",
                        "indications": ["Spasmodic pain", "Better warmth and pressure", "Neuralgic pains"],
                        "modalities": "Worse: Cold, touch, night. Better: Warmth, pressure, doubling up",
                        "constitution": "Cramping, spasmodic pains"
                    }
                ]
            },
            
            # Infectious/inflammatory
            "fever": {
                "remedies": [
                    {
                        "name": "Aconitum napellus",
                        "common_name": "Monkshood",
                        "potency": "30C",
                        "indications": ["Sudden high fever", "Dry burning skin", "Anxiety", "Thirst for cold water"],
                        "modalities": "Worse: Evening, night, warm room. Better: Open air",
                        "constitution": "First stage of fever, sudden onset"
                    },
                    {
                        "name": "Ferrum phosphoricum",
                        "common_name": "Iron Phosphate",
                        "potency": "30C",
                        "indications": ["Early stage fever", "No clear symptoms", "Gradual onset", "Flushed face"],
                        "modalities": "Worse: Night, touch, jarring. Better: Cold applications",
                        "constitution": "First stage inflammation, vague symptoms"
                    }
                ]
            },
            
            # Musculoskeletal
            "joint_pain": {
                "remedies": [
                    {
                        "name": "Rhus toxicodendron",
                        "common_name": "Poison Ivy",
                        "potency": "30C",
                        "indications": ["Stiffness worse on first motion", "Better continued motion", "Worse rest and cold"],
                        "modalities": "Worse: Rest, cold, damp, initial motion. Better: Continued motion, warmth",
                        "constitution": "Rheumatic complaints, restless"
                    },
                    {
                        "name": "Bryonia alba",
                        "common_name": "White Bryony",
                        "potency": "30C",
                        "indications": ["Worse slightest motion", "Better pressure and rest", "Stitching pains"],
                        "modalities": "Worse: Motion, heat, touch. Better: Pressure, rest, cold",
                        "constitution": "Wants to be still, irritable"
                    }
                ]
            },
            
            "back_pain": {
                "remedies": [
                    {
                        "name": "Arnica montana",
                        "common_name": "Leopard's Bane",
                        "potency": "30C",
                        "indications": ["Soreness from overexertion", "Bruised feeling", "Bed feels too hard"],
                        "modalities": "Worse: Touch, motion, dampness. Better: Lying down",
                        "constitution": "Trauma, overexertion, soreness"
                    },
                    {
                        "name": "Hypericum perforatum",
                        "common_name": "St. John's Wort",
                        "potency": "30C",
                        "indications": ["Nerve pain", "Shooting pains", "Injury to nerve-rich areas", "Tailbone pain"],
                        "modalities": "Worse: Touch, cold, jarring. Better: Bending backward",
                        "constitution": "Nerve injuries, puncture wounds"
                    }
                ]
            },
            
            # Anxiety/Mental
            "anxiety": {
                "remedies": [
                    {
                        "name": "Argentum nitricum",
                        "common_name": "Silver Nitrate",
                        "potency": "30C",
                        "indications": ["Anticipatory anxiety", "Fear of heights", "Claustrophobia", "Impulsive"],
                        "modalities": "Worse: Warmth, crowds, anticipation. Better: Cool air, pressure",
                        "constitution": "Performance anxiety, impulsive, hurried"
                    },
                    {
                        "name": "Gelsemium sempervirens",
                        "common_name": "Yellow Jasmine",
                        "potency": "30C",
                        "indications": ["Anticipation anxiety", "Trembling", "Weakness", "Drowsiness"],
                        "modalities": "Worse: Anticipation, bad news, humidity. Better: Urination, open air",
                        "constitution": "Stage fright, exam anxiety"
                    }
                ]
            }
        }
    
    def get_remedies_for_condition(self, condition: str) -> List[HomeopathicRemedy]:
        """
        Get homeopathic remedy suggestions for a given condition.
        
        Args:
            condition: Clinical condition or symptom pattern
            
        Returns:
            List of HomeopathicRemedy objects
        """
        # Normalize condition name
        condition_key = condition.lower().replace(" ", "_").replace("-", "_")
        
        # Check if this is an alias for another condition
        if condition_key in self.condition_aliases:
            condition_key = self.condition_aliases[condition_key]
        
        # Try exact match
        if condition_key in self.remedy_database:
            remedies_data = self.remedy_database[condition_key]["remedies"]
            return [HomeopathicRemedy(**remedy) for remedy in remedies_data]
        
        # Try partial matching
        for key in self.remedy_database.keys():
            if condition_key in key or key in condition_key:
                remedies_data = self.remedy_database[key]["remedies"]
                return [HomeopathicRemedy(**remedy) for remedy in remedies_data]
        
        return []
    
    def get_remedies_for_symptoms(self, symptoms: List[str]) -> List[HomeopathicRemedy]:
        """
        Get homeopathic remedies based on symptom list.
        
        Args:
            symptoms: List of symptoms
            
        Returns:
            List of HomeopathicRemedy objects
        """
        all_remedies = []
        seen_remedies = set()
        
        for symptom in symptoms:
            remedies = self.get_remedies_for_condition(symptom)
            for remedy in remedies:
                if remedy.name not in seen_remedies:
                    all_remedies.append(remedy)
                    seen_remedies.add(remedy.name)
        
        return all_remedies[:5]  # Return top 5 most relevant


# Singleton instance
_homeopathy_service = HomeopathyService()


def get_homeopathy_service() -> HomeopathyService:
    """Get the homeopathy service singleton."""
    return _homeopathy_service
