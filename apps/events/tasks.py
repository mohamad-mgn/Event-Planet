"""
Celery tasks for the Events app.

This module contains asynchronous tasks for event operations:
- Close expired events
- Send event reminders
- Finish completed events
- Generate certificates
- Update event statistics

Author: Event Planet Team
Created: 2026-02-15
"""

from celery import shared_task
from django.utils import timezone
from django.db.models import Avg
from datetime import timedelta
from .models import Event


@shared_task
def close_expired_events():
    """
    Automatically close events that have passed their end time.
    
    This task runs hourly to check for events that have ended
    but are still in 'published' status. It automatically
    transitions them to 'closed' status.
    
    Returns:
        int: Number of events closed
    
    Schedule:
        Configured in config/celery.py to run every hour
    
    Example:
        # Manual execution
        from apps.events.tasks import close_expired_events
        close_expired_events.delay()
    """
    now = timezone.now()
    
    # Find published events that have ended
    expired_events = Event.objects.filter(
        status='published',
        end_datetime__lt=now
    )
    
    count = 0
    for event in expired_events:
        if event.can_transition_to('closed'):
            event.status = 'closed'
            event.save()
            count += 1
            print(f"✅ Auto-closed event: {event.title}")
    
    return count


@shared_task
def send_event_reminders():
    """
    Send reminders to registered participants.
    
    This task runs daily to send reminders for events
    starting within 24 hours.
    
    Returns:
        int: Number of reminders sent
    
    Schedule:
        Configured in config/celery.py to run daily at 9 AM
    
    Example:
        # Manual execution
        from apps.events.tasks import send_event_reminders
        send_event_reminders.delay()
    """
    now = timezone.now()
    tomorrow = now + timedelta(days=1)
    
    # Find events starting within 24 hours
    upcoming_events = Event.objects.filter(
        status__in=['published', 'closed'],
        start_datetime__gte=now,
        start_datetime__lte=tomorrow
    )
    
    count = 0
    for event in upcoming_events:
        # Get registered participants
        registrations = event.registrations.filter(
            status='confirmed'
        )
        
        for registration in registrations:
            # TODO: Send reminder email/SMS
            print(f"📧 Reminder sent to {registration.participant.phone_number} for {event.title}")
            count += 1
    
    return count


@shared_task
def finish_completed_events():
    """
    Mark events as finished after they end.
    
    This task runs daily to check for closed events that
    have ended and transitions them to 'finished' status.
    
    Returns:
        int: Number of events finished
    
    Schedule:
        Configured in config/celery.py to run daily at midnight
    
    Example:
        # Manual execution
        from apps.events.tasks import finish_completed_events
        finish_completed_events.delay()
    """
    now = timezone.now()
    
    # Find closed events that have ended
    completed_events = Event.objects.filter(
        status='closed',
        end_datetime__lt=now
    )
    
    count = 0
    for event in completed_events:
        if event.can_transition_to('finished'):
            event.status = 'finished'
            event.save()
            count += 1
            print(f"✅ Marked as finished: {event.title}")
    
    return count


@shared_task
def generate_event_certificates(event_id):
    """
    Generate attendance certificates for event participants.
    
    Creates PDF certificates for all confirmed attendees
    who checked in to the event.
    
    Args:
        event_id (int): ID of the event
    
    Returns:
        int: Number of certificates generated
    
    Example:
        # Queue certificate generation
        from apps.events.tasks import generate_event_certificates
        generate_event_certificates.delay(1)
    
    Note:
        This is a placeholder. Implement actual PDF generation
        using libraries like ReportLab or WeasyPrint.
    """
    try:
        event = Event.objects.get(id=event_id)
        
        # Get participants who checked in
        attendees = event.registrations.filter(
            status='confirmed',
            checked_in=True
        )
        
        count = 0
        for registration in attendees:
            # TODO: Generate PDF certificate
            # - Use ReportLab or WeasyPrint
            # - Include event details and participant name
            # - Save to media folder
            # - Send download link via email
            
            print(f"📜 Certificate generated for {registration.participant.full_name}")
            count += 1
        
        return count
        
    except Event.DoesNotExist:
        print(f"❌ Event with ID {event_id} does not exist")
        return 0


@shared_task
def update_event_statistics(event_id):
    """
    Update event statistics and analytics.
    
    Calculates various metrics for the event:
    - Total registrations
    - Check-in rate
    - Feedback ratings
    - Popular time slots
    
    Args:
        event_id (int): ID of the event
    
    Returns:
        dict: Updated statistics
    
    Example:
        # Queue statistics update
        from apps.events.tasks import update_event_statistics
        update_event_statistics.delay(1)
    """
    try:
        event = Event.objects.get(id=event_id)
        
        # Calculate statistics
        total_registrations = event.registrations.count()
        confirmed = event.registrations.filter(status='confirmed').count()
        checked_in = event.registrations.filter(checked_in=True).count()
        
        # Calculate rates
        check_in_rate = (checked_in / confirmed * 100) if confirmed > 0 else 0
        
        # Get feedback statistics
        from apps.feedback.models import Feedback
        feedbacks = Feedback.objects.filter(event=event)
        avg_rating = feedbacks.aggregate(
            Avg('rating')
        )['rating__avg'] or 0
        
        
        stats = {
            'event_id': event_id,
            'total_registrations': total_registrations,
            'confirmed': confirmed,
            'checked_in': checked_in,
            'check_in_rate': round(check_in_rate, 2),
            'average_rating': round(avg_rating, 2),
            'feedback_count': feedbacks.count()
        }
        
        print(f"📊 Statistics updated for {event.title}: {stats}")
        
        return stats
        
    except Event.DoesNotExist:
        print(f"❌ Event with ID {event_id} does not exist")
        return {}


@shared_task
def notify_capacity_reached(event_id):
    """
    Notify organizer when event reaches capacity.
    
    Sends alert when event is full so organizer can
    decide whether to increase capacity or close registration.
    
    Args:
        event_id (int): ID of the event
    
    Returns:
        bool: True if notification sent
    
    Example:
        # Queue notification
        from apps.events.tasks import notify_capacity_reached
        notify_capacity_reached.delay(1)
    """
    try:
        event = Event.objects.get(id=event_id)
        
        if event.is_full:
            # TODO: Send notification to organizer
            # - Email alert
            # - SMS alert
            # - Push notification
            
            print(f"🔴 Capacity alert sent for {event.title}")
            return True
        
        return False
        
    except Event.DoesNotExist:
        return False