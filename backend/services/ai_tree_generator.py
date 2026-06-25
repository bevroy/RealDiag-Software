"""
AI Decision Tree Generator
Automatically creates diagnostic decision trees for symptom combinations not in database
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import openai
from anthropic import Anthropic

# Try to import medical code databases
try:
    from backend.data.icd10_codes import search_icd10_by_diagnosis
except ImportError:
    def search_icd10_by_diagnosis(diagnosis: str) -> list:
        return []

try:
    from backend.data.snomed_codes import get_snomed_codes_for_diagnosis
except ImportError:
    def get_snomed_codes_for_diagnosis(diagnosis: str) -> list:
        return []


class AITreeGenerator:
    """Generates diagnostic decision trees using LLM"""
    
    def __init__(self, provider: str = "openai", api_key: Optional[str] = None):
        """
        Initialize the generator
        
        Args:
            provider: "openai" or "claude"
            api_key: API key for the provider (reads from env if not provided)
        """
        self.provider = provider
        
        if provider == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if self.api_key:
                openai.api_key = self.api_key
        elif provider == "claude":
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if self.api_key:
                self.client = Anthropic(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _create_medical_prompt(self, symptoms: List[str], additional_context: Optional[str] = None) -> str:
        """Create the prompt for LLM to generate a decision tree"""
        
        symptoms_text = ", ".join(symptoms)
        
        prompt = f"""You are a medical expert creating a diagnostic decision tree. Generate a comprehensive diagnostic decision tree for a patient presenting with the following symptoms:

Symptoms: {symptoms_text}

{additional_context or ""}

Create a detailed decision tree in JSON format with the following structure:

{{
  "tree_id": "ai_generated_[unique_id]",
  "name": "[Primary diagnosis name]",
  "description": "[Brief clinical description]",
  "icd10": "[ICD-10 code if applicable]",
  "snomed": ["[SNOMED codes if applicable]"],
  "chief_complaint": "[Main presenting symptom]",
  "family": "[Medical specialty family]",
  "specialty": "[Specific specialty]",
  "urgency": "[emergent/urgent/routine]",
  "questions": [
    {{
      "id": "q1",
      "text": "[Diagnostic question]",
      "type": "boolean|multiple_choice",
      "answers": [
        {{
          "text": "[Answer text]",
          "next": "q2|diagnosis",
          "weight": 0.8
        }}
      ]
    }}
  ],
  "diagnosis": {{
    "name": "[Final diagnosis]",
    "confidence": 0.85,
    "clinical_presentation": "[Typical presentation]",
    "differential_diagnoses": ["[Alternative diagnosis 1]", "[Alternative diagnosis 2]"],
    "workup": [
      {{
        "test": "[Lab/imaging test]",
        "rationale": "[Why this test]",
        "findings": "[Expected findings]"
      }}
    ],
    "treatment": [
      {{
        "intervention": "[Treatment name]",
        "details": "[Treatment details]",
        "considerations": "[Special considerations]"
      }}
    ],
    "clinical_pearls": ["[Pearl 1]", "[Pearl 2]"],
    "red_flags": ["[Warning sign 1]", "[Warning sign 2]"],
    "referrals": ["[Specialty if needed]"],
    "follow_up": "[Follow-up recommendations]"
  }}
}}

Requirements:
1. Create 3-7 diagnostic questions that narrow down to specific diagnosis
2. Include differential diagnoses (at least 2-3 alternatives)
3. Provide evidence-based workup (labs, imaging)
4. Include first-line and alternative treatments
5. Add clinical pearls and red flags
6. Assign appropriate urgency level
7. Use current medical guidelines (2024-2025)
8. Include ICD-10 and SNOMED codes where applicable

