"""
WSGI config for connectly project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectly.settings')

_application = get_wsgi_application()

def application(environ, start_response):
    """
    Control #5: WSGI wrapper to remove Server header from responses
    """
    def custom_start_response(status, headers, exc_info=None):
        # Remove Server header to prevent information disclosure
        headers = [(name, value) for name, value in headers if name.lower() != 'server']
        return start_response(status, headers, exc_info)

    return _application(environ, custom_start_response)
