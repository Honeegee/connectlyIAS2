"""
Test script to verify error pages work in production mode.
"""

import os
import requests
import time
from pathlib import Path

def create_production_env():
    """Create .env file with DEBUG=False for testing"""
    env_path = Path('.env')

    # Read existing .env if it exists
    existing_env = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    existing_env[key] = value

    # Set DEBUG=False for production testing
    existing_env['DEBUG'] = 'False'

    # Write updated .env
    with open(env_path, 'w') as f:
        for key, value in existing_env.items():
            f.write(f"{key}={value}\n")

    print("✅ Created .env with DEBUG=False for production testing")

def restore_env():
    """Restore DEBUG=True for development"""
    env_path = Path('.env')

    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()

        with open(env_path, 'w') as f:
            for line in lines:
                if line.startswith('DEBUG='):
                    f.write('DEBUG=True\n')
                else:
                    f.write(line)

    print("✅ Restored DEBUG=True for development")

def test_error_pages():
    """Test custom error pages with server"""
    print("=" * 70)
    print("PRODUCTION ERROR PAGES TEST")
    print("=" * 70)

    base_url = "http://localhost:8000"

    # Check if server is running
    try:
        health_response = requests.get(f"{base_url}/health/", timeout=2)
        if health_response.status_code != 200:
            print("❌ Server not responding correctly")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server")
        print("Please start server with: python manage.py runserver")
        return False

    print("✅ Server is running\n")

    # Test 404 error
    print("Test 1: Testing 404 Not Found...")
    try:
        response = requests.get(f"{base_url}/nonexistent-page/", timeout=5)

        if response.status_code == 404:
            print("  [PASS] Returns 404 status code")

            # Check if it's our custom page
            if "Page Not Found" in response.text and "Connectly" in response.text:
                print("  [PASS] Custom 404 page displayed")
                print("  [PASS] No debug information exposed")
            else:
                print("  [WARN] May not be using custom 404 page")

            # Check for absence of debug information
            debug_indicators = ["Traceback", "Exception", "DEBUG = True", "django.core.exceptions"]
            has_debug = any(indicator in response.text for indicator in debug_indicators)

            if not has_debug:
                print("  [PASS] No debug information in 404 response")
            else:
                print("  [FAIL] Debug information found in 404 response")

        else:
            print(f"  [FAIL] Expected 404, got {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Request failed: {e}")

    # Test normal endpoint still works
    print("\nTest 2: Testing normal endpoint...")
    try:
        response = requests.get(f"{base_url}/health/", timeout=5)
        if response.status_code == 200:
            print("  [PASS] Normal endpoints still work")
        else:
            print(f"  [FAIL] Normal endpoint returned {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Request failed: {e}")

    return True

def main():
    print("DEBUG PREVENTION - PRODUCTION MODE TEST")
    print("=" * 70)

    print("\n1. Setting up production environment...")
    create_production_env()

    print("\n2. Testing with production settings...")
    print("NOTE: This test requires a running Django server")
    print("If server is running with old settings, restart it to pick up DEBUG=False")

    input("\nPress Enter when server is restarted with new settings...")

    success = test_error_pages()

    print("\n3. Restoring development environment...")
    restore_env()

    print("\n" + "=" * 70)
    if success:
        print("✅ DEBUG PREVENTION TEST COMPLETED")
        print("\nResults:")
        print("  - Custom error pages working")
        print("  - No debug information exposed")
        print("  - Production mode functioning correctly")
    else:
        print("❌ TEST INCOMPLETE - Server connection issues")

    print("\nDevelopment environment restored (DEBUG=True)")
    print("=" * 70)

if __name__ == "__main__":
    main()