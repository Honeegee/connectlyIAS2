from django.urls import path
from .views import google_login, oauth_demo, oauth_callback, RateLimitedObtainAuthToken

urlpatterns = [
    path('token/', RateLimitedObtainAuthToken.as_view(), name='api-token-auth-ratelimited'),
    path('google/', google_login, name='google-login'),
    path('demo/', oauth_demo, name='oauth-demo'),
    path('callback/', oauth_callback, name='oauth-callback'),
] 