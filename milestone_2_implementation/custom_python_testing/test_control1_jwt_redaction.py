"""
OWASP ZAP Test Script for Control #1: JWT Token Redaction in Logs
This script tests whether JWT tokens are properly redacted in application logs.
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
# Fixed: Use the actual log file path from logger_singleton.py
LOG_FILE_PATH = f"c:/Users/Honey/Desktop/ConnectlyIPT/school-connectly/logs/connectly_{datetime.now().strftime('%Y%m%d')}.log"

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def test_jwt_token_redaction():
    """Test JWT token redaction in logs"""
    print_header("Control #1: JWT Token Redaction Test")

    # Step 1: Register a test user
    print("\n[Step 1] Registering test user...")
    register_data = {
        "username": f"zaptest_{int(time.time())}",
        "email": f"zaptest_{int(time.time())}@example.com",
        "password": "TestPassword123!",
        "first_name": "ZAP",
        "last_name": "Test"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/signup/",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Registration Status: {response.status_code}")

        if response.status_code != 201:
            print(f"Registration failed: {response.text}")
            return False

    except Exception as e:
        print(f"Error during registration: {e}")
        return False

    # Step 2: Login to get JWT token
    print("\n[Step 2] Logging in to obtain JWT token...")
    login_data = {
        "username": register_data["username"],
        "password": register_data["password"]
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/token/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Login Status: {response.status_code}")

        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return False

        token_data = response.json()
        token = token_data.get("token")

        if not token:
            print("No token received")
            return False

        print(f"Token received (first 20 chars): {token[:20]}...")

    except Exception as e:
        print(f"Error during login: {e}")
        return False

    # Step 3: Make authenticated request
    print("\n[Step 3] Making authenticated request...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/posts/",
            headers={
                "Authorization": f"Token {token}",
                "Content-Type": "application/json"
            }
        )
        print(f"Authenticated Request Status: {response.status_code}")

    except Exception as e:
        print(f"Error during authenticated request: {e}")
        return False

    # Step 4: Check log file for token leakage
    print("\n[Step 4] Checking log file for token leakage...")
    time.sleep(2)  # Wait for logs to be written

    if not os.path.exists(LOG_FILE_PATH):
        print(f"⚠️  Log file not found at: {LOG_FILE_PATH}")
        print("    Cannot verify token redaction")
        return None

    try:
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            log_content = f.read()

        # Check if the actual token appears in logs
        if token in log_content:
            print("❌ FAILED: Full JWT token found in logs!")
            print("   Token should be redacted but appears in plain text")
            return False
        else:
            print("✓ PASSED: Full JWT token not found in logs")

        # Check if redacted token appears in logs
        if "[REDACTED]" in log_content or "REDACTED-TOKEN" in log_content:
            print("✓ PASSED: Redaction mechanism is working")
            print("   Tokens are being properly redacted in logs")
            return True
        else:
            print("⚠️  WARNING: No redaction markers found in recent logs")
            print("    This could mean tokens aren't being logged at all")
            return None

    except Exception as e:
        print(f"Error reading log file: {e}")
        return None

def main():
    """Main test execution"""
    print_header("OWASP ZAP - Control #1 Testing")
    print("Testing: JWT Token Redaction in Application Logs")
    print(f"Target: {BASE_URL}")
    print(f"Log File: {LOG_FILE_PATH}")

    # Clear previous log entries (optional - comment out if you want to keep history)
    # if os.path.exists(LOG_FILE_PATH):
    #     with open(LOG_FILE_PATH, 'w') as f:
    #         f.write("")
    #     print("\n[INFO] Cleared previous log entries")

    result = test_jwt_token_redaction()

    print_header("Test Results")
    if result is True:
        print("✓ Control #1 is WORKING CORRECTLY")
        print("  JWT tokens are properly redacted in logs")
        return 0
    elif result is False:
        print("❌ Control #1 FAILED")
        print("  JWT tokens are exposed in logs")
        return 1
    else:
        print("⚠️  Control #1 INCONCLUSIVE")
        print("  Unable to verify token redaction")
        return 2

if __name__ == "__main__":
    exit(main())
