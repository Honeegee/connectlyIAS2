@echo off
echo ===============================================
echo OWASP ZAP Rate Limiting Test Script for Windows
echo ===============================================
echo.

echo Checking if Django server is running...
curl -s http://localhost:8000/health/ > nul
if %errorlevel% neq 0 (
    echo ERROR: Django server is not running on http://localhost:8000
    echo Please start the server with: python manage.py runserver 0.0.0.0:8000
    pause
    exit /b 1
)

echo Django server is running!
echo.

echo Testing basic rate limiting...
python test_rate_limiting.py
echo.

echo Testing progressive rate limiting...
python test_progressive_rate_limiting.py
echo.

echo ===============================================
echo Manual OWASP ZAP Testing Instructions:
echo ===============================================
echo 1. Start OWASP ZAP
echo 2. Configure proxy: 127.0.0.1:8080
echo 3. Set target: http://localhost:8000
echo 4. Run active scan on authentication endpoints
echo 5. Verify no brute force vulnerabilities detected
echo.
echo Expected Results:
echo - No "Brute Force" alerts in ZAP
echo - HTTP 429 responses for rate limited requests
echo - Progressive delays for repeated failed attempts
echo.

echo Press any key to continue with manual testing...
pause > nul

echo.
echo ===============================================
echo Quick Manual Test Commands:
echo ===============================================
echo You can manually test with these curl commands:
echo.
echo Test token endpoint (first 5 attempts):
echo curl -X POST http://localhost:8000/api/auth/token/ ^
echo   -H "Content-Type: application/json" ^
echo   -d "{\"username\":\"test\",\"password\":\"wrong\"}" ^
echo   -w "%%{http_code}\n"
echo.
echo Test admin login:
echo curl -X POST http://localhost:8000/admin/login/ ^
echo   -d "username=admin&password=wrong" ^
echo   -w "%%{http_code}\n"
echo.

echo Press any key to exit...
pause > nul
