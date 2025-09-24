"""
Test script to verify rate limiting on authentication endpoints.
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_token_endpoint_rate_limit():
    """Test rate limiting on /api/auth/token/ endpoint"""
    print("=" * 70)
    print("Testing Rate Limiting on Token Endpoint")
    print("=" * 70)
    print(f"\nEndpoint: {BASE_URL}/api/auth/token/")
    print("Rate Limit: 5 requests per minute per IP")
    print("\nAttempting 7 requests in quick succession...\n")

    results = []

    for i in range(1, 8):
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/token/",
                json={
                    "username": "testuser",
                    "password": "wrongpassword"
                },
                timeout=5
            )

            timestamp = datetime.now().strftime("%H:%M:%S")
            status_code = response.status_code

            if status_code == 429:
                print(f"[{timestamp}] Request {i}: RATE LIMITED (429)")
                results.append(f"Request {i}: BLOCKED [PASS]")
            elif status_code == 400:
                print(f"[{timestamp}] Request {i}: Allowed (400 - Bad credentials)")
                results.append(f"Request {i}: ALLOWED")
            else:
                print(f"[{timestamp}] Request {i}: Status {status_code}")
                results.append(f"Request {i}: Status {status_code}")

            # Small delay to prevent network issues
            time.sleep(0.1)

        except requests.exceptions.RequestException as e:
            print(f"[{timestamp}] Request {i}: Error - {str(e)}")
            results.append(f"Request {i}: ERROR")

    print("\n" + "=" * 70)
    print("RESULTS SUMMARY:")
    print("=" * 70)
    for result in results:
        print(f"  {result}")

    print("\nExpected: First 5 requests allowed, requests 6-7 blocked (429)")
    print("=" * 70)


def test_google_login_rate_limit():
    """Test rate limiting on /api/auth/google/ endpoint"""
    print("\n\n" + "=" * 70)
    print("Testing Rate Limiting on Google Login Endpoint")
    print("=" * 70)
    print(f"\nEndpoint: {BASE_URL}/api/auth/google/")
    print("Rate Limit: 5 requests per minute per IP")
    print("\nAttempting 7 requests in quick succession...\n")

    results = []

    for i in range(1, 8):
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/google/",
                json={
                    "access_token": "fake_token_for_testing"
                },
                timeout=5
            )

            timestamp = datetime.now().strftime("%H:%M:%S")
            status_code = response.status_code

            if status_code == 429:
                print(f"[{timestamp}] Request {i}: RATE LIMITED (429)")
                results.append(f"Request {i}: BLOCKED [PASS]")
            elif status_code in [400, 401]:
                print(f"[{timestamp}] Request {i}: Allowed ({status_code} - Invalid token)")
                results.append(f"Request {i}: ALLOWED")
            else:
                print(f"[{timestamp}] Request {i}: Status {status_code}")
                results.append(f"Request {i}: Status {status_code}")

            # Small delay to prevent network issues
            time.sleep(0.1)

        except requests.exceptions.RequestException as e:
            print(f"[{timestamp}] Request {i}: Error - {str(e)}")
            results.append(f"Request {i}: ERROR")

    print("\n" + "=" * 70)
    print("RESULTS SUMMARY:")
    print("=" * 70)
    for result in results:
        print(f"  {result}")

    print("\nExpected: First 5 requests allowed, requests 6-7 blocked (429)")
    print("=" * 70)


def main():
    print("\nRATE LIMITING TEST SUITE")
    print("=" * 70)
    print("NOTE: Django server must be running on http://localhost:8000")
    print("Start server with: python manage.py runserver")
    print("=" * 70)

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health/", timeout=2)
        if response.status_code != 200:
            print("\nServer is not responding correctly")
            print("Please start the Django server first: python manage.py runserver")
            return
    except requests.exceptions.RequestException:
        print("\nCannot connect to server at http://localhost:8000")
        print("Please start the Django server first: python manage.py runserver")
        return

    print("\nServer is running\n")

    # Run tests
    test_token_endpoint_rate_limit()
    test_google_login_rate_limit()

    print("\n\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\nTo reset rate limits, wait 1 minute or restart the Django server")
    print("=" * 70)


if __name__ == "__main__":
    main()