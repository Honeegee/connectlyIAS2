# COMPREHENSIVE MANUAL PENETRATION TESTING GUIDE
## ConnectlyIPT Django Application - Hands-On Vulnerability Validation

**Objective:** Understand and manually validate the 18 vulnerabilities discovered by OWASP ZAP 2.16.1 through hands-on testing

---

## 🛠️ MANUAL TESTING TOOLS SETUP

### **Primary Tools (Choose Based on Your OS):**

#### **1. Browser-Based Testing (Easiest)**
- **Firefox Developer Tools** (F12)
- **Chrome DevTools** (F12) 
- **Burp Suite Community Edition** (Free)
- **Browser Extensions:** Wappalyzer, Cookie-Editor

#### **2. Command Line Tools (Intermediate)**
- **curl** (HTTP requests)
- **wget** (HTTP requests)
- **nmap** (Port scanning)
- **sqlmap** (SQL injection testing)

#### **3. Specialized Tools (Advanced)**
- **Postman** (API testing)
- **Insomnia** (API testing)
- **Burp Suite Professional** (Full pentesting)
- **Nikto** (Web scanner)

### **Installation Commands:**
```bash
# Install curl (Windows)
# Already available in Windows 10/11

# Install Burp Suite Community (Free)
# Download from: https://portswigger.net/burp/communitydownload

# Install Postman (Free)
# Download from: https://www.postman.com/downloads/
```

---

## 🎯 MANUAL TESTING METHODOLOGY

### **Phase 1: Information Disclosure Testing**
*Validating 12 OWASP ZAP Information Disclosure Vulnerabilities*

#### **Test 1.1: Debug Information Exposure**
**What We're Testing:** Django DEBUG=True exposing sensitive information

**Manual Steps:**
1. **Start Your Django Server:**
   ```bash
   cd "C:\Users\Honey\Desktop\ConnectlyIPT\school-connectly"
   python manage.py runserver
   ```

2. **Test Valid Endpoints:**
   ```bash
   curl -v http://127.0.0.1:8000/
   curl -v http://127.0.0.1:8000/admin/
   curl -v http://127.0.0.1:8000/api/posts/
   ```

3. **Test Invalid Endpoints (Force Errors):**
   ```bash
   curl -v http://127.0.0.1:8000/nonexistent-page
   curl -v http://127.0.0.1:8000/admin/nonexistent
   curl -v http://127.0.0.1:8000/api/invalid-endpoint
   ```

4. **What to Look For:**
   - **VULNERABLE:** See `django.views.debug` in response
   - **VULNERABLE:** See `DEBUG = True` information
   - **VULNERABLE:** See Python traceback with file paths
   - **VULNERABLE:** See `SECRET_KEY` values
   - **SECURE:** See generic error page only

**Expected Result:** You should see detailed Django error pages with sensitive information

#### **Test 1.2: Browser-Based Information Disclosure**
**Manual Steps:**
1. **Open Browser and Navigate To:**
   - `http://127.0.0.1:8000/does-not-exist`
   - `http://127.0.0.1:8000/admin/fake-url`

2. **Open Developer Tools (F12):**
   - Go to **Network** tab
   - Refresh the page
   - Click on the failed request
   - Look at **Response Headers**

3. **What to Look For:**
   - **Server:** Header showing `WSGIServer/0.2 CPython/3.12.6`
   - **X-Frame-Options:** Missing or incorrect
   - **Content-Security-Policy:** Missing
   - **Detailed error information in HTML**

---

### **Phase 2: Authentication Brute Force Testing**
*Validating 3 OWASP ZAP Rate Limiting Vulnerabilities*

#### **Test 2.1: Manual Brute Force Attack**
**What We're Testing:** No rate limiting on authentication endpoints

**Manual Steps with curl:**
1. **Test Admin Login Endpoint:**
   ```bash
   # Attempt 1
   curl -X POST http://127.0.0.1:8000/admin/login/ \
   -d "username=admin&password=wrong1" \
   -H "Content-Type: application/x-www-form-urlencoded"
   
   # Attempt 2 (immediately)
   curl -X POST http://127.0.0.1:8000/admin/login/ \
   -d "username=admin&password=wrong2" \
   -H "Content-Type: application/x-www-form-urlencoded"
   
   # Attempt 3 (immediately)
   curl -X POST http://127.0.0.1:8000/admin/login/ \
   -d "username=admin&password=wrong3" \
   -H "Content-Type: application/x-www-form-urlencoded"
   
   # Continue for 10+ attempts rapidly...
   ```

