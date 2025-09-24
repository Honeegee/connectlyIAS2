# Security Implementation Plan

**Prepared and Presented by:**

[Insert Learner's Name Here]  
[Insert Learner Program and Specialization]  
[Term] [Academic Year]

---

**Intellectual Property Notice**

This template is an exclusive property of Mapua-Malayan Digital College and is protected under Republic Act No. 8293, also known as the Intellectual Property Code of the Philippines (IP Code). It is provided solely for educational purposes within this course. Students may use this template to complete their tasks but may not modify, distribute, sell, upload, or claim ownership of the template itself. Such actions constitute copyright infringement under Sections 172, 177, and 216 of the IP Code and may result in legal consequences. Unauthorized use beyond this course may result in legal or academic consequences.

Additionally, students must comply with the Mapua-Malayan Digital College Student Handbook, particularly with the following provisions:
- **Offenses Related to MMDC IT:**
  - Section 6.2 – Unauthorized copying of files
  - Section 6.8 – Extraction of protected, copyrighted, and/or confidential information by electronic means using MMDC IT infrastructure
- **Offenses Related to MMDC Admin, IT, and Operations:**
  - Section 4.5 – Unauthorized collection or extraction of money, checks, or other instruments of monetary equivalent in connection with matters pertaining to MMDC

Violations of these policies may result in disciplinary actions ranging from suspension to dismissal, in accordance with the Student Handbook.

For permissions or inquiries, please contact MMDC-ISD at isd@mmdc.mcl.edu.ph.

---

**TABLE OF CONTENTS**

| Section |  |
|---------|---|
| 1 | Project Summary & Scope |
| 2 | Summary of Security Audit Findings |
| 3 | Finalized Controls for Implementation |
|   | Full List of Considered Controls (2–4) |
|   | Selected Controls for Milestone 2 Implementation |
| 4 | Implementation Strategy |
| 5 | Updated System or Workflow Diagram |

---

## 1. Project Summary & Scope

| Item | Details |
|------|---------|
| **Project Title** | ConnectlyIPT - Social Media Platform Backend |
| **Brief Description** | Django REST API backend for a social media platform providing token-based authentication, role-based access control (RBAC), social media features (posts, comments, likes), personalized feeds, and comprehensive security configurations |
| **Tech Stack** | **Backend:** Django 5.2, Django REST Framework 3.16.0<br>**Database:** PostgreSQL 15<br>**Authentication:** JWT tokens, Google OAuth (django-allauth)<br>**Security:** Argon2 password hashing, CORS headers<br>**Deployment:** Docker, Gunicorn, WhiteNoise<br>**Additional:** Redis caching, Nginx reverse proxy |
| **Deployment Environment** | Docker containerized environment with PostgreSQL database, running on localhost:8000 for testing (production-like configuration with SSL/TLS capabilities) |

---

## 2. Summary of Security Audit Findings

| Category | Details |
|----------|---------|
| **Working Controls** | • Role-Based Access Control (RBAC) - Fully functional with admin/user/guest roles<br>• Input Validation & SQL Injection Prevention - Django ORM provides protection<br>• Token-based Authentication - JWT implementation working correctly<br>• Password Security - Argon2 hashing implemented |
| **Broken / Missing** | • Debug Mode Enabled - Critical information disclosure<br>• Rate Limiting - No protection against brute force attacks<br>• Database Encryption - Lacks encryption at rest<br>• JWT Token Redaction - Tokens exposed in logs and error messages<br>• Error Handling - Stack traces exposed to users<br>• Server Information Disclosure - WSGIServer version exposed<br>• Cache Security - File-based cache instead of Redis, no SHA-256 hashing |
| **Key Risks Identified** | • **18 Total Vulnerabilities** (15 High-risk, 3 Low-risk) **CONFIRMED BY OWASP ZAP 2.16.1**<br>• **Information Disclosure Epidemic** - 12 vulnerabilities exposing debug info, secret keys<br>• **Authentication Bypass Potential** - 3 missing rate limiting vulnerabilities on all auth endpoints<br>• **Server Configuration Exposure** - 3 server information disclosure vulnerabilities<br>• **Complete System Compromise Possible** via exposed configuration and lack of security controls |

---

## 3. Finalized Controls for Implementation

### Full List of Considered Controls (10 Total Controls)

**Controls Successfully Implemented and Retained:**

| Control | Feasible? | Impact | Notes |
|---------|-----------|--------|-------|
| **Role-Based Access Control (RBAC)** | Yes | High | Successfully implemented and functioning - **VALIDATED BY OWASP ZAP** |
| **Input Validation & SQL Injection Prevention** | Yes | High | Django ORM provides good protection - **VALIDATED BY OWASP ZAP** |

**Controls Requiring Revision:**

| Control | Feasible? | Impact | Notes |
|---------|-----------|--------|-------|
| **JWT Token Redaction in Logs** | Yes | High | Critical for preventing token exposure - **FAILED (12 vulnerabilities found by OWASP ZAP)** |
| **Rate Limiting for Login API** | Yes | High | Critical security gap, easily implementable - **FAILED (3 vulnerabilities confirmed by OWASP ZAP)** |
| **Environment-Based Secret Management** | Yes | High | Partially implemented but server info disclosed - **PARTIAL (3 issues found by OWASP ZAP)** |
| **Cache Key Validation and Hashing** | Yes | Medium | Basic implementation present but needs enhancement - **PARTIAL** |
| **Database Encryption and Backup** | Yes | Medium | Not implemented, requires infrastructure changes - **FAILED (deferred to Milestone 3)** |

**New Controls Discovered Through Professional Testing:**

| Control | Feasible? | Impact | Notes |
|---------|-----------|--------|-------|
| **Debug Information Disclosure Prevention** | Yes | High | **12 critical vulnerabilities discovered by OWASP ZAP** - debug info exposed |
| **Server Information Disclosure Prevention** | Yes | Medium | **3 server info vulnerabilities confirmed by OWASP ZAP** - WSGIServer disclosed |
| **Professional Security Monitoring** | Yes | Medium | Continuous OWASP ZAP integration needed for ongoing validation |

### Selected Controls for Milestone 2 Implementation

**7 High-Priority Controls Selected for Milestone 2 Implementation:**

| Control | Why Selected | Feasibility | Tools/Libraries |
|---------|--------------|-------------|----------------|
| **JWT Token Redaction in Logs** | **CRITICAL** - 12 information disclosure vulnerabilities confirmed by OWASP ZAP professional testing | High | Custom logging filters, Django middleware, token sanitization |
| **Rate Limiting for Login API** | **CRITICAL EXPLOIT** - 3 missing rate limiting vulnerabilities exploited by OWASP ZAP brute force testing | High | django-ratelimit library, Redis backend |
| **Debug Information Disclosure Prevention** | **CRITICAL** - 12 debug information disclosure vulnerabilities confirmed by OWASP ZAP across multiple endpoints | High | Django settings configuration, custom error templates |
| **Environment-Based Secret Management** | **MODERATE** - 3 server information disclosure issues confirmed by OWASP ZAP | High | python-dotenv, Django settings enhancement, .env configuration |
| **Server Information Disclosure Prevention** | **MODERATE** - 3 server information vulnerabilities confirmed by OWASP ZAP | High | Custom SecurityHeadersMiddleware, server header removal |
| **Cache Key Validation and Hashing** | **MODERATE** - Missing SHA-256 hashing and Redis backend requirements from IAS 1 specifications | Medium | Redis migration, SHA-256 implementation, input validation |
| **Professional Security Monitoring** | **INFRASTRUCTURE** - Need for ongoing professional-grade security validation | Medium | OWASP ZAP API integration, SIEM logging, incident response protocols |

**Controls Deferred:**
- **Database Encryption and Backup** - Infrastructure-heavy, requires comprehensive architecture changes (Milestone 3)

---

## 4. Implementation Strategy

| Control | Integration Plan | Tool / Library | Why Chosen |
|---------|------------------|----------------|------------|
| **JWT Token Redaction in Logs** | Implement comprehensive token filtering in `singletons/logger_singleton.py`, sanitize OAuth responses in `authentication/views.py:87`, create secure error handling patterns for all authentication flows | Custom logging middleware + Django filters | Addresses 12 OWASP ZAP confirmed vulnerabilities, prevents credential exposure, meets NIST SP 800-92 logging standards |
| **Rate Limiting for Login API** | Install django-ratelimit package, apply rate limiting decorators to all authentication endpoints (`/admin/login/`, `/api/auth/`, `/api/token/`), configure Redis backend for tracking, implement progressive delay mechanisms | django-ratelimit + Redis backend | Addresses 3 OWASP ZAP confirmed brute force vulnerabilities, industry standard solution, integrates with existing Django architecture |
| **Debug Information Disclosure Prevention** | Set `DEBUG = False` in production settings (`connectly/settings.py`), implement custom error templates (404.html, 500.html, 403.html), remove debug toolbar, configure secure Django settings for production deployment | Django built-in security settings + custom templates | Addresses 12 OWASP ZAP critical information disclosure vulnerabilities, immediate implementation possible |
| **Environment-Based Secret Management** | Remove hardcoded SECRET_KEY fallback and Google Client ID from source code, implement comprehensive `.env` file configuration, eliminate all insecure fallback values, add secret validation mechanisms | python-dotenv + Django settings enhancement | Addresses 3 OWASP ZAP server disclosure issues, production security standard, meets OWASP ASVS 4.0 requirements |
| **Server Information Disclosure Prevention** | Configure secure server headers in custom Django middleware, remove server version information from HTTP responses, implement comprehensive security headers (HSTS, X-Frame-Options, CSP), add Content Security Policy implementation | Custom SecurityHeadersMiddleware + Django middleware | Addresses 3 OWASP ZAP server information vulnerabilities, professional deployment standard |
| **Cache Key Validation and Hashing** | Migrate from file-based to Redis cache backend, implement SHA-256 hashing for all cache key generation in `posts/views.py:990-1008`, add input validation and sanitization for cache parameters, implement cache invalidation security | Redis + hashlib + input validation | Meets IAS 1 specifications, prevents cache poisoning attacks, improves performance |
| **Professional Security Monitoring** | Integrate OWASP ZAP 2.16.1 into CI/CD pipeline, implement Security Information and Event Management (SIEM) logging, develop automated security testing procedures, create incident response protocols based on ZAP findings | OWASP ZAP API + monitoring tools + custom automation | Ensures continuous professional-grade security validation, industry-standard methodology |

---

## 5. Updated System or Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    CONNECTLY SECURITY ARCHITECTURE - MILESTONE 2 IMPLEMENTATION     │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐    ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLIENT APPS    │    │  NGINX PROXY    │    │   DJANGO APP     │    │  REDIS CACHE    │
│                  │    │                 │    │                  │    │                 │
│ • Web Interface  │◄──►│ • Rate Limiting │◄──►│ • Authentication │◄──►│ • Rate Limit    │
│ • Mobile App     │    │ • SSL/TLS       │    │ • RBAC Control   │    │   Tracking      │
│ • API Clients    │    │ • Security      │    │ • Input Valid.   │    │ • SHA-256       │
│                  │    │   Headers (NEW) │    │ • Custom Errors  │    │   Cache Keys    │
│                  │    │ • Server Info   │    │ • JWT Token      │    │ • Session Store │
│                  │    │   Hiding (NEW)  │    │   Redaction(NEW) │    │                 │
└──────────────────┘    └─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                        ┌─────────────────┐             │
                        │  POSTGRESQL DB  │             │
                        │                 │◄────────────┤
                        │ • Encrypted     │             │
                        │   Connections   │             │
                        │ • User Data     │             │
                        │ • Application   │             │
                        │   State         │             │
                        └─────────────────┘             │
                                                         │
                        ┌─────────────────┐             │
                        │ SECURITY        │             │
                        │ MONITORING      │◄────────────┘
                        │                 │
                        │ • OWASP ZAP     │
                        │   Integration   │
                        │ • SIEM Logging  │
                        │ • Incident      │
                        │   Response      │
                        └─────────────────┘

MILESTONE 2 SECURITY CONTROLS IMPLEMENTATION:
├── Authentication Security Layer
│   ├── JWT Token Redaction System (NEW) - Addresses 12 OWASP ZAP vulnerabilities
│   ├── Rate Limiting Protection (NEW) - Addresses 3 OWASP ZAP brute force vulnerabilities
│   ├── OAuth2 Integration (Google) - RETAINED
│   └── Secure Password Hashing (Argon2) - RETAINED
├── Authorization Layer
│   ├── Role-Based Access Control - RETAINED (OWASP ZAP Validated)
│   └── Resource-Level Permissions - RETAINED (OWASP ZAP Validated)
├── Data Protection Layer
│   ├── Input Validation & Sanitization - RETAINED (OWASP ZAP Validated)
│   ├── SQL Injection Prevention - RETAINED (OWASP ZAP Validated)
│   ├── SHA-256 Cache Key Hashing (NEW) - Meets IAS 1 specifications
│   └── Database Connection Encryption - RETAINED
├── Infrastructure Security
│   ├── Debug Mode Disabled (NEW) - Addresses 12 OWASP ZAP information disclosure vulnerabilities
│   ├── Custom Error Handling (NEW) - Prevents sensitive information exposure
│   ├── Security Headers Implementation (NEW) - Addresses 3 OWASP ZAP server info vulnerabilities
│   ├── Server Information Hiding (NEW) - Removes WSGIServer version disclosure
│   └── Environment-Based Secret Management (ENHANCED) - Addresses 3 OWASP ZAP issues
└── Monitoring & Continuous Security
    ├── OWASP ZAP Integration (NEW) - Professional-grade continuous testing
    ├── Security Information and Event Management (NEW)
    └── Incident Response Protocols (NEW)
```

**Note:** This is a design-phase diagram showing planned Milestone 2 implementation. The diagram will be revised in Milestone 2 to reflect what was actually implemented and tested.

**Implementation Priority:**
- **Phase 1 (Week 1-2):** Critical Security Gaps - JWT Token Redaction, Rate Limiting, Debug Prevention
- **Phase 2 (Week 3-4):** Moderate Security Improvements - Environment Secrets, Server Headers, Cache Validation
- **Phase 3 (Week 5-6):** Infrastructure Enhancement - Professional Security Monitoring Integration