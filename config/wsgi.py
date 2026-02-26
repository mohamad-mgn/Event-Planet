"""
WSGI configuration for the 'config' Django project.

This file exposes the WSGI callable as a module-level variable named `application`.
WSGI is the entry point for WSGI-compatible web servers to serve your Django project.

For detailed information, visit:
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the default Django settings module for the WSGI application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create the WSGI application callable for the project
application = get_wsgi_application()
