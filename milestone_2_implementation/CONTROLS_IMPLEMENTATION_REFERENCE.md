# Controls Implementation Reference Guide

## Quick Reference for All 5 Security Controls

This document contains everything you need to review, study, and understand each implemented control.

---

## 📋 **Control #1: JWT Token Redaction in Application Logs**

### **Purpose:**
Prevent sensitive JWT tokens and credentials from being exposed in application log files.

### **What Was Done:**

#### **File 1: `singletons/logger_singleton.py`**
**Location:** Lines 13-44

**Implementation:**
```python
class SensitiveDataFilter(logging.Filter):
    """Filter to redact sensitive data from log records."""

    REDACTION_PATTERNS = [
        (re.compile(r'(Bearer\s+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(Authorization[:\s]+Bearer\s+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(token["\s:=]+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(access_token["\s:=]+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(refresh_token["\s:=]+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(api[_-]?key["\s:=]+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(password["\s:=]+)[^\s,}"\']+', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(secret["\s:=]+)[^\s,}"\']+', re.IGNORECASE), r'\1[REDACTED]'),
    ]
```

**What It Does:**
- Creates 8 regex patterns to detect sensitive data
- Replaces tokens with `[REDACTED]` marker
- Applied to both console and file handlers

#### **File 2: `authentication/views.py`**
**Location:** Lines 111-117

**Before:**
```python
logger.error(f"Failed to verify Google token: {google_response.text}")
```

**After:**
```python
if not google_response.ok:
    logger.error(f"Failed to verify Google token: Status {google_response.status_code}")
    # Token content NOT logged
```

### **How to Verify:**
1. Check logs in `logs/connectly_YYYYMMDD.log`
2. Search for tokens: `cat logs/connectly_*.log | grep -i "token"`
3. Should see `[REDACTED]` instead of actual tokens

### **Security Standard:**
- NIST SP 800-92: Guide to Computer Security Log Management
- OWASP A09:2021 – Security Logging and Monitoring Failures

---

## 📋 **Control #2: Rate Limiting for Authentication Endpoints**

### **Purpose:**
Prevent brute force attacks on authentication endpoints by limiting requests to 5 per minute per IP address.

### **What Was Done:**

#### **File 1: `authentication/views.py`**
**Location:** Lines 24-41

**Implementation:**
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

**Configuration:**
- `key='ip'` - Rate limit per IP address
- `rate='5/m'` - 5 requests per minute
- `block=True` - Block requests after limit
- Returns HTTP 429 with clear error message

#### **File 2: `authentication/views.py`**
**Location:** Line 86

**Google Login Rate Limiting:**
```python
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def google_login(request):
    """Rate limited to 5 requests per minute per IP address."""
```

#### **File 3: `authentication/urls.py`**
**Updated URL routing to use rate-limited endpoint**

### **Endpoints Protected:**
- `/api/auth/token/` - Token authentication
- `/api/auth/google/` - Google OAuth login
- `/api/auth/register/` - User registration (if implemented)

### **How to Verify:**
1. Send 6 rapid requests:
   ```bash
   for i in {1..6}; do curl -X POST http://127.0.0.1:8000/api/auth/token/ \
     -H "Content-Type: application/json" \
     -d '{"username":"test","password":"test"}'; done
   ```
2. Expected: First 5 return 400/401, 6th returns 429

### **Security Standard:**
- OWASP A07:2021 – Identification and Authentication Failures
- Prevents brute force, credential stuffing, account enumeration

---

## 📋 **Control #3: Debug Information Disclosure Prevention**

### **Purpose:**
Prevent Django debug pages and stack traces from being exposed to users in production.

### **What Was Done:**

#### **File 1: `connectly/settings.py`**
**Location:** Line 33

**Implementation:**
```python
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
# Default: False (production-safe)
```

**Additional Security Settings:**
```python
if not DEBUG:
    SILENCED_SYSTEM_CHECKS = []
    ADMINS = []  # Prevent email debug info to admins
    logging.getLogger('django.request').setLevel(logging.ERROR)
```

#### **File 2: `authentication/error_handling_middleware.py`**
**Custom Middleware for Secure Error Handling**

**Implementation:**
- Returns custom error templates instead of Django debug pages
- Logs errors internally without exposing to users
- Only active when DEBUG=False

#### **File 3: Custom Error Templates**
**Location:** `templates/`

- `404.html` - Custom Not Found page
- `403.html` - Custom Forbidden page
- `500.html` - Custom Server Error page

**What They Contain:**
- User-friendly error messages
- No stack traces or internal paths
- No Django version information

### **How to Verify:**
1. Set `DEBUG=False` in .env
2. Visit non-existent URL: `http://127.0.0.1:8000/test-404`
3. Should see custom 404 page, NOT Django debug page

### **Security Standard:**
- OWASP A05:2021 - Security Misconfiguration
- CWE-209: Generation of Error Message Containing Sensitive Information

