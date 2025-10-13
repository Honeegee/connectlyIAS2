"""
URL configuration for connectly project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.views import obtain_auth_token
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK")

def root_page(request):
    """Simple root page to help ZAP discover API endpoints"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Connectly API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            ul { list-style-type: none; padding: 0; }
            li { margin: 10px 0; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>Connectly API</h1>
        <p>Available endpoints for ZAP discovery:</p>
        <ul>
            <li><a href="/health/">Health Check</a></li>
            <li><a href="/api/">API Root</a></li>
            <li><a href="/api/auth/">Authentication API</a></li>
            <li><a href="/admin/">Admin Panel</a></li>
        </ul>
        <p><strong>Note:</strong> This page helps OWASP ZAP discover all API endpoints for security testing.</p>
    </body>
    </html>
    """
    return HttpResponse(html_content)

urlpatterns = [
    path('', root_page, name='root'),
    path('admin/', admin.site.urls),

    # Auth endpoints
    # NEW (COMMENTED OUT):
    # path('api/auth/token/', csrf_exempt(obtain_auth_token), name='api-token-auth'),  # Replaced with rate-limited version
    path('api/auth/', include('authentication.urls')),  # Google OAuth + Rate-limited token endpoint + token-info
    path('api/auth/', include('dj_rest_auth.urls')),  # Regular authentication endpoints
    
    # API endpoints
    path('api/', include('posts.urls')),
    
    # Health check
    path('health/', health_check, name='health_check'),
]
