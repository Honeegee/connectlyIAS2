# Control #1: JWT Token Redaction - Manual Implementation Guide

## Overview
This guide provides step-by-step instructions to manually implement JWT token redaction in application logs. This security control prevents sensitive authentication tokens from being exposed in log files.

---

## Learning Objectives
By following this guide, you will learn:
1. How to create custom logging filters in Python
2. How to use regular expressions for pattern matching
3. How to integrate security filters into existing logging infrastructure
4. How to test and validate security controls

---

## Prerequisites

### Required Knowledge
- Basic Python programming
- Understanding of regular expressions (regex)
- Familiarity with Django logging
- Git version control basics

### Required Files
- `singletons/logger_singleton.py` (existing)
- `authentication/views.py` (existing)

---

## Step-by-Step Implementation

### Step 1: Understanding the Problem

**What are we protecting?**
- JWT tokens (eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...)
- Bearer tokens in Authorization headers
- API keys, passwords, and secrets

**Why is this important?**
- Logs are often stored for long periods
- Multiple people may have access to logs
- Logs might be sent to external monitoring systems
- Exposed tokens can be used for unauthorized access

**Current vulnerable logging:**
```python
# BAD - This exposes the token
logger.error(f"Failed to verify Google token: {google_response.text}")
```

---

### Step 2: Create the Sensitive Data Filter Class

**Location:** `singletons/logger_singleton.py`

**Step 2.1: Import Required Modules**

Add `re` (regular expressions) to your imports:

```python
import logging
import os
import re  # <-- ADD THIS LINE
from datetime import datetime
from typing import Optional
```

**Why?** The `re` module provides regex pattern matching to detect tokens in log messages.

---

**Step 2.2: Create the Filter Class**

Add this class BEFORE the `LoggerSingleton` class:

```python
class SensitiveDataFilter(logging.Filter):
    """Filter to redact sensitive data from log records."""

    REDACTION_PATTERNS = [
        # Pattern 1: Bearer tokens with spaces
        (re.compile(r'(Bearer\s+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),

        # Pattern 2: Authorization header with Bearer
        (re.compile(r'(Authorization[:\s]+Bearer\s+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),

        # Pattern 3: Generic token field
        (re.compile(r'(token["\s:=]+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),

        # Pattern 4: access_token field
        (re.compile(r'(access_token["\s:=]+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),

        # Pattern 5: refresh_token field
        (re.compile(r'(refresh_token["\s:=]+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),

        # Pattern 6: API keys
        (re.compile(r'(api[_-]?key["\s:=]+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),

        # Pattern 7: Passwords
        (re.compile(r'(password["\s:=]+)[^\s,}"\']+', re.IGNORECASE), r'\1[REDACTED]'),

        # Pattern 8: Secrets
        (re.compile(r'(secret["\s:=]+)[^\s,}"\']+', re.IGNORECASE), r'\1[REDACTED]'),
    ]

    def filter(self, record):
        # Redact sensitive data in the main message
        if hasattr(record, 'msg'):
            message = str(record.msg)
            for pattern, replacement in self.REDACTION_PATTERNS:
                message = pattern.sub(replacement, message)
            record.msg = message

        # Redact sensitive data in message arguments
        if hasattr(record, 'args') and record.args:
            args = list(record.args) if isinstance(record.args, tuple) else [record.args]
            redacted_args = []
            for arg in args:
                arg_str = str(arg)
                for pattern, replacement in self.REDACTION_PATTERNS:
                    arg_str = pattern.sub(replacement, arg_str)
                redacted_args.append(arg_str)
            record.args = tuple(redacted_args)

        return True
```

**Understanding the Code:**

1. **REDACTION_PATTERNS**: List of tuples containing:
   - Regex pattern to detect sensitive data
   - Replacement string (keeps the field name, redacts the value)

2. **Regex Pattern Breakdown** (using Pattern 1 as example):
   ```python
   r'(Bearer\s+)[A-Za-z0-9\-._~+/]+=*'
   ```
   - `(Bearer\s+)` - Capture group: "Bearer" followed by whitespace (this is kept)
   - `[A-Za-z0-9\-._~+/]+=*` - Match the token characters (this is removed)
   - `re.IGNORECASE` - Match case-insensitive (bearer, BEARER, Bearer all match)

3. **filter() method**:
   - Checks `record.msg` (the log message)
   - Checks `record.args` (any additional parameters)
   - Applies all patterns to redact sensitive data
   - Returns True to allow the log record to pass through

---

### Step 3: Apply the Filter to Logger Handlers

**Location:** Still in `singletons/logger_singleton.py`, inside the `_initialize()` method

**Step 3.1: Create Filter Instance**

Add this line after creating the logs directory:

```python
def _initialize(self) -> None:
    """Initialize the logger with proper configuration."""
    self.logger = logging.getLogger("connectly_logger")
    self.logger.setLevel(logging.INFO)

    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create sensitive data filter
    sensitive_filter = SensitiveDataFilter()  # <-- ADD THIS LINE
```

**Step 3.2: Apply Filter to Console Handler**

