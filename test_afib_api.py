"""
Test the symptom search API for atrial fibrillation
"""

from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Import the main app
sys.path.insert(0, str(Path(__file__).parent))
from main import app

client = TestClient(app)

def test_afib_symptom_search():
    """Test that atrial fibrillation appears for the reported symptoms"""
    
    print("=" * 80)
    print("Testing Atrial Fibrillation via API")
    print("=" * 80)
    
    # Test with the user's reported symptoms
    test_data = {
        "symptoms": ["palpitations", "dizziness", "irregular pulse"],
        "age": 65,
        "sex": "M"
    }
    
    print(f"\nRequest:")
    print(f"  Symptoms: {test_data['symptoms']}")
    print(f"  Age: {test_data['age']}")
    print(f"  Sex: {test_data['sex']}")
    print("-" * 80)
    
    response = client.post("/search/by-symptoms", json=test_data)
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"ERROR: {response.json()}")
        return
    
    data = response.json()
    results = data.get("results", [])
    
    print(f"Total Results: {data.get('total_results', 0)}")
    print("\nTop 10 Results:")
    print("-" * 80)
    
    afib_found = False
    afib_rank = None
    afib_score = None
    
    for i, result in enumerate(results[:10], 1):
        label = result.get("label", "Unknown")
        score = result.get("match_score", 0)
        matched = result.get("matched_presentations", [])
        
        is_afib = "atrial fibrillation" in label.lower()
        marker = " ← ATRIAL FIBRILLATION ✓" if is_afib else ""
        
        print(f"{i}. {label} (Score: {score:.2f}){marker}")
        
        if is_afib:
            afib_found = True
            afib_rank = i
            afib_score = score
            print(f"   Matched presentations: {len(matched)}")
            for mp in matched[:3]:
                print(f"     • {mp}")
    
    print("\n" + "=" * 80)
    if afib_found:
        print(f"✓ SUCCESS: Atrial Fibrillation found in results")
        print(f"  Rank: #{afib_rank}")
        print(f"  Match Score: {afib_score:.2f}")
    else:
        print(f"✗ FAILURE: Atrial Fibrillation NOT in top 10 results")
        print(f"\nSearching all results...")
        for i, result in enumerate(results, 1):
            if "atrial fibrillation" in result.get("label", "").lower():
                print(f"  Found at rank #{i} with score {result.get('match_score', 0):.2f}")
                afib_found = True
                break
        if not afib_found:
            print(f"  Atrial Fibrillation not found in any results")
    print("=" * 80)


if __name__ == "__main__":
    test_afib_symptom_search()
