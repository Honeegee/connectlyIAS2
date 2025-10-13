"""
Control #5: Server Information Disclosure Prevention

This middleware removes server version information from HTTP response headers
and adds comprehensive security headers to protect against various attacks.

Implements:
- Server header removal (prevents version disclosure)
- Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- Content Security Policy (CSP)
- HTTP Strict Transport Security (HSTS)
- Permissions Policy

Addresses OWASP A05:2021 - Security Misconfiguration
"""

class SecurityHeadersMiddleware:
    """
    Middleware to add comprehensive security headers to prevent information disclosure
    and enhance overall application security
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Control #5: Remove server information headers to prevent version disclosure
        # Use both dict-style and attribute access to ensure removal
        try:
            del response['Server']
        except KeyError:
            pass

        try:
            del response['X-Powered-By']
        except KeyError:
            pass
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['X-Permitted-Cross-Domain-Policies'] = 'none'
        response['Cross-Origin-Embedder-Policy'] = 'require-corp'
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        response['Cross-Origin-Resource-Policy'] = 'same-origin'
        
        # Content Security Policy - Secure configuration without unsafe directives
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self'; "  # No unsafe-inline or unsafe-eval
            "style-src 'self'; "   # No unsafe-inline
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "object-src 'none'; "
            "media-src 'self'; "
            "worker-src 'self'; "
            "manifest-src 'self'"
        )
        response['Content-Security-Policy'] = csp_policy
        
        # Permissions Policy
        permissions_policy = (
            "accelerometer=(), "
            "camera=(), "
            "geolocation=(), "
            "microphone=(), "
            "payment=(), "
            "usb=(), "
            "interest-cohort=()"
        )
        response['Permissions-Policy'] = permissions_policy
        
        # HSTS (only if HTTPS)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response
