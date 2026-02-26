"""
Signals for the Events app.

This module contains signal handlers for event-related events:
- Event creation notifications
- Event publication notifications
- Event status change tracking
- Automatic event closure
- Stage creation notifications
- Result publication notifications

Author: Event Planet Team
Created: 2026-02-15
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Event, EventStage, EventResult


@receiver(post_save, sender=Event)
def event_created_notification(sender, instance, created, **kwargs):
    """
    Send notification when new event is created.
    
    Args:
        sender: The model class (Event)
        instance: The actual Event instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    
    Actions:
        - Log event creation
        - Notify system administrators
        - Update organizer statistics
    """
    if created:
        print(f"🎪 New event created: {instance.title} by {instance.organizer.phone_number}")
        
        # Additional actions for new events
        # - Send notification to admins
        # - Update organizer's event count
        # - Log in analytics


@receiver(post_save, sender=Event)
def event_published_notification(sender, instance, created, **kwargs):
    """
    Send notification when event is published.
    
    Notifies followers and interested users when an event
    goes from draft to published status.
    
    Args:
        sender: The model class (Event)
        instance: The actual Event instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    
    Actions:
        - Notify category followers
        - Send email to subscribers
        - Post to social media (if integrated)
        - Update search index
    """
    if not created and instance.status == 'published':
        print(f"📢 Event published: {instance.title}")
        
        # Notify followers of this category
        # from apps.accounts.tasks import notify_category_followers
        # notify_category_followers.delay(
        #     category_id=instance.category.id,
        #     event_id=instance.id
        # )


@receiver(post_save, sender=Event)
def event_closed_notification(sender, instance, created, **kwargs):
    """
    Send notification when event registration is closed.
    
    Notifies all registered participants that registration
    has closed and provides final event details.
    
    Args:
        sender: The model class (Event)
        instance: The actual Event instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    
    Actions:
        - Notify registered participants
        - Send final event details
        - Lock registration system
    """
    if not created and instance.status == 'closed':
        print(f"🔒 Event registration closed: {instance.title}")
        
        # Notify all registered participants
        # from apps.registrations.tasks import notify_registered_users
        # notify_registered_users.delay(
        #     event_id=instance.id,
        #     message="Registration is now closed. See you at the event!"
        # )


@receiver(post_save, sender=Event)
def event_finished_notification(sender, instance, created, **kwargs):
    """
    Send notification when event is finished.
    
    Triggers post-event workflows like feedback requests
    and certificate generation.
    
    Args:
        sender: The model class (Event)
        instance: The actual Event instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    
    Actions:
        - Request feedback from attendees
        - Generate attendance certificates
        - Archive event data
        - Calculate statistics
    """
    if not created and instance.status == 'finished':
        print(f"✅ Event finished: {instance.title}")
        
        # Request feedback from participants
        # from apps.feedback.tasks import request_event_feedback
        # request_event_feedback.delay(event_id=instance.id)
        
        # Generate certificates if applicable
        # from apps.events.tasks import generate_certificates
        # generate_certificates.delay(event_id=instance.id)


@receiver(post_delete, sender=Event)
def event_deleted_notification(sender, instance, **kwargs):
    """
    Handle event deletion.
    
    Performs cleanup when an event is deleted.
    
    Args:
        sender: The model class (Event)
        instance: The actual Event instance being deleted
        **kwargs: Additional keyword arguments
    
    Actions:
        - Notify registered participants
        - Refund payments (if applicable)
        - Clean up related files
        - Archive for records
    """
    print(f"🗑️  Event deleted: {instance.title}")
    
    # Notify registered participants if event was published
    # if instance.status in ['published', 'closed']:
    #     from apps.registrations.tasks import notify_event_cancellation
    #     notify_event_cancellation.delay(
    #         event_id=instance.id,
    #         event_title=instance.title
    #     )


@receiver(pre_save, sender=Event)
def track_event_changes(sender, instance, **kwargs):
    """
    Track changes to event fields.
    
    Monitors important field changes like status transitions,
    datetime changes, and capacity modifications.
    
    Args:
        sender: The model class (Event)
        instance: The actual Event instance being saved
        **kwargs: Additional keyword arguments
    
    Actions:
        - Log status transitions
        - Notify on datetime changes
        - Alert on capacity changes
    """
    if instance.pk:
        try:
            old_event = Event.objects.get(pk=instance.pk)
            
            # Track status changes
            if old_event.status != instance.status:
                print(f"🔄 Event status changed: {old_event.status} -> {instance.status} for {instance.title}")
            
            # Track datetime changes
            if old_event.start_datetime != instance.start_datetime:
                print(f"📅 Event start time changed for {instance.title}")
                # Notify registered participants
            
            # Track capacity changes
            if old_event.capacity != instance.capacity:
                print(f"👥 Event capacity changed from {old_event.capacity} to {instance.capacity}")
        
        except Event.DoesNotExist:
            pass


@receiver(post_save, sender=EventStage)
def stage_created_notification(sender, instance, created, **kwargs):
    """
    Send notification when new stage is added to event.
    
    Args:
        sender: The model class (EventStage)
        instance: The actual EventStage instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    
    Actions:
        - Notify event organizer
        - Update event schedule
    """
    if created:
        print(f"🎭 New stage added: {instance.title} to event {instance.event.title}")


@receiver(post_save, sender=EventResult)
def result_published_notification(sender, instance, created, **kwargs):
    """
    Send notification when event results are published.
    
    Args:
        sender: The model class (EventResult)
        instance: The actual EventResult instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    
    Actions:
        - Notify all registered participants
        - Send results via email
        - Update event page
    """
    if created:
        print(f"🏆 Results published for event: {instance.event.title}")
        
        # Notify all participants
        # from apps.registrations.tasks import notify_event_results
        # notify_event_results.delay(
        #     event_id=instance.event.id,
        #     result_id=instance.id
        # )