Modify the console handler section:

```python
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(sensitive_filter)  # <-- ADD THIS LINE
```

**Step 3.3: Apply Filter to File Handler**

Modify the file handler section:

```python
    # Create file handler
    file_handler = logging.FileHandler(
        f'logs/connectly_{datetime.now().strftime("%Y%m%d")}.log'
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.addFilter(sensitive_filter)  # <-- ADD THIS LINE
```

**Why apply to both handlers?**
- Console handler: Protects terminal/console output
- File handler: Protects log files from exposure

---

### Step 4: Sanitize Existing Logging Statements

**Location:** `authentication/views.py`

**Step 4.1: Find Vulnerable Logging**

Search for line 89 (or look for this pattern):

```python
# BEFORE (VULNERABLE):
if not google_response.ok:
    logger.error(f"Failed to verify Google token: {google_response.text}")
    return Response(
        {'error': 'Invalid Google token'},
        status=status.HTTP_401_UNAUTHORIZED
    )
```

**Step 4.2: Replace with Safe Logging**

```python
# AFTER (SECURE):
if not google_response.ok:
    logger.error(f"Failed to verify Google token: Status {google_response.status_code}")
    return Response(
        {'error': 'Invalid Google token'},
        status=status.HTTP_401_UNAUTHORIZED
    )
```

**What changed?**
- `{google_response.text}` → `Status {google_response.status_code}`
- We log the status code (401, 403, etc.) instead of the full response
- The response might contain tokens or sensitive error details

---

### Step 5: Create a Test Script

**Location:** Create new file `test_token_redaction.py` in project root

**Step 5.1: Create the Test File**

```python
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
```

**What does this test do?**
1. Imports the logger singleton
2. Creates 6 test cases with different sensitive data patterns
3. Logs each test case
4. Shows console output and creates log file
5. Allows you to verify redaction worked

---

### Step 6: Run and Verify

**Step 6.1: Run the Test**

```bash
python test_token_redaction.py
```

**Expected Console Output:**
```
Testing token redaction...
============================================================

Test Cases (these will be logged with redaction):

1. User authenticated with Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token
2. Authorization: Bearer abc123token456def789
3. Received access_token: sk_test_1234567890abcdef
4. API request with token=sensitive_api_key_12345
5. Login attempt with password: MySecretPass123
6. Configuration loaded with secret: my_secret_key_value

============================================================
Check the log file in logs/ directory to verify redaction
All tokens should appear as [REDACTED]
============================================================
2025-09-24 12:56:45,275 - INFO - User authenticated with Bearer [REDACTED]
2025-09-24 12:56:45,276 - INFO - Authorization: Bearer [REDACTED]
2025-09-24 12:56:45,276 - INFO - Received access_token: [REDACTED]
2025-09-24 12:56:45,276 - INFO - API request with token=[REDACTED]
2025-09-24 12:56:45,276 - INFO - Login attempt with password: [REDACTED]
2025-09-24 12:56:45,276 - INFO - Configuration loaded with secret: [REDACTED]
```

**Step 6.2: Check Log File**

```bash
# On Windows:
type logs\connectly_20250924.log | findstr /C:"[REDACTED]"

# On Linux/Mac:
tail -10 logs/connectly_$(date +%Y%m%d).log
```

**Expected Log File Content:**
```
2025-09-24 12:56:45,275 - INFO - [connectly_logger] - User authenticated with Bearer [REDACTED]
2025-09-24 12:56:45,276 - INFO - [connectly_logger] - Authorization: Bearer [REDACTED]
2025-09-24 12:56:45,276 - INFO - [connectly_logger] - Received access_token: [REDACTED]
2025-09-24 12:56:45,276 - INFO - [connectly_logger] - API request with token=[REDACTED]
2025-09-24 12:56:45,276 - INFO - [connectly_logger] - Login attempt with password: [REDACTED]
2025-09-24 12:56:45,276 - INFO - [connectly_logger] - Configuration loaded with secret: [REDACTED]
```

---

### Step 7: Commit Your Changes

**Step 7.1: Check What Changed**

```bash
git status
```

You should see:
- Modified: `singletons/logger_singleton.py`
- Modified: `authentication/views.py`
- New file: `test_token_redaction.py`

**Step 7.2: Stage Your Changes**

```bash
git add singletons/logger_singleton.py
git add authentication/views.py
git add test_token_redaction.py
```

**Step 7.3: Commit with Descriptive Message**

```bash
git commit -m "Implement Control #1: JWT Token Redaction in Logs

- Added SensitiveDataFilter class to logger_singleton.py
- Implemented regex patterns to redact Bearer tokens, JWT, passwords, secrets
- Applied filter to both console and file logging handlers
- Sanitized OAuth error logging to prevent token exposure
- Created test_token_redaction.py for validation
- All tests passing - sensitive data successfully redacted

Security Impact: Prevents authentication token exposure in application logs"
```

**Step 7.4: Push to Repository**

```bash
git push origin master
```

---

## Common Issues and Troubleshooting

### Issue 1: "No module named singletons"

