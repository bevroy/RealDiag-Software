#!/usr/bin/env python3
"""
Create Test User Accounts for RealDiag

This script creates test accounts with different roles for testing:
- Admin user
- Provider (healthcare professional)
- Regular user
- Patient user

Usage:
    python scripts/create_test_users.py
    
Or with custom backend URL:
    python scripts/create_test_users.py --url http://localhost:8000
"""

import requests
import json
import argparse
from typing import Dict, Any, Optional
import sys

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_section(title: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")


def create_user(base_url: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create a user account.
    
    Args:
        base_url: Backend API base URL
        user_data: User registration data
        
    Returns:
        Response data if successful, None otherwise
    """
    try:
        response = requests.post(
            f"{base_url}/users/register",
            json=user_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            return data
        elif response.status_code == 400:
            error_detail = response.json().get("detail", "")
            if "already registered" in error_detail.lower():
                print_warning(f"User {user_data['email']} already exists")
                # Try to login instead
                login_response = requests.post(
                    f"{base_url}/users/login",
                    json={
                        "email": user_data["email"],
                        "password": user_data["password"]
                    },
                    timeout=10
                )
                if login_response.status_code == 200:
                    return login_response.json()
            else:
                print_error(f"Registration failed: {error_detail}")
        else:
            print_error(f"Registration failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
        
        return None
        
    except Exception as e:
        print_error(f"Error creating user: {str(e)}")
        return None


def update_user_role(base_url: str, user_id: str, role: str, access_token: str) -> bool:
    """
    Update user role (requires admin access).
    
    Args:
        base_url: Backend API base URL
        user_id: User ID to update
        role: New role (admin, provider, user, guest)
        access_token: Admin access token
        
    Returns:
        True if successful
    """
    try:
        response = requests.put(
            f"{base_url}/users/{user_id}/role",
            json={"role": role},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        return response.status_code == 200
        
    except Exception as e:
        print_error(f"Error updating role: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Create test user accounts for RealDiag")
    parser.add_argument(
        "--url",
        default="https://realdiag-software.onrender.com",
        help="Backend API base URL (default: production)"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use local development server (http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    base_url = "http://localhost:8000" if args.local else args.url
    base_url = base_url.rstrip('/')
    
    print_section("RealDiag Test User Creation")
    print_info(f"Backend URL: {base_url}")
    
    # Define test users
    test_users = [
        {
            "email": "admin@realdiag.org",
            "password": "Admin123!Test",
            "full_name": "Admin User",
            "specialty": "Administration",
            "institution": "RealDiag LLC",
            "role_display": "Administrator"
        },
        {
            "email": "provider@realdiag.org",
            "password": "Provider123!Test",
            "full_name": "Dr. Sarah Provider",
            "specialty": "Internal Medicine",
            "institution": "Memorial Hospital",
            "role_display": "Healthcare Provider"
        },
        {
            "email": "doctor@example.com",
            "password": "Doctor123!Test",
            "full_name": "Dr. John Smith",
            "specialty": "Cardiology",
            "institution": "City Medical Center",
            "role_display": "Resident/Intern"
        },
        {
            "email": "patient@example.com",
            "password": "Patient123!Test",
            "full_name": "Jane Patient",
            "specialty": None,
            "institution": None,
            "role_display": "Patient User"
        }
    ]
    
    print("\n" + "=" * 70)
    print("Creating test accounts...")
    print("=" * 70 + "\n")
    
    created_users = []
    
    for user_data in test_users:
        role_display = user_data.pop("role_display")
        print(f"\n{Colors.BOLD}Creating {role_display}:{Colors.END}")
        print(f"  Email: {user_data['email']}")
        print(f"  Password: {user_data['password']}")
        
        # Remove None values
        user_data_clean = {k: v for k, v in user_data.items() if v is not None}
        
        result = create_user(base_url, user_data_clean)
        
        if result:
            user = result.get("user", {})
            token = result.get("access_token")
            
            created_users.append({
                "email": user_data['email'],
                "password": user_data['password'],
                "full_name": user.get("full_name", user_data['full_name']),
                "user_id": user.get("user_id"),
                "access_token": token,
                "role": role_display
            })
            
            print_success(f"Created/Logged in: {user_data['email']}")
            if user.get("user_id"):
                print_info(f"  User ID: {user['user_id']}")
            if token:
                print_info(f"  Token: {token[:20]}...")
        else:
            print_error(f"Failed to create {role_display}")
    
    # Print summary
    print_section("Test Users Summary")
    
    if created_users:
        print(f"\n{Colors.GREEN}{len(created_users)} test account(s) ready for use:{Colors.END}\n")
        
        for user in created_users:
            print(f"{Colors.BOLD}{user['role']}:{Colors.END}")
            print(f"  📧 Email:    {user['email']}")
            print(f"  🔑 Password: {user['password']}")
            print(f"  👤 Name:     {user['full_name']}")
            if user.get('user_id'):
                print(f"  🆔 User ID:  {user['user_id']}")
            print()
        
        print(f"{Colors.BLUE}{'=' * 70}{Colors.END}")
        print(f"{Colors.BOLD}Login URLs:{Colors.END}")
        print(f"  • Web UI:  https://realdiag.netlify.app/account")
        print(f"  • API:     {base_url}/users/login")
        print(f"{Colors.BLUE}{'=' * 70}{Colors.END}\n")
        
        print_info("You can now use these accounts to test different user features!")
        print_info("Employee emails (@realdiag.org) may have additional verification requirements.")
        
        # Save to file
        output_file = "test_users_credentials.json"
        try:
            with open(output_file, 'w') as f:
                json.dump({
                    "backend_url": base_url,
                    "users": [
                        {
                            "email": u["email"],
                            "password": u["password"],
                            "full_name": u["full_name"],
                            "role": u["role"]
                        }
                        for u in created_users
                    ]
                }, f, indent=2)
            print_success(f"Credentials saved to: {output_file}")
        except Exception as e:
            print_warning(f"Could not save credentials to file: {e}")
    else:
        print_error("No users were created successfully")
        sys.exit(1)


if __name__ == "__main__":
    main()
