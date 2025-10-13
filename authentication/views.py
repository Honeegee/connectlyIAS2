from django.shortcuts import render, redirect
import requests
import urllib.parse
from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from allauth.socialaccount.models import SocialAccount
from singletons.logger_singleton import LoggerSingleton
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from django.utils.decorators import method_decorator
from .rate_limit_utils import get_client_ip
from .progressive_rate_limit import (
    get_progressive_rate_limit_key, 
    handle_failed_authentication,
    handle_successful_authentication
)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

logger = LoggerSingleton().get_logger()

@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key=get_client_ip, rate='5/m', method='POST', block=False)
def register_user(request):
    """
    Endpoint to register a new user.
    Rate limited to 5 requests per minute per IP address.
    """
    # Check if rate limited
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        client_ip = get_client_ip(None, request)
        logger.warning(f"Rate limit exceeded for registration from IP: {client_ip}")
        return Response(
            {'error': 'Rate limit exceeded', 'detail': 'Too many requests. Please try again later.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    # Validate required fields
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if field not in request.data:
            return Response(
                {'error': f'Missing required field: {field}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')

    # Validate password strength
    try:
        validate_password(password)
    except ValidationError as e:
        return Response(
            {'error': 'Password validation failed', 'details': list(e.messages)},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if username or email already exists
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_409_CONFLICT
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email already exists'},
            status=status.HTTP_409_CONFLICT
        )

    try:
        # Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )

        # Create token for the user
        token = Token.objects.create(user=user)

        logger.info(f"User {username} registered successfully")

        # Return success response with token
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)

    except IntegrityError as e:
        logger.error(f"IntegrityError during user registration: {str(e)}")
        return Response(
            {'error': 'An account with this username or email already exists.'},
            status=status.HTTP_409_CONFLICT
        )
    except Exception as e:
        logger.error(f"Error during user registration: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred during registration'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Added RateLimitedObtainAuthToken Class

class RateLimitedObtainAuthToken(ObtainAuthToken):
    """
    Custom token authentication view with progressive rate limiting.
    Implements exponential backoff for repeated failed attempts.
    """

    @method_decorator(ratelimit(key=get_progressive_rate_limit_key, rate='5/m', method='POST', block=False))
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to check rate limit before processing request"""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Debug: Log the IP that will be used for rate limiting
        client_ip = get_client_ip(None, request)
        logger.debug(f"Token auth request from IP: {client_ip} (X-Forwarded-For: {request.META.get('HTTP_X_FORWARDED_FOR', 'None')}, REMOTE_ADDR: {request.META.get('REMOTE_ADDR', 'None')})")

        # Check if rate limited  (block=False means we check manually)
        was_limited = getattr(request, 'limited', False)
        if was_limited:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return Response(
                {'error': 'Rate limit exceeded', 'detail': 'Too many requests. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        try:
            response = super().post(request, *args, **kwargs)
            
            # Check if authentication was successful
            if response.status_code == 200:
                # Successful authentication - reset failed attempts
                handle_successful_authentication(request)
                logger.info(f"Token obtained successfully for user from IP: {client_ip}")
            else:
                # Failed authentication - track failed attempts
                failed_response = handle_failed_authentication(request, 'token_endpoint')
                # Return the original response from parent class, not the failed response
                # This preserves the 400/401 status codes from the parent class
                return response
                
            return response
        except Exception as e:
            logger.error(f"Error during token authentication: {str(e)}")
            raise

def oauth_demo(request):
    """Render the Google OAuth demo page."""
    # Load OAuth configuration from environment variables (Control #4: Secret Management)
    import os
    from django.core.exceptions import ImproperlyConfigured

    auth_uri = os.environ.get('GOOGLE_AUTH_URI')
    client_id = os.environ.get('GOOGLE_CLIENT_ID')

    # Validate required environment variables
    if not auth_uri or not client_id:
        logger.error("Missing required Google OAuth environment variables")
        raise ImproperlyConfigured(
            "Google OAuth is not properly configured. "
            "Please set GOOGLE_AUTH_URI and GOOGLE_CLIENT_ID in your .env file."
        )

    # Get the current hostname for the redirect_uri
    host = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    redirect_uri = f"{protocol}://{host}/api/auth/callback/"

    # Log configuration (secrets already redacted by logger_singleton)
    logger.info(f"OAuth demo requested - Auth URI: {auth_uri}")
    logger.info(f"OAuth demo requested - Redirect URI: {redirect_uri}")
    
    # Build params exactly as Google expects
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'token',
        'scope': 'openid email profile',
        'include_granted_scopes': 'true',
        'state': 'pass-through-value'
    }
    
    oauth_url = f"{auth_uri}?{urllib.parse.urlencode(params)}"
    
    context = {
        'oauth_url': oauth_url,
        'redirect_uri': redirect_uri
    }
    return render(request, 'authentication/demo.html', context)

def oauth_callback(request):
    """Handle the OAuth callback."""
    # The token will be in the URL fragment, which is not sent to the server
    # We'll redirect to the demo page with the token as a query parameter
    # The demo page will then extract the token and send it to our API
    return render(request, 'authentication/callback.html')

@api_view(['GET'])
@permission_classes([AllowAny])
def token_info(request):
    """
    GET endpoint for ZAP testing and documentation.
    Returns information about how to use the token endpoint.
    """
    return Response({
        'message': 'Token authentication endpoint',
        'description': 'Use POST method with username and password to obtain authentication token',
        'example_request': {
            'method': 'POST',
            'url': '/api/auth/token/',
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': {
                'username': 'your_username',
                'password': 'your_password'
            }
        },
        'rate_limiting': '5 requests per minute per IP address',
        'note': 'This endpoint is protected by progressive rate limiting'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key=get_progressive_rate_limit_key, rate='5/m', method='POST', block=False)
def google_login(request):
    """
    Endpoint to handle Google OAuth login with progressive rate limiting.
    Implements exponential backoff for repeated failed attempts.

    Expects a token from the Google OAuth process.
    Returns a DRF token for authenticated API access.
    """
    # Check if rate limited
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        client_ip = get_client_ip(None, request)
        logger.warning(f"Rate limit exceeded for Google login from IP: {client_ip}")
        return Response(
            {'error': 'Rate limit exceeded', 'detail': 'Too many requests. Please try again later.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    # Validate input
    if 'access_token' not in request.data:
        return Response(
            {'error': 'Access token is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    token = request.data.get('access_token')
    
    try:
        # Verify the token with Google
        google_response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {token}'},
            timeout=10  # Add timeout to prevent hanging requests
        )
        
        # NEW (SECURE): for Outh sanitation error logging
        if not google_response.ok:
            logger.error(f"Failed to verify Google token: Status {google_response.status_code}")
            return Response(
                {'error': 'Invalid Google token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Parse user info from Google
        user_data = google_response.json()
        
        if 'email' not in user_data:
            logger.error("Email not provided in Google response")
            return Response(
                {'error': 'Email not provided by Google'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email = user_data['email']
        google_id = user_data['sub']
        name = user_data.get('name', email.split('@')[0])
        picture = user_data.get('picture')
        
        # Handle user creation/authentication
        try:
            # Try to find if this Google account is already linked to a user
            social_account = SocialAccount.objects.filter(
                provider='google',
                uid=google_id
            ).first()
            
            if social_account:
                # If the account exists, get the user
                user = social_account.user
                logger.info(f"User {user.username} logged in via existing Google account")
            else:
                # Check if a user with this email already exists
                user = User.objects.filter(email=email).first()
                
                if user:
                    # Link the existing user to this Google account
                    SocialAccount.objects.create(
                        user=user,
                        provider='google',
                        uid=google_id,
                        extra_data=user_data
                    )
                    logger.info(f"Linked Google account to existing user {user.username}")
                else:
                    # Create a new user with the Google data
                    username = email.split('@')[0]
                    base_username = username
                    count = 1
                    
                    # Ensure username uniqueness
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{count}"
                        count += 1
                    
                    # Create the new user
                    user = User.objects.create(
                        username=username,
                        email=email,
                        first_name=user_data.get('given_name', ''),
                        last_name=user_data.get('family_name', ''),
                        is_active=True
                    )
                    
                    # Set a unusable password for security
                    user.set_unusable_password()
                    user.save()
                    
                    # Create the social account
                    SocialAccount.objects.create(
                        user=user,
                        provider='google',
                        uid=google_id,
                        extra_data=user_data
                    )
                    logger.info(f"Created new user {user.username} from Google account")
            
            # Get or create token for the user
            token, created = Token.objects.get_or_create(user=user)
            
            # Update last login time
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # Successful authentication - reset failed attempts
            handle_successful_authentication(request)
            
            # Return the token to the client
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'picture': picture
            })
            
        except IntegrityError as e:
            logger.error(f"IntegrityError during Google login: {str(e)}")
            return Response(
                {'error': 'An account with this username already exists.'}, 
                status=status.HTTP_409_CONFLICT
            )
            
    except Exception as e:
        logger.error(f"Error during Google login: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