**Cause:** Running the test from wrong directory

**Solution:**
```bash
# Make sure you're in the project root
cd C:\Users\Honey\Desktop\ConnectlyIPT\school-connectly
python test_token_redaction.py
```

### Issue 2: Tokens Still Appearing in Logs

**Cause:** Filter not applied correctly

**Solution:**
1. Check that `sensitive_filter = SensitiveDataFilter()` is created
2. Verify `addFilter(sensitive_filter)` is called on BOTH handlers
3. Restart any running Django servers

### Issue 3: Log File Not Found

**Cause:** Logger hasn't created the file yet

**Solution:**
```bash
# Create logs directory manually
mkdir logs

# Run the test again
python test_token_redaction.py
```

---

## Understanding Regex Patterns (Deep Dive)

### Pattern Anatomy

Let's break down one pattern in detail:

```python
(re.compile(r'(Bearer\s+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]')
```

**Components:**

1. **`r'...'`** - Raw string (treats backslashes literally)

2. **`(Bearer\s+)`** - First capture group (kept):
   - `Bearer` - Literal text "Bearer"
   - `\s+` - One or more whitespace characters

3. **`[A-Za-z0-9\-._~+/]+=*`** - Token pattern (removed):
   - `[A-Za-z0-9\-._~+/]+` - One or more of these characters
   - `=*` - Zero or more equals signs (JWT padding)

4. **`re.IGNORECASE`** - Match regardless of case

5. **`r'\1[REDACTED]'`** - Replacement:
   - `\1` - Keep first capture group (Bearer )
   - `[REDACTED]` - Replace token with this text

**Result:**
- Input: `"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"`
- Output: `"Bearer [REDACTED]"`

### Creating Your Own Patterns

**Template:**
```python
(re.compile(r'(FIELD_NAME[:\s=]+)TOKEN_PATTERN', re.IGNORECASE), r'\1[REDACTED]')
```

**Example - Redact Session IDs:**
```python
(re.compile(r'(sessionid[:\s=]+)[A-Za-z0-9]+', re.IGNORECASE), r'\1[REDACTED]')
```

---

## Testing Checklist

Use this checklist to verify your implementation:

- [ ] SensitiveDataFilter class created with all 8 patterns
- [ ] Filter applied to console handler
- [ ] Filter applied to file handler
- [ ] Vulnerable logging in authentication/views.py fixed
- [ ] Test script created (test_token_redaction.py)
- [ ] Test script runs without errors
- [ ] Console output shows [REDACTED] tokens
- [ ] Log file shows [REDACTED] tokens
- [ ] All 6 test cases pass
- [ ] Changes committed to git
- [ ] Changes pushed to repository

---

## Learning Exercise

**Try adding these additional patterns yourself:**

1. **Credit Card Redaction:**
```python
(re.compile(r'(card[_\s]?number[:\s=]+)\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}', re.IGNORECASE), r'\1[REDACTED]')
```

2. **Email Redaction (partial):**
```python
(re.compile(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[A-Z|a-z]{2,})', re.IGNORECASE), r'[REDACTED]@\2')
```

3. **IP Address Redaction:**
```python
(re.compile(r'(ip[:\s=]+)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', re.IGNORECASE), r'\1[REDACTED]')
```

**Challenge:** Implement one of these and test it!

---

## Review Questions

Test your understanding:

1. **Why do we use capture groups `()` in regex patterns?**
   <details>
   <summary>Answer</summary>
   To keep the field name (like "Bearer ") while replacing only the sensitive value.
   </details>

2. **What's the difference between console_handler and file_handler?**
   <details>
   <summary>Answer</summary>
   Console handler outputs to terminal/screen, file handler writes to log files. Both need the filter!
   </details>

3. **Why sanitize `google_response.text` in authentication/views.py?**
   <details>
   <summary>Answer</summary>
   The response text might contain tokens or sensitive error details that shouldn't be logged.
   </details>

4. **What does `re.IGNORECASE` do?**
   <details>
   <summary>Answer</summary>
   Makes the pattern match regardless of case (bearer, BEARER, Bearer all match).
   </details>

---

## Summary

**What You Implemented:**
- ✅ Custom logging filter to redact sensitive data
- ✅ Regex patterns for 8 types of sensitive data
- ✅ Filter integration into existing logging infrastructure
- ✅ Sanitization of vulnerable logging statements
- ✅ Comprehensive testing and validation

**Security Impact:**
- Prevents token exposure in logs
- Protects against credential leakage
- Reduces risk of unauthorized access from log breaches

**Skills Learned:**
- Python logging filters
- Regular expression pattern matching
- Security-first logging practices
- Test-driven security validation

---

## Next Steps

After mastering Control #1, you'll implement:
- **Control #2:** Rate Limiting
- **Control #3:** Debug Prevention
- **Control #4:** Secret Management
- **Control #5:** Server Info Hiding

Each control builds on these foundational skills!

---

**Created:** 2025-09-24
**Author:** Security Implementation Team
**Control:** #1 - JWT Token Redaction
**Status:** ✅ Complete and Tested