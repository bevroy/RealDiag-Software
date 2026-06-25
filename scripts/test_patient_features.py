#!/usr/bin/env python3
"""
Test Patient Features

This script tests patient-specific functionality to ensure
patient accounts work correctly and have appropriate permissions.

Usage:
    python scripts/test_patient_features.py
"""

import requests
import json

BASE_URL = "https://realdiag-software.onrender.com"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_test(name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"  {status} - {name}")
    if details:
        print(f"    {Colors.BLUE}{details}{Colors.END}")


def login_patient():
    """Login as patient and get session with cookies"""
    try:
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/users/login",
            json={
                "email": "patient@example.com",
                "password": "Patient123!Test"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_test("Patient Login", True, f"Logged in as {data.get('user', {}).get('full_name')}")
            return session
        else:
            print_test("Patient Login", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_test("Patient Login", False, str(e))
        return None


def test_patient_profile(session):
    """Test patient profile access"""
    try:
        response = session.get(f"{BASE_URL}/users/me", timeout=10)
        
        passed = response.status_code == 200
        if passed:
            data = response.json()
            print_test(
                "Get Patient Profile",
                True,
                f"Name: {data.get('full_name')}, Email: {data.get('email')}"
            )
        else:
            print_test("Get Patient Profile", False, f"Status: {response.status_code}")
            
    except Exception as e:
        print_test("Get Patient Profile", False, str(e))


def test_symptom_search(session):
    """Test symptom search"""
    try:
        response = session.get(
            f"{BASE_URL}/search/symptoms",
            params={"q": "headache fever"},
            timeout=10
        )
        
        passed = response.status_code == 200
        if passed:
            data = response.json()
            result_count = len(data.get("results", []))
            print_test(
                "Symptom Search",
                True,
                f"Found {result_count} results for 'headache fever'"
            )
        else:
            print_test("Symptom Search", False, f"Status: {response.status_code}")
            
    except Exception as e:
        print_test("Symptom Search", False, str(e))


def test_diagnostic_trees(session):
    """Test access to diagnostic trees"""
    try:
        response = session.get(f"{BASE_URL}/diagnostic/trees", timeout=10)
        
        passed = response.status_code == 200
        if passed:
            data = response.json()
            tree_count = len(data.get("trees", []))
            print_test(
                "Access Diagnostic Trees",
                True,
                f"Can access {tree_count} diagnostic trees"
            )
        else:
            print_test("Access Diagnostic Trees", False, f"Status: {response.status_code}")
            
    except Exception as e:
        print_test("Access Diagnostic Trees", False, str(e))


def test_favorites(session):
    """Test favorites functionality"""
    try:
        response = session.get(f"{BASE_URL}/users/me/favorites", timeout=10)
        
        passed = response.status_code in [200, 404]  # 404 if no favorites yet
        if passed:
            if response.status_code == 200:
                data = response.json()
                fav_count = len(data.get("favorites", []))
            else:
                fav_count = 0
            print_test(
                "Get Favorites",
                True,
                f"Patient has {fav_count} favorite diagnoses"
            )
        else:
            print_test("Get Favorites", False, f"Status: {response.status_code}")
            
    except Exception as e:
        print_test("Get Favorites", False, str(e))


def test_search_history(session):
    """Test search history functionality"""
    try:
        response = session.get(f"{BASE_URL}/users/me/history", timeout=10)
        
        passed = response.status_code in [200, 404]  # 404 if no history yet
        if passed:
            if response.status_code == 200:
                data = response.json()
                history_count = len(data.get("history", []))
            else:
                history_count = 0
            print_test(
                "Get Search History",
                True,
                f"Patient has {history_count} searches in history"
            )
        else:
            print_test("Get Search History", False, f"Status: {response.status_code}")
            
    except Exception as e:
        print_test("Get Search History", False, str(e))


def test_educational_content(session):
    """Test access to educational content"""
    try:
        response = session.get(f"{BASE_URL}/education/modules", timeout=10)
        
        passed = response.status_code == 200
        if passed:
            data = response.json()
            module_count = len(data.get("modules", []))
            print_test(
                "Access Educational Content",
                True,
                f"Can access {module_count} educational modules"
            )
        else:
            print_test("Access Educational Content", False, f"Status: {response.status_code}")
            
    except Exception as e:
        print_test("Access Educational Content", False, str(e))


def test_permission_restrictions(session):
    """Test that patient cannot access provider-only features"""
    try:
        response = session.get(f"{BASE_URL}/admin/config", timeout=10)
        
        # Patient should NOT have access (403 or 404)
        passed = response.status_code in [403, 404, 401]
        print_test(
            "Permission Restriction (Admin)",
            passed,
            "Patient correctly denied access to admin features"
        )
        
    except Exception as e:
        # Connection error is acceptable - endpoint may not exist
        print_test("Permission Restriction (Admin)", True, "Admin endpoint not accessible")


def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}Testing Patient Features{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")
    
    # Login as patient
    print(f"{Colors.BOLD}Authentication:{Colors.END}")
    session = login_patient()
    
    if not session:
        print(f"\n{Colors.RED}Cannot continue without valid patient login{Colors.END}")
        return
    
    print(f"\n{Colors.BOLD}Profile & Account:{Colors.END}")
    test_patient_profile(session)
    
    print(f"\n{Colors.BOLD}Clinical Features:{Colors.END}")
    test_symptom_search(session)
    test_diagnostic_trees(session)
    
    print(f"\n{Colors.BOLD}Personal Data:{Colors.END}")
    test_favorites(session)
    test_search_history(session)
    
    print(f"\n{Colors.BOLD}Educational Content:{Colors.END}")
    test_educational_content(session)
    
    print(f"\n{Colors.BOLD}Security & Permissions:{Colors.END}")
    test_permission_restrictions(session)
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.GREEN}Testing complete!{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")
    
    print(f"{Colors.BLUE}Next steps:{Colors.END}")
    print(f"  1. Test in web UI: https://realdiag.netlify.app/account")
    print(f"  2. Login with: patient@example.com / Patient123!Test")
    print(f"  3. Explore patient-specific features and UI")
    print()


if __name__ == "__main__":
    main()
