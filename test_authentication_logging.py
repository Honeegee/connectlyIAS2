#!/usr/bin/env python
"""
Test authentication endpoints to verify JWT token redaction in real scenarios.
Simulates authentication flow without requiring full Django server.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectly.settings')
django.setup()

from singletons.logger_singleton import LoggerSingleton
from authentication.views import sanitize_user_data_for_logging

def test_authentication_scenarios():
    """Test various authentication scenarios that would normally expose tokens."""

    print("TESTING AUTHENTICATION SCENARIOS WITH TOKEN REDACTION")
    print("=" * 60)

    # Get logger instance
    logger = LoggerSingleton().get_logger()

    # Simulate various authentication scenarios
    test_scenarios = [
        {
            "name": "Google OAuth Response",
            "data": {
                "access_token": "ya29.A0AfH6SMDexampleGoogleAccessTokenVeryLongString123456789",
                "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjE2NzAyOGY4ZjE2OGVhODg2MTI3YzMxMjVlNjM5NWI3N2M1NDJhYjIiLCJ0eXAiOiJKV1QifQ",
                "email": "user@example.com",
                "name": "Test User"
            }
        },
        {
            "name": "Django Token Authentication",
            "data": {
                "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
                "user_id": 123,
                "username": "testuser"
            }
        },
        {
            "name": "API Key Authentication",
            "data": {
                "api_key": "sk-1234567890abcdef1234567890abcdef1234567890abcdef",
                "client_id": "app_12345678901234567890123456789012"
            }
        },
        {
            "name": "Bearer Token Request",
            "data": {
                "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0",
                "refresh_token": "rt_1234567890abcdef1234567890abcdef1234567890"
            }
        }
    ]

    print("\\n1. TESTING LOGGER REDACTION:")
    print("-" * 40)

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\\n{i}. {scenario['name']}:")

        # Test logging various sensitive data patterns
        logger.info(f"Authentication attempt with data: {scenario['data']}")
        logger.error(f"Failed authentication: access_token={scenario['data'].get('access_token', 'N/A')}")
        logger.warning(f"Token validation failed for token: {scenario['data'].get('token', scenario['data'].get('id_token', 'N/A'))}")

        print(f"   [OK] Logged authentication scenario - tokens should be redacted")

    print("\\n\\n2. TESTING DATABASE SANITIZATION:")
    print("-" * 40)

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\\n{i}. {scenario['name']} Database Storage:")

        # Test database sanitization
        sanitized = sanitize_user_data_for_logging(scenario['data'])

        print(f"   Original keys: {list(scenario['data'].keys())}")
        print(f"   Sanitized data:")
        for key, value in sanitized.items():
            print(f"     {key}: {value}")

        # Check if sensitive fields were properly redacted
        sensitive_fields = ['access_token', 'id_token', 'token', 'api_key', 'refresh_token', 'authorization']
        redacted_count = sum(1 for field in sensitive_fields if field in sanitized and '[REDACTED_TOKEN]' in str(sanitized[field]))
        total_sensitive = sum(1 for field in sensitive_fields if field in scenario['data'])

        if redacted_count == total_sensitive:
            print(f"   [OK] All {total_sensitive} sensitive fields redacted")
        else:
            print(f"   [WARNING] Only {redacted_count}/{total_sensitive} fields redacted")

    print("\\n\\n3. TESTING ERROR SCENARIOS:")
    print("-" * 40)

    # Test error scenarios that might expose tokens
    error_scenarios = [
        "Failed to validate JWT token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature",
        "Google API error with Bearer ya29.A0AfH6SMDexampleToken",
        "Invalid access_token: sk-1234567890abcdef1234567890abcdef",
        "Authorization header malformed: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
    ]

    for i, error_msg in enumerate(error_scenarios, 1):
        print(f"\\n{i}. Error scenario:")
        print(f"   Original: {error_msg[:50]}...")
        logger.error(error_msg)
        print(f"   [OK] Error logged - sensitive data should be redacted")

    print("\\n\\n4. TESTING COMPLEX TOKEN PATTERNS:")
    print("-" * 40)

    complex_patterns = [
        "User login: {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9', 'token': '1234567890abcdef'}",
        "OAuth flow: access_token=ya29.example&refresh_token=rt_example&id_token=eyJ.jwt.token",
        "Multiple tokens: Bearer token1, api_key=key123, Token token2",
        "JSON response: {\"access_token\": \"secret123\", \"token_type\": \"Bearer\"}"
    ]

    for i, pattern in enumerate(complex_patterns, 1):
        print(f"\\n{i}. Complex pattern test:")
        print(f"   Original: {pattern[:50]}...")
        logger.info(f"Processing complex auth pattern: {pattern}")
        print(f"   [OK] Complex pattern logged - should be redacted")

    print("\\n\\n" + "=" * 60)
    print("AUTHENTICATION LOGGING TEST COMPLETED!")
    print("Check logs/connectly_YYYYMMDD.log for redacted output")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_authentication_scenarios()
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        sys.exit(1)