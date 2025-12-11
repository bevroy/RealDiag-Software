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
    
    def _initialize_remedy_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize remedy database based on Boericke's Materia Medica and Kent's Repertory.
        Organized by symptom patterns and clinical conditions.
        """
        # Define cardiac remedies (reused for multiple conditions)
        cardiac_remedies = [
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
        
        return {
            # Cardiovascular conditions - symptoms
            "chest_pain": {
                "remedies": cardiac_remedies
            },
            
            # Cardiovascular conditions - diagnoses (aliases)
            "acute_coronary_syndrome": {
                "remedies": cardiac_remedies
            },
            "myocardial_infarction": {
                "remedies": cardiac_remedies
            },
            "angina": {
                "remedies": cardiac_remedies
            },
            "heart_attack": {
                "remedies": cardiac_remedies
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
            
            # Neurological conditions - symptoms
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
            
            # Headache/Migraine diagnoses (aliases)
            "migraine": {
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
            "tension_headache": {
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
            
            # Vertigo/Dizziness diagnoses (aliases)
            "dizziness": {
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
            
            # Respiratory conditions - symptoms
            respiratory_cough_remedies = {
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
            }
            
            # Add respiratory keys
            self.remedy_database["cough"] = respiratory_cough_remedies
            self.remedy_database["bronchitis"] = respiratory_cough_remedies
            self.remedy_database["acute_bronchitis"] = respiratory_cough_remedies
            self.remedy_database["chronic_bronchitis"] = respiratory_cough_remedies
            self.remedy_database["pneumonia"] = respiratory_cough_remedies
            self.remedy_database["community_acquired_pneumonia"] = respiratory_cough_remedies
            self.remedy_database["upper_respiratory_infection"] = respiratory_cough_remedies
            self.remedy_database["uri"] = respiratory_cough_remedies
            self.remedy_database["common_cold"] = respiratory_cough_remedies
            self.remedy_database["influenza"] = respiratory_cough_remedies
            self.remedy_database["flu"] = respiratory_cough_remedies
            
            respiratory_dyspnea_remedies = {
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
            }
            
            # Add dyspnea keys
            self.remedy_database["dyspnea"] = respiratory_dyspnea_remedies
            self.remedy_database["shortness_of_breath"] = respiratory_dyspnea_remedies
            self.remedy_database["asthma"] = respiratory_dyspnea_remedies
            self.remedy_database["copd"] = respiratory_dyspnea_remedies
            self.remedy_database["chronic_obstructive_pulmonary_disease"] = respiratory_dyspnea_remedies
            self.remedy_database["wheezing"] = respiratory_dyspnea_remedies
            
            # Gastrointestinal conditions - symptoms
            gi_nausea_remedies = {
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
            }
            
            # Add GI nausea keys
            self.remedy_database["nausea_vomiting"] = gi_nausea_remedies
            self.remedy_database["nausea"] = gi_nausea_remedies
            self.remedy_database["vomiting"] = gi_nausea_remedies
            self.remedy_database["gastritis"] = gi_nausea_remedies
            self.remedy_database["gastroenteritis"] = gi_nausea_remedies
            self.remedy_database["food_poisoning"] = gi_nausea_remedies
            
            gi_diarrhea_remedies = {
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
            }
            
            # Add diarrhea keys
            self.remedy_database["diarrhea"] = gi_diarrhea_remedies
            self.remedy_database["acute_diarrhea"] = gi_diarrhea_remedies
            self.remedy_database["travelers_diarrhea"] = gi_diarrhea_remedies
            self.remedy_database["infectious_diarrhea"] = gi_diarrhea_remedies
            
            gi_abdominal_pain_remedies = {
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
            }
            
            # Add abdominal pain keys
            self.remedy_database["abdominal_pain"] = gi_abdominal_pain_remedies
            self.remedy_database["stomach_pain"] = gi_abdominal_pain_remedies
            self.remedy_database["colitis"] = gi_abdominal_pain_remedies
            self.remedy_database["ibs"] = gi_abdominal_pain_remedies
            self.remedy_database["irritable_bowel_syndrome"] = gi_abdominal_pain_remedies
            self.remedy_database["cramps"] = gi_abdominal_pain_remedies
            self.remedy_database["gerd"] = gi_abdominal_pain_remedies
            self.remedy_database["acid_reflux"] = gi_abdominal_pain_remedies
            
            # Infectious/inflammatory - symptoms
            fever_remedies = {
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
            }
            
            # Add fever keys
            self.remedy_database["fever"] = fever_remedies
            self.remedy_database["high_fever"] = fever_remedies
            self.remedy_database["pyrexia"] = fever_remedies
            self.remedy_database["febrile_illness"] = fever_remedies
            
            # Musculoskeletal - symptoms
            joint_pain_remedies = {
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
            }
            
            # Add joint pain keys
            self.remedy_database["joint_pain"] = joint_pain_remedies
            self.remedy_database["arthritis"] = joint_pain_remedies
            self.remedy_database["osteoarthritis"] = joint_pain_remedies
            self.remedy_database["rheumatoid_arthritis"] = joint_pain_remedies
            self.remedy_database["arthralgia"] = joint_pain_remedies
            self.remedy_database["joint_stiffness"] = joint_pain_remedies
            
            back_pain_remedies = {
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
            }
            
            # Add back pain keys
            self.remedy_database["back_pain"] = back_pain_remedies
            self.remedy_database["low_back_pain"] = back_pain_remedies
            self.remedy_database["lumbago"] = back_pain_remedies
            self.remedy_database["sciatica"] = back_pain_remedies
            self.remedy_database["spinal_pain"] = back_pain_remedies
            
            # Anxiety/Mental - symptoms
            anxiety_remedies = {
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
            
            # Add anxiety keys
            self.remedy_database["anxiety"] = anxiety_remedies
            self.remedy_database["anxiety_disorder"] = anxiety_remedies
            self.remedy_database["panic_disorder"] = anxiety_remedies
            self.remedy_database["panic_attack"] = anxiety_remedies
            self.remedy_database["generalized_anxiety_disorder"] = anxiety_remedies
            self.remedy_database["gad"] = anxiety_remedies
            self.remedy_database["stress"] = anxiety_remedies
            self.remedy_database["nervousness"] = anxiety_remedies
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
        
        # Try exact match first
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
