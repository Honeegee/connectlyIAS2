# ConnectlyIPT Security Controls - System Architecture Diagram

## Milestone 2 Implementation - Controls 1-5

```mermaid
graph TB
    subgraph "Client Layer"
        CLIENT[Client Browser/App]
    end

    subgraph "Control #5: Server Information Hiding"
        NGINX[Nginx Reverse Proxy<br/>- server_tokens off<br/>- proxy_hide_header Server<br/>- Shows: 'Server: nginx']
    end

    subgraph "WSGI Application Server"
        GUNICORN[Gunicorn<br/>Production WSGI Server<br/>Port: 8000 internal]
    end

    subgraph "Django Application Layer"
        MIDDLEWARE_STACK[Middleware Stack]

        subgraph "Control #5: Security Headers"
            SEC_HEADERS[SecurityHeadersMiddleware<br/>- Remove Server/X-Powered-By<br/>- Add CSP, HSTS, X-Frame-Options<br/>- Add X-Content-Type-Options<br/>- Add Permissions-Policy]
        end

        subgraph "Control #3: Debug Prevention"
            ERROR_HANDLER[SecureErrorHandlingMiddleware<br/>- DEBUG=False<br/>- Custom error pages 404/403/500<br/>- No stack traces exposed]
        end

        subgraph "Control #2: Rate Limiting"
            RATE_LIMIT[django-ratelimit Decorators<br/>- 5 requests/minute per IP<br/>- Applied to auth endpoints<br/>- LocMemCache backend]
        end

        DJANGO_CORE[Django Core<br/>Views & URL Routing]
    end

    subgraph "Authentication Module"
        subgraph "Control #1: JWT Token Redaction"
            LOGGER[LoggerSingleton<br/>SensitiveDataFilter<br/>- Redact Bearer tokens<br/>- Redact JWT tokens<br/>- Redact passwords/secrets]
        end

        AUTH_VIEWS[Authentication Views<br/>- google_login @ratelimit<br/>- RateLimitedObtainAuthToken<br/>- OAuth response sanitization]
    end

    subgraph "Control #4: Secret Management"
        ENV_CONFIG[Environment Variables<br/>.env file<br/>- SECRET_KEY<br/>- GOOGLE_CLIENT_ID<br/>- DATABASE_URL<br/>- python-dotenv loader]

        VALIDATION[Secret Validation<br/>ImproperlyConfigured<br/>- Fail if secrets missing<br/>- No hardcoded fallbacks]
    end

    subgraph "Data Layer"
        POSTGRES[(PostgreSQL Database<br/>Docker service: db)]
        CACHE[(LocMemCache<br/>Rate limit tracking)]
        LOGS[Log Files<br/>- Redacted tokens<br/>- Security events]
    end

    subgraph "Configuration Files"
        SETTINGS[connectly/settings.py<br/>- DEBUG=False default<br/>- Secret validation<br/>- Middleware config]

        NGINX_CONF[nginx.conf<br/>- server_tokens off<br/>- proxy configuration]

        DOCKER[docker-compose.yml<br/>- Nginx service<br/>- Web service Gunicorn<br/>- PostgreSQL service]
    end

    %% Request Flow
    CLIENT -->|HTTP Request| NGINX
    NGINX -->|Proxy to port 8000| GUNICORN
    GUNICORN -->|WSGI| MIDDLEWARE_STACK

    MIDDLEWARE_STACK --> SEC_HEADERS
    SEC_HEADERS --> ERROR_HANDLER
    ERROR_HANDLER --> DJANGO_CORE

    DJANGO_CORE -->|Auth requests| RATE_LIMIT
    RATE_LIMIT -->|Check limit| CACHE
    RATE_LIMIT -->|If allowed| AUTH_VIEWS

    AUTH_VIEWS --> LOGGER
    LOGGER -->|Redacted logs| LOGS

    AUTH_VIEWS -->|Query| POSTGRES

    %% Configuration Flow
    ENV_CONFIG -.->|Load secrets| SETTINGS
    SETTINGS -.->|Validate| VALIDATION
    VALIDATION -.->|Configure| DJANGO_CORE

    NGINX_CONF -.->|Configure| NGINX
    DOCKER -.->|Deploy| NGINX
    DOCKER -.->|Deploy| GUNICORN
    DOCKER -.->|Deploy| POSTGRES

    %% Response Flow
    DJANGO_CORE -->|Response| SEC_HEADERS
    SEC_HEADERS -->|Add headers| GUNICORN
    GUNICORN -->|HTTP Response| NGINX
    NGINX -->|Hide server info| CLIENT

    %% Styling
    classDef control1 fill:#e1f5e1,stroke:#4caf50,stroke-width:3px
    classDef control2 fill:#e3f2fd,stroke:#2196f3,stroke-width:3px
    classDef control3 fill:#fff3e0,stroke:#ff9800,stroke-width:3px
    classDef control4 fill:#fce4ec,stroke:#e91e63,stroke-width:3px
    classDef control5 fill:#f3e5f5,stroke:#9c27b0,stroke-width:3px

    class LOGGER,AUTH_VIEWS,LOGS control1
    class RATE_LIMIT,CACHE control2
    class ERROR_HANDLER control3
    class ENV_CONFIG,VALIDATION control4
    class SEC_HEADERS,NGINX,NGINX_CONF control5
```

## Control Summary

| Control # | Name | Components | Status |
|-----------|------|------------|--------|
| **Control #1** | JWT Token Redaction | LoggerSingleton, SensitiveDataFilter | ✅ PASS |
| **Control #2** | Rate Limiting | django-ratelimit, LocMemCache | ✅ PASS |
| **Control #3** | Debug Prevention | DEBUG=False, Custom error pages, SecureErrorHandlingMiddleware | ✅ PASS |
| **Control #4** | Secret Management | python-dotenv, .env, ImproperlyConfigured validation | ✅ PASS |
| **Control #5** | Server Info Hiding | Nginx reverse proxy, SecurityHeadersMiddleware | ✅ PASS |

