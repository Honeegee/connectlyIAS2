"""
Error handling middleware for secure error responses.
Prevents debug information disclosure in production.
"""

from django.shortcuts import render
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SecureErrorHandlingMiddleware:
    """
    Middleware to handle errors securely without exposing debug information.
    Returns custom error pages instead of Django debug pages.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Handle exceptions and return secure error pages.
        Only active when DEBUG=False to prevent information disclosure.
        """
        if settings.DEBUG:
            # In debug mode, let Django handle exceptions normally
            return None

        # Log the actual error for debugging (server-side only)
        logger.error(f"Exception in view: {exception}", exc_info=True)

        # Return secure error pages without exposing details
        if isinstance(exception, Http404):
            return render(request, '404.html', status=404)
        elif isinstance(exception, PermissionDenied):
            return render(request, '403.html', status=403)
        else:
            # For any other server error
            return render(request, '500.html', status=500)