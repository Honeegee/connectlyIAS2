# OWASP ZAP Security Testing for Milestone 2

This directory contains OWASP ZAP security testing scripts for validating Control #1 and Control #2 implementations.

## Overview

- **Test Date**: October 3, 2025
- **OWASP ZAP Version**: 2.16.1
- **Target Application**: Connectly Django REST API
- **Controls Tested**:
  - Control #1: JWT Token Redaction in Logs
  - Control #2: Rate Limiting for Authentication Endpoints

## Prerequisites

### 1. OWASP ZAP Installation

OWASP ZAP is already installed via Chocolatey:
```bash
choco install zap -y
```

Version: **2.16.1** (Official OWASP Tool)
Location: `C:\Program Files\ZAP\Zed Attack Proxy\`

### 2. Start OWASP ZAP in Daemon Mode

```bash
cd "C:\Program Files\ZAP\Zed Attack Proxy"
"C:\Program Files\Java\jdk-17\bin\java.exe" -Xmx512m -jar zap-2.16.1.jar -daemon -host 127.0.0.1 -port 8080
```

ZAP will run in the background on port 8080 and provide an API for automated testing.

### 3. Start Django Development Server

Ensure the database is running and start the Django server:

```bash
# Option 1: Using Docker Compose
docker-compose up

# Option 2: Local PostgreSQL
set DATABASE_URL=postgres://postgres:[your_password]@localhost:5432/connectly
python manage.py runserver
```

The application should be running at `http://127.0.0.1:8000`

## Test Scripts

### Script 1: JWT Token Redaction Test
**File**: `test_control1_jwt_redaction.py`

**Purpose**: Validates that JWT tokens are properly redacted in application logs.

**Test Flow**:
1. Register a new test user
2. Login to obtain JWT token
3. Make authenticated API requests
4. Check log files for token leakage
5. Verify redaction mechanism is working

**Run**:
```bash
python milestone_2_implementation/owasp_testing/test_control1_jwt_redaction.py
```

**Expected Results**:
- ✓ Full JWT token NOT found in logs
- ✓ Redaction markers (`[REDACTED]` or `REDACTED-TOKEN`) present in logs
- ✓ Authentication still works properly

### Script 2: Rate Limiting Test
**File**: `test_control2_rate_limiting.py`

**Purpose**: Validates that rate limiting is enforced on authentication endpoints.

**Test Flow**:
1. Send rapid login attempts (10 requests)
2. Send rapid registration attempts (10 requests)
3. Count 429 (Too Many Requests) responses
4. Verify rate limit is enforced

**Run**:
```bash
python milestone_2_implementation/owasp_testing/test_control2_rate_limiting.py
```

**Expected Results**:
- ✓ After 5 requests, subsequent requests return HTTP 429
- ✓ Rate limiting applies to both login and registration endpoints
- ✓ Rate limit resets after the timeout period

### Script 3: ZAP Integrated Security Scan
**File**: `test_zap_integrated.py`

**Purpose**: Uses OWASP ZAP's API to perform comprehensive security testing.

**Test Flow**:
1. Spider scan - Discover all endpoints
2. Passive scan - Analyze responses for vulnerabilities
3. Active scan - Test for security issues
4. Generate HTML security report

**Run**:
```bash
python milestone_2_implementation/owasp_testing/test_zap_integrated.py
```

**Expected Results**:
- Complete vulnerability scan
- HTML report generated: `zap_report.html`
- Security alerts categorized by risk level

## Test Execution Procedure

### Step 1: Environment Setup
```bash
# Terminal 1: Start OWASP ZAP
cd "C:\Program Files\ZAP\Zed Attack Proxy"
"C:\Program Files\Java\jdk-17\bin\java.exe" -Xmx512m -jar zap-2.16.1.jar -daemon -host 127.0.0.1 -port 8080

# Terminal 2: Start Django Server
cd c:\Users\Honey\Desktop\ConnectlyIPT\school-connectly
docker-compose up
# OR
set DATABASE_URL=postgres://postgres:[password]@localhost:5432/connectly
python manage.py runserver
```