## Request Flow Diagram

```mermaid
sequenceDiagram
    participant Client
    participant Nginx as Nginx<br/>(Control #5)
    participant Gunicorn
    participant SecurityHeaders as SecurityHeadersMiddleware<br/>(Control #5)
    participant ErrorHandler as ErrorHandlingMiddleware<br/>(Control #3)
    participant RateLimit as RateLimitDecorator<br/>(Control #2)
    participant AuthView as Authentication View
    participant Logger as LoggerSingleton<br/>(Control #1)
    participant EnvConfig as Environment Config<br/>(Control #4)
    participant Database

    Client->>Nginx: HTTP Request
    Note over Nginx: Remove version info<br/>server_tokens off
    Nginx->>Gunicorn: Proxy request
    Gunicorn->>SecurityHeaders: WSGI request
    Note over SecurityHeaders: Add security headers<br/>Remove Server/X-Powered-By
    SecurityHeaders->>ErrorHandler: Pass through
    Note over ErrorHandler: DEBUG=False<br/>Custom error templates
    ErrorHandler->>RateLimit: Route to auth endpoint
    Note over RateLimit: Check IP rate limit<br/>5 requests/minute

    alt Rate limit exceeded
        RateLimit-->>Client: HTTP 429 Too Many Requests
    else Rate limit OK
        RateLimit->>AuthView: Process request
        AuthView->>EnvConfig: Load secrets
        Note over EnvConfig: Load from .env<br/>Validate secrets
        EnvConfig-->>AuthView: Secrets loaded
        AuthView->>Database: Query user
        Database-->>AuthView: User data
        AuthView->>Logger: Log authentication
        Note over Logger: Redact JWT tokens<br/>Redact passwords
        Logger-->>AuthView: Logged safely
        AuthView-->>SecurityHeaders: Response
        SecurityHeaders-->>Gunicorn: Add security headers
        Gunicorn-->>Nginx: HTTP response
        Note over Nginx: Hide server version
        Nginx-->>Client: Secure response
    end
```

## Production Architecture

```mermaid
graph LR
    subgraph "External"
        Internet((Internet))
    end

    subgraph "Docker Container: Nginx"
        NginxServer[Nginx<br/>Port 8000<br/>server_tokens off]
    end

    subgraph "Docker Container: Web"
        GunicornServer[Gunicorn<br/>Internal Port 8000]
        DjangoApp[Django Application<br/>5 Security Controls]

        GunicornServer --> DjangoApp
    end

    subgraph "Docker Container: PostgreSQL"
        DB[(PostgreSQL<br/>Port 5432)]
    end

    subgraph "Configuration"
        EnvFile[.env file<br/>Secrets loaded]
    end

    Internet -->|HTTPS Request| NginxServer
    NginxServer -->|Reverse Proxy| GunicornServer
    DjangoApp -->|SQL Queries| DB
    EnvFile -.->|Load at startup| DjangoApp

    style NginxServer fill:#f3e5f5,stroke:#9c27b0,stroke-width:3px
    style DjangoApp fill:#e1f5e1,stroke:#4caf50,stroke-width:3px
    style DB fill:#e3f2fd,stroke:#2196f3,stroke-width:3px
    style EnvFile fill:#fce4ec,stroke:#e91e63,stroke-width:3px
```

## Security Controls Mapping

### Control #1: JWT Token Redaction (Green)
- **Component**: `singletons/logger_singleton.py`
- **Flow**: All log messages → SensitiveDataFilter → Redaction → Log files
- **Pattern Matching**: Bearer tokens, JWT, access_token, passwords, secrets

### Control #2: Rate Limiting (Blue)
- **Component**: `django-ratelimit` decorators
- **Flow**: Auth request → Check cache → Allow/Block based on IP
- **Backend**: Django LocMemCache (5 requests/minute)

### Control #3: Debug Prevention (Orange)
- **Component**: `SecureErrorHandlingMiddleware`
- **Flow**: Exception → Custom error page (404/403/500) → No stack trace
- **Configuration**: DEBUG=False by default

### Control #4: Secret Management (Pink)
- **Component**: `python-dotenv` + `.env` file
- **Flow**: App startup → Load .env → Validate → ImproperlyConfigured if missing
- **Secrets**: SECRET_KEY, GOOGLE_CLIENT_ID, DATABASE_URL

### Control #5: Server Information Hiding (Purple)
- **Component**: Nginx + SecurityHeadersMiddleware
- **Flow**: Response → Add security headers → Nginx removes version → Client
- **Headers**: CSP, HSTS, X-Frame-Options, removes Server header version

## File Locations

```
school-connectly/
├── authentication/
│   ├── views.py                          # Control #1, #2: Rate limited auth views
│   ├── security_headers_middleware.py    # Control #5: Security headers
│   └── error_handling_middleware.py      # Control #3: Secure error handling
├── singletons/
│   └── logger_singleton.py               # Control #1: Token redaction
├── connectly/
│   ├── settings.py                       # Control #3, #4: DEBUG, secrets validation
│   └── wsgi.py                           # Control #5: WSGI wrapper
├── .env                                  # Control #4: Environment secrets
├── nginx.conf                            # Control #5: Nginx configuration
├── docker-compose.yml                    # Control #5: Production deployment
└── gunicorn_config.py                    # Control #5: Gunicorn config
```

---

**Diagram Version**: 1.0
**Last Updated**: 2025-10-04
**Status**: Complete - All 5 controls documented
