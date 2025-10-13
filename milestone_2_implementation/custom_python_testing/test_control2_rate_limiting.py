"""
OWASP ZAP Test Script for Control #2: Rate Limiting for Authentication Endpoints
This script tests whether rate limiting is properly enforced on authentication endpoints.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
RATE_LIMIT = 5  # Expected rate limit (requests per minute)
TEST_REQUESTS = 10  # Number of requests to send

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def test_login_rate_limiting():
    """Test rate limiting on login endpoint"""
    print_header("Testing Login Endpoint Rate Limiting")
    print(f"Endpoint: {BASE_URL}/api/auth/token/")
    print(f"Expected Rate Limit: {RATE_LIMIT} requests per minute")
    print(f"Test: Sending {TEST_REQUESTS} rapid requests")

    results = []
    blocked_count = 0
    success_count = 0

    login_data = {
        "username": "nonexistent_user",
        "password": "wrong_password"
    }

    print("\n[Testing] Sending rapid login attempts...")
    start_time = time.time()

    for i in range(TEST_REQUESTS):
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/token/",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )

            result = {
                "request_num": i + 1,
                "status_code": response.status_code,
                "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3]
            }

            if response.status_code == 429:
                blocked_count += 1
                result["result"] = "BLOCKED (Rate Limited)"
                print(f"  Request {i+1}: {response.status_code} - Rate Limited ✓")
            elif response.status_code in [200, 400, 401]:
                success_count += 1
                result["result"] = "ALLOWED"
                print(f"  Request {i+1}: {response.status_code} - Allowed")
            else:
                result["result"] = f"UNEXPECTED ({response.status_code})"
                print(f"  Request {i+1}: {response.status_code} - Unexpected")

            results.append(result)

            # Small delay to ensure rapid succession
            time.sleep(0.1)

        except Exception as e:
            print(f"  Request {i+1}: Error - {e}")
            results.append({
                "request_num": i + 1,
                "status_code": "ERROR",
                "result": str(e),
                "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3]
            })

    elapsed_time = time.time() - start_time

    return results, blocked_count, success_count, elapsed_time

def test_register_rate_limiting():
    """Test rate limiting on registration endpoint"""
    print_header("Testing Registration Endpoint Rate Limiting")
    print(f"Endpoint: {BASE_URL}/api/auth/register/")
    print(f"Expected Rate Limit: {RATE_LIMIT} requests per minute")
    print(f"Test: Sending {TEST_REQUESTS} rapid requests")

    results = []
    blocked_count = 0
    success_count = 0

    print("\n[Testing] Sending rapid registration attempts...")
    start_time = time.time()

    for i in range(TEST_REQUESTS):
        register_data = {
            "username": f"ratelimitest_{int(time.time())}_{i}",
            "email": f"ratelimitest_{int(time.time())}_{i}@example.com",
            "password": "TestPassword123!",
            "first_name": "Rate",
            "last_name": "Test"
        }

        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register/",
                json=register_data,
                headers={"Content-Type": "application/json"}
            )

            result = {
                "request_num": i + 1,
                "status_code": response.status_code,
                "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3]
            }

            if response.status_code == 429:
                blocked_count += 1
                result["result"] = "BLOCKED (Rate Limited)"
                print(f"  Request {i+1}: {response.status_code} - Rate Limited ✓")
            elif response.status_code in [200, 201, 400]:
                success_count += 1
                result["result"] = "ALLOWED"
                print(f"  Request {i+1}: {response.status_code} - Allowed")
            else:
                result["result"] = f"UNEXPECTED ({response.status_code})"
                print(f"  Request {i+1}: {response.status_code} - Unexpected")

            results.append(result)

            # Small delay to ensure rapid succession
            time.sleep(0.1)

        except Exception as e:
            print(f"  Request {i+1}: Error - {e}")
            results.append({
                "request_num": i + 1,
                "status_code": "ERROR",
                "result": str(e),
                "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3]
            })

    elapsed_time = time.time() - start_time

    return results, blocked_count, success_count, elapsed_time

def main():
    """Main test execution"""
    print_header("OWASP ZAP - Control #2 Testing")
    print("Testing: Rate Limiting for Authentication Endpoints")
    print(f"Target: {BASE_URL}")

    # Test 1: Login Rate Limiting
    login_results, login_blocked, login_allowed, login_time = test_login_rate_limiting()

    # Wait a bit before next test
    print("\n[INFO] Waiting 60 seconds before next test to allow rate limit reset...")
    time.sleep(60)

    # Test 2: Registration Rate Limiting
    register_results, register_blocked, register_allowed, register_time = test_register_rate_limiting()

    # Print Summary
    print_header("Test Summary")

    print("\n📊 Login Endpoint Results:")
    print(f"   Total Requests: {len(login_results)}")
    print(f"   Allowed: {login_allowed}")
    print(f"   Blocked (429): {login_blocked}")
    print(f"   Time Elapsed: {login_time:.2f} seconds")

    if login_blocked >= RATE_LIMIT:
        print("   Status: ✓ PASSED - Rate limiting is active")
    elif login_blocked > 0:
        print("   Status: ⚠️  PARTIAL - Some requests blocked but may need tuning")
    else:
        print("   Status: ❌ FAILED - No rate limiting detected")

    print("\n📊 Registration Endpoint Results:")
    print(f"   Total Requests: {len(register_results)}")
    print(f"   Allowed: {register_allowed}")
    print(f"   Blocked (429): {register_blocked}")
    print(f"   Time Elapsed: {register_time:.2f} seconds")

    if register_blocked >= RATE_LIMIT:
        print("   Status: ✓ PASSED - Rate limiting is active")
    elif register_blocked > 0:
        print("   Status: ⚠️  PARTIAL - Some requests blocked but may need tuning")
    else:
        print("   Status: ❌ FAILED - No rate limiting detected")

    print_header("Final Result")

    if login_blocked > 0 and register_blocked > 0:
        print("✓ Control #2 is WORKING CORRECTLY")
        print("  Rate limiting is enforced on authentication endpoints")
        return 0
    elif login_blocked > 0 or register_blocked > 0:
        print("⚠️  Control #2 PARTIALLY WORKING")
        print("  Rate limiting is active but may need adjustment")
        return 1
    else:
        print("❌ Control #2 FAILED")
        print("  Rate limiting is not properly enforced")
        return 2

if __name__ == "__main__":
    exit(main())
