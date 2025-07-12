#!/usr/bin/env python3
"""
Manual verification test for tianurien@gmail.com club account
"""

import requests
import json

# Use the public endpoint from the frontend .env file
BASE_URL = "https://44807d79-6707-4de4-af2d-bda42117593c.preview.emergentagent.com/api"

def check_club_account(email):
    """Check if a club account exists and get its details"""
    print(f"\n===== Checking Club Account: {email} =====")
    
    # Get all clubs
    response = requests.get(f"{BASE_URL}/clubs")
    if response.status_code != 200:
        print(f"❌ Failed to get clubs list: {response.status_code} - {response.text}")
        return None
    
    clubs = response.json()
    target_club = None
    
    print(f"🔍 Searching through {len(clubs)} clubs...")
    for club in clubs:
        if club.get("email") == email:
            target_club = club
            break
    
    if not target_club:
        print(f"❌ Club account {email} not found in database")
        print("\n📋 Available club accounts:")
        for club in clubs:
            print(f"  - {club.get('name', 'Unknown')} ({club.get('email', 'No email')}) - Verified: {club.get('is_verified', False)}")
        return None
    
    print(f"✅ Found club account:")
    print(f"   Name: {target_club['name']}")
    print(f"   Email: {target_club['email']}")
    print(f"   ID: {target_club['id']}")
    print(f"   Location: {target_club.get('location', 'Unknown')}")
    print(f"   Verified: {target_club.get('is_verified', False)}")
    print(f"   Created: {target_club.get('created_at', 'Unknown')}")
    
    return target_club

def get_verification_status(email, user_type="club"):
    """Get verification status for an account"""
    print(f"\n🔍 Getting verification status for {email}...")
    
    response = requests.get(f"{BASE_URL}/check-verification-status", params={
        "email": email,
        "user_type": user_type
    })
    
    if response.status_code == 200:
        status = response.json()
        print(f"✅ Verification status retrieved:")
        print(f"   Email: {status.get('email')}")
        print(f"   Name: {status.get('name')}")
        print(f"   Verified: {status.get('is_verified')}")
        return status
    else:
        print(f"❌ Failed to get verification status: {response.status_code} - {response.text}")
        return None

def test_verification_endpoint(token="test-token", user_type="club"):
    """Test the verification endpoint with a token"""
    print(f"\n🔍 Testing verification endpoint with token: {token[:10]}...")
    
    verify_data = {
        "token": token,
        "user_type": user_type
    }
    
    response = requests.post(f"{BASE_URL}/verify-email", json=verify_data)
    
    print(f"   Response: {response.status_code}")
    if response.status_code != 200:
        result = response.json()
        print(f"   Detail: {result.get('detail', 'No detail')}")
    else:
        result = response.json()
        print(f"   Success: {result}")
    
    return response.status_code == 200

def manual_verify_account(email, token):
    """Manually verify an account using the provided token"""
    print(f"\n🔧 Attempting manual verification for {email}...")
    
    verify_data = {
        "token": token,
        "user_type": "club"
    }
    
    response = requests.post(f"{BASE_URL}/verify-email", json=verify_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Account verified successfully!")
        print(f"   Response: {result}")
        return True
    else:
        result = response.json()
        print(f"❌ Verification failed: {response.status_code}")
        print(f"   Detail: {result.get('detail', 'No detail')}")
        return False

def test_login(email, password="TestPassword123!"):
    """Test login with the account"""
    print(f"\n🔍 Testing login for {email}...")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/clubs/login", json=login_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Login successful!")
        print(f"   Club: {result.get('name')}")
        print(f"   Email: {result.get('email')}")
        print(f"   Verified: {result.get('is_verified')}")
        return True
    elif response.status_code == 401:
        print(f"❌ Login failed - Invalid credentials")
        print(f"   This could mean the password is incorrect")
        return False
    elif response.status_code == 403:
        result = response.json()
        if "verify your email" in result.get("detail", "").lower():
            print(f"❌ Login blocked - Account not verified")
            return False
        else:
            print(f"❌ Login blocked - {result.get('detail')}")
            return False
    else:
        print(f"❌ Unexpected login response: {response.status_code} - {response.text}")
        return False

def main():
    """Main function to check and verify the club account"""
    target_email = "tianurien@gmail.com"
    
    print("===== Manual Club Account Verification Tool =====")
    print(f"Target email: {target_email}")
    
    # Step 1: Check if the account exists
    club = check_club_account(target_email)
    
    if not club:
        print(f"\n❌ Club account {target_email} does not exist in the system")
        print("   You may need to register this account first")
        return
    
    # Step 2: Get verification status
    status = get_verification_status(target_email)
    
    if not status:
        print("❌ Could not get verification status")
        return
    
    # Step 3: Check if already verified
    if status.get('is_verified', False):
        print(f"\n✅ Account {target_email} is already verified!")
        
        # Test login
        test_login(target_email)
        return
    
    # Step 4: Account needs verification
    print(f"\n⚠️  Account {target_email} is NOT verified")
    print("   Manual verification is required")
    
    # Step 5: Test verification endpoint functionality
    test_verification_endpoint("invalid-test-token")
    
    # Step 6: Provide manual verification instructions
    print(f"\n📋 Manual Verification Instructions:")
    print(f"   To verify the account {target_email}, you need to:")
    print(f"   1. Access the MongoDB database directly")
    print(f"   2. Find the club document with email '{target_email}'")
    print(f"   3. Get the 'verification_token' field value")
    print(f"   4. Use the verification command below:")
    print(f"")
    print(f"   curl -X POST '{BASE_URL}/verify-email' \\")
    print(f"        -H 'Content-Type: application/json' \\")
    print(f"        -d '{{\"token\":\"<VERIFICATION_TOKEN_FROM_DATABASE>\",\"user_type\":\"club\"}}'")
    print(f"")
    print(f"   5. After verification, test login with:")
    print(f"   curl -X POST '{BASE_URL}/clubs/login' \\")
    print(f"        -H 'Content-Type: application/json' \\")
    print(f"        -d '{{\"email\":\"{target_email}\",\"password\":\"<ACTUAL_PASSWORD>\"}}'")
    
    # Step 7: Try to get a fresh verification token
    print(f"\n🔄 Attempting to resend verification email...")
    resend_data = {
        "email": target_email,
        "user_type": "club"
    }
    
    response = requests.post(f"{BASE_URL}/resend-verification", json=resend_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Verification email resend successful!")
        print(f"   Response: {result.get('message', 'Success')}")
    elif response.status_code == 500:
        result = response.json()
        if "Failed to send verification email" in result.get("detail", ""):
            print(f"⚠️  Email sending failed (expected due to Resend testing mode)")
            print(f"   But this confirms the account exists and needs verification")
        else:
            print(f"❌ Unexpected error: {result}")
    else:
        print(f"❌ Resend verification failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()