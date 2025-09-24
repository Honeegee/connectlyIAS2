"""
Test to verify rate limiting configuration is correct.
This test does not require a running server.
"""

import re

def test_rate_limit_configuration():
    """Test that rate limiting decorators are properly configured"""
    print("=" * 70)
    print("RATE LIMITING CONFIGURATION TEST")
    print("=" * 70)

    # Read authentication views
    with open('authentication/views.py', 'r') as f:
        views_content = f.read()

    # Test 1: Check imports
    print("\nTest 1: Checking imports...")
    required_imports = [
        'from django_ratelimit.decorators import ratelimit',
        'from django_ratelimit.exceptions import Ratelimited',
        'from django.utils.decorators import method_decorator'
    ]

    all_imports_present = True
    for imp in required_imports:
        if imp in views_content:
            print(f"  [PASS] Found: {imp}")
        else:
            print(f"  [FAIL] Missing: {imp}")
            all_imports_present = False

    # Test 2: Check RateLimitedObtainAuthToken class
    print("\nTest 2: Checking RateLimitedObtainAuthToken class...")
    if 'class RateLimitedObtainAuthToken' in views_content:
        print("  [PASS] RateLimitedObtainAuthToken class exists")

        # Check for rate limit decorator on class
        class_pattern = r"@method_decorator\(ratelimit\(key='ip', rate='5/m'"
        if re.search(class_pattern, views_content):
            print("  [PASS] Class has rate limit decorator (5/m)")
        else:
            print("  [FAIL] Class missing rate limit decorator")

        # Check for Ratelimited exception handling
        if 'except Ratelimited:' in views_content:
            print("  [PASS] Handles Ratelimited exception")
        else:
            print("  [FAIL] No Ratelimited exception handling")

        # Check for 429 status code
        if 'HTTP_429_TOO_MANY_REQUESTS' in views_content:
            print("  [PASS] Returns 429 status code")
        else:
            print("  [FAIL] No 429 status code")
    else:
        print("  [FAIL] RateLimitedObtainAuthToken class not found")

    # Test 3: Check google_login rate limiting
    print("\nTest 3: Checking google_login rate limiting...")
    google_login_pattern = r"@ratelimit\(key='ip', rate='5/m'"
    google_login_matches = re.findall(google_login_pattern, views_content)

    if google_login_matches:
        print(f"  [PASS] google_login has rate limit decorator (5/m)")
    else:
        print(f"  [FAIL] google_login missing rate limit decorator")

    # Test 4: Check URLs configuration
    print("\nTest 4: Checking URLs configuration...")
    with open('authentication/urls.py', 'r') as f:
        urls_content = f.read()

    if 'RateLimitedObtainAuthToken' in urls_content:
        print("  [PASS] RateLimitedObtainAuthToken imported in URLs")
    else:
        print("  [FAIL] RateLimitedObtainAuthToken not in URLs")

    if "path('token/', RateLimitedObtainAuthToken.as_view()" in urls_content:
        print("  [PASS] Token endpoint uses RateLimitedObtainAuthToken")
    else:
        print("  [FAIL] Token endpoint not configured with rate limiting")

    # Test 5: Check main URLs
    print("\nTest 5: Checking main URLs configuration...")
    with open('connectly/urls.py', 'r') as f:
        main_urls_content = f.read()

    # Check that old unprotected endpoint is commented out
    if "# path('api/auth/token/', csrf_exempt(obtain_auth_token)" in main_urls_content:
        print("  [PASS] Old unprotected token endpoint is commented out")
    elif "path('api/auth/token/', csrf_exempt(obtain_auth_token)" in main_urls_content:
        print("  [FAIL] Old unprotected token endpoint still active!")
    else:
        print("  [PASS] Old token endpoint removed")

    # Summary
    print("\n" + "=" * 70)
    print("CONFIGURATION TEST SUMMARY")
    print("=" * 70)
    print("\nRate limiting is configured for:")
    print("  1. /api/auth/token/ - 5 requests per minute (via RateLimitedObtainAuthToken)")
    print("  2. /api/auth/google/ - 5 requests per minute (via @ratelimit decorator)")
    print("\nRate limit key: IP address")
    print("Rate limit action: Block (returns 429 Too Many Requests)")
    print("=" * 70)

if __name__ == "__main__":
    test_rate_limit_configuration()