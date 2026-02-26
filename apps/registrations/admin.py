"""
Admin configuration for Registrations app.

This module configures the Django admin interface for Registration model.

Features:
- List view with event, participant, status, check-in info
- Filtering by status, event, check-in status
- Search by participant and event
- Bulk check-in and status change actions
- Event and participant details display

Author: Event Planet Team
Created: 2026-02-15
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    """
    Admin interface for Registration model.
    
    Provides comprehensive registration management with:
    - List view with key information
    - Filtering by status, event, dates
    - Search by participant and event
    - Bulk actions for status changes
    - Check-in management
    """
    
    # Fields to display in list view
    list_display = [
        'get_participant_name',
        'get_event_title',
        'status_badge',
        'checked_in_badge',
        'created_at'
    ]
    
    # Filters in sidebar
    list_filter = [
        'status',
        'checked_in',
        'created_at',
        'event__start_datetime'
    ]
    
    # Search fields
    search_fields = [
        'participant__phone_number',
        'participant__full_name',
        'event__title',
        'notes'
    ]
    
    # Default ordering (newest first)
    ordering = ['-created_at']
    
    # Read-only fields
    readonly_fields = [
        'created_at',
        'updated_at',
        'checked_in_at',
        'cancelled_at'
    ]
    
    # Fieldsets for detailed view
    fieldsets = (
        # Basic Information
        ('Registration Information', {
            'fields': (
                'event',
                'participant',
                'status',
                'notes'
            )
        }),
        
        # Check-in Information
        ('Check-in', {
            'fields': (
                'checked_in',
                'checked_in_at'
            )
        }),
        
        # Cancellation Information
        ('Cancellation', {
            'fields': (
                'cancelled_at',
                'cancellation_reason'
            ),
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
    
    def get_participant_name(self, obj):
        """
        Display participant name with link to user admin.
        
        Args:
            obj (Registration): Registration instance
        
        Returns:
            str: HTML with participant name link
        """
        url = f'/admin/accounts/user/{obj.participant.id}/change/'
        return format_html(
            '<a href="{}" style="color: #007bff;">{}</a>',
            url,
            obj.participant.full_name or obj.participant.phone_number
        )
    
    get_participant_name.short_description = 'Participant'
    get_participant_name.admin_order_field = 'participant__full_name'
    
    def get_event_title(self, obj):
        """
        Display event title with link to event admin.
        
        Args:
            obj (Registration): Registration instance
        
        Returns:
            str: HTML with event title link
        """
        url = f'/admin/events/event/{obj.event.id}/change/'
        return format_html(
            '<a href="{}" style="color: #007bff;">{}</a>',
            url,
            obj.event.title
        )
    
    get_event_title.short_description = 'Event'
    get_event_title.admin_order_field = 'event__title'
    
    def status_badge(self, obj):
        """
        Display status as colored badge.
        
        Args:
            obj (Registration): Registration instance
        
        Returns:
            str: HTML badge showing status
        """
        colors = {
            'pending': '#ffc107',
            'confirmed': '#28a745',
            'cancelled': '#dc3545',
            'rejected': '#6c757d',
        }
        
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    
    status_badge.short_description = 'Status'
    
    def checked_in_badge(self, obj):
        """
        Display check-in status as badge.
        
        Args:
            obj (Registration): Registration instance
        
        Returns:
            str: HTML badge showing check-in status
        """
        if obj.checked_in:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 10px; border-radius: 3px;">✓ Checked In</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6c757d; color: white; '
                'padding: 3px 10px; border-radius: 3px;">Not Checked In</span>'
            )
    
    checked_in_badge.short_description = 'Check-in Status'
    
    # Custom admin actions
    actions = [
        'confirm_registrations',
        'cancel_registrations',
        'check_in_participants'
    ]
    
    def confirm_registrations(self, request, queryset):
        """
        Bulk action to confirm registrations.
        
        Args:
            request: HTTP request
            queryset: Selected registrations
        """
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(
            request,
            f'{updated} registration(s) confirmed successfully.'
        )
    confirm_registrations.short_description = 'Confirm selected registrations'
    
    def cancel_registrations(self, request, queryset):
        """
        Bulk action to cancel registrations.
        
        Args:
            request: HTTP request
            queryset: Selected registrations
        """
        from django.utils import timezone
        
        count = 0
        for registration in queryset.filter(status__in=['pending', 'confirmed']):
            if registration.can_cancel:
                registration.status = 'cancelled'
                registration.cancelled_at = timezone.now()
                registration.save()
                count += 1
        
        self.message_user(
            request,
            f'{count} registration(s) cancelled successfully.'
        )
    cancel_registrations.short_description = 'Cancel selected registrations'
    
    def check_in_participants(self, request, queryset):
        """
        Bulk action to check in participants.
        
        Args:
            request: HTTP request
            queryset: Selected registrations
        """
        count = 0
        for registration in queryset.filter(status='confirmed', checked_in=False):
            if registration.check_in_participant():
                count += 1
        
        self.message_user(
            request,
            f'{count} participant(s) checked in successfully.'
        )
    check_in_participants.short_description = 'Check in selected participants'
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related.
        
        Args:
            request: HTTP request
        
        Returns:
            QuerySet: Optimized queryset
        """
        queryset = super().get_queryset(request)
        
        # Use select_related for efficient queries
        queryset = queryset.select_related(
            'event',
            'participant'
        )
        
        return queryset