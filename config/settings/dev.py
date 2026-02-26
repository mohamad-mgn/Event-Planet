"""
Development settings for Event Planet project.

This module contains settings specific to the development environment.
Inherits from base.py and overrides/adds development-specific configurations.

Features:
- Debug mode enabled
- Development toolbar
- Detailed error pages
- Console email backend
- Relaxed security settings

Author: Event Planet Team
Created: 2026-02-15
"""

from .base import *

# ----------------------------------------------------------------------
# Debug settings
# ----------------------------------------------------------------------
# Enable debug mode for development (shows detailed error pages)
DEBUG = True

# Allow all hosts in development for convenience
ALLOWED_HOSTS = ['*']

# Print development settings loaded message
print("🚀 Development settings loaded successfully!")

# ----------------------------------------------------------------------
# Development apps
# ----------------------------------------------------------------------
# Add Django Debug Toolbar for development debugging
INSTALLED_APPS += [
    'debug_toolbar',  # Development debugging toolbar
]

# ----------------------------------------------------------------------
# Development middleware
# ----------------------------------------------------------------------
# Add Debug Toolbar middleware
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# ----------------------------------------------------------------------
# Debug Toolbar configuration
# ----------------------------------------------------------------------
# Internal IPs that can access the debug toolbar
INTERNAL_IPS = [
    '127.0.0.1',      # Localhost IPv4
    'localhost',       # Localhost hostname
    '::1',            # Localhost IPv6
]

# ----------------------------------------------------------------------
# Email backend
# ----------------------------------------------------------------------
# Use console backend for development (prints emails to console instead of sending)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ----------------------------------------------------------------------
# CORS settings
# ----------------------------------------------------------------------
# Allow all origins in development for easier testing
CORS_ALLOW_ALL_ORIGINS = True

# ----------------------------------------------------------------------
# Logging configuration
# ----------------------------------------------------------------------
# Detailed logging for development debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Debug level for our apps
            'propagate': False,
        },
    },
}

# ----------------------------------------------------------------------
# Static files
# ----------------------------------------------------------------------
# Serve static files directly in development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'