"""
Base settings for the Event Planet Django project.

This module contains the core configuration shared across all environments
(development, staging, production). It includes settings for:
- Installed apps and middleware
- Database configuration
- Authentication & JWT settings
- REST Framework configuration
- Static & media files handling
- Celery, Redis, and cache configuration
- Third-party integrations (CORS, Spectacular, Phone numbers)

Author: Event Planet Team
Created: 2026-02-15
"""

from pathlib import Path
from decouple import config, Csv
from datetime import timedelta

# ----------------------------------------------------------------------
# Project directories
# ----------------------------------------------------------------------
# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Root project directory

# ----------------------------------------------------------------------
# Security settings
# ----------------------------------------------------------------------
# SECURITY WARNING: keep the secret key used in production secret!
# Load from environment variable or use default (insecure) for development
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-key')

# SECURITY WARNING: don't run with debug turned on in production!
# Debug mode should only be enabled in development
DEBUG = config('DEBUG', default=False, cast=bool)

# List of host/domain names that this Django site can serve
# Must be properly configured in production for security
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# ----------------------------------------------------------------------
# Application definition
# ----------------------------------------------------------------------
INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',       # Admin interface
    'django.contrib.auth',        # Authentication framework
    'django.contrib.contenttypes', # Content type system
    'django.contrib.sessions',    # Session framework
    'django.contrib.messages',    # Messaging framework
    'django.contrib.staticfiles', # Static file management
    
    # Third-party apps
    'rest_framework',              # Django REST Framework for API
    'rest_framework_simplejwt',    # JWT authentication
    'corsheaders',                 # Cross-Origin Resource Sharing
    'drf_spectacular',             # OpenAPI/Swagger documentation
    'phonenumber_field',           # International phone number validation
    'django_redis',                # Redis cache backend
    
    # Local apps (Event Planet specific)
    'apps.accounts',               # User authentication & OTP
    'apps.events',                 # Event management
    'apps.categories',             # Event categories
    'apps.registrations',          # Event registration system
    'apps.feedback',               # Feedback & rating system
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Security enhancements
    'corsheaders.middleware.CorsMiddleware',          # CORS headers (must be before CommonMiddleware)
    'django.contrib.sessions.middleware.SessionMiddleware',  # Session management
    'django.middleware.common.CommonMiddleware',      # Common utilities
    'django.middleware.csrf.CsrfViewMiddleware',      # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # User authentication
    'django.contrib.messages.middleware.MessageMiddleware',  # Message framework
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Clickjacking protection
]

# Root URL configuration module
ROOT_URLCONF = 'config.urls'

# ----------------------------------------------------------------------
# Template configuration
# ----------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Custom templates directory
        'APP_DIRS': True,  # Enable app-level template directories
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',      # Debug info in templates
                'django.template.context_processors.request',    # Request object in templates
                'django.contrib.auth.context_processors.auth',   # User auth info in templates
                'django.contrib.messages.context_processors.messages',  # Messages in templates
            ],
        },
    },
]

# WSGI application for deployment
WSGI_APPLICATION = 'config.wsgi.application'

# ----------------------------------------------------------------------
# Database configuration
# ----------------------------------------------------------------------
# Using PostgreSQL as the primary database
# All values loaded from environment variables for security
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='event_planet_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# ----------------------------------------------------------------------
# Password validation
# ----------------------------------------------------------------------
# Password validators are disabled for development
# Should be enabled in production for security
AUTH_PASSWORD_VALIDATORS = []

# ----------------------------------------------------------------------
# Internationalization
# ----------------------------------------------------------------------
# Language and timezone settings
LANGUAGE_CODE = 'en-us'  # Default language
TIME_ZONE = 'UTC'        # Use UTC for all datetime storage
USE_I18N = True          # Enable internationalization
USE_TZ = True            # Enable timezone support

# ----------------------------------------------------------------------
# Static & Media files configuration
# ----------------------------------------------------------------------
# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'                      # URL prefix for static files
STATIC_ROOT = BASE_DIR / 'staticfiles'      # Production static files directory
STATICFILES_DIRS = [BASE_DIR / 'static']    # Additional static files directories

# Media files (User uploaded files)
MEDIA_URL = 'media/'                        # URL prefix for media files
MEDIA_ROOT = BASE_DIR / 'media'             # User uploaded files directory

# ----------------------------------------------------------------------
# Default primary key field type
# ----------------------------------------------------------------------
# Use BigAutoField for better scalability
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ----------------------------------------------------------------------
# Custom User Model
# ----------------------------------------------------------------------
# Use custom user model instead of Django's default User
# This allows phone number authentication instead of username
AUTH_USER_MODEL = 'accounts.User'

