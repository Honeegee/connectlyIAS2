"""
Custom handler for rate limit exceptions to return HTTP 429
"""
from django.http import JsonResponse


def ratelimited_error(request, exception=None):
    """
    Custom view to handle rate-limited requests.
    Returns HTTP 429 Too Many Requests with a JSON response.
    """
    return JsonResponse(
        {
            'error': 'Rate limit exceeded',
            'detail': 'Too many requests. Please try again later.'
        },
        status=429
    )