### Step 2: Run Control #1 Test
```bash
# Terminal 3: Run JWT Redaction Test
python milestone_2_implementation/owasp_testing/test_control1_jwt_redaction.py
```

**What to Look For**:
- Test creates a user and obtains a token
- Checks `debug.log` for token leakage
- Verifies redaction is working

### Step 3: Run Control #2 Test
```bash
# Run Rate Limiting Test
python milestone_2_implementation/owasp_testing/test_control2_rate_limiting.py
```

**What to Look For**:
- First 5 requests are allowed
- Subsequent requests blocked with HTTP 429
- Rate limit applies to both endpoints

### Step 4: Run Comprehensive ZAP Scan (Optional)
```bash
# Run Full ZAP Security Scan (takes 10-15 minutes)
python milestone_2_implementation/owasp_testing/test_zap_integrated.py
```

**What to Look For**:
- Spider discovers authentication endpoints
- Security alerts generated
- HTML report created in `owasp_testing/zap_report.html`

## Understanding Test Results

### Control #1: JWT Token Redaction
| Result | Meaning |
|--------|---------|
| ✓ PASSED | Tokens are redacted in logs, no leakage detected |
| ❌ FAILED | Full token found in logs - security issue! |
| ⚠️ INCONCLUSIVE | Cannot access logs or no tokens logged |

### Control #2: Rate Limiting
| Result | Meaning |
|--------|---------|
| ✓ PASSED | Rate limiting active, requests blocked after limit |
| ⚠️ PARTIAL | Some blocking but needs tuning |
| ❌ FAILED | No rate limiting detected |

### ZAP Security Scan
ZAP categorizes findings by risk:
- 🔴 **High**: Critical security issues requiring immediate attention
- 🟡 **Medium**: Important issues that should be addressed
- 🔵 **Low**: Minor issues or improvements
- ⚪ **Informational**: Best practices and recommendations

## Troubleshooting

### Issue: ZAP Not Starting
**Solution**: Ensure Java is installed and ZAP path is correct
```bash
java -version
cd "C:\Program Files\ZAP\Zed Attack Proxy"
dir zap-2.16.1.jar
```

### Issue: Cannot Connect to ZAP API
**Solution**: Check if ZAP is running on port 8080
```bash
curl http://127.0.0.1:8080
```

### Issue: Django Server Not Running
**Solution**: Check database connection
```bash
# Test database connection
python manage.py check
python manage.py migrate
```

### Issue: Database Connection Failed
**Solution**: Verify database credentials
```bash
# Check .env file
cat .env | grep DATABASE_URL

# Test PostgreSQL connection
psql -U postgres -d connectly -h localhost
```

## Output Files

After running tests, the following files will be generated:

1. **Test Results**: Console output with pass/fail status
2. **ZAP Report**: `owasp_testing/zap_report.html` - Comprehensive security report
3. **Log Files**: Check `debug.log` for JWT redaction verification

## Security Best Practices Verified

### Control #1: JWT Token Redaction
- ✓ Prevents token exposure in log files
- ✓ Protects against unauthorized access via log review
- ✓ Complies with OWASP A09:2021 – Security Logging and Monitoring Failures

### Control #2: Rate Limiting
- ✓ Prevents brute force attacks on authentication
- ✓ Mitigates credential stuffing attempts
- ✓ Complies with OWASP A07:2021 – Identification and Authentication Failures

## Next Steps

1. ✅ Review test results
2. ✅ Document findings in Implementation Log
3. ✅ Address any failures or warnings
4. ✅ Generate final security report
5. ✅ Update documentation with test evidence

## References

- [OWASP ZAP Documentation](https://www.zaproxy.org/docs/)
- [OWASP Top 10 2021](https://owasp.org/www-project-top-ten/)
- [Django Security Best Practices](https://docs.djangoproject.com/en/stable/topics/security/)
- [Rate Limiting Best Practices](https://owasp.org/www-community/controls/Blocking_Brute_Force_Attacks)

## Testing Completed By

- **Date**: October 3-4, 2025
- **Tools Used**: OWASP ZAP 2.16.1, Python 3.11, Django 5.2
