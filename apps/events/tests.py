"""
Celery tasks for events app.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def close_expired_events():
    """
    Close events that have passed their end time.
    """
    from .models import Event
    
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
            print(f"✅ Closed expired event: {event.title}")
    
    return f"Closed {count} expired events"


@shared_task
def send_event_reminders():
    """
    Send reminders to participants 24 hours before event.
    """
    from .models import Event
    from apps.registrations.models import Registration
    
    now = timezone.now()
    tomorrow = now + timedelta(hours=24)
    
    # Find events starting in 24 hours
    upcoming_events = Event.objects.filter(
        status='published',
        start_datetime__gte=now,
        start_datetime__lte=tomorrow
    )
    
    count = 0
    for event in upcoming_events:
        registrations = Registration.objects.filter(
            event=event,
            status='confirmed'
        ).select_related('user')
        
        for registration in registrations:
            print(f"📧 Sending reminder to {registration.user.phone_number} for {event.title}")
            # TODO: Send actual SMS/Email
            count += 1
    
    return f"Sent {count} reminders"


@shared_task
def finish_completed_events():
    """
    Mark closed events as finished after they end.
    """
    from .models import Event
    
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
            print(f"🏁 Finished event: {event.title}")
    
    return f"Finished {count} events"