---

## 📋 **Control #4: Environment-Based Secret Management**

### **Purpose:**
Remove all hardcoded secrets from source code and manage them securely through environment variables.

### **What Was Done:**

#### **File 1: `.env` (Environment Configuration)**
**Added:**
```bash
SECRET_KEY=prod-secure-key-change-this-in-production-never-commit-real-keys
GOOGLE_CLIENT_ID=135591834469-2eh68nfpmuj5afhfqoi20fk816nmr04r.apps.googleusercontent.com
GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/connectly
```

#### **File 2: `connectly/settings.py`**
**Location:** Lines 29-46

**Before:**
```python
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-zkktfou^524j17gl...')
# Insecure fallback allowed
```

**After:**
```python
SECRET_KEY = os.getenv('SECRET_KEY')

if not SECRET_KEY:
    raise ImproperlyConfigured(
        "SECRET_KEY environment variable is not set. "
        "Please configure SECRET_KEY in your .env file for security."
    )

if SECRET_KEY.startswith('django-insecure-'):
    import warnings
    warnings.warn("You are using an insecure SECRET_KEY.", RuntimeWarning)
```

**What Changed:**
- ✅ No insecure fallback values
- ✅ Application fails safely if SECRET_KEY missing
- ✅ Warns if using insecure development key

#### **File 3: `authentication/views.py`**
**Location:** Lines 43-58

**Before:**
```python
auth_uri = "https://accounts.google.com/o/oauth2/auth"
client_id = "135591834469-2eh68nfpmuj5afhfqoi20fk816nmr04r.apps.googleusercontent.com"
# Hardcoded secrets
```

**After:**
```python
import os
from django.core.exceptions import ImproperlyConfigured

auth_uri = os.environ.get('GOOGLE_AUTH_URI')
client_id = os.environ.get('GOOGLE_CLIENT_ID')

if not auth_uri or not client_id:
    logger.error("Missing required Google OAuth environment variables")
    raise ImproperlyConfigured(
        "Google OAuth is not properly configured. "
        "Please set GOOGLE_AUTH_URI and GOOGLE_CLIENT_ID in your .env file."
    )
```

### **How to Verify:**
1. Rename .env to .env.backup
2. Try starting Django: `python manage.py check`
3. Should FAIL with clear error: "SECRET_KEY environment variable is not set"
4. Restore .env and verify it works

### **Security Standard:**
- OWASP ASVS 4.0: Secret Management
- CWE-798: Use of Hard-coded Credentials

---

## 📋 **Control #5: Server Information Disclosure Prevention**

### **Purpose:**
Remove server version information from HTTP response headers to prevent reconnaissance attacks.

### **What Was Done:**

#### **File: `authentication/security_headers_middleware.py`**
**Location:** Full file

**Implementation:**
```python
class SecurityHeadersMiddleware:
    def __call__(self, request):
        response = self.get_response(request)

        # Control #5: Remove server information headers
        if 'Server' in response:
            del response['Server']
        if 'X-Powered-By' in response:
            del response['X-Powered-By']

        # Add comprehensive security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response['Content-Security-Policy'] = csp_policy

        # Permissions Policy
        permissions_policy = (
            "accelerometer=(), camera=(), geolocation=(), "
            "microphone=(), payment=(), usb=(), interest-cohort=()"
        )
        response['Permissions-Policy'] = permissions_policy

        # HSTS (only if HTTPS)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

        return response
```

**What It Does:**
1. **Removes Server Headers:**
   - Deletes `Server: WSGIServer/0.2 CPython/3.12.x`
   - Deletes `X-Powered-By` if present