2. **Test API Token Endpoint:**
   ```bash
   # Rapid API token attempts
   curl -X POST http://127.0.0.1:8000/api/auth/token/ \
   -d '{"username":"admin","password":"wrong1"}' \
   -H "Content-Type: application/json"
   
   curl -X POST http://127.0.0.1:8000/api/auth/token/ \
   -d '{"username":"admin","password":"wrong2"}' \
   -H "Content-Type: application/json"
   
   # Continue rapidly...
   ```

3. **What to Look For:**
   - **VULNERABLE:** All requests return normally without blocking
   - **VULNERABLE:** No delay between failed attempts
   - **VULNERABLE:** No account lockout after multiple failures
   - **SECURE:** Requests get blocked or delayed after 3-5 attempts

#### **Test 2.2: Browser-Based Brute Force**
**Manual Steps:**
1. **Open Multiple Browser Tabs**
2. **Navigate to:** `http://127.0.0.1:8000/admin/login/`
3. **Try Multiple Wrong Passwords Rapidly:**
   - admin / password123
   - admin / wrongpass
   - admin / 12345
   - admin / admin
   - Continue rapidly...

4. **What to Look For:**
   - **VULNERABLE:** Can attempt unlimited login tries
   - **VULNERABLE:** No CAPTCHA appears
   - **VULNERABLE:** No delays between attempts

---

### **Phase 3: JWT Token Exposure Testing**
*Validating JWT Token Security Issues*

#### **Test 3.1: Log File Analysis**
**Manual Steps:**
1. **Trigger OAuth Login (if possible):**
   ```bash
   # Try to access OAuth endpoints
   curl -v http://127.0.0.1:8000/api/auth/google/login/
   ```

2. **Check Django Server Console Output:**
   - Look at your terminal where Django server is running
   - Look for any token values in plain text
   - Check for Google OAuth responses

3. **Check Application Logs:**
   ```bash
   # If you have log files
   find . -name "*.log" -exec grep -i "token" {} \;
   find . -name "*.log" -exec grep -i "jwt" {} \;
   ```

#### **Test 3.2: Error Response Analysis**
**Manual Steps:**
1. **Force Authentication Errors:**
   ```bash
   curl -X GET http://127.0.0.1:8000/api/posts/ \
   -H "Authorization: Bearer invalid-token-here"
   
   curl -X GET http://127.0.0.1:8000/api/posts/ \
   -H "Authorization: Token fake-jwt-token"
   ```

2. **What to Look For:**
   - **VULNERABLE:** Actual token values in error messages
   - **VULNERABLE:** JWT payload visible in responses
   - **SECURE:** Generic "Invalid token" messages only

---

### **Phase 4: Server Information Disclosure**
*Validating Server Header Exposure*

#### **Test 4.1: HTTP Header Analysis**
**Manual Steps:**
1. **Check Server Headers with curl:**
   ```bash
   curl -I http://127.0.0.1:8000/
   curl -I http://127.0.0.1:8000/admin/
   curl -I http://127.0.0.1:8000/api/posts/
   ```

2. **Using Browser Developer Tools:**
   - Open DevTools (F12)
   - Go to **Network** tab
   - Visit `http://127.0.0.1:8000/`
   - Click on the request
   - Check **Response Headers**

3. **What to Look For:**
   - **VULNERABLE:** `Server: WSGIServer/0.2 CPython/3.12.6`
   - **VULNERABLE:** Missing security headers:
     - `X-Content-Type-Options`
     - `X-Frame-Options` 
     - `X-XSS-Protection`
     - `Content-Security-Policy`
     - `Strict-Transport-Security`

#### **Test 4.2: Technology Fingerprinting**
**Manual Steps:**
1. **Use Wappalyzer Browser Extension:**
   - Install Wappalyzer from browser extension store
   - Navigate to your site
   - Check detected technologies

2. **Manual Technology Detection:**
   ```bash
   # Check for Django-specific responses
   curl -v http://127.0.0.1:8000/admin/login/ | grep -i django
   
   # Check for Python-specific headers
   curl -I http://127.0.0.1:8000/ | grep -i python
   ```

