"""
Production settings for Event Planet project.

This module contains settings specific to the production environment.
Inherits from base.py and adds production-specific configurations.

Features:
- Maximum security settings
- Performance optimizations
- Error tracking integration
- Production-grade logging
- Cloud storage for static/media files

Author: Event Planet Team
Created: 2026-02-15
"""

from .base import *

# ----------------------------------------------------------------------
# Debug settings
# ----------------------------------------------------------------------
# CRITICAL: Debug must be False in production
DEBUG = False

# Allowed hosts must be explicitly configured from environment
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Print production settings loaded message
print("🚀 Production settings loaded successfully!")

# ----------------------------------------------------------------------
# Security settings
# ----------------------------------------------------------------------
# Maximum security configuration for production

# SSL/HTTPS settings
SECURE_SSL_REDIRECT = True                    # Force HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookie security
SESSION_COOKIE_SECURE = True                  # Session cookie only over HTTPS
CSRF_COOKIE_SECURE = True                     # CSRF cookie only over HTTPS
SESSION_COOKIE_HTTPONLY = True                # Prevent JavaScript access to session cookie
CSRF_COOKIE_HTTPONLY = True                   # Prevent JavaScript access to CSRF cookie

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000               # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True         # Apply to all subdomains
SECURE_HSTS_PRELOAD = True                    # Allow browser HSTS preloading

# Content security
SECURE_CONTENT_TYPE_NOSNIFF = True            # Prevent MIME type sniffing
X_FRAME_OPTIONS = 'DENY'                      # Prevent clickjacking

# ----------------------------------------------------------------------
# Database settings
# ----------------------------------------------------------------------
# Production database with connection pooling
DATABASES['default'].update({
    'CONN_MAX_AGE': 600,  # Connection pooling (10 minutes)
    'OPTIONS': {
        'connect_timeout': 10,
        'options': '-c statement_timeout=30000',  # 30 second statement timeout
    }
})

# ----------------------------------------------------------------------
# Password validation
# ----------------------------------------------------------------------
# Enable all password validators in production
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ----------------------------------------------------------------------
# Email backend
# ----------------------------------------------------------------------
# Production email backend (SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@eventplanet.com')
SERVER_EMAIL = config('SERVER_EMAIL', default='server@eventplanet.com')

# ----------------------------------------------------------------------
# Static and Media files
# ----------------------------------------------------------------------
# Use WhiteNoise for efficient static file serving
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Optional: Use cloud storage (AWS S3, Google Cloud Storage, etc.)
# Uncomment and configure if using cloud storage
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')

# ----------------------------------------------------------------------
# Caching
# ----------------------------------------------------------------------
# Aggressive caching for production performance
CACHES['default'].update({
    'OPTIONS': {
        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        'CONNECTION_POOL_KWARGS': {'max_connections': 50},
        'SOCKET_CONNECT_TIMEOUT': 5,
        'SOCKET_TIMEOUT': 5,
    }
})

# ----------------------------------------------------------------------
# Logging configuration
# ----------------------------------------------------------------------
# Comprehensive logging for production monitoring
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'production.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'errors.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ----------------------------------------------------------------------
# Admin emails
# ----------------------------------------------------------------------
# Email addresses to receive error notifications
ADMINS = [
    ('Admin', config('ADMIN_EMAIL', default='admin@eventplanet.com')),
]
MANAGERS = ADMINS