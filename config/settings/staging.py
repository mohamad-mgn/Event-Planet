"""
Staging settings for Event Planet project.

This module contains settings specific to the staging environment.
Inherits from base.py and adds staging-specific configurations.

Staging environment mirrors production but allows for testing
before deploying to production.

Features:
- Debug mode disabled
- Similar security to production
- Separate database
- Email backend configured

Author: Event Planet Team
Created: 2026-02-15
"""

from .base import *

# ----------------------------------------------------------------------
# Debug settings
# ----------------------------------------------------------------------
# Disable debug mode in staging (production-like behavior)
DEBUG = False

# Allowed hosts must be explicitly configured
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Print staging settings loaded message
print("🎯 Staging settings loaded successfully!")

# ----------------------------------------------------------------------
# Security settings
# ----------------------------------------------------------------------
# Enable security middleware features
SECURE_SSL_REDIRECT = True                    # Redirect all HTTP to HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True                  # Only send session cookie over HTTPS
CSRF_COOKIE_SECURE = True                     # Only send CSRF cookie over HTTPS
SECURE_HSTS_SECONDS = 31536000               # 1 year HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True         # Apply HSTS to all subdomains
SECURE_HSTS_PRELOAD = True                    # Allow HSTS preloading

# ----------------------------------------------------------------------
# Email backend
# ----------------------------------------------------------------------
# Use SMTP backend for staging (actual email sending)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@eventplanet.com')

# ----------------------------------------------------------------------
# Static and Media files
# ----------------------------------------------------------------------
# Use WhiteNoise for serving static files in staging
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ----------------------------------------------------------------------
# Logging configuration
# ----------------------------------------------------------------------
# Production-like logging for staging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'staging.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}