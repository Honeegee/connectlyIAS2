"""
OWASP ZAP Integrated Test Script
This script uses ZAP's API to perform security testing on the authentication endpoints.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
ZAP_API_KEY = "changeme"  # Default ZAP API key
ZAP_URL = "http://127.0.0.1:8080"
TARGET_URL = "http://127.0.0.1:8000"

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def zap_api_call(endpoint, params=None):
    """Make a call to ZAP API"""
    if params is None:
        params = {}
    params['apikey'] = ZAP_API_KEY

    try:
        response = requests.get(f"{ZAP_URL}{endpoint}", params=params)
        return response.json()
    except Exception as e:
        print(f"Error calling ZAP API: {e}")
        return None

def check_zap_status():
    """Check if ZAP is running and accessible"""
    print_header("Checking OWASP ZAP Status")
    try:
        response = zap_api_call("/JSON/core/view/version/")
        if response:
            print(f"✓ ZAP is running: Version {response.get('version', 'Unknown')}")
            return True
        else:
            print("❌ Cannot connect to ZAP")
            return False
    except Exception as e:
        print(f"❌ Error checking ZAP: {e}")
        return False

def spider_target():
    """Use ZAP spider to discover endpoints"""
    print_header("Spider Scan - Discovering Endpoints")
    print(f"Target: {TARGET_URL}")

    # Start spider scan
    print("\n[1] Starting spider scan...")
    result = zap_api_call("/JSON/spider/action/scan/", {"url": TARGET_URL})

    if not result:
        print("❌ Failed to start spider")
        return False

    scan_id = result.get('scan')
    print(f"✓ Spider scan started with ID: {scan_id}")

    # Wait for spider to complete
    print("\n[2] Waiting for spider to complete...")
    while True:
        status = zap_api_call("/JSON/spider/view/status/", {"scanId": scan_id})
        progress = int(status.get('status', 0))
        print(f"   Progress: {progress}%", end='\r')

        if progress >= 100:
            break
        time.sleep(2)

    print("\n✓ Spider scan completed")

    # Get discovered URLs
    urls = zap_api_call("/JSON/spider/view/results/", {"scanId": scan_id})
    if urls and 'results' in urls:
        print(f"\n[3] Discovered {len(urls['results'])} URLs:")
        auth_endpoints = [url for url in urls['results'] if 'auth' in url]
        for url in auth_endpoints[:10]:  # Show first 10 auth endpoints
            print(f"   • {url}")
    return True

def passive_scan():
    """Enable passive scanning"""
    print_header("Passive Scan - Analyzing Responses")

    # Enable all passive scanners
    print("\n[1] Enabling passive scanners...")
    zap_api_call("/JSON/pscan/action/enableAllScanners/")
    print("✓ Passive scanners enabled")

    # Wait for passive scan to process
    print("\n[2] Waiting for passive scan to process...")
    time.sleep(10)

    # Get passive scan records
    records = zap_api_call("/JSON/pscan/view/recordsToScan/")
    print(f"✓ Records to scan: {records.get('recordsToScan', 0)}")

    return True

def active_scan():
    """Perform active scan on authentication endpoints"""
    print_header("Active Scan - Testing Vulnerabilities")
    print(f"Target: {TARGET_URL}/api/auth/")

    # Start active scan
    print("\n[1] Starting active scan...")
    result = zap_api_call("/JSON/ascan/action/scan/", {
        "url": f"{TARGET_URL}/api/auth/",
        "recurse": "true",
        "inScopeOnly": "false"
    })

    if not result:
        print("❌ Failed to start active scan")
        return False

    scan_id = result.get('scan')
    print(f"✓ Active scan started with ID: {scan_id}")

    # Wait for active scan to complete
    print("\n[2] Waiting for active scan to complete...")
    print("   (This may take several minutes...)")

    while True:
        status = zap_api_call("/JSON/ascan/view/status/", {"scanId": scan_id})
        progress = int(status.get('status', 0))
        print(f"   Progress: {progress}%", end='\r')

        if progress >= 100:
            break
        time.sleep(5)

    print("\n✓ Active scan completed")
    return True

def get_alerts():
    """Retrieve and display security alerts"""
    print_header("Security Alerts")

    alerts = zap_api_call("/JSON/alert/view/alerts/", {"baseurl": TARGET_URL})

    if not alerts or 'alerts' not in alerts:
        print("No alerts found")
        return []

    alert_list = alerts['alerts']
    print(f"\nTotal Alerts: {len(alert_list)}")

    # Group alerts by risk
    risk_groups = {
        'High': [],
        'Medium': [],
        'Low': [],
        'Informational': []
    }

    for alert in alert_list:
        risk = alert.get('risk', 'Informational')
        risk_groups[risk].append(alert)

    # Print summary
    print("\n📊 Alert Summary by Risk Level:")
    print(f"   🔴 High: {len(risk_groups['High'])}")
    print(f"   🟡 Medium: {len(risk_groups['Medium'])}")
    print(f"   🔵 Low: {len(risk_groups['Low'])}")
    print(f"   ⚪ Informational: {len(risk_groups['Informational'])}")

    # Print high and medium risk alerts in detail
    if risk_groups['High']:
        print("\n🔴 HIGH RISK ALERTS:")
        for alert in risk_groups['High']:
            print(f"\n   Alert: {alert.get('alert')}")
            print(f"   URL: {alert.get('url')}")
            print(f"   Description: {alert.get('description', '')[:100]}...")

    if risk_groups['Medium']:
        print("\n🟡 MEDIUM RISK ALERTS:")
        for alert in risk_groups['Medium']:
            print(f"\n   Alert: {alert.get('alert')}")
            print(f"   URL: {alert.get('url')}")
            print(f"   Description: {alert.get('description', '')[:100]}...")

    return alert_list

def check_authentication_controls(alerts):
    """Check specific controls based on alerts"""
    print_header("Control Verification")

    # Control #1: Check for information disclosure
    info_disclosure_alerts = [
        a for a in alerts
        if 'information disclosure' in a.get('alert', '').lower() or
           'debug' in a.get('alert', '').lower() or
           'token' in a.get('description', '').lower()
    ]

    print("\n📋 Control #1: JWT Token Redaction / Information Disclosure")
    if info_disclosure_alerts:
        print(f"   ⚠️  Found {len(info_disclosure_alerts)} potential information disclosure issues")
        for alert in info_disclosure_alerts[:3]:  # Show first 3
            print(f"   • {alert.get('alert')}")
    else:
        print("   ✓ No information disclosure alerts found")

    # Control #2: Check for rate limiting
    # ZAP doesn't specifically test rate limiting, so we note this
    print("\n📋 Control #2: Rate Limiting")
    print("   ℹ️  Note: ZAP doesn't automatically test rate limiting")
    print("   → Use dedicated rate limit test script for thorough testing")

    # Additional security checks
    auth_bypass_alerts = [
        a for a in alerts
        if 'authentication' in a.get('alert', '').lower() or
           'bypass' in a.get('alert', '').lower()
    ]

    print("\n📋 Additional Security Checks:")
    if auth_bypass_alerts:
        print(f"   ⚠️  Found {len(auth_bypass_alerts)} authentication-related issues")
        for alert in auth_bypass_alerts[:3]:
            print(f"   • {alert.get('alert')}")
    else:
        print("   ✓ No authentication bypass issues found")

def generate_report():
    """Generate HTML report"""
    print_header("Generating Report")

    try:
        report = zap_api_call("/OTHER/core/other/htmlreport/")
        report_path = "c:/Users/Honey/Desktop/ConnectlyIPT/school-connectly/milestone_2_implementation/owasp_testing/zap_report.html"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✓ Report generated: {report_path}")
        return True
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return False

def main():
    """Main test execution"""
    print_header("OWASP ZAP Security Testing")
    print(f"ZAP Proxy: {ZAP_URL}")
    print(f"Target Application: {TARGET_URL}")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Check ZAP status
    if not check_zap_status():
        print("\n❌ ZAP is not running. Please start ZAP first.")
        return 1

    # Step 2: Spider scan
    if not spider_target():
        print("\n⚠️  Spider scan had issues, continuing...")

    # Step 3: Passive scan
    passive_scan()

    # Step 4: Active scan
    print("\n⚠️  Active scan can take 10-15 minutes. Continue? (Press Ctrl+C to skip)")
    try:
        time.sleep(3)
        active_scan()
    except KeyboardInterrupt:
        print("\n\n[INFO] Active scan skipped")

    # Step 5: Get and analyze alerts
    alerts = get_alerts()

    # Step 6: Check controls
    check_authentication_controls(alerts)

    # Step 7: Generate report
    generate_report()

    print_header("Test Complete")
    print("Review the generated report and alerts above.")
    print("\nNext Steps:")
    print("1. Review ZAP report: milestone_2_implementation/owasp_testing/zap_report.html")
    print("2. Run dedicated control tests:")
    print("   • python test_control1_jwt_redaction.py")
    print("   • python test_control2_rate_limiting.py")

    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n[INFO] Test interrupted by user")
        exit(1)
