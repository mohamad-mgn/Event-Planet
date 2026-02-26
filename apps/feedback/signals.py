"""
Signals for the Feedback app.

This module contains signal handlers for feedback-related events:
- Feedback creation notifications
- Feedback update tracking
- Organizer response notifications
- Rating statistics updates

Author: Event Planet Team
Created: 2026-02-15
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Feedback


@receiver(post_save, sender=Feedback)
def feedback_created_notification(sender, instance, created, **kwargs):
    """
    Send notification when new feedback is created.
    
    Notifies event organizer about new feedback.
    
    Args:
        sender: The model class (Feedback)
        instance: The actual Feedback instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    
    Actions:
        - Notify event organizer
        - Update event rating statistics
        - Send thank you to participant
    """
    if created:
        print(f"⭐ New feedback: {instance.rating} stars for {instance.event.title}")
        
        # Notify event organizer
        # from apps.feedback.tasks import notify_organizer_new_feedback
        # notify_organizer_new_feedback.delay(instance.id)
        
        # Send thank you to participant
        # from apps.feedback.tasks import send_feedback_thank_you
        # send_feedback_thank_you.delay(instance.id)
        
        # Update event statistics
        # from apps.events.tasks import update_event_statistics
        # update_event_statistics.delay(instance.event.id)


@receiver(post_save, sender=Feedback)
def organizer_response_notification(sender, instance, created, **kwargs):
    """
    Send notification when organizer responds to feedback.
    
    Args:
        sender: The model class (Feedback)
        instance: The actual Feedback instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    
    Actions:
        - Notify participant about response
        - Update feedback engagement metrics
    """
    if not created and instance.has_response:
        # Check if response was just added
        try:
            old_feedback = Feedback.objects.get(pk=instance.pk)
            if not old_feedback.organizer_response and instance.organizer_response:
                print(f"💬 Organizer responded to feedback for {instance.event.title}")
                
                # Notify participant
                # from apps.feedback.tasks import notify_participant_response
                # notify_participant_response.delay(instance.id)
        except Feedback.DoesNotExist:
            pass


@receiver(post_save, sender=Feedback)
def feedback_published_notification(sender, instance, created, **kwargs):
    """
    Track feedback publication status changes.
    
    Args:
        sender: The model class (Feedback)
        instance: The actual Feedback instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    
    Actions:
        - Update public rating statistics when published
        - Remove from statistics when unpublished
    """
    if not created:
        print(f"📊 Feedback publication status: {'Published' if instance.is_published else 'Unpublished'}")


@receiver(post_delete, sender=Feedback)
def feedback_deleted_notification(sender, instance, **kwargs):
    """
    Handle feedback deletion.
    
    Args:
        sender: The model class (Feedback)
        instance: The actual Feedback instance being deleted
        **kwargs: Additional keyword arguments
    
    Actions:
        - Update event rating statistics
        - Log deletion for audit
    """
    print(f"🗑️  Feedback deleted: {instance.rating} stars for {instance.event.title}")
    
    # Update event statistics
    # from apps.events.tasks import update_event_statistics
    # update_event_statistics.delay(instance.event.id)


@receiver(pre_save, sender=Feedback)
def track_feedback_changes(sender, instance, **kwargs):
    """
    Track changes to feedback fields.
    
    Args:
        sender: The model class (Feedback)
        instance: The actual Feedback instance being saved
        **kwargs: Additional keyword arguments
    
    Actions:
        - Log rating changes
        - Track review edits
        - Monitor response additions
    """
    if instance.pk:
        try:
            old_feedback = Feedback.objects.get(pk=instance.pk)
            
            # Track rating changes
            if old_feedback.rating != instance.rating:
                print(f"🔄 Rating changed: {old_feedback.rating} -> {instance.rating} stars")
            
            # Track review edits
            if old_feedback.review != instance.review:
                print(f"✏️  Review edited for {instance.event.title}")
            
            # Track response additions
            if not old_feedback.organizer_response and instance.organizer_response:
                print(f"💬 Response added to feedback")
        
        except Feedback.DoesNotExist:
            pass