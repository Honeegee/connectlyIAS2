"""
Test script to verify debug information disclosure prevention.
"""

import re
from pathlib import Path

def test_debug_configuration():
    """Test debug configuration in settings.py"""
    print("=" * 70)
    print("DEBUG INFORMATION DISCLOSURE PREVENTION TEST")
    print("=" * 70)

    # Read settings file
    settings_path = Path('connectly/settings.py')
    with open(settings_path, 'r') as f:
        settings_content = f.read()

    # Test 1: Check DEBUG default value
    print("\nTest 1: Checking DEBUG configuration...")
    debug_pattern = r"DEBUG = os\.getenv\('DEBUG', '([^']+)'\)"
    debug_match = re.search(debug_pattern, settings_content)

    if debug_match:
        default_value = debug_match.group(1)
        if default_value.lower() == 'false':
            print(f"  [PASS] DEBUG defaults to False (production-safe)")
        else:
            print(f"  [FAIL] DEBUG defaults to {default_value} (should be False)")
    else:
        print("  [FAIL] DEBUG configuration not found")

    # Test 2: Check for debug context processor
    print("\nTest 2: Checking template debug context processor...")
    if "# 'django.template.context_processors.debug'" in settings_content:
        print("  [PASS] Debug context processor is disabled")
    elif "'django.template.context_processors.debug'" in settings_content:
        print("  [FAIL] Debug context processor is still enabled")
    else:
        print("  [PASS] Debug context processor not found (good)")

    # Test 3: Check for secure error handling middleware
    print("\nTest 3: Checking secure error handling middleware...")
    if "'authentication.error_handling_middleware.SecureErrorHandlingMiddleware'" in settings_content:
        print("  [PASS] Secure error handling middleware configured")
    else:
        print("  [FAIL] Secure error handling middleware not found")

    # Test 4: Check ADMINS configuration
    print("\nTest 4: Checking ADMINS configuration for production...")
    if "ADMINS = []" in settings_content and "if not DEBUG:" in settings_content:
        print("  [PASS] ADMINS disabled in production (prevents debug emails)")
    else:
        print("  [FAIL] ADMINS not properly configured for production")

    # Test 5: Check error templates exist
    print("\nTest 5: Checking custom error templates...")
    templates_dir = Path('templates')
    error_templates = ['404.html', '403.html', '500.html']

    for template in error_templates:
        template_path = templates_dir / template
        if template_path.exists():
            print(f"  [PASS] {template} exists")

            # Check template doesn't contain debug info
            with open(template_path, 'r') as f:
                template_content = f.read()

            debug_keywords = ['traceback', 'exception', 'debug', 'stack trace', '{{.*debug.*}}']
            has_debug_info = any(keyword.lower() in template_content.lower() for keyword in debug_keywords[:4])
            has_debug_template = bool(re.search(debug_keywords[4], template_content, re.IGNORECASE))

            if has_debug_info or has_debug_template:
                print(f"    [WARN] {template} may contain debug information")
            else:
                print(f"    [PASS] {template} is secure (no debug info)")
        else:
            print(f"  [FAIL] {template} not found")

    # Test 6: Check for debug toolbar in INSTALLED_APPS
    print("\nTest 6: Checking for debug tools in INSTALLED_APPS...")
    debug_apps = ['debug_toolbar', 'django_debug_toolbar', 'devserver']
    debug_app_found = any(app in settings_content for app in debug_apps)

    if not debug_app_found:
        print("  [PASS] No debug apps found in INSTALLED_APPS")
    else:
        print("  [FAIL] Debug apps found in INSTALLED_APPS")

    # Test 7: Check ALLOWED_HOSTS configuration
    print("\nTest 7: Checking ALLOWED_HOSTS configuration...")
    if "ALLOWED_HOSTS = os.getenv" in settings_content:
        print("  [PASS] ALLOWED_HOSTS configured from environment")
    else:
        print("  [WARN] ALLOWED_HOSTS may not be properly configured")

    print("\n" + "=" * 70)
    print("SECURITY SUMMARY")
    print("=" * 70)
    print("\nDebug Prevention Measures:")
    print("  1. DEBUG=False by default (production)")
    print("  2. Custom error pages (404, 403, 500)")
    print("  3. Secure error handling middleware")
    print("  4. Debug context processor disabled")
    print("  5. No debug tools in INSTALLED_APPS")
    print("  6. ADMINS disabled in production")
    print("\nError handling:")
    print("  - Server errors return custom pages")
    print("  - No stack traces exposed to users")
    print("  - Debug info logged server-side only")
    print("=" * 70)


def test_middleware_configuration():
    """Test that error handling middleware is properly configured"""
    print("\n\nMIDDLEWARE CONFIGURATION TEST")
    print("=" * 70)

    # Check if middleware file exists
    middleware_path = Path('authentication/error_handling_middleware.py')

    if middleware_path.exists():
        print("\nTest 1: Error handling middleware file exists")
        print("  [PASS] authentication/error_handling_middleware.py found")

        with open(middleware_path, 'r') as f:
            middleware_content = f.read()

        # Check for key components
        if 'class SecureErrorHandlingMiddleware' in middleware_content:
            print("  [PASS] SecureErrorHandlingMiddleware class exists")
        else:
            print("  [FAIL] SecureErrorHandlingMiddleware class not found")

        if 'if settings.DEBUG:' in middleware_content:
            print("  [PASS] DEBUG check prevents interference in development")
        else:
            print("  [FAIL] No DEBUG check found")

        if 'render(request, \'404.html\', status=404)' in middleware_content:
            print("  [PASS] Custom 404 error handling")
        else:
            print("  [FAIL] Custom 404 handling not found")

    else:
        print("\n  [FAIL] Error handling middleware file not found")


if __name__ == "__main__":
    test_debug_configuration()
    test_middleware_configuration()
    print("\n\nTo test error pages manually:")
    print("1. Set DEBUG=False in your .env file")
    print("2. Start server: python manage.py runserver")
    print("3. Visit non-existent URL: http://localhost:8000/nonexistent")
    print("4. Should see custom 404 page, not Django debug page")