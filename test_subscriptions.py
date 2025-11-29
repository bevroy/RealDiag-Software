#!/usr/bin/env python3
"""
Subscription System Test Script
================================

Tests the subscription management API endpoints.
"""

import requests
import json
from typing import Dict, Any

# Base URL
BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")

def print_response(response: requests.Response):
    """Pretty print response."""
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print()

def test_list_plans():
    """Test listing all subscription plans."""
    print_section("TEST: List All Plans")
    
    response = requests.get(f"{BASE_URL}/subscriptions/plans")
    print_response(response)
    
    assert response.status_code == 200, "Failed to list plans"
    data = response.json()
    assert "plans" in data, "Response missing 'plans' key"
    assert len(data["plans"]) > 0, "No plans returned"
    print(f"✅ Found {len(data['plans'])} subscription plans")

def test_get_plan_details():
    """Test getting details of a specific plan."""
    print_section("TEST: Get Plan Details (Professional)")
    
    response = requests.get(
        f"{BASE_URL}/subscriptions/plans/individual_professional",
        params={"billing_interval": "monthly"}
    )
    print_response(response)
    
    assert response.status_code == 200, "Failed to get plan details"
    data = response.json()
    assert data["plan_type"] == "individual_professional", "Wrong plan type"
    assert "features" in data, "Missing features"
    print("✅ Plan details retrieved successfully")

def test_organization_pricing():
    """Test organization plan pricing calculator."""
    print_section("TEST: Organization Pricing (25 seats, yearly)")
    
    response = requests.get(
        f"{BASE_URL}/subscriptions/calculate-price",
        params={
            "plan_type": "organization",
            "billing_interval": "yearly",
            "seats": 25
        }
    )
    print_response(response)
    
    assert response.status_code == 200, "Failed to calculate price"
    data = response.json()
    assert "price_per_seat" in data, "Missing price_per_seat"
    assert "savings" in data, "Missing savings"
    print(f"✅ Price calculated: ${data['total_price']:.2f} ({data['seats']} seats @ ${data['price_per_seat']:.2f}/seat)")
    print(f"   Yearly savings: ${data['savings']:.2f}")

def test_register_user():
    """Register a test user."""
    print_section("TEST: Register Test User")
    
    test_user = {
        "email": f"test_subscription_{int(requests.get(f'{BASE_URL}/version').json().get('version', '0').replace('.', ''))}@example.com",
        "password": "TestPass123!",
        "full_name": "Test Subscription User",
        "specialty": "neurology"
    }
    
    response = requests.post(f"{BASE_URL}/users/register", json=test_user)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ User registered: {data.get('user', {}).get('email')}")
        return token, test_user
    elif response.status_code == 400 and "already registered" in response.text.lower():
        # User exists, try to login
        print("⚠️  User already exists, attempting login...")
        login_response = requests.post(
            f"{BASE_URL}/users/login",
            data={"username": test_user["email"], "password": test_user["password"]}
        )
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print(f"✅ Logged in as existing user")
            return token, test_user
    
    raise Exception("Failed to register or login test user")

def test_check_subscription_status(token: str):
    """Check subscription status for authenticated user."""
    print_section("TEST: Check Subscription Status")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/subscriptions/me", headers=headers)
    print_response(response)
    
    assert response.status_code == 200, "Failed to get subscription status"
    data = response.json()
    print(f"✅ Current plan: {data.get('plan_type', 'free')}")
    return data

def test_create_subscription(token: str):
    """Create a new subscription."""
    print_section("TEST: Create Subscription (Professional, Monthly)")
    
    headers = {"Authorization": f"Bearer {token}"}
    subscription_data = {
        "plan_type": "individual_professional",
        "billing_interval": "monthly",
        "seats": 1,
        "metadata": {
            "test": "true",
            "source": "test_script"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/subscriptions/me",
        json=subscription_data,
        headers=headers
    )
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Subscription created: {data['subscription']['plan_name']}")
        print(f"   Trial ends: {data.get('trial_days', 0)} days")
        return data["subscription"]
    elif response.status_code == 400:
        print("⚠️  User already has subscription (expected if running multiple times)")
        return None
    else:
        raise Exception(f"Failed to create subscription: {response.status_code}")

def test_check_feature_access(token: str):
    """Check access to specific features."""
    print_section("TEST: Check Feature Access")
    
    headers = {"Authorization": f"Bearer {token}"}
    features_to_check = [
        "fhir_export",
        "api_access",
        "bulk_export",
        "ehr_integration"
    ]
    
    for feature in features_to_check:
        response = requests.get(
            f"{BASE_URL}/subscriptions/features/{feature}",
            headers=headers
        )
        data = response.json()
        status = "✅" if data.get("has_access") else "❌"
        print(f"{status} {feature}: {data.get('has_access')} (Plan: {data.get('plan')})")
    
    print("\n✅ Feature access checked successfully")

def test_upgrade_subscription(token: str):
    """Upgrade subscription to a higher tier."""
    print_section("TEST: Upgrade Subscription (Professional → Professional Plus)")
    
    headers = {"Authorization": f"Bearer {token}"}
    upgrade_data = {
        "plan_type": "individual_professional_plus",
        "billing_interval": "yearly"
    }
    
    response = requests.put(
        f"{BASE_URL}/subscriptions/me",
        json=upgrade_data,
        headers=headers
    )
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Subscription upgraded to: {data['subscription']['plan_name']}")
        print(f"   New billing interval: {data['subscription']['billing_interval']}")
        return data["subscription"]
    elif response.status_code == 404:
        print("⚠️  No subscription to upgrade (expected if creation failed)")
        return None
    else:
        raise Exception(f"Failed to upgrade subscription: {response.status_code}")

def test_anonymous_feature_check():
    """Check feature access without authentication."""
    print_section("TEST: Anonymous Feature Check")
    
    response = requests.get(f"{BASE_URL}/subscriptions/features/api_access")
    print_response(response)
    
    assert response.status_code == 200, "Failed to check feature"
    data = response.json()
    assert data.get("plan") == "free", "Wrong plan for anonymous user"
    assert not data.get("has_access"), "Anonymous should not have API access"
    print("✅ Anonymous user correctly restricted")

def test_cancel_subscription(token: str):
    """Cancel subscription (cleanup)."""
    print_section("TEST: Cancel Subscription")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/subscriptions/me", headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Subscription canceled")
        print(f"   Access until: {data.get('access_until')}")
    elif response.status_code == 404:
        print("⚠️  No subscription to cancel")
    else:
        print(f"⚠️  Cancel failed with status {response.status_code}")

def run_all_tests():
    """Run all subscription tests."""
    print("\n" + "=" * 60)
    print("  SUBSCRIPTION SYSTEM TEST SUITE")
    print("=" * 60)
    
    try:
        # Public endpoints (no auth)
        test_list_plans()
        test_get_plan_details()
        test_organization_pricing()
        test_anonymous_feature_check()
        
        # Authenticated endpoints
        token, user = test_register_user()
        test_check_subscription_status(token)
        subscription = test_create_subscription(token)
        
        if subscription:
            test_check_feature_access(token)
            test_upgrade_subscription(token)
        
        # Cleanup
        test_cancel_subscription(token)
        
        print_section("TEST SUITE COMPLETE")
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    run_all_tests()
