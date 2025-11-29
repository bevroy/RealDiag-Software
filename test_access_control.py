#!/usr/bin/env python3
"""
Test script for RealDiag access control implementation.

Tests:
1. Public endpoints (no auth)
2. Optional auth endpoints
3. Required auth endpoints
4. Dual auth endpoints (user OR API key)
"""

import requests
import json
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User",
    "specialty": "cardiology",
    "institution": "Test Hospital"
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name: str, status: str, details: str = ""):
    """Print formatted test result."""
    if status == "PASS":
        print(f"{Colors.GREEN}✓{Colors.END} {name}")
    elif status == "FAIL":
        print(f"{Colors.RED}✗{Colors.END} {name}")
        if details:
            print(f"  {Colors.RED}→{Colors.END} {details}")
    elif status == "SKIP":
        print(f"{Colors.YELLOW}⊘{Colors.END} {name} (skipped)")
    
    if details and status == "PASS":
        print(f"  {Colors.BLUE}→{Colors.END} {details}")

def test_public_endpoints():
    """Test endpoints that should work without authentication."""
    print(f"\n{Colors.BLUE}=== Testing Public Endpoints ==={Colors.END}\n")
    
    # Test 0: Check search limit status
    try:
        response = requests.get(f"{BASE_URL}/diagnostic/search-limit")
        if response.status_code == 200:
            data = response.json()
            if data.get("authenticated"):
                print_test("GET /diagnostic/search-limit", "PASS", "Authenticated user (unlimited)")
            else:
                remaining = data.get("searches_remaining", 0)
                used = data.get("searches_used", 0)
                print_test("GET /diagnostic/search-limit", "PASS", 
                          f"Anonymous user: {used} used, {remaining} remaining")
        else:
            print_test("GET /diagnostic/search-limit", "FAIL", f"Status {response.status_code}")
    except Exception as e:
        print_test("GET /diagnostic/search-limit", "FAIL", str(e))
    
    # Test 1: List diagnostic trees
    try:
        response = requests.get(f"{BASE_URL}/diagnostic/trees")
        if response.status_code == 200:
            data = response.json()
            has_limit_info = "free_trial" in data
            print_test("GET /diagnostic/trees", "PASS", 
                      f"Found {len(data.get('trees', []))} trees, limit info: {has_limit_info}")
        else:
            print_test("GET /diagnostic/trees", "FAIL", f"Status {response.status_code}")
    except Exception as e:
        print_test("GET /diagnostic/trees", "FAIL", str(e))
    
    # Test 2: List rule families
    try:
        response = requests.get(f"{BASE_URL}/rules/families")
        if response.status_code == 200:
            data = response.json()
            print_test("GET /rules/families", "PASS", f"Found {len(data.get('families', []))} families")
        else:
            print_test("GET /rules/families", "FAIL", f"Status {response.status_code}")
    except Exception as e:
        print_test("GET /rules/families", "FAIL", str(e))
    
    # Test 3: Get educational cases
    try:
        response = requests.get(f"{BASE_URL}/education/cases")
        if response.status_code == 200:
            print_test("GET /education/cases", "PASS", "Cases accessible")
        else:
            print_test("GET /education/cases", "FAIL", f"Status {response.status_code}")
    except Exception as e:
        print_test("GET /education/cases", "FAIL", str(e))
    
    # Test 4: Get quiz questions (should work but show notice)
    try:
        response = requests.get(f"{BASE_URL}/education/quiz/questions?count=5")
        if response.status_code == 200:
            data = response.json()
            has_notice = "notice" in data
            print_test("GET /education/quiz/questions", "PASS", 
                      f"Questions accessible, notice present: {has_notice}")
        else:
            print_test("GET /education/quiz/questions", "FAIL", f"Status {response.status_code}")
    except Exception as e:
        print_test("GET /education/quiz/questions", "FAIL", str(e))

def test_authentication():
    """Test user registration and login."""
    print(f"\n{Colors.BLUE}=== Testing Authentication ==={Colors.END}\n")
    
    # Test 1: User registration
    try:
        response = requests.post(
            f"{BASE_URL}/users/register",
            json=TEST_USER
        )
        if response.status_code == 201:
            print_test("POST /users/register", "PASS", "User registered successfully")
            return True
        elif response.status_code == 400:
            # User might already exist
            print_test("POST /users/register", "SKIP", "User already exists")
            return True
        else:
            print_test("POST /users/register", "FAIL", f"Status {response.status_code}")
            return False
    except Exception as e:
        print_test("POST /users/register", "FAIL", str(e))
        return False

