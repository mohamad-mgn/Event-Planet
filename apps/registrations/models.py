"""
Models for the Registrations app.

This module defines the Registration model for event registration management.

Registration supports different statuses:
- pending: Registration submitted, awaiting confirmation
- confirmed: Registration confirmed
- cancelled: Registration cancelled by participant
- rejected: Registration rejected by organizer

Author: Event Planet Team
Created: 2026-02-15
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.core.models import TimeStampedModel
from apps.accounts.models import User
from apps.events.models import Event


class Registration(TimeStampedModel):
    """
    Registration model for event participation.
    
    Tracks user registrations for events with complete lifecycle
    from submission to attendance.
    
    Fields:
        event: Event being registered for
        participant: User registering for event
        status: Registration status
        notes: Additional notes from participant
        checked_in: Whether participant checked in at event
        checked_in_at: Check-in timestamp
        cancelled_at: Cancellation timestamp
        cancellation_reason: Reason for cancellation
    
    Inherited from TimeStampedModel:
        created_at: Registration creation timestamp
        updated_at: Last update timestamp
    
    Business Rules:
        - User can only register once per event
        - Cannot register for full events
        - Cannot register for past events
        - Cannot register for draft events
    """
    
    # Status choices for registration lifecycle
    STATUS_CHOICES = [
        ('pending', 'Pending'),       # Awaiting confirmation
        ('confirmed', 'Confirmed'),   # Registration confirmed
        ('cancelled', 'Cancelled'),   # Cancelled by participant
        ('rejected', 'Rejected'),     # Rejected by organizer
    ]
    
    # Event and Participant
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name='Event',
        help_text='Event to register for'
    )
    
    participant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name='Participant',
        help_text='User registering for the event'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='confirmed',
        db_index=True,
        verbose_name='Status',
        help_text='Current registration status'
    )
    
    # Additional Information
    notes = models.TextField(
        blank=True,
        verbose_name='Notes',
        help_text='Additional notes or questions from participant'
    )
    
    # Check-in tracking
    checked_in = models.BooleanField(
        default=False,
        verbose_name='Checked In',
        help_text='Whether participant has checked in at the event'
    )
    
    checked_in_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Checked In At',
        help_text='Timestamp when participant checked in'
    )
    
    # Cancellation tracking
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Cancelled At',
        help_text='Timestamp when registration was cancelled'
    )
    
    cancellation_reason = models.TextField(
        blank=True,
        verbose_name='Cancellation Reason',
        help_text='Reason for cancellation'
    )
    
    class Meta:
        verbose_name = 'Registration'
        verbose_name_plural = 'Registrations'
        ordering = ['-created_at']
        # Ensure one registration per user per event
        unique_together = ['event', 'participant']
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['participant', 'status']),
            models.Index(fields=['checked_in']),
        ]
    
    def __str__(self):
        """String representation of registration."""
        return f"{self.participant.full_name} - {self.event.title}"
    
    def clean(self):
        """
        Validate registration data.
        
        Business rules:
        - Cannot register for past events
        - Cannot register for draft events
        - Cannot register for full events
        - Participant must have participant role
        
        Raises:
            ValidationError: If validation fails
        """
        # Check event exists
        if not self.event:
            return
        
        # Check event is not in the past
        if self.event.is_past:
            raise ValidationError(
                'Cannot register for past events.'
            )
        
        # Check event is published
        if self.event.status not in ['published', 'closed']:
            raise ValidationError(
                'Event is not accepting registrations.'
            )
        
        # Check event is not full (only for new registrations)
        if not self.pk and self.event.is_full:
            raise ValidationError(
                'Event is full. No more registrations accepted.'
            )
        
        # Check participant role
        if self.participant and self.participant.role != 'participant':
            raise ValidationError(
                'Only users with participant role can register for events.'
            )
    
    def save(self, *args, **kwargs):
        """
        Override save to validate before saving.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        # Run validation
        self.full_clean()
        
        # Call parent save
        super().save(*args, **kwargs)
    
    # Properties
    
    @property
    def is_confirmed(self):
        """
        Check if registration is confirmed.
        
        Returns:
            bool: True if status is 'confirmed'
        """
        return self.status == 'confirmed'
    
    @property
    def is_cancelled(self):
        """
        Check if registration is cancelled.
        
        Returns:
            bool: True if status is 'cancelled'
        """
        return self.status == 'cancelled'
    
    @property
    def is_pending(self):
        """
        Check if registration is pending.
        
        Returns:
            bool: True if status is 'pending'
        """
        return self.status == 'pending'
    
    @property
    def can_check_in(self):
        """
        Check if participant can check in.
        
        Participant can check in if:
        - Registration is confirmed
        - Not already checked in
        - Event is today or ongoing
        
        Returns:
            bool: True if can check in
        """
        if not self.is_confirmed:
            return False
        
        if self.checked_in:
            return False
        
        # Check if event is today or ongoing
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0)
        
        return (
            self.event.start_datetime >= today_start or
            self.event.is_ongoing
        )
    
    @property
    def can_cancel(self):
        """
        Check if registration can be cancelled.
        
        Can cancel if:
        - Status is confirmed or pending
        - Event hasn't started yet
        
        Returns:
            bool: True if can cancel
        """
        if self.status not in ['confirmed', 'pending']:
            return False
        
        return self.event.is_upcoming
    
    # Action methods
    
    def confirm(self):
        """
        Confirm the registration.
        
        Changes status from pending to confirmed.
        """
        if self.status == 'pending':
            self.status = 'confirmed'
            self.save()
    
    def cancel(self, reason=''):
        """
        Cancel the registration.
        
        Args:
            reason (str): Cancellation reason
        """
        if self.can_cancel:
            self.status = 'cancelled'
            self.cancelled_at = timezone.now()
            self.cancellation_reason = reason
            self.save()
    
    def check_in_participant(self):
        """
        Check in the participant.
        
        Marks participant as checked in with timestamp.
        
        Returns:
            bool: True if check-in successful
        """
        if self.can_check_in:
            self.checked_in = True
            self.checked_in_at = timezone.now()
            self.save()
            return True
        return False
    
    def reject(self, reason=''):
        """
        Reject the registration.
        
        Args:
            reason (str): Rejection reason
        """
        if self.status == 'pending':
            self.status = 'rejected'
            self.cancellation_reason = reason
            self.save()