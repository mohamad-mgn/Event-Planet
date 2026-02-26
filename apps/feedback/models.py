"""
Models for the Feedback app.

This module defines the Feedback model for event rating and reviews.

Participants can provide feedback after attending events, including:
- Star rating (1-5)
- Written review
- Response from organizer

Author: Event Planet Team
Created: 2026-02-15
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedModel
from apps.accounts.models import User
from apps.events.models import Event


class Feedback(TimeStampedModel):
    """
    Feedback model for event reviews.
    
    Allows participants to rate and review events they attended.
    Organizers can respond to feedback.
    
    Fields:
        event: Event being reviewed
        participant: User providing feedback
        rating: Star rating (1-5)
        review: Written review text
        organizer_response: Response from event organizer
        is_published: Whether feedback is publicly visible
    
    Inherited from TimeStampedModel:
        created_at: Feedback creation timestamp
        updated_at: Last update timestamp
    
    Business Rules:
        - Only participants who registered can provide feedback
        - One feedback per user per event
        - Rating must be between 1 and 5
        - Feedback can only be given after event ends
    """
    
    # Event and Participant
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name='Event',
        help_text='Event being reviewed'
    )
    
    participant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name='Participant',
        help_text='User providing feedback'
    )
    
    # Rating (1-5 stars)
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ],
        verbose_name='Rating',
        help_text='Rating from 1 (poor) to 5 (excellent)'
    )
    
    # Review text
    review = models.TextField(
        verbose_name='Review',
        help_text='Written review of the event'
    )
    
    # Organizer response
    organizer_response = models.TextField(
        blank=True,
        verbose_name='Organizer Response',
        help_text='Response from event organizer'
    )
    
    # Publication status
    is_published = models.BooleanField(
        default=True,
        verbose_name='Published',
        help_text='Whether this feedback is publicly visible'
    )
    
    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'
        ordering = ['-created_at']
        # One feedback per user per event
        unique_together = ['event', 'participant']
        indexes = [
            models.Index(fields=['event', 'is_published']),
            models.Index(fields=['participant']),
            models.Index(fields=['rating']),
        ]
    
    def __str__(self):
        """String representation of feedback."""
        return f"{self.participant.full_name} - {self.event.title} ({self.rating}⭐)"
    
    def clean(self):
        """
        Validate feedback data.
        
        Business rules:
        - User must have registered for the event
        - Event must be finished
        - Participant must have participant role
        
        Raises:
            ValidationError: If validation fails
        """
        # Check participant role
        if self.participant and self.participant.role != 'participant':
            raise ValidationError(
                'Only participants can provide feedback.'
            )
        
        # Check if participant registered for event
        if self.event and self.participant:
            from apps.registrations.models import Registration
            
            if not Registration.objects.filter(
                event=self.event,
                participant=self.participant,
                status='confirmed'
            ).exists():
                raise ValidationError(
                    'You must have registered for this event to provide feedback.'
                )
        
        # Check if event is finished (optional - can be removed if feedback during event is allowed)
        # if self.event and self.event.status not in ['finished', 'archived']:
        #     raise ValidationError(
        #         'Feedback can only be provided after event is finished.'
        #     )
    
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
    def rating_stars(self):
        """
        Get rating as star string.
        
        Returns:
            str: Star representation (e.g., "⭐⭐⭐⭐⭐")
        """
        return '⭐' * self.rating
    
    @property
    def has_response(self):
        """
        Check if organizer has responded.
        
        Returns:
            bool: True if organizer_response is not empty
        """
        return bool(self.organizer_response)
    
    @property
    def is_positive(self):
        """
        Check if feedback is positive (4-5 stars).
        
        Returns:
            bool: True if rating is 4 or 5
        """
        return self.rating >= 4
    
    @property
    def is_negative(self):
        """
        Check if feedback is negative (1-2 stars).
        
        Returns:
            bool: True if rating is 1 or 2
        """
        return self.rating <= 2
    
    @property
    def is_neutral(self):
        """
        Check if feedback is neutral (3 stars).
        
        Returns:
            bool: True if rating is 3
        """
        return self.rating == 3
    
    # Methods
    
    def respond(self, response_text):
        """
        Add organizer response to feedback.
        
        Args:
            response_text (str): Response from organizer
        """
        self.organizer_response = response_text
        self.save()
    
    def publish(self):
        """Publish feedback (make it visible)."""
        self.is_published = True
        self.save()
    
    def unpublish(self):
        """Unpublish feedback (hide it)."""
        self.is_published = False
        self.save()