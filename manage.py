#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.

This script serves as the entry point for running management commands
like `runserver`, `migrate`, `createsuperuser`, etc. It sets up the
environment and delegates execution to Django's management system.
"""

import os
import sys


def main():
    """Execute administrative tasks for the Django project."""
    # Set the default settings module for the Django project
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Provide a clear error message if Django is not installed
        raise ImportError(
            "Django could not be imported. Ensure it is installed and "
            "available on your PYTHONPATH environment variable. "
            "Also, verify that your virtual environment (if any) is activated."
        ) from exc
    
    # Pass command-line arguments to Django's management utility
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()