#!/usr/bin/env python3
"""
Manual Verification Tests for Medium-Risk Findings
Detailed investigation of the findings from advanced penetration testing
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_admin_access_control():
    """Investigate admin panel access control issues"""
    print("=== ADMIN ACCESS CONTROL INVESTIGATION ===")
    
    admin_urls = [
        "/admin/",
        "/admin/auth/user/1/",
        "/admin/auth/user/999/",
        "/admin/login/",
        "/admin/auth/",
        "/admin/posts/"
    ]
    
    findings = []
    
    for url in admin_urls:
        try:
            response = requests.get(f"{BASE_URL}{url}", timeout=10)
            
            result = {
                "url": url,
                "status_code": response.status_code,
                "content_length": len(response.content),
                "response_type": response.headers.get('Content-Type', ''),
                "requires_auth": False,
                "risk_level": "INFO"
            }
            
            # Analyze the response
            if response.status_code == 200:
                # Check if it's actually Django admin content
                response_text = response.text.lower()
                
                if any(indicator in response_text for indicator in ['django', 'administration', 'login', 'username', 'password']):
                    if 'login' in response_text or 'username' in response_text:
                        result["requires_auth"] = True
                        result["risk_level"] = "LOW"
                        result["details"] = "Admin panel requires authentication"
                    else:
                        result["requires_auth"] = False  
                        result["risk_level"] = "HIGH"
                        result["details"] = "Admin panel accessible without authentication!"
                else:
                    result["details"] = "Non-admin content accessible"
                    
            elif response.status_code == 302:
                redirect_location = response.headers.get('Location', '')
                if 'login' in redirect_location:
                    result["requires_auth"] = True
                    result["risk_level"] = "SECURE"
                    result["details"] = f"Redirects to login: {redirect_location}"
                else:
                    result["details"] = f"Redirects to: {redirect_location}"
                    
            elif response.status_code == 401:
                result["requires_auth"] = True
                result["risk_level"] = "SECURE"
                result["details"] = "Requires authentication (401)"
                
            elif response.status_code == 403:
                result["requires_auth"] = True
                result["risk_level"] = "SECURE"
                result["details"] = "Access forbidden (403)"
                
            else:
                result["details"] = f"Unexpected status: {response.status_code}"
            
            findings.append(result)
            
            # Print immediate results
            risk_indicator = {"SECURE": "[SECURE]", "LOW": "[LOW]", "HIGH": "[HIGH]", "INFO": "[INFO]"}
            print(f"{risk_indicator.get(result['risk_level'], '[INFO]')} {url} - Status: {response.status_code}")
            print(f"    Details: {result.get('details', 'N/A')}")
            
        except Exception as e:
            print(f"[ERROR] {url} - Error: {str(e)}")
            findings.append({
                "url": url,
                "status_code": "ERROR",
                "details": str(e),
                "risk_level": "INFO"
            })
    
    return findings

def test_session_management_detailed():
    """Detailed session management testing"""
    print("\n=== SESSION MANAGEMENT DETAILED TESTING ===")
    
    findings = []
    session = requests.Session()
    
    # Test 1: Session creation
    try:
        response = session.get(f"{BASE_URL}/admin/login/")
        initial_cookies = dict(session.cookies)
        
        finding = {
            "test": "Session Cookie Creation",
            "cookies_set": list(initial_cookies.keys()),
            "secure_flags": {},
            "httponly_flags": {}
        }
        
        # Check cookie security flags
        for cookie_name, cookie_obj in session.cookies.items():
            finding["secure_flags"][cookie_name] = getattr(cookie_obj, 'secure', False)
            finding["httponly_flags"][cookie_name] = getattr(cookie_obj, 'has_nonstandard_attr', lambda x: False)('HttpOnly')
        
        findings.append(finding)
        print(f"[INFO] Session cookies created: {list(initial_cookies.keys())}")
        
        # Test 2: CSRF token handling
        if 'csrftoken' in initial_cookies:
            csrf_token = initial_cookies['csrftoken']
            print(f"[INFO] CSRF token present: {csrf_token[:10]}...")
            
            # Test CSRF protection
            try:
                post_response = session.post(f"{BASE_URL}/admin/login/", 
                                           data={"username": "test", "password": "test"})
                
                csrf_finding = {
                    "test": "CSRF Protection",
                    "status_code": post_response.status_code,
                    "csrf_required": "csrf" in post_response.text.lower() or post_response.status_code == 403
                }
                findings.append(csrf_finding)
                
                if csrf_finding["csrf_required"]:
                    print("[SECURE] CSRF protection active")
                else:
                    print("[MEDIUM] CSRF protection unclear")
                    
            except Exception as e:
                print(f"[INFO] CSRF test error: {str(e)}")
        
    except Exception as e:
        print(f"[ERROR] Session management test failed: {str(e)}")
    
    return findings

def test_api_authentication_flows():
    """Test API authentication mechanisms"""
    print("\n=== API AUTHENTICATION FLOW TESTING ===")
    
    findings = []
    
    # Test different authentication endpoints
    auth_endpoints = [
        {"url": "/api/auth/token/", "method": "POST", "data": {"username": "test", "password": "test"}},
        {"url": "/api/auth/login/", "method": "POST", "data": {"username": "test", "password": "test"}},
        {"url": "/api/auth/registration/", "method": "POST", "data": {"username": "testuser", "password1": "testpass123", "password2": "testpass123", "email": "test@test.com"}},
    ]
    
    for endpoint in auth_endpoints:
        try:
            if endpoint["method"] == "POST":
                response = requests.post(f"{BASE_URL}{endpoint['url']}", 
                                       json=endpoint["data"], timeout=10)
            else:
                response = requests.get(f"{BASE_URL}{endpoint['url']}", timeout=10)
            
            finding = {
                "endpoint": endpoint["url"],
                "method": endpoint["method"],
                "status_code": response.status_code,
                "response_size": len(response.content),
                "content_type": response.headers.get('Content-Type', ''),
                "error_handling": "proper" if 400 <= response.status_code < 500 else "review_needed"
            }
            
            # Check for detailed error messages
            response_text = response.text.lower()
            if any(sensitive in response_text for sensitive in ['traceback', 'debug', 'internal', 'sql', 'database']):
                finding["information_leak"] = "POTENTIAL"
                finding["risk_level"] = "MEDIUM"
            else:
                finding["information_leak"] = "NONE"
                finding["risk_level"] = "LOW"
            
            findings.append(finding)
            
            risk_indicator = "[MEDIUM]" if finding.get("information_leak") == "POTENTIAL" else "[LOW]"
            print(f"{risk_indicator} {endpoint['url']} - Status: {response.status_code}")
            
        except Exception as e:
            print(f"[ERROR] {endpoint['url']} - Error: {str(e)}")
    
    return findings

def generate_manual_test_report(admin_findings, session_findings, api_findings):
    """Generate comprehensive manual testing report"""
    
    report = {
        "test_type": "Manual Security Verification",
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "admin_access_findings": len(admin_findings),
            "session_management_findings": len(session_findings),  
            "api_authentication_findings": len(api_findings)
        },
        "detailed_findings": {
            "admin_access_control": admin_findings,
            "session_management": session_findings,
            "api_authentication": api_findings
        },
        "recommendations": [
            "Review admin panel access controls - ensure proper authentication is enforced",
            "Implement proper session security flags (Secure, HttpOnly, SameSite)",
            "Ensure CSRF protection is active on all state-changing operations",
            "Verify rate limiting is working on authentication endpoints",
            "Test privilege escalation scenarios manually"
        ]
    }
    
    return report

def main():
    print("Manual Verification Tests for Security Findings")
    print("=" * 55)
    
    # Run detailed investigations
    admin_findings = test_admin_access_control()
    session_findings = test_session_management_detailed()
    api_findings = test_api_authentication_flows()
    
    # Generate report
    report = generate_manual_test_report(admin_findings, session_findings, api_findings)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"manual_verification_report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n" + "=" * 55)
    print(f"Manual verification completed!")
    print(f"Detailed report saved to: {report_file}")
    
    # Summary
    high_risk = sum(1 for f in admin_findings if f.get('risk_level') == 'HIGH')
    medium_risk = sum(1 for f in admin_findings if f.get('risk_level') == 'MEDIUM')
    
    if high_risk > 0:
        print(f"[ALERT] {high_risk} HIGH risk findings require immediate attention")
    if medium_risk > 0:
        print(f"[WARNING] {medium_risk} MEDIUM risk findings need review")
        
    print("\nRecommendation: Proceed with manual testing of rate limiting and privilege escalation")

if __name__ == "__main__":
    main()