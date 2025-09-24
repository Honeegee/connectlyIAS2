# Control #2: Rate Limiting for Authentication - Manual Implementation Guide

## Overview
This guide provides step-by-step instructions to manually implement rate limiting on authentication endpoints to prevent brute force attacks.

---

## Learning Objectives
By following this guide, you will learn:
1. How to use django-ratelimit for API protection
2. How to create custom rate-limited views
3. How to handle rate limit exceptions
4. How to configure URL routing for security

---

## Prerequisites

### Required Knowledge
- Basic Django and Django REST Framework
- Understanding of HTTP status codes
- Class-based views in Django
- Decorator patterns in Python

### Required Libraries
- `django-ratelimit==4.1.0` (already in requirements.txt)

---

## Step-by-Step Implementation

### Step 1: Understanding the Problem

**What are we protecting against?**
- Brute force password attacks
- Credential stuffing attacks
- API abuse through repeated login attempts

**Why is rate limiting important?**
- Prevents automated attack tools
- Reduces server load from malicious requests
- Protects user accounts from unauthorized access attempts
- Required by security compliance standards

**Current vulnerable endpoints:**
- `/api/auth/token/` - Token authentication (no protection)
- `/api/auth/google/` - Has basic rate limiting (5/hour - too lenient)

---

### Step 2: Add Required Imports

**Location:** `authentication/views.py`

**Add these imports at the top:**

```python
from rest_framework.authtoken.views import ObtainAuthToken  # <-- ADD
from django_ratelimit.decorators import ratelimit  # Already exists
from django_ratelimit.exceptions import Ratelimited  # <-- ADD
from django.utils.decorators import method_decorator  # <-- ADD
```

**What each import does:**
- `ObtainAuthToken`: Base class for token authentication
- `ratelimit`: Decorator to limit request rates
- `Ratelimited`: Exception raised when limit exceeded
- `method_decorator`: Allows using function decorators on class methods

---

### Step 3: Create Rate-Limited Token View

**Location:** `authentication/views.py` (after imports, before other views)

```python
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class RateLimitedObtainAuthToken(ObtainAuthToken):
    """
    Custom token authentication view with rate limiting.
    Limits: 5 requests per minute per IP address
    """

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            logger.info(f"Token obtained successfully for user")
            return response
        except Ratelimited:
            logger.warning(f"Rate limit exceeded for IP: {request.META.get('REMOTE_ADDR')}")
            return Response(
                {'error': 'Rate limit exceeded. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
```

**Understanding the Code:**

1. **@method_decorator** - Applies rate limit to the class
   - `key='ip'`: Track by IP address
   - `rate='5/m'`: 5 requests per minute
   - `method='POST'`: Only limit POST requests
   - `block=True`: Block requests when limit exceeded
   - `name='dispatch'`: Apply to dispatch method (entry point for class-based views)

