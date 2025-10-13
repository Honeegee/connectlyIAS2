from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
import json
from .rate_limit_utils import get_client_ip
from .progressive_rate_limit import (
    get_progressive_rate_limit_key,
    handle_failed_authentication,
    handle_successful_authentication
)
from singletons.logger_singleton import LoggerSingleton

logger = LoggerSingleton().get_logger()

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
            '/api/auth/token',       # Without trailing slash
            '/api/auth/login/',      # dj-rest-auth login
            '/api/auth/login',       # Without trailing slash
            '/api/auth/registration/', # dj-rest-auth registration
            '/api/auth/registration', # Without trailing slash
            '/admin/login/',         # Django admin login
            '/admin/login',          # Without trailing slash
        ]

        # Apply rate limiting to auth endpoints
        if request.path in auth_endpoints:
            if request.method == 'POST':
                try:
                    # Apply progressive rate limiting: 5 attempts per minute per IP
                    @ratelimit(key=get_progressive_rate_limit_key, rate='5/m', method='POST', block=True)
                    def rate_limited_view(req):
                        return None
    
                    rate_limited_view(request)
                except Ratelimited:
                    client_ip = get_client_ip(None, request)
                    logger.warning(f"Rate limit exceeded for admin login from IP: {client_ip}")
                    return JsonResponse({
                        'error': 'Rate limit exceeded. Too many authentication attempts. Please try again later.',
                        'detail': 'Maximum 5 attempts per minute allowed.'
                    }, status=429)

        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, Ratelimited):
            return JsonResponse({
                'error': 'Rate limit exceeded. Too many authentication attempts. Please try again later.',
                'detail': 'Maximum 5 attempts per minute allowed.'
            }, status=429)
        return None
