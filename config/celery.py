"""
Celery configuration for Event Planet project.

This module configures Celery for asynchronous task processing.
It includes:
- Celery app initialization
- Task auto-discovery from all Django apps
- Periodic task scheduling (Celery Beat)

Celery is used for:
- Sending OTP codes
- Sending email notifications
- Auto-closing expired events
- Cleaning up expired OTP codes
- Sending event reminders

Author: Event Planet Team
Created: 2026-02-15
"""

import os
from celery import Celery
from celery.schedules import crontab

# ----------------------------------------------------------------------
# Django settings module
# ----------------------------------------------------------------------
# Set the default Django settings module for Celery
# This tells Celery which Django settings to use
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

# ----------------------------------------------------------------------
# Create Celery app
# ----------------------------------------------------------------------
# Initialize Celery app with the project name
app = Celery('event_planet')

# ----------------------------------------------------------------------
# Load configuration from Django settings
# ----------------------------------------------------------------------
# Load Celery config from Django settings with 'CELERY_' prefix
# Example: CELERY_BROKER_URL in settings.py becomes broker_url in Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# ----------------------------------------------------------------------
# Auto-discover tasks
# ----------------------------------------------------------------------
# Automatically discover tasks from all installed Django apps
# Celery will look for tasks.py in each app
app.autodiscover_tasks()

# ----------------------------------------------------------------------
# Periodic tasks schedule (Celery Beat)
# ----------------------------------------------------------------------
# Define periodic tasks that run automatically on a schedule
app.conf.beat_schedule = {
    # Close expired events every hour
    'close-expired-events': {
        'task': 'apps.events.tasks.close_expired_events',
        'schedule': crontab(minute=0),  # Every hour at minute 0
        'options': {
            'expires': 3600,  # Task expires after 1 hour if not executed
        }
    },
    
    # Send event reminders daily at 9 AM
    'send-event-reminders': {
        'task': 'apps.events.tasks.send_event_reminders',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9:00 AM
        'options': {
            'expires': 86400,  # Task expires after 24 hours
        }
    },
    
    # Clean up expired OTP codes every 30 minutes
    'cleanup-expired-otps': {
        'task': 'apps.accounts.tasks.cleanup_expired_otps',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,  # Task expires after 30 minutes
        }
    },
    
    # Finish completed events daily at midnight
    'finish-completed-events': {
        'task': 'apps.events.tasks.finish_completed_events',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
        'options': {
            'expires': 86400,  # Task expires after 24 hours
        }
    },
}

# ----------------------------------------------------------------------
# Celery task configuration
# ----------------------------------------------------------------------
# General task settings
app.conf.update(
    # Task result expiration (1 day)
    result_expires=86400,
    
    # Task acknowledgment mode (after task completion)
    task_acks_late=True,
    
    # Prefetch limit (how many tasks a worker can reserve at once)
    worker_prefetch_multiplier=1,
    
    # Task time limit (10 minutes)
    task_time_limit=600,
    
    # Task soft time limit (8 minutes - warning before hard limit)
    task_soft_time_limit=480,
    
    # Task rejection on worker lost
    task_reject_on_worker_lost=True,
)

# ----------------------------------------------------------------------
# Debug task
# ----------------------------------------------------------------------
@app.task(bind=True)
def debug_task(self):
    """
    Simple debug task for testing Celery configuration.
    
    Usage:
        from config.celery import debug_task
        debug_task.delay()
    """
    print(f'Request: {self.request!r}')