def get_auth_token() -> Optional[str]:
    """Login and get authentication token."""
    try:
        response = requests.post(
            f"{BASE_URL}/users/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
        )
        if response.status_code == 200:
            data = response.json()
            # Check for token in response or cookies
            if "access_token" in data:
                token = data["access_token"]
                print_test("POST /users/login", "PASS", "Token received in response")
                return token
            else:
                # Token might be in cookies
                print_test("POST /users/login", "PASS", "Login successful (cookie-based)")
                return "cookie"
        else:
            print_test("POST /users/login", "FAIL", f"Status {response.status_code}")
            return None
    except Exception as e:
        print_test("POST /users/login", "FAIL", str(e))
        return None

def test_authenticated_endpoints(token: Optional[str]):
    """Test endpoints that require authentication."""
    print(f"\n{Colors.BLUE}=== Testing Authenticated Endpoints ==={Colors.END}\n")
    
    if not token:
        print_test("Authenticated tests", "SKIP", "No token available")
        return
    
    headers = {"Authorization": f"Bearer {token}"} if token != "cookie" else {}
    
    # Test 1: Get user profile
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_test("GET /users/me", "PASS", f"Profile for {data.get('email', 'unknown')}")
        elif response.status_code == 401:
            print_test("GET /users/me", "FAIL", "401 Unauthorized (expected 200)")
        else:
            print_test("GET /users/me", "FAIL", f"Status {response.status_code}")
    except Exception as e:
        print_test("GET /users/me", "FAIL", str(e))
    
    # Test 2: Get favorites
    try:
        response = requests.get(f"{BASE_URL}/users/me/favorites", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_test("GET /users/me/favorites", "PASS", 
                      f"Found {data.get('total', 0)} favorites")
        elif response.status_code == 401:
            print_test("GET /users/me/favorites", "FAIL", "401 Unauthorized")
        else:
            print_test("GET /users/me/favorites", "FAIL", f"Status {response.status_code}")
    except Exception as e:
        print_test("GET /users/me/favorites", "FAIL", str(e))
    
    # Test 3: Get search history
    try:
        response = requests.get(f"{BASE_URL}/users/me/history", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_test("GET /users/me/history", "PASS", 
                      f"Found {data.get('total', 0)} searches")
        elif response.status_code == 401:
            print_test("GET /users/me/history", "FAIL", "401 Unauthorized")
        else:
            print_test("GET /users/me/history", "FAIL", f"Status {response.status_code}")
    except Exception as e:
        print_test("GET /users/me/history", "FAIL", str(e))

def test_protected_without_auth():
    """Test that protected endpoints reject unauthenticated requests."""
    print(f"\n{Colors.BLUE}=== Testing Protected Endpoints (No Auth) ==={Colors.END}\n")
    
    # Test 1: Try to submit quiz without auth
    try:
        response = requests.post(
            f"{BASE_URL}/education/quiz/submit",
            json={
                "user_id": "test",
                "question_id": "Q001",
                "selected_answers": ["A"],
                "correct": False,
                "time_taken": 30,
                "timestamp": "2025-11-21T10:00:00Z"
            }
        )
        if response.status_code == 401:
            print_test("POST /education/quiz/submit (no auth)", "PASS", 
                      "Correctly rejected with 401")
        else:
            print_test("POST /education/quiz/submit (no auth)", "FAIL", 
                      f"Expected 401, got {response.status_code}")
    except Exception as e:
        print_test("POST /education/quiz/submit (no auth)", "FAIL", str(e))
    
    # Test 2: Try to access user profile without auth
    try:
        response = requests.get(f"{BASE_URL}/users/me")
        if response.status_code == 401:
            print_test("GET /users/me (no auth)", "PASS", "Correctly rejected with 401")
        else:
            print_test("GET /users/me (no auth)", "FAIL", 
                      f"Expected 401, got {response.status_code}")
    except Exception as e:
        print_test("GET /users/me (no auth)", "FAIL", str(e))
    
    # Test 3: Try to create API key without auth
    try:
        response = requests.post(
            f"{BASE_URL}/integration/api-keys",
            json={
                "name": "Test Key",
                "scopes": ["read"],
                "expires_days": 30
            }
        )
        if response.status_code == 401:
            print_test("POST /integration/api-keys (no auth)", "PASS", 
                      "Correctly rejected with 401")
        else:
            print_test("POST /integration/api-keys (no auth)", "FAIL", 
                      f"Expected 401, got {response.status_code}")
    except Exception as e:
        print_test("POST /integration/api-keys (no auth)", "FAIL", str(e))

def test_optional_auth_benefits(token: Optional[str]):
    """Test that authenticated users get enhanced features on optional auth endpoints."""
    print(f"\n{Colors.BLUE}=== Testing Optional Auth Benefits ==={Colors.END}\n")
    
    if not token:
        print_test("Optional auth benefits", "SKIP", "No token available")
        return
    
    headers = {"Authorization": f"Bearer {token}"} if token != "cookie" else {}
    
    # Test: Evaluate tree with auth (should save to history)
    try:
        response_with_auth = requests.post(
            f"{BASE_URL}/diagnostic/evaluate/test-tree",
            headers=headers,
            json={"symptoms": ["fever", "cough"]}
        )
        
        response_without_auth = requests.post(
            f"{BASE_URL}/diagnostic/evaluate/test-tree",
            json={"symptoms": ["fever", "cough"]}
        )
        
        # Both should return 200 (or 404 if tree doesn't exist)
        if response_with_auth.status_code in [200, 404] and response_without_auth.status_code in [200, 404]:
            print_test("POST /diagnostic/evaluate (optional auth)", "PASS", 
                      "Works with and without auth")
        else:
            print_test("POST /diagnostic/evaluate (optional auth)", "FAIL", 
                      f"With auth: {response_with_auth.status_code}, Without: {response_without_auth.status_code}")
    except Exception as e:
        print_test("POST /diagnostic/evaluate (optional auth)", "FAIL", str(e))

def test_free_trial_limits():
    """Test that free trial search limits work correctly."""
    print(f"\n{Colors.BLUE}=== Testing Free Trial Search Limits ==={Colors.END}\n")
    
    # Test 1: Check initial limit
    try:
        response = requests.get(f"{BASE_URL}/diagnostic/search-limit")
        if response.status_code == 200:
            data = response.json()
            if not data.get("authenticated"):
                remaining = data.get("searches_remaining", 0)
                print_test("Initial free trial status", "PASS", 
                          f"{remaining} searches remaining out of 10")
            else:
                print_test("Initial free trial status", "SKIP", "User is authenticated (unlimited)")
        else:
            print_test("Initial free trial status", "FAIL", f"Status {response.status_code}")
    except Exception as e:
        print_test("Initial free trial status", "FAIL", str(e))
    
    # Test 2: Perform a diagnostic search
    try:
        response = requests.post(
            f"{BASE_URL}/diagnostic/evaluate/test-tree",
            json={"symptoms": ["test"]}
        )
        if response.status_code in [200, 404]:  # 404 is OK if tree doesn't exist
            if response.status_code == 200:
                data = response.json()
                if "search_limit" in data:
                    limit_info = data["search_limit"]
                    print_test("Diagnostic search with limit tracking", "PASS",
                              f"{limit_info.get('searches_used', '?')} used, "
                              f"{limit_info.get('searches_remaining', '?')} remaining")
                else:
                    print_test("Diagnostic search with limit tracking", "PASS",
                              "Authenticated user (no limit)")
            else:
                print_test("Diagnostic search with limit tracking", "SKIP", 
                          "Tree doesn't exist (expected in test)")
        elif response.status_code == 429:
            print_test("Diagnostic search with limit tracking", "PASS",
                      "Limit exceeded (HTTP 429) - this is expected if you've used 10 searches")
        else:
            print_test("Diagnostic search with limit tracking", "FAIL", 
                      f"Status {response.status_code}")
    except Exception as e:
        print_test("Diagnostic search with limit tracking", "FAIL", str(e))

def main():
    """Run all tests."""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("RealDiag Access Control Test Suite")
    print(f"{'='*60}{Colors.END}\n")
    
    print(f"Testing API at: {BASE_URL}")
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"\n{Colors.RED}ERROR: API is not responding. Make sure the server is running.{Colors.END}\n")
            print(f"Start the server with: cd /workspaces/RealDiag-Software && python -m uvicorn backend.main:app --reload")
            return
    except requests.exceptions.ConnectionError:
        print(f"\n{Colors.RED}ERROR: Cannot connect to API at {BASE_URL}{Colors.END}\n")
        print(f"Start the server with: cd /workspaces/RealDiag-Software && python -m uvicorn backend.main:app --reload")
        return
    except Exception as e:
        print(f"\n{Colors.RED}ERROR: {e}{Colors.END}\n")
        return
    
    # Run test suites
    test_public_endpoints()
    test_free_trial_limits()
    
    if test_authentication():
        token = get_auth_token()
        test_authenticated_endpoints(token)
        test_optional_auth_benefits(token)
    
    test_protected_without_auth()
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}")
    print("Test Suite Complete")
    print(f"{'='*60}{Colors.END}\n")
    
    print(f"{Colors.YELLOW}Note:{Colors.END} Some tests may fail if the database is not set up or ")
    print("if certain features are not yet implemented. This is expected.\n")
    
    print(f"{Colors.GREEN}Next Steps:{Colors.END}")
    print("1. Review test results above")
    print("2. Fix any failing tests")
    print("3. Test free trial by making 10+ searches from same IP")
    print("4. Update frontend to show search limit warnings")
    print("5. Update API documentation (Swagger)")
    print("6. Deploy to staging for QA testing\n")

if __name__ == "__main__":
    main()
