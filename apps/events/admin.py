"""
Admin configuration for Events app.

This module configures the Django admin interface for event models.

Features:
- Event management with statistics
- Stage and role inline editing
- Attribute value management
- Event result publishing
- Bulk status change actions

Author: Event Planet Team
Created: 2026-02-15
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    Event,
    EventStage,
    StageRole,
    AttributeDefinition,
    EventAttributeValue,
    EventResult
)


class EventStageInline(admin.TabularInline):
    """
    Inline admin for event stages.
    
    Allows editing stages directly from event admin page.
    """
    model = EventStage
    extra = 1
    fields = [
        'order',
        'title',
        'start_datetime',
        'end_datetime',
        'location',
        'capacity'
    ]
    ordering = ['order']


class EventAttributeValueInline(admin.TabularInline):
    """
    Inline admin for event attribute values.
    
    Allows setting dynamic attributes for events.
    """
    model = EventAttributeValue
    extra = 1
    fields = ['attribute', 'get_value_field']
    readonly_fields = ['get_value_field']
    
    def get_value_field(self, obj):
        """Display appropriate value field."""
        if obj.pk:
            return obj.get_value()
        return "-"
    get_value_field.short_description = 'Value'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin interface for Event model.
    
    Provides comprehensive event management with:
    - List view with key information
    - Filtering by status, category, dates
    - Search by title and organizer
    - Inline stage and attribute editing
    - Bulk status change actions
    """
    
    # Fields to display in list view
    list_display = [
        'title',
        'organizer',
        'category',
        'status_badge',
        'start_datetime',
        'capacity',
        'get_registration_count',
        'views_count'
    ]
    
    # Filters in sidebar
    list_filter = [
        'status',
        'category',
        'is_online',
        'created_at',
        'start_datetime'
    ]
    
    # Search fields
    search_fields = [
        'title',
        'description',
        'organizer__phone_number',
        'organizer__full_name'
    ]
    
    # Prepopulated fields
    prepopulated_fields = {'slug': ('title',)}
    
    # Default ordering
    ordering = ['-created_at']
    
    # Read-only fields
    readonly_fields = [
        'created_at',
        'updated_at',
        'views_count',
        'get_registration_count',
        'get_available_slots',
        'get_is_full'
    ]
    
    # Fieldsets for organized display
    fieldsets = (
        # Basic Information
        ('Basic Information', {
            'fields': (
                'title',
                'slug',
                'description',
                'organizer',
                'category'
            )
        }),
        
        # Date & Time
        ('Date & Time', {
            'fields': (
                'start_datetime',
                'end_datetime'
            )
        }),
        
        # Location
        ('Location', {
            'fields': (
                'location',
                'is_online',
                'online_link'
            )
        }),
        
        # Capacity
        ('Capacity', {
            'fields': (
                'capacity',
                'get_registration_count',
                'get_available_slots',
                'get_is_full'
            )
        }),
        
        # Status & Media
        ('Status & Media', {
            'fields': (
                'status',
                'cover_image'
            )
        }),
        
        # Statistics
        ('Statistics', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
        
        # Timestamps
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    # Inline models
    inlines = [EventStageInline, EventAttributeValueInline]
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'draft': '#6c757d',
            'published': '#28a745',
            'closed': '#ffc107',
            'finished': '#17a2b8',
            'archived': '#343a40',
        }
        
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    
    status_badge.short_description = 'Status'
    
    def get_registration_count(self, obj):
        """Display registration count."""
        from apps.registrations.models import Registration
        count = Registration.objects.filter(event=obj).count()
        
        if count > 0:
            url = f'/admin/registrations/registration/?event__id__exact={obj.id}'
            return format_html(
                '<a href="{}" style="color: #007bff;">{} registrations</a>',
                url,
                count
            )
        return '0'
    
    get_registration_count.short_description = 'Registrations'
    
    def get_available_slots(self, obj):
        """Display available slots."""
        slots = obj.available_slots
        
        if slots == 'Unlimited':
            return format_html(
                '<span style="color: #28a745;">♾️ Unlimited</span>'
            )
        elif slots == 0:
            return format_html(
                '<span style="color: #dc3545;">🔴 Full</span>'
            )
        else:
            return format_html(
                '<span style="color: #007bff;">{} slots</span>',
                slots
            )
    
    get_available_slots.short_description = 'Available Slots'
    
    def get_is_full(self, obj):
        """Display if event is full."""
        if obj.is_full:
            return format_html(
                '<span style="color: #dc3545;">✖ Full</span>'
            )
        else:
            return format_html(
                '<span style="color: #28a745;">✓ Available</span>'
            )
    
    get_is_full.short_description = 'Is Full'
    
    # Custom actions
    actions = [
        'publish_events',
        'close_events',
        'finish_events'
    ]
    
    def publish_events(self, request, queryset):
        """Bulk publish events."""
        count = 0
        for event in queryset.filter(status='draft'):
            if event.can_transition_to('published'):
                event.status = 'published'
                event.save()
                count += 1
        
        self.message_user(
            request,
            f'{count} event(s) published successfully.'
        )
    publish_events.short_description = 'Publish selected events'
    
    def close_events(self, request, queryset):
        """Bulk close events."""
        count = 0
        for event in queryset.filter(status='published'):
            if event.can_transition_to('closed'):
                event.status = 'closed'
                event.save()
                count += 1
        
        self.message_user(
            request,
            f'{count} event(s) closed successfully.'
        )
    close_events.short_description = 'Close selected events'
    
    def finish_events(self, request, queryset):
        """Bulk finish events."""
        count = 0
        for event in queryset.filter(status='closed'):
            if event.can_transition_to('finished'):
                event.status = 'finished'
                event.save()
                count += 1
        
        self.message_user(
            request,
            f'{count} event(s) marked as finished.'
        )
    finish_events.short_description = 'Finish selected events'


class StageRoleInline(admin.TabularInline):
    """Inline admin for stage roles."""
    model = StageRole
    extra = 1
    fields = [
        'role_type',
        'name',
        'bio',
        'profile_image'
    ]


@admin.register(EventStage)
class EventStageAdmin(admin.ModelAdmin):
    """Admin interface for EventStage model."""
    
    list_display = [
        'get_event_title',
        'order',
        'title',
        'start_datetime',
        'end_datetime'
    ]
    
    list_filter = ['event', 'created_at']
    search_fields = ['title', 'description', 'event__title']
    ordering = ['event', 'order']
    
    inlines = [StageRoleInline]
    
    def get_event_title(self, obj):
        """Get event title."""
        return obj.event.title
    get_event_title.short_description = 'Event'
    get_event_title.admin_order_field = 'event__title'


@admin.register(StageRole)
class StageRoleAdmin(admin.ModelAdmin):
    """Admin interface for StageRole model."""
    
    list_display = [
        'name',
        'role_type',
        'get_stage',
        'get_event'
    ]
    
    list_filter = ['role_type', 'created_at']
    search_fields = [
        'name',
        'bio',
        'stage__title',
        'stage__event__title'
    ]
    
    def get_stage(self, obj):
        """Get stage title."""
        return obj.stage.title
    get_stage.short_description = 'Stage'
    
    def get_event(self, obj):
        """Get event title."""
        return obj.stage.event.title
    get_event.short_description = 'Event'


@admin.register(AttributeDefinition)
class AttributeDefinitionAdmin(admin.ModelAdmin):
    """Admin interface for AttributeDefinition model."""
    
    list_display = [
        'display_name',
        'name',
        'data_type',
        'is_required'
    ]
    
    list_filter = ['data_type', 'is_required']
    search_fields = ['name', 'display_name', 'description']
    ordering = ['display_name']


@admin.register(EventAttributeValue)
class EventAttributeValueAdmin(admin.ModelAdmin):
    """Admin interface for EventAttributeValue model."""
    
    list_display = [
        'get_event_title',
        'get_attribute_name',
        'display_value'
    ]
    
    list_filter = ['attribute', 'created_at']
    search_fields = ['event__title', 'attribute__display_name']
    
    def get_event_title(self, obj):
        """Get event title."""
        return obj.event.title
    get_event_title.short_description = 'Event'
    
    def get_attribute_name(self, obj):
        """Get attribute name."""
        return obj.attribute.display_name
    get_attribute_name.short_description = 'Attribute'
    
    def display_value(self, obj):
        """Display the value."""
        return obj.get_value()
    display_value.short_description = 'Value'


@admin.register(EventResult)
class EventResultAdmin(admin.ModelAdmin):
    """Admin interface for EventResult model."""
    
    list_display = [
        'get_event_title',
        'title',
        'published_at'
    ]
    
    list_filter = ['published_at']
    search_fields = ['event__title', 'title', 'content']
    readonly_fields = ['published_at', 'created_at', 'updated_at']
    
    def get_event_title(self, obj):
        """Get event title."""
        return obj.event.title
    get_event_title.short_description = 'Event'