---

### **Phase 5: Cache Security Testing**
*Validating Cache Implementation Issues*

#### **Test 5.1: Cache Poisoning Attempt**
**Manual Steps:**
1. **Test Cache Parameters:**
   ```bash
   # Normal request
   curl -v "http://127.0.0.1:8000/api/posts/"
   
   # Attempt cache poisoning
   curl -v "http://127.0.0.1:8000/api/posts/?malicious=<script>alert(1)</script>"
   curl -v "http://127.0.0.1:8000/api/posts/?../../../etc/passwd"
   ```

2. **Check Cache Key Generation:**
   - Look for predictable cache keys
   - Test if user input directly affects caching

---

## 📊 MANUAL TESTING WITH POSTMAN

### **Setup Postman Collection:**

1. **Create New Collection:** "ConnectlyIPT Manual Pentest"

2. **Add These Requests:**

#### **Request 1: Information Disclosure Test**
- **Method:** GET
- **URL:** `http://127.0.0.1:8000/nonexistent-page`
- **Expected:** Django error page with sensitive info

#### **Request 2: Rate Limiting Test**
- **Method:** POST  
- **URL:** `http://127.0.0.1:8000/api/auth/token/`
- **Body:** `{"username":"admin","password":"wrong"}`
- **Action:** Send 10 times rapidly
- **Expected:** No blocking

#### **Request 3: Server Header Test**
- **Method:** HEAD
- **URL:** `http://127.0.0.1:8000/`
- **Check:** Response headers for server info

#### **Request 4: JWT Test**
- **Method:** GET
- **URL:** `http://127.0.0.1:8000/api/posts/`
- **Header:** `Authorization: Bearer fake-token`
- **Expected:** Token exposure in error

---

## 🔍 BURP SUITE MANUAL TESTING

### **Setup Burp Suite Community:**

1. **Download and Install Burp Suite Community Edition**
2. **Configure Browser Proxy:**
   - Set browser proxy to `127.0.0.1:8080`
   - Import Burp certificate

3. **Manual Testing with Burp:**

#### **Intercept and Modify Requests:**
1. **Turn on Intercept**
2. **Navigate to your application**
3. **Modify requests in real-time:**
   - Change parameter values
   - Add malicious headers
   - Test different authentication tokens

#### **Use Burp Repeater:**
1. **Send requests to Repeater**
2. **Modify and resend multiple times**
3. **Test for rate limiting bypasses**

---

## 📝 DOCUMENTATION TEMPLATE

**Create this file:** `MANUAL_TESTING_RESULTS.md`

```markdown
# Manual Testing Results - ConnectlyIPT

## Test 1: Information Disclosure
**Date:** [Date]
**Tool Used:** curl / Browser
**Vulnerability Found:** [Yes/No]
**Evidence:** [Screenshot/Response]
**Notes:** [Your observations]

## Test 2: Rate Limiting
**Date:** [Date]
**Tool Used:** [Tool name]
**Vulnerability Found:** [Yes/No]  
**Evidence:** [Number of successful attempts]
**Notes:** [Your observations]

[Continue for each test...]
```

---

## 🎯 SUCCESS CRITERIA

### **You've Successfully Completed Manual Testing When:**

✅ **Information Disclosure:** You can see Django debug pages with sensitive information  
✅ **Rate Limiting:** You can make 10+ rapid login attempts without blocking  
✅ **Server Headers:** You can identify WSGIServer version and missing security headers  
✅ **JWT Security:** You understand how tokens might be exposed  
✅ **Documentation:** You've recorded all findings with evidence  

### **Understanding Achievement:**
- **Beginner Level:** Can follow the curl commands and see the vulnerabilities
- **Intermediate Level:** Can use Postman/Burp Suite and modify requests
- **Advanced Level:** Can create your own test scenarios and find new issues

---

## 🚀 NEXT STEPS AFTER MANUAL TESTING

1. **Compare your manual findings with OWASP ZAP results**
2. **Document any additional vulnerabilities you discovered**
3. **Understand why each vulnerability is dangerous**
4. **Prepare for Milestone 2 implementation with hands-on knowledge**

This manual testing will give you deep understanding of the security issues before you implement the fixes in Milestone 2! 

**Ready to start? Begin with Phase 1 (Information Disclosure Testing) - it's the most visual and easy to understand!**