Return ONLY the JSON object, no additional text."""

        return prompt
    
    async def generate_tree(
        self,
        symptoms: List[str],
        additional_context: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict:
        """
        Generate a decision tree for given symptoms
        
        Args:
            symptoms: List of presenting symptoms
            additional_context: Additional context (age, gender, history, etc.)
            temperature: LLM temperature (lower = more conservative)
            
        Returns:
            Dict containing the generated decision tree
        """
        if not symptoms:
            raise ValueError("At least one symptom required")
        
        prompt = self._create_medical_prompt(symptoms, additional_context)
        
        try:
            if self.provider == "openai":
                response = await self._generate_openai(prompt, temperature)
            elif self.provider == "claude":
                response = await self._generate_claude(prompt, temperature)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
            
            # Parse JSON response
            tree_data = json.loads(response)
            
            # Enrich with medical codes
            tree_data = self._enrich_with_codes(tree_data)
            
            # Add metadata
            tree_data["metadata"] = {
                "generated_by": "ai",
                "provider": self.provider,
                "generated_at": datetime.utcnow().isoformat(),
                "source_symptoms": symptoms,
                "status": "pending_review",
                "version": "1.0"
            }
            
            # Validate structure
            if self._validate_tree_structure(tree_data):
                return tree_data
            else:
                raise ValueError("Generated tree failed validation")
                
        except Exception as e:
            raise Exception(f"Tree generation failed: {str(e)}")
    
    async def _generate_openai(self, prompt: str, temperature: float) -> str:
        """Generate using OpenAI GPT-4"""
        response = await openai.ChatCompletion.acreate(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical expert specializing in diagnostic reasoning and clinical decision support. Generate accurate, evidence-based diagnostic decision trees."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=4000
        )
        return response.choices[0].message.content.strip()
    
    async def _generate_claude(self, prompt: str, temperature: float) -> str:
        """Generate using Anthropic Claude"""
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=temperature,
            system="You are a medical expert specializing in diagnostic reasoning and clinical decision support. Generate accurate, evidence-based diagnostic decision trees.",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return message.content[0].text.strip()
    
    def _enrich_with_codes(self, tree_data: Dict) -> Dict:
        """Enrich tree with ICD-10 and SNOMED codes from databases"""
        diagnosis_name = tree_data.get("diagnosis", {}).get("name", "")
        
        if diagnosis_name:
            # Add ICD-10 codes
            if not tree_data.get("icd10"):
                icd10_matches = search_icd10_by_diagnosis(diagnosis_name)
                if icd10_matches:
                    tree_data["icd10"] = icd10_matches[0]
            
            # Add SNOMED codes
            if not tree_data.get("snomed"):
                snomed_matches = get_snomed_codes_for_diagnosis(diagnosis_name)
                if snomed_matches:
                    tree_data["snomed"] = list(snomed_matches)
        
        return tree_data
    
    def _validate_tree_structure(self, tree_data: Dict) -> bool:
        """Validate that generated tree has required structure"""
        required_fields = ["tree_id", "name", "chief_complaint", "family", "specialty", "urgency", "questions", "diagnosis"]
        
        # Check top-level fields
        for field in required_fields:
            if field not in tree_data:
                return False
        
        # Validate questions
        if not isinstance(tree_data["questions"], list) or len(tree_data["questions"]) < 2:
            return False
        
        for question in tree_data["questions"]:
            if not all(k in question for k in ["id", "text", "answers"]):
                return False
        
        # Validate diagnosis
        diagnosis = tree_data["diagnosis"]
        if not isinstance(diagnosis, dict):
            return False
        
        if not all(k in diagnosis for k in ["name", "workup", "treatment"]):
            return False
        
        return True
    
    def save_tree(self, tree_data: Dict, status: str = "pending") -> str:
        """
        Save generated tree to file system
        
        Args:
            tree_data: The generated tree
            status: "pending" or "approved"
            
        Returns:
            File path where tree was saved
        """
        # Create directories if needed
        base_dir = "backend/data/generated_trees"
        status_dir = os.path.join(base_dir, status)
        os.makedirs(status_dir, exist_ok=True)
        
        # Generate filename
        tree_id = tree_data.get("tree_id", f"ai_gen_{datetime.utcnow().timestamp()}")
        filename = f"{tree_id}.json"
        filepath = os.path.join(status_dir, filename)
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(tree_data, f, indent=2)
        
        return filepath
    
    def load_pending_trees(self) -> List[Dict]:
        """Load all pending trees for review"""
        pending_dir = "backend/data/generated_trees/pending"
        if not os.path.exists(pending_dir):
            return []
        
        trees = []
        for filename in os.listdir(pending_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(pending_dir, filename)
                with open(filepath, 'r') as f:
                    trees.append(json.load(f))
        
        return trees
    
    def approve_tree(self, tree_id: str, reviewer_notes: Optional[str] = None) -> bool:
        """
        Approve a pending tree and move to approved directory
        
        Args:
            tree_id: ID of tree to approve
            reviewer_notes: Optional notes from reviewer
            
        Returns:
            True if successful
        """
        pending_path = f"backend/data/generated_trees/pending/{tree_id}.json"
        approved_path = f"backend/data/generated_trees/approved/{tree_id}.json"
        
        if not os.path.exists(pending_path):
            return False
        
        # Load tree
        with open(pending_path, 'r') as f:
            tree_data = json.load(f)
        
        # Update metadata
        tree_data["metadata"]["status"] = "approved"
        tree_data["metadata"]["approved_at"] = datetime.utcnow().isoformat()
        if reviewer_notes:
            tree_data["metadata"]["reviewer_notes"] = reviewer_notes
        
        # Save to approved directory
        os.makedirs(os.path.dirname(approved_path), exist_ok=True)
        with open(approved_path, 'w') as f:
            json.dump(tree_data, f, indent=2)
        
        # Remove from pending
        os.remove(pending_path)
        
        return True
    
    def reject_tree(self, tree_id: str, reason: str) -> bool:
        """
        Reject a pending tree
        
        Args:
            tree_id: ID of tree to reject
            reason: Reason for rejection
            
        Returns:
            True if successful
        """
        pending_path = f"backend/data/generated_trees/pending/{tree_id}.json"
        rejected_path = f"backend/data/generated_trees/rejected/{tree_id}.json"
        
        if not os.path.exists(pending_path):
            return False
        
        # Load tree
        with open(pending_path, 'r') as f:
            tree_data = json.load(f)
        
        # Update metadata
        tree_data["metadata"]["status"] = "rejected"
        tree_data["metadata"]["rejected_at"] = datetime.utcnow().isoformat()
        tree_data["metadata"]["rejection_reason"] = reason
        
        # Save to rejected directory
        os.makedirs(os.path.dirname(rejected_path), exist_ok=True)
        with open(rejected_path, 'w') as f:
            json.dump(tree_data, f, indent=2)
        
        # Remove from pending
        os.remove(pending_path)
        
        return True


# Convenience functions
async def generate_tree_from_symptoms(
    symptoms: List[str],
    provider: str = "openai",
    save: bool = True
) -> Dict:
    """
    Quick function to generate a tree from symptoms
    
    Args:
        symptoms: List of symptoms
        provider: "openai" or "claude"
        save: Whether to save to pending directory
        
    Returns:
        Generated tree data
    """
    generator = AITreeGenerator(provider=provider)
    tree = await generator.generate_tree(symptoms)
    
    if save:
        generator.save_tree(tree, status="pending")
    
    return tree
