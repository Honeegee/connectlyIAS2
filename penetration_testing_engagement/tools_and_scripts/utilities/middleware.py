from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
import json

class AuthRateLimitMiddleware:
    """
    Middleware to apply rate limiting to authentication endpoints
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if this is an authentication endpoint
        auth_endpoints = [
            '/api/auth/token/',      # Django token auth
            '/api/auth/login/',      # dj-rest-auth login
            '/api/auth/registration/', # dj-rest-auth registration
            '/admin/login/',         # Django admin login
        ]
        
        # Apply rate limiting to auth endpoints
        if any(request.path.startswith(endpoint) for endpoint in auth_endpoints):
            if request.method == 'POST':
                try:
                    # Apply rate limiting: 5 attempts per hour per IP
                    @ratelimit(key='ip', rate='5/h', method='POST', block=True)
                    def rate_limited_view(req):
                        return None
                    
                    rate_limited_view(request)
                except Ratelimited:
                    return JsonResponse({
                        'error': 'Rate limit exceeded. Too many authentication attempts. Please try again later.',
                        'detail': 'Maximum 5 attempts per hour allowed.'
                    }, status=429)

        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, Ratelimited):
            return JsonResponse({
                'error': 'Rate limit exceeded. Too many authentication attempts. Please try again later.',
                'detail': 'Maximum 5 attempts per hour allowed.'
            }, status=429)
        return None