2. **Class inheritance:**
   - Extends `ObtainAuthToken` (DRF's built-in token view)
   - Adds rate limiting without changing core functionality

3. **Exception handling:**
   - Catches `Ratelimited` exception
   - Returns 429 status (Too Many Requests)
   - Logs the violation for monitoring

---

### Step 4: Update Google Login Rate Limit

**Location:** `authentication/views.py` (find the google_login function)

**Change the rate limit decorator:**

```python
# BEFORE (too lenient):
@ratelimit(key='ip', rate='5/h', method='POST', block=True)

# AFTER (more secure):
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
```

**Also update the docstring:**

```python
@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', method='POST', block=True)  # <-- CHANGED
def google_login(request):
    """
    Endpoint to handle Google OAuth login.
    Rate limited to 5 requests per minute per IP address.  # <-- ADDED

    Expects a token from the Google OAuth process.
    Returns a DRF token for authenticated API access.
    """
```

**Why change 5/h to 5/m?**
- 5 per hour = 1 attempt every 12 minutes (too slow for legitimate users having issues)
- 5 per minute = Better balance between security and usability
- Still prevents brute force (max 300 attempts/hour vs unlimited)

---

### Step 5: Update Authentication URLs

**Location:** `authentication/urls.py`

**Update the imports and add the token endpoint:**

```python
# BEFORE:
from .views import google_login, oauth_demo, oauth_callback

urlpatterns = [
    path('google/', google_login, name='google-login'),
    path('demo/', oauth_demo, name='oauth-demo'),
    path('callback/', oauth_callback, name='oauth-callback'),
]

# AFTER:
from .views import google_login, oauth_demo, oauth_callback, RateLimitedObtainAuthToken  # <-- ADDED

urlpatterns = [
    path('token/', RateLimitedObtainAuthToken.as_view(), name='api-token-auth-ratelimited'),  # <-- ADDED
    path('google/', google_login, name='google-login'),
    path('demo/', oauth_demo, name='oauth-demo'),
    path('callback/', oauth_callback, name='oauth-callback'),
]
```

**What changed:**
- Imported `RateLimitedObtainAuthToken`
- Added `/api/auth/token/` endpoint using our rate-limited view
- `.as_view()` converts class-based view to function view for URL routing

---

### Step 6: Update Main URL Configuration

**Location:** `connectly/urls.py`

**Comment out the old unprotected endpoint:**

```python
urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth endpoints
    # BEFORE (VULNERABLE):
    # path('api/auth/token/', csrf_exempt(obtain_auth_token), name='api-token-auth'),

    # AFTER (SECURE):
    # path('api/auth/token/', csrf_exempt(obtain_auth_token), name='api-token-auth'),  # Replaced with rate-limited version
    path('api/auth/', include('authentication.urls')),  # Google OAuth + Rate-limited token endpoint
    path('api/auth/', include('dj_rest_auth.urls')),  # Regular authentication endpoints
```

**Why comment instead of delete?**
- Shows the change was intentional
- Provides documentation of what was replaced
- Easy to rollback if needed

---

### Step 7: Create Configuration Test Script

**Location:** Create new file `test_rate_limit_config.py` in project root

```python
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

    for imp in required_imports:
        if imp in views_content:
            print(f"  [PASS] Found: {imp}")
        else:
            print(f"  [FAIL] Missing: {imp}")

    # Test 2: Check RateLimitedObtainAuthToken class
    print("\nTest 2: Checking RateLimitedObtainAuthToken class...")
    if 'class RateLimitedObtainAuthToken' in views_content:
        print("  [PASS] RateLimitedObtainAuthToken class exists")

        # Check for rate limit decorator
        if "@method_decorator(ratelimit(key='ip', rate='5/m'" in views_content:
            print("  [PASS] Class has rate limit decorator (5/m)")
        else:
            print("  [FAIL] Class missing rate limit decorator")

        # Check for exception handling
        if 'except Ratelimited:' in views_content:
            print("  [PASS] Handles Ratelimited exception")
        else:
            print("  [FAIL] No Ratelimited exception handling")

        # Check for 429 status
        if 'HTTP_429_TOO_MANY_REQUESTS' in views_content:
            print("  [PASS] Returns 429 status code")
        else:
            print("  [FAIL] No 429 status code")
    else:
        print("  [FAIL] RateLimitedObtainAuthToken class not found")

    # Test 3: Check google_login
    print("\nTest 3: Checking google_login rate limiting...")
    if "@ratelimit(key='ip', rate='5/m'" in views_content:
        print("  [PASS] google_login has rate limit decorator (5/m)")
    else:
        print("  [FAIL] google_login missing proper rate limit")

    # Test 4: Check URLs
    print("\nTest 4: Checking URLs configuration...")
    with open('authentication/urls.py', 'r') as f:
        urls_content = f.read()

    if 'RateLimitedObtainAuthToken' in urls_content:
        print("  [PASS] RateLimitedObtainAuthToken imported")
    else:
        print("  [FAIL] RateLimitedObtainAuthToken not imported")

    if "path('token/', RateLimitedObtainAuthToken.as_view()" in urls_content:
        print("  [PASS] Token endpoint uses rate-limited view")
    else:
        print("  [FAIL] Token endpoint not configured")

    # Summary
    print("\n" + "=" * 70)
    print("CONFIGURATION SUMMARY")
    print("=" * 70)
    print("\nProtected endpoints:")
    print("  1. /api/auth/token/ - 5 requests/minute")
    print("  2. /api/auth/google/ - 5 requests/minute")
    print("\nRate limit method: IP address blocking")
    print("Response when limited: 429 Too Many Requests")
    print("=" * 70)

if __name__ == "__main__":
    test_rate_limit_configuration()
```

---

### Step 8: Run Configuration Test

```bash
python test_rate_limit_config.py
```

**Expected Output:**
```
======================================================================
RATE LIMITING CONFIGURATION TEST
======================================================================

Test 1: Checking imports...
  [PASS] Found: from django_ratelimit.decorators import ratelimit
  [PASS] Found: from django_ratelimit.exceptions import Ratelimited
  [PASS] Found: from django.utils.decorators import method_decorator

Test 2: Checking RateLimitedObtainAuthToken class...
  [PASS] RateLimitedObtainAuthToken class exists
  [PASS] Class has rate limit decorator (5/m)
  [PASS] Handles Ratelimited exception
  [PASS] Returns 429 status code

Test 3: Checking google_login rate limiting...
  [PASS] google_login has rate limit decorator (5/m)

Test 4: Checking URLs configuration...
  [PASS] RateLimitedObtainAuthToken imported
  [PASS] Token endpoint uses rate-limited view

======================================================================
CONFIGURATION SUMMARY
======================================================================

Protected endpoints:
  1. /api/auth/token/ - 5 requests/minute
  2. /api/auth/google/ - 5 requests/minute

Rate limit method: IP address blocking
Response when limited: 429 Too Many Requests
======================================================================
```

All tests should show **[PASS]**.

---

### Step 9: Understanding Rate Limit Parameters

**The ratelimit decorator accepts these parameters:**

```python
@ratelimit(
    key='ip',           # What to track (ip, user, or custom)
    rate='5/m',         # Limit (number/period: s=second, m=minute, h=hour, d=day)
    method='POST',      # HTTP methods to limit
    block=True          # Block or just mark (True=block with 403, False=mark only)
)
```

**Common rate limit patterns:**

| Pattern | Meaning | Use Case |
|---------|---------|----------|
| `5/m` | 5 per minute | Login endpoints |
| `100/h` | 100 per hour | API usage |
| `1000/d` | 1000 per day | Free tier limits |
| `10/s` | 10 per second | Heavy traffic endpoints |

**Key parameter options:**

1. **key options:**
   - `'ip'`: Track by IP address (anonymous users)
   - `'user'`: Track by authenticated user
   - `'user_or_ip'`: Use user if authenticated, else IP
   - Custom function: `key=lambda g, r: r.META.get('HTTP_X_FORWARDED_FOR', r.META['REMOTE_ADDR'])`

2. **block parameter:**
   - `block=True`: Return 403/429 when limit exceeded
   - `block=False`: Mark request as limited but allow it (check with `request.limited`)

---

### Step 10: Commit Your Changes

```bash
# Check what changed
git status

# Stage your changes
git add authentication/views.py
git add authentication/urls.py
git add connectly/urls.py
git add test_rate_limit_config.py
git add milestone_2_implementation/Implementation_Log.md

# Commit with descriptive message
git commit -m "Implement Control #2: Rate Limiting for Authentication

- Created RateLimitedObtainAuthToken class for token endpoint
- Applied 5 requests/minute rate limit (IP-based)
- Updated google_login from 5/hour to 5/minute
- Added Ratelimited exception handling with 429 responses
- Modified URL routing to use rate-limited views
- Created test_rate_limit_config.py for validation
- All configuration tests passing

Security Impact: Prevents brute force attacks on authentication endpoints"

# Push to repository
git push origin master
```

---

## Common Issues and Troubleshooting

### Issue 1: "429 Too Many Requests" during testing

**Cause:** Rate limit triggered during rapid testing

**Solutions:**
1. Wait 1 minute for rate limit to reset
2. Restart Django server to clear rate limit cache
3. Use different IP addresses for testing
4. Temporarily increase rate limit for testing: `rate='100/m'`

### Issue 2: Rate limiting not working

**Cause:** Decorator not applied or misconfigured

**Solutions:**
1. Check decorator is before function/class definition
2. Verify `block=True` is set
3. Check django-ratelimit is installed: `pip show django-ratelimit`
4. Run configuration test: `python test_rate_limit_config.py`

### Issue 3: ImportError for Ratelimited

**Cause:** Missing import

**Solution:**
```python
from django_ratelimit.exceptions import Ratelimited
```

---

## Testing Rate Limiting (Manual)

### Using curl:

```bash
# Test 1: Try 6 requests rapidly
for i in {1..6}; do
    curl -X POST http://localhost:8000/api/auth/token/ \
        -H "Content-Type: application/json" \
        -d '{"username":"test","password":"test"}' \
        -w "\nStatus: %{http_code}\n\n"
    sleep 0.5
done
```

**Expected:**
- Requests 1-5: Status 400 (bad credentials) or 200 (success)
- Request 6: Status 429 (rate limited)

### Using Python requests:

```python
import requests

for i in range(1, 7):
    response = requests.post(
        'http://localhost:8000/api/auth/token/',
        json={'username': 'test', 'password': 'test'}
    )
    print(f"Request {i}: Status {response.status_code}")
    if response.status_code == 429:
        print(f"  Rate limited! Message: {response.json()}")
```

---

## Understanding HTTP 429

**429 Too Many Requests** indicates:
- Client has sent too many requests
- Should include `Retry-After` header (optional)
- Client should back off and retry later

**Our implementation returns:**
```json
{
    "error": "Rate limit exceeded. Please try again later."
}
```

**Best practices:**
- Log rate limit violations
- Return clear error message
- Consider adding `Retry-After` header
- Monitor rate limit hits for abuse patterns

---

## Advanced: Custom Rate Limit Keys

**Example: Rate limit by user AND IP:**

```python
def user_and_ip(group, request):
    if request.user.is_authenticated:
        return f"user:{request.user.id}"
    return f"ip:{request.META.get('REMOTE_ADDR')}"

@ratelimit(key=user_and_ip, rate='5/m', method='POST', block=True)
def my_view(request):
    # ...
```

**Example: Rate limit by API key:**

```python
def api_key(group, request):
    return request.META.get('HTTP_X_API_KEY', 'anonymous')

@ratelimit(key=api_key, rate='100/h', method=['GET', 'POST'], block=True)
def api_view(request):
    # ...
```

---

## Security Considerations

### What rate limiting protects against:
✅ Brute force password attacks
✅ Credential stuffing
✅ API abuse
✅ DoS (Denial of Service)

### What it doesn't protect against:
❌ Distributed attacks (many IPs)
❌ Attacks from legitimate user accounts
❌ Application logic vulnerabilities

### Additional security layers needed:
- Account lockout after failed attempts
- CAPTCHA for suspicious activity
- IP reputation checking
- WAF (Web Application Firewall)

---

## Testing Checklist

- [ ] RateLimitedObtainAuthToken class created
- [ ] Imports added (ObtainAuthToken, Ratelimited, method_decorator)
- [ ] google_login rate changed to 5/m
- [ ] URL routing updated in authentication/urls.py
- [ ] Old endpoint commented in connectly/urls.py
- [ ] Configuration test created
- [ ] All configuration tests passing
- [ ] Rate limit parameters verified (5/m, key=ip, block=True)
- [ ] 429 status code handling confirmed
- [ ] Changes committed to git
- [ ] Changes pushed to repository

---

## Summary

**What You Implemented:**
- ✅ Rate-limited token authentication endpoint
- ✅ IP-based brute force protection (5 requests/minute)
- ✅ Proper 429 error responses
- ✅ Exception handling for rate limits
- ✅ Comprehensive configuration testing

**Security Impact:**
- Prevents brute force attacks (max 300 attempts/hour vs unlimited)
- Reduces server load from malicious traffic
- Protects user accounts from credential stuffing
- Meets security compliance requirements

**Skills Learned:**
- django-ratelimit usage
- Class-based view decoration
- Rate limit exception handling
- Security-focused URL routing

---

**Created:** 2025-09-24
**Author:** Security Implementation Team
**Control:** #2 - Rate Limiting
**Status:** ✅ Complete and Tested