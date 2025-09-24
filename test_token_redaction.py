"""
Test script to verify JWT token redaction in logs.
"""

from singletons.logger_singleton import LoggerSingleton

def test_token_redaction():
    """Test that sensitive tokens are redacted in logs."""
    logger = LoggerSingleton().get_logger()

    print("Testing token redaction...")
    print("=" * 60)

    test_cases = [
        "User authenticated with Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token",
        "Authorization: Bearer abc123token456def789",
        "Received access_token: sk_test_1234567890abcdef",
        "API request with token=sensitive_api_key_12345",
        "Login attempt with password: MySecretPass123",
        "Configuration loaded with secret: my_secret_key_value"
    ]

    print("\nTest Cases (these will be logged with redaction):\n")
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case}")
        logger.info(test_case)

    print("\n" + "=" * 60)
    print("Check the log file in logs/ directory to verify redaction")
    print("All tokens should appear as [REDACTED]")
    print("=" * 60)

if __name__ == "__main__":
    test_token_redaction()