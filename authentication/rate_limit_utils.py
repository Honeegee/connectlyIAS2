"""
Rate Limiting Utility Functions
Provides custom key functions for django-ratelimit to properly handle proxied requests
"""

def get_client_ip(group, request):
    """
    Get the real client IP address, accounting for proxies.

    Priority:
    1. X-Forwarded-For header (set by nginx/proxy)
    2. X-Real-IP header (alternative proxy header)
    3. REMOTE_ADDR (direct connection)

    Args:
        group: Rate limit group (unused, required by django-ratelimit)
        request: Django HTTP request object

    Returns:
        str: Client IP address
    """
    # Get X-Forwarded-For header (nginx sets this)
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs: "client, proxy1, proxy2"
        # The first IP is the original client
        ip = forwarded_for.split(',')[0].strip()
        return ip

    # Fallback to X-Real-IP
    real_ip = request.META.get('HTTP_X_REAL_IP')
    if real_ip:
        return real_ip.strip()

    # Fallback to REMOTE_ADDR (direct connection or last proxy)
    return request.META.get('REMOTE_ADDR', 'unknown')
