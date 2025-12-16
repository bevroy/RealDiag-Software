"""
AI Content Enricher for Diagnostic Trees
Automatically generates missing clinical content (treatment, pearls, referrals, homeopathy)
"""

import json
import os
from typing import Dict, List, Optional
from anthropic import Anthropic
import openai


class AIContentEnricher:
    """Enriches diagnostic tree data with AI-generated clinical content"""
    
    def __init__(self, provider: str = "claude", api_key: Optional[str] = None):
        """
        Initialize the enricher
        
        Args:
            provider: "openai" or "claude" (default: claude for medical content)
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
    
    def _create_enrichment_prompt(
        self, 
        diagnosis_name: str,
        icd10: str,
        existing_data: Dict,
        missing_sections: List[str]
    ) -> str:
        """Create prompt for generating missing clinical content"""
        
        sections_text = ", ".join(missing_sections)
        
        prompt = f"""You are a medical expert. Generate comprehensive clinical content for the following diagnosis:

Diagnosis: {diagnosis_name}
ICD-10: {icd10 or "Not specified"}

Existing information:
{json.dumps(existing_data, indent=2)}

Please generate the following MISSING sections: {sections_text}

Provide your response as a JSON object with these exact keys (only include sections that are missing):

{{
  "workup": [
    "Detailed workup item 1 with rationale",
    "Detailed workup item 2 with specific tests",
    "Include lab values, imaging, physical exam findings"
  ],
  "treatment": [
    "First-line treatment with specific medications and dosages",
    "Alternative treatments with clear indications",
    "When to escalate care or adjust therapy",
    "Non-pharmacologic interventions"
  ],
  "clinical_pearls": [
    "Key diagnostic pearl or red flag",
    "Common pitfall to avoid",
    "Practice tip for management",
    "Prognostic information"
  ],
  "referrals": [
    "Specialty to refer to: indication for referral",
    "Emergency department: urgent criteria",
    "Additional specialty: specific indications"
  ],
  "homeopathy": [
    {{
      "remedy": "Remedy Name Potency (e.g., Arnica 30C)",
      "indications": "Specific symptom pattern and modalities"
    }},
    {{
      "remedy": "Another Remedy 30C",
      "indications": "Different symptom presentation"
    }}
  ],
  "presentations": [
    "Common presenting symptom 1",
    "Typical clinical presentation 2",
    "Key historical features"
  ]
}}

IMPORTANT GUIDELINES:
1. Base all recommendations on current evidence-based medical guidelines
2. Include specific medication names, dosages, and durations when applicable
3. Clinical pearls should be actionable and clinically relevant
4. Homeopathic remedies should match classical indications with constitutional types
5. Referral criteria should be clear and specific
6. Workup should follow standard diagnostic algorithms
7. Be concise but comprehensive - aim for 3-5 items per section
8. Use professional medical terminology appropriately

Return ONLY the JSON object, no additional text."""

        return prompt
    
    async def enrich_diagnosis(
        self,
        diagnosis_name: str,
        icd10: str = "",
        existing_data: Optional[Dict] = None,
        temperature: float = 0.3
    ) -> Dict:
        """
        Generate missing clinical content for a diagnosis
        
        Args:
            diagnosis_name: Name of the diagnosis
            icd10: ICD-10 code (optional)
            existing_data: Already available data (to avoid regenerating)
            temperature: LLM temperature (lower = more conservative)
            
        Returns:
            Dict containing the enriched clinical content
        """
        if existing_data is None:
            existing_data = {}
        
        # Determine which sections are missing or empty
        missing_sections = []
        if not existing_data.get('workup'):
            missing_sections.append('workup')
        if not existing_data.get('treatment'):
            missing_sections.append('treatment')
        if not existing_data.get('clinical_pearls'):
            missing_sections.append('clinical_pearls')
        if not existing_data.get('referrals'):
            missing_sections.append('referrals')
        if not existing_data.get('homeopathic_remedies') and not existing_data.get('homeopathy'):
            missing_sections.append('homeopathy')
        if not existing_data.get('presentations'):
            missing_sections.append('presentations')
        
        # If nothing is missing, return existing data
        if not missing_sections:
            return existing_data
        
        # Generate content
        prompt = self._create_enrichment_prompt(
            diagnosis_name, 
            icd10, 
            existing_data,
            missing_sections
        )
        
        try:
            if self.provider == "claude":
                response = await self._generate_claude(prompt, temperature)
            else:
                response = await self._generate_openai(prompt, temperature)
            
            # Parse JSON response
            enriched_data = json.loads(response)
            
            # Merge with existing data (don't overwrite existing content)
            result = {**existing_data}
            for key, value in enriched_data.items():
                if not result.get(key):
                    result[key] = value
            
            # Add metadata about AI generation
            result['ai_enriched'] = True
            result['ai_enriched_sections'] = missing_sections
            
            return result
            
        except Exception as e:
            print(f"Error enriching diagnosis: {e}")
            # Return original data if enrichment fails
            return existing_data
    
    async def _generate_claude(self, prompt: str, temperature: float) -> str:
        """Generate content using Claude"""
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            temperature=temperature,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return message.content[0].text
    
    async def _generate_openai(self, prompt: str, temperature: float) -> str:
        """Generate content using OpenAI"""
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a medical expert providing evidence-based clinical information. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=4096
        )
        
        return response.choices[0].message.content
    
    def detect_missing_content(self, clinical_data: Dict) -> List[str]:
        """
        Detect which sections are missing or incomplete
        
        Args:
            clinical_data: Clinical data dict from tree
            
        Returns:
            List of missing section names
        """
        missing = []
        
        # Check each important section
        if not clinical_data.get('workup') or len(clinical_data.get('workup', [])) == 0:
            missing.append('workup')
        if not clinical_data.get('treatment') or len(clinical_data.get('treatment', [])) == 0:
            missing.append('treatment')
        if not clinical_data.get('clinical_pearls') or len(clinical_data.get('clinical_pearls', [])) == 0:
            missing.append('clinical_pearls')
        if not clinical_data.get('referrals') or len(clinical_data.get('referrals', [])) == 0:
            missing.append('referrals')
        if not clinical_data.get('homeopathic_remedies') or len(clinical_data.get('homeopathic_remedies', [])) == 0:
            missing.append('homeopathic_remedies')
        if not clinical_data.get('presentations') or len(clinical_data.get('presentations', [])) == 0:
            missing.append('presentations')
        
        return missing