2. **Adds Security Headers:**
   - `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
   - `X-Frame-Options: DENY` - Prevents clickjacking
   - `X-XSS-Protection: 1; mode=block` - XSS protection
   - `Content-Security-Policy` - Restricts resource loading
   - `Strict-Transport-Security` - Forces HTTPS
   - `Permissions-Policy` - Disables dangerous browser features

#### **Registration in `connectly/settings.py`**
**Location:** Line 103

```python
MIDDLEWARE = [
    # ... other middleware ...
    'authentication.security_headers_middleware.SecurityHeadersMiddleware',
]
```

### **How to Verify:**

**Before Control #5:**
```bash
curl -I http://127.0.0.1:8000/api/auth/token/
# Output:
# Server: WSGIServer/0.2 CPython/3.12.7  # <-- BAD: Version exposed
```

**After Control #5:**
```bash
curl -I http://127.0.0.1:8000/api/auth/token/
# Output:
# (NO Server header)
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# Strict-Transport-Security: max-age=31536000
# Content-Security-Policy: default-src 'self'; ...
```

### **Security Standard:**
- OWASP A05:2021 - Security Misconfiguration
- CWE-200: Exposure of Sensitive Information to an Unauthorized Actor

---

## 📊 **Summary Table: All Controls**

| Control | File(s) Modified | Lines | Key Feature | How to Test |
|---------|-----------------|-------|-------------|-------------|
| #1 JWT Redaction | logger_singleton.py, authentication/views.py | 13-44, 111-117 | 8 regex patterns redact tokens | Check logs for `[REDACTED]` |
| #2 Rate Limiting | authentication/views.py, urls.py | 24-41, 86 | 5 req/min per IP, HTTP 429 | Send 6 rapid requests |
| #3 Debug Prevention | settings.py, error_handling_middleware.py, templates/ | 33-46 | DEBUG=False, custom error pages | Visit /test-404, see custom page |
| #4 Secret Management | .env, settings.py, authentication/views.py | 29-46, 43-58 | No hardcoded secrets, fails safely | Rename .env, check fails |
| #5 Server Headers | security_headers_middleware.py | Full file | Remove Server header, add security headers | curl -I, no Server header |

---

## 🎯 **Quick Testing Commands**

### **Test Control #1 (JWT Redaction):**
```bash
# Generate logs with authentication
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# Check logs
cat logs/connectly_*.log | grep -i "token"
# Should see: [REDACTED] not actual tokens
```

### **Test Control #2 (Rate Limiting):**
```bash
# Send 6 rapid requests
for i in {1..6}; do
  curl -X POST http://127.0.0.1:8000/api/auth/token/ \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"test"}'
  echo ""
done
# Expected: 6th request returns HTTP 429
```

### **Test Control #3 (Debug Prevention):**
```bash
# Ensure DEBUG=False in .env
curl http://127.0.0.1:8000/nonexistent-page/
# Should show custom 404 page, NOT Django debug page
```

### **Test Control #4 (Secret Management):**
```bash
# Test that app fails without .env
mv .env .env.backup
python manage.py check
# Should fail: "SECRET_KEY environment variable is not set"

# Restore
mv .env.backup .env
python manage.py check
# Should succeed
```

### **Test Control #5 (Server Headers):**
```bash
# Check headers
curl -I http://127.0.0.1:8000/api/auth/token/
# Should NOT see: Server: WSGIServer
# Should see: X-Content-Type-Options, X-Frame-Options, etc.
```

---

## 📁 **File Locations Quick Reference**

```
school-connectly/
├── .env                                    # Control #4: Secrets storage
├── connectly/
│   └── settings.py                         # Controls #3, #4: Security config
├── authentication/
│   ├── views.py                            # Controls #1, #2, #4: Auth logic
│   ├── urls.py                             # Control #2: Rate-limited URLs
│   ├── security_headers_middleware.py      # Control #5: Server headers
│   └── error_handling_middleware.py        # Control #3: Error handling
├── singletons/
│   └── logger_singleton.py                 # Control #1: Token redaction
└── templates/
    ├── 404.html                            # Control #3: Custom errors
    ├── 403.html
    └── 500.html
```

---

## 🎓 **Key Concepts to Understand**

### **Control #1 - Why Token Redaction Matters:**
- Log files are often accessible to multiple people (devs, ops, support)
- Tokens in logs = anyone with log access can impersonate users
- Regex patterns catch tokens in various formats (Bearer, token=, etc.)
- Filter applied at logging level = comprehensive coverage

### **Control #2 - Why Rate Limiting Matters:**
- Attackers try thousands of passwords per minute (brute force)
- 5 requests/minute = 300 attempts/hour (reasonable for legitimate users)
- IP-based = each attacker IP limited separately
- HTTP 429 = standard response for rate limiting

### **Control #3 - Why Debug Prevention Matters:**
- Debug pages show: SECRET_KEY, file paths, installed packages, SQL queries
- This gives attackers complete system knowledge
- Custom error pages = secure + better UX
- Errors still logged internally for debugging

### **Control #4 - Why Secret Management Matters:**
- Hardcoded secrets = visible to anyone with code access
- Git history preserves deleted secrets forever
- Environment variables = outside source control
- Fail-safe design = app won't start if secrets missing

### **Control #5 - Why Header Removal Matters:**
- Server version info = tells attackers which exploits to use
- "WSGIServer/0.2 CPython/3.12" = exact version for targeted attacks
- Security headers = additional protection layers
- Defense in depth strategy

---

## 🚀 **Before/After Comparison**

### **Milestone 1 (Before):**
- 18 Total Vulnerabilities
- 15 High-Risk Issues
- 3 Low-Risk Issues
- NOT Production Ready

### **Milestone 2 (After):**
- 0 Critical Vulnerabilities (expected)
- 0 High-Risk Issues (expected)
- 94% Risk Reduction (expected)
- Production Ready (expected)

---

**Created:** 2025-10-03
**Last Updated:** 2025-10-03
**Status:** Complete Implementation Reference
**Use:** Study, review, and understand all implemented controls
