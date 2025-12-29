#!/usr/bin/env python3
"""
Test AI diagnosis suggestions feature.
Shows how symptom search now queries AI for additional diagnoses when tree results are insufficient.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Enable AI for testing
os.environ["ENABLE_AI_GENERATION"] = "true"

from fastapi.testclient import TestClient
from main import app

def test_ai_suggestions():
    """Test that AI provides additional diagnoses when tree results are limited."""
    print("\n" + "="*70)
    print("AI-POWERED DIAGNOSIS SUGGESTIONS - TEST")
    print("="*70)
    
    client = TestClient(app)
    
    # Test 1: Obscure symptom combination that may have few tree matches
    print("\n📋 TEST 1: Unusual symptom combination")
    print("-" * 70)
    print("Symptoms: 'jaw pain', 'fatigue', 'shortness of breath with exertion'")
    print("(This could be atypical angina, especially in women)")
    
    response = client.post(
        "/search/by-symptoms",
        json={
            "symptoms": ["jaw pain", "fatigue", "shortness of breath with exertion"],
            "age": 55,
            "sex": "F"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Status: {response.status_code}")
        print(f"📊 Total Results: {data['total_results']}")
        
        # Separate tree-based from AI-suggested
        tree_results = [r for r in data['results'] if not r.get('ai_suggested', False)]
        ai_results = [r for r in data['results'] if r.get('ai_suggested', False)]
        
        print(f"\n🌳 Results from decision trees: {len(tree_results)}")
        if tree_results:
            for i, r in enumerate(tree_results[:3], 1):
                print(f"   {i}. {r['label']} (Score: {r['match_score']})")
        
        print(f"\n🤖 AI-suggested diagnoses (no tree yet): {len(ai_results)}")
        if ai_results:
            for i, r in enumerate(ai_results[:5], 1):
                icd10 = ', '.join(r.get('icd10', []))
                print(f"   {i}. {r['label']} (Score: {r['match_score']})")
                print(f"      Specialty: {r['family']}")
                if icd10:
                    print(f"      ICD-10: {icd10}")
                print(f"      💡 User can request AI to generate decision tree")
        else:
            print("   ⚠️  No AI suggestions (AI may be disabled or sufficient tree matches found)")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.json())
    
    # Test 2: Very specific rare symptom
    print("\n\n📋 TEST 2: Rare symptom combination")
    print("-" * 70)
    print("Symptoms: 'periodic fever', 'mouth ulcers', 'swollen lymph nodes'")
    print("(Could indicate PFAPA syndrome or other periodic fever syndromes)")
    
    response = client.post(
        "/search/by-symptoms",
        json={
            "symptoms": ["periodic fever", "mouth ulcers", "swollen lymph nodes"],
            "age": 4
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Status: {response.status_code}")
        print(f"📊 Total Results: {data['total_results']}")
        
        tree_results = [r for r in data['results'] if not r.get('ai_suggested', False)]
        ai_results = [r for r in data['results'] if r.get('ai_suggested', False)]
        
        print(f"\n🌳 Tree-based: {len(tree_results)}")
        print(f"🤖 AI-suggested: {len(ai_results)}")
        
        if ai_results:
            print(f"\nTop AI suggestions:")
            for i, r in enumerate(ai_results[:3], 1):
                print(f"   {i}. {r['label']}")
                key_features = r.get('matched_presentations', [])
                if key_features:
                    print(f"      Key features: {', '.join(key_features[:2])}")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70)
    print("\n💡 KEY FEATURES:")
    print("   • AI queries triggered when <5 tree results OR low match scores")
    print("   • AI suggests up to 10 additional diagnoses from medical knowledge")
    print("   • Results flagged with ai_suggested=True and has_tree=False")
    print("   • Users can request tree generation for any AI-suggested diagnosis")
    print("   • Covers rare conditions not in your 676 existing trees")
    print("\n")

if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  WARNING: No AI API key found")
        print("Set ANTHROPIC_API_KEY or OPENAI_API_KEY to test AI suggestions")
        print("Continuing with limited functionality...\n")
    
    try:
        test_ai_suggestions()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
