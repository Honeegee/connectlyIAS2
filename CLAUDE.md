# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Connectly** is a Django REST API backend for a social media platform that provides:
- Token-based authentication (Standard login + Google OAuth via django-allauth)
- Role-based access control (RBAC) with admin/user/guest roles
- Social media features: posts, comments, likes, personalized feeds
- API documentation via Swagger/OpenAPI
- File-based caching for performance
- Comprehensive security configurations

## Architecture

### Core Applications
- **`authentication/`** - User management, OAuth integration, RBAC with UserProfile model
- **`posts/`** - Post, Comment, Like models with privacy controls and metadata support
- **`connectly/`** - Django project settings and URL routing
- **`factories/`** - Factory classes for test data generation
- **`singletons/`** - Shared utilities (config manager, logging singleton)

### Key Models
- `User` (Django built-in) + `UserProfile` with role-based permissions
- `Post` with types (text/image/video/link), privacy (public/private), JSON metadata
- `Comment` and `Like` with foreign key relationships

### Authentication Flow
- Standard Django token authentication via `/api/auth/token/`
- Google OAuth via django-allauth at `/api/auth/`
- RBAC enforced through custom permissions and middleware

## Development Commands

### Database Operations
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Or use custom command:
python manage.py create_superuser

# Wait for database (useful in Docker)
python manage.py wait_for_db
```

### Development Server
```bash
# Local development
python manage.py runserver

# Docker development
docker-compose up

# Collect static files
python manage.py collectstatic
```

### Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test posts
python manage.py test authentication
```

### API Documentation
```bash
# Generate Swagger schema
python manage.py generate_swagger

# Access documentation at:
# http://localhost:8000/swagger/ (Swagger UI)
# http://localhost:8000/redoc/ (ReDoc)
```

## Important Files

### Configuration
- **`connectly/settings.py`** - Main Django settings with security configurations
- **`docker-compose.yml`** - PostgreSQL + Django web service setup
- **`requirements.txt`** - Python dependencies (Django 5.2, DRF, OAuth, etc.)
- **`.env`** - Environment variables (DATABASE_URL, SECRET_KEY, Google OAuth credentials)

### Security Settings
The project implements comprehensive security measures:
- SSL redirect, secure cookies, HSTS headers
- CORS configuration with specific allowed origins
- Strong password hashers (Argon2, PBKDF2, BCrypt)
- Token-based authentication with proper CSRF handling

### API Structure
- **Base URL**: `/api/`
- **Authentication**: `/api/auth/` (includes token, Google OAuth, registration)
- **Posts**: `/api/posts/` (CRUD operations, comments, likes)
- **Documentation**: `/swagger/`, `/redoc/`
- **Health Check**: `/health/`

## Database Setup

The application uses PostgreSQL with the following configuration:
```bash
# Environment variables in .env:
DATABASE_URL=postgres://postgres:postgres@localhost:5432/connectly

# Docker setup provides PostgreSQL automatically
docker-compose up db
```

## Caching Strategy

File-based caching is configured in `django_cache/` directory:
- 5-minute default timeout
- 1000 entry maximum
- Used for performance optimization on API responses

## Testing Strategy

Tests are located in each app's `tests.py`:
- `authentication/tests.py` - User authentication and OAuth flows
- `posts/tests.py` - CRUD operations, permissions, relationships
- Factory classes in `factories/` for generating test data

## Role-Based Access Control

Three user roles implemented via `UserProfile.role`:
- **admin** - Full system access (auto-assigned to staff users)
- **user** - Standard user permissions
- **guest** - Limited read access

Permissions are enforced through:
- Custom permission classes in `posts/permissions.py`
- Django's built-in permission system
- Middleware-level role checking

## API Integration Notes

When working with the API:
- All authenticated endpoints require `Authorization: Token <token>` header
- CSRF tokens required for state-changing operations
- Content-Type should be `application/json` for POST/PUT requests
- Rate limiting may be implemented (check middleware configuration)

## Deployment Considerations

- Environment variables must be set in production
- Static files collected via `collectstatic`
- Database migrations applied
- SSL certificates configured for HTTPS
- ALLOWED_HOSTS updated for production domains