# ----------------------------------------------------------------------
# REST Framework configuration
# ----------------------------------------------------------------------
# Django REST Framework settings for API functionality
REST_FRAMEWORK = {
    # Authentication classes (JWT tokens)
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    
    # Default permissions (require authentication for all endpoints)
    # Individual views can override this
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # Response renderers (JSON only for API)
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    
    # Request parsers (JSON only)
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    
    # Pagination settings
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,  # Default page size for all paginated endpoints
    
    # Filtering and search backends
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',     # Enable search on list endpoints
        'rest_framework.filters.OrderingFilter',   # Enable ordering on list endpoints
    ],
    
    # API schema generation (for Swagger/OpenAPI)
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
    # Custom exception handler for consistent error responses
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}

# ----------------------------------------------------------------------
# JWT (JSON Web Token) Settings
# ----------------------------------------------------------------------
# Configuration for JWT authentication tokens
SIMPLE_JWT = {
    # Token lifetime settings (loaded from environment)
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=config('JWT_ACCESS_TOKEN_LIFETIME', default=60, cast=int)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        minutes=config('JWT_REFRESH_TOKEN_LIFETIME', default=1440, cast=int)
    ),
    
    # Token rotation and blacklisting
    'ROTATE_REFRESH_TOKENS': True,        # Issue new refresh token on refresh
    'BLACKLIST_AFTER_ROTATION': True,     # Blacklist old refresh token
    'UPDATE_LAST_LOGIN': True,            # Update user's last_login on token generation
    
    # Algorithm and signing
    'ALGORITHM': 'HS256',                 # HMAC with SHA-256
    'SIGNING_KEY': SECRET_KEY,            # Use Django's SECRET_KEY for signing
    
    # Token headers
    'AUTH_HEADER_TYPES': ('Bearer',),     # Authorization: Bearer <token>
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    
    # User identification
    'USER_ID_FIELD': 'id',                # Field to identify user
    'USER_ID_CLAIM': 'user_id',           # Claim name in token payload
    
    # Token types
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',     # Claim to identify token type
}

# ----------------------------------------------------------------------
# DRF Spectacular settings (API Documentation)
# ----------------------------------------------------------------------
# OpenAPI/Swagger documentation configuration
SPECTACULAR_SETTINGS = {
    'TITLE': 'Event Planet API',                          # API title
    'DESCRIPTION': 'Event Planning & Management Platform API',  # API description
    'VERSION': '1.0.0',                                   # API version
    'SERVE_INCLUDE_SCHEMA': False,                        # Don't include schema in browsable API
    'COMPONENT_SPLIT_REQUEST': True,                      # Split request/response schemas
    'SCHEMA_PATH_PREFIX': '/api/',                        # URL prefix for API endpoints
}

# ----------------------------------------------------------------------
# CORS (Cross-Origin Resource Sharing) configuration
# ----------------------------------------------------------------------
# Allow specific origins to make requests to the API
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://localhost:8000',
    cast=Csv()
)
# Allow cookies/credentials in CORS requests
CORS_ALLOW_CREDENTIALS = True

# ----------------------------------------------------------------------
# Redis configuration
# ----------------------------------------------------------------------
# Redis server settings for caching and Celery
REDIS_HOST = config('REDIS_HOST', default='localhost')
REDIS_PORT = config('REDIS_PORT', default=6379, cast=int)

# ----------------------------------------------------------------------
# Cache configuration
# ----------------------------------------------------------------------
# Use Redis as the cache backend
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/1',  # Redis database 1
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# ----------------------------------------------------------------------
# Celery configuration
# ----------------------------------------------------------------------
# Asynchronous task queue settings
CELERY_BROKER_URL = config(
    'CELERY_BROKER_URL',
    default='redis://localhost:6379/0'  # Redis database 0 for Celery
)
CELERY_RESULT_BACKEND = config(
    'CELERY_RESULT_BACKEND',
    default='redis://localhost:6379/0'
)
CELERY_ACCEPT_CONTENT = ['json']           # Accept only JSON serialized messages
CELERY_TASK_SERIALIZER = 'json'            # Serialize tasks as JSON
CELERY_RESULT_SERIALIZER = 'json'          # Serialize results as JSON
CELERY_TIMEZONE = TIME_ZONE                # Use same timezone as Django

# ----------------------------------------------------------------------
# OTP (One-Time Password) configuration
# ----------------------------------------------------------------------
# Time in seconds before OTP expires (5 minutes default)
OTP_EXPIRY_TIME = config('OTP_EXPIRY_TIME', default=300, cast=int)

# ----------------------------------------------------------------------
# Phone number settings
# ----------------------------------------------------------------------
# Default region for phone number validation
PHONENUMBER_DEFAULT_REGION = 'IR'          # Iran
# Database storage format for phone numbers
PHONENUMBER_DB_FORMAT = 'INTERNATIONAL'    # Store in international format (+98...)