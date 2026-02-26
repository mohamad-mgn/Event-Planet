"""
Models for the Events app.

This module defines models for event management:
- Event: Main event model with full event lifecycle
- EventStage: Multi-stage events (e.g., conference with multiple sessions)
- StageRole: People involved in stages (speakers, hosts, performers)
- AttributeDefinition: Dynamic attributes for events (EAV pattern)
- EventAttributeValue: Values for dynamic attributes
- EventResult: Event results and announcements

The Event model supports a complete lifecycle:
draft -> published -> closed -> finished -> archived

Author: Event Planet Team
Created: 2026-02-15
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify
from apps.core.models import TimeStampedModel
from apps.accounts.models import User
from apps.categories.models import Category


class Event(TimeStampedModel):
    """
    Main Event model.
    
    Represents an event with complete lifecycle management.
    Events can be single-session or multi-stage (conferences, festivals).
    
    Status Flow:
        draft -> published -> closed -> finished -> archived
    
    Fields:
        title: Event title
        slug: URL-friendly identifier (auto-generated)
        description: Detailed event description
        organizer: User who created the event
        category: Event category
        start_datetime: Event start date and time
        end_datetime: Event end date and time
        location: Physical location (if not online)
        is_online: Whether event is online
        online_link: Link for online events
        capacity: Maximum attendees (null = unlimited)
        status: Current event status
        cover_image: Event cover image
        views_count: Number of times event was viewed
    
    Inherited from TimeStampedModel:
        created_at: Event creation timestamp
        updated_at: Last update timestamp
    """
    
    # Status choices for event lifecycle
    STATUS_CHOICES = [
        ('draft', 'Draft'),           # Being created/edited
        ('published', 'Published'),   # Live and accepting registrations
        ('closed', 'Closed'),         # Registration closed, event ongoing/upcoming
        ('finished', 'Finished'),     # Event completed
        ('archived', 'Archived'),     # Historical record
    ]
    
    # Basic Information
    title = models.CharField(
        max_length=200,
        verbose_name='Event Title',
        help_text='Event title (e.g., "Tech Conference 2026")'
    )
    
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        verbose_name='Slug',
        help_text='URL-friendly identifier (auto-generated from title)'
    )
    
    description = models.TextField(
        verbose_name='Description',
        help_text='Detailed description of the event'
    )
    
    # Organizer and Category
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events',
        verbose_name='Organizer',
        help_text='User who created this event'
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,  # Prevent category deletion if events exist
        related_name='events',
        verbose_name='Category',
        help_text='Event category'
    )
    
    # Date and Time
    start_datetime = models.DateTimeField(
        verbose_name='Start Date & Time',
        help_text='When the event starts'
    )
    
    end_datetime = models.DateTimeField(
        verbose_name='End Date & Time',
        help_text='When the event ends'
    )
    
    # Location
    location = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Location',
        help_text='Physical location (address, venue name)'
    )
    
    is_online = models.BooleanField(
        default=False,
        verbose_name='Online Event',
        help_text='Whether this is an online event'
    )
    
    online_link = models.URLField(
        blank=True,
        verbose_name='Online Link',
        help_text='Link for online event (Zoom, Google Meet, etc.)'
    )
    
    # Capacity
    capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name='Capacity',
        help_text='Maximum number of attendees (leave empty for unlimited)'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True,
        verbose_name='Status',
        help_text='Current event status'
    )
    
    # Media
    cover_image = models.ImageField(
        upload_to='events/covers/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Cover Image',
        help_text='Event cover image'
    )
    
    # Statistics
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Views Count',
        help_text='Number of times this event was viewed'
    )
    
    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'start_datetime']),
            models.Index(fields=['organizer', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        """String representation of event."""
        return self.title
    
    def save(self, *args, **kwargs):
        """
        Override save to auto-generate slug.
        
        Creates a URL-friendly slug from title if not provided.
        Ensures slug uniqueness by appending numbers if needed.
        """
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            
            # Ensure unique slug
            while Event.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """
        Validate event data.
        
        Ensures business rules are followed:
        - End datetime must be after start datetime
        - Online events must have online link
        """
        from django.core.exceptions import ValidationError
        
        # Validate datetime fields exist before comparing
        if self.end_datetime and self.start_datetime:
            if self.end_datetime <= self.start_datetime:
                raise ValidationError(
                    'End datetime must be after start datetime.'
                )
        
        # Validate online event has link
        if self.is_online and not self.online_link:
            raise ValidationError(
                'Online link is required for online events.'
            )
    
    # Properties for computed fields
    
    @property
    def registration_count(self):
        """
        Get number of registrations.
        
        Returns:
            int: Total number of registrations (all statuses)
        """
        return self.registrations.count()
    
    @property
    def confirmed_registrations_count(self):
        """
        Get number of confirmed registrations.
        
        Returns:
            int: Number of confirmed registrations
        """
        return self.registrations.filter(status='confirmed').count()
    
    @property
    def available_slots(self):
        """
        Get number of available slots.
        
        Returns:
            int or str: Available slots or 'Unlimited'
        """
        if self.capacity is None:
            return 'Unlimited'
        
        registered = self.confirmed_registrations_count
        return max(0, self.capacity - registered)
    
    @property
    def is_full(self):
        """
        Check if event is at capacity.
        
        Returns:
            bool: True if event is full
        """
        if self.capacity is None:
            return False
        
        return self.confirmed_registrations_count >= self.capacity
    
    @property
    def is_upcoming(self):
        """
        Check if event is in the future.
        
        Returns:
            bool: True if event hasn't started yet
        """
        return timezone.now() < self.start_datetime
    
    @property
    def is_ongoing(self):
        """
        Check if event is currently happening.
        
        Returns:
            bool: True if event is in progress
        """
        now = timezone.now()
        return self.start_datetime <= now <= self.end_datetime
    
    @property
    def is_past(self):
        """
        Check if event has ended.
        
        Returns:
            bool: True if event is over
        """
        return timezone.now() > self.end_datetime
    
    @property
    def duration_hours(self):
        """
        Calculate event duration in hours.
        
        Returns:
            float: Duration in hours
        """
        delta = self.end_datetime - self.start_datetime
        return delta.total_seconds() / 3600
    
    # Status transition methods
    
    def can_transition_to(self, new_status):
        """
        Check if status transition is allowed.
        
        Enforces valid status transitions:
        - draft -> published
        - published -> closed
        - closed -> finished
        - finished -> archived
        
        Args:
            new_status (str): Target status
        
        Returns:
            bool: True if transition is allowed
        """
        allowed_transitions = {
            'draft': ['published'],
            'published': ['closed', 'draft'],
            'closed': ['finished'],
            'finished': ['archived'],
            'archived': [],
        }
        
        return new_status in allowed_transitions.get(self.status, [])
    
    def publish(self):
        """Publish the event (make it public)."""
        if self.can_transition_to('published'):
            self.status = 'published'
            self.save()
    
    def close_registration(self):
        """Close registration for the event."""
        if self.can_transition_to('closed'):
            self.status = 'closed'
            self.save()
    
    def mark_as_finished(self):
        """Mark event as finished."""
        if self.can_transition_to('finished'):
            self.status = 'finished'
            self.save()
    
    def archive(self):
        """Archive the event."""
        if self.can_transition_to('archived'):
            self.status = 'archived'
            self.save()
    
    def increment_views(self):
        """Increment view count (thread-safe)."""
        Event.objects.filter(pk=self.pk).update(
            views_count=models.F('views_count') + 1
        )


class EventStage(TimeStampedModel):
    """
    Event Stage model for multi-stage events.
    
    Allows events to have multiple stages/sessions (e.g., conference days,
    festival stages, workshop sessions).
    
    Fields:
        event: Parent event
        order: Stage order (1, 2, 3...)
        title: Stage title
        description: Stage description
        start_datetime: Stage start time
        end_datetime: Stage end time
        location: Stage-specific location
        capacity: Stage-specific capacity (overrides event capacity)
    """
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='stages',
        verbose_name='Event'
    )
    
    order = models.PositiveIntegerField(
        default=1,
        verbose_name='Order',
        help_text='Display order of this stage'
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='Stage Title'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    
    start_datetime = models.DateTimeField(
        verbose_name='Start Time'
    )
    
    end_datetime = models.DateTimeField(
        verbose_name='End Time'
    )
    
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Location',
        help_text='Stage-specific location (if different from event)'
    )
    
    capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Capacity',
        help_text='Stage capacity (if different from event)'
    )
    
    class Meta:
        verbose_name = 'Event Stage'
        verbose_name_plural = 'Event Stages'
        ordering = ['event', 'order', 'start_datetime']
        unique_together = ['event', 'order']
    
    def __str__(self):
        return f"{self.event.title} - {self.title}"


class StageRole(TimeStampedModel):
    """
    People involved in event stages.
    
    Tracks speakers, hosts, performers, etc. for each stage.
    
    Fields:
        stage: Related stage
        role_type: Type of role (speaker, host, performer, etc.)
        name: Person's name
        bio: Short biography
        profile_image: Person's photo
    """
    
    ROLE_CHOICES = [
        ('speaker', 'Speaker'),
        ('host', 'Host'),
        ('performer', 'Performer'),
        ('moderator', 'Moderator'),
        ('panelist', 'Panelist'),
        ('other', 'Other'),
    ]
    
    stage = models.ForeignKey(
        EventStage,
        on_delete=models.CASCADE,
        related_name='roles',
        verbose_name='Stage'
    )
    
    role_type = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name='Role Type'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='Name'
    )
    
    bio = models.TextField(
        blank=True,
        verbose_name='Biography'
    )
    
    profile_image = models.ImageField(
        upload_to='stages/profiles/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Profile Image'
    )
    
    class Meta:
        verbose_name = 'Stage Role'
        verbose_name_plural = 'Stage Roles'
        ordering = ['stage', 'role_type']
    
    def __str__(self):
        return f"{self.name} ({self.get_role_type_display()})"


class AttributeDefinition(TimeStampedModel):
    """
    Dynamic attribute definitions (EAV pattern).
    
    Allows adding custom attributes to events without changing schema.
    Examples: dress_code, age_restriction, parking_available, etc.
    
    Fields:
        name: Attribute name (snake_case)
        display_name: Human-readable name
        data_type: Type of value (string, integer, boolean, etc.)
        description: Attribute description
        is_required: Whether this attribute is required
    """
    
    DATA_TYPE_CHOICES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('decimal', 'Decimal'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('datetime', 'DateTime'),
        ('text', 'Text'),
    ]
    
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Attribute Name',
        help_text='Internal name (snake_case, e.g., "dress_code")'
    )
    
    display_name = models.CharField(
        max_length=100,
        verbose_name='Display Name',
        help_text='Human-readable name (e.g., "Dress Code")'
    )
    
    data_type = models.CharField(
        max_length=20,
        choices=DATA_TYPE_CHOICES,
        verbose_name='Data Type'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    
    is_required = models.BooleanField(
        default=False,
        verbose_name='Required',
        help_text='Whether this attribute is required for events'
    )
    
    class Meta:
        verbose_name = 'Attribute Definition'
        verbose_name_plural = 'Attribute Definitions'
        ordering = ['display_name']
    
    def __str__(self):
        return self.display_name


class EventAttributeValue(TimeStampedModel):
    """
    Attribute values for events (EAV pattern).
    
    Stores actual attribute values for each event.
    Uses multiple value fields to support different data types.
    
    Fields:
        event: Related event
        attribute: Attribute definition
        value_string: String value
        value_integer: Integer value
        value_decimal: Decimal value
        value_boolean: Boolean value
        value_date: Date value
        value_datetime: DateTime value
        value_text: Text value (long text)
    """
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='attribute_values',
        verbose_name='Event'
    )
    
    attribute = models.ForeignKey(
        AttributeDefinition,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name='Attribute'
    )
    
    # Value fields (only one will be used based on data_type)
    value_string = models.CharField(max_length=200, blank=True, null=True)
    value_integer = models.IntegerField(blank=True, null=True)
    value_decimal = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    value_boolean = models.BooleanField(blank=True, null=True)
    value_date = models.DateField(blank=True, null=True)
    value_datetime = models.DateTimeField(blank=True, null=True)
    value_text = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Event Attribute Value'
        verbose_name_plural = 'Event Attribute Values'
        unique_together = ['event', 'attribute']
        ordering = ['event', 'attribute']
    
    def __str__(self):
        return f"{self.event.title} - {self.attribute.display_name}"
    
    def get_value(self):
        """
        Get the appropriate value based on attribute data type.
        
        Returns:
            Value of appropriate type
        """
        data_type = self.attribute.data_type
        
        value_map = {
            'string': self.value_string,
            'integer': self.value_integer,
            'decimal': self.value_decimal,
            'boolean': self.value_boolean,
            'date': self.value_date,
            'datetime': self.value_datetime,
            'text': self.value_text,
        }
        
        return value_map.get(data_type)
    
    def set_value(self, value):
        """
        Set the appropriate value field based on attribute data type.
        
        Args:
            value: Value to set
        """
        data_type = self.attribute.data_type
        
        # Clear all value fields first
        self.value_string = None
        self.value_integer = None
        self.value_decimal = None
        self.value_boolean = None
        self.value_date = None
        self.value_datetime = None
        self.value_text = None
        
        # Set appropriate field
        if data_type == 'string':
            self.value_string = str(value)
        elif data_type == 'integer':
            self.value_integer = int(value)
        elif data_type == 'decimal':
            self.value_decimal = float(value)
        elif data_type == 'boolean':
            self.value_boolean = bool(value)
        elif data_type == 'date':
            self.value_date = value
        elif data_type == 'datetime':
            self.value_datetime = value
        elif data_type == 'text':
            self.value_text = str(value)


class EventResult(TimeStampedModel):
    """
    Event results and announcements.
    
    Stores results, outcomes, winners, or final announcements after
    an event is finished.
    
    Fields:
        event: Related event
        title: Result title
        content: Result content/description
        attachment: Optional file attachment
        published_at: When result was published
    """
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='Event'
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='Title'
    )
    
    content = models.TextField(
        verbose_name='Content'
    )
    
    attachment = models.FileField(
        upload_to='events/results/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Attachment',
        help_text='PDF, spreadsheet, or other file'
    )
    
    published_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Published At'
    )
    
    class Meta:
        verbose_name = 'Event Result'
        verbose_name_plural = 'Event Results'
        ordering = ['-published_at']
    
    def __str__(self):
        return f"{self.event.title} - {self.title}"