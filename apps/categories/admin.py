"""
Admin configuration for Categories app.

This module configures the Django admin interface for Category model.
Provides an interface for managing event categories.

Features:
- List view with name, icon, event count, active status
- Search by name and description
- Filter by active status
- Inline statistics display
- Custom actions for bulk operations

Author: Event Planet Team
Created: 2026-02-15
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Category model.
    
    Provides comprehensive category management with statistics
    and bulk operations.
    
    Features:
        - List view with icon preview and event counts
        - Search by name and description
        - Filter by active status
        - Auto-generated slug field
        - Event count display
        - Bulk activate/deactivate actions
    """
    
    # Fields to display in list view
    list_display = [
        'icon_preview',
        'name',
        'slug',
        'get_events_count',
        'is_active_badge',
        'created_at'
    ]
    
    # Filters in sidebar
    list_filter = [
        'is_active',
        'created_at'
    ]
    
    # Search fields
    search_fields = [
        'name',
        'description'
    ]
    
    # Prepopulated fields (slug from name)
    prepopulated_fields = {
        'slug': ('name',)
    }
    
    # Default ordering (alphabetical)
    ordering = ['name']
    
    # Read-only fields
    readonly_fields = [
        'created_at',
        'updated_at',
        'get_events_count'
    ]
    
    # Fieldsets for detailed view
    fieldsets = (
        # Basic Information
        ('Basic Information', {
            'fields': (
                'name',
                'slug',
                'icon'
            )
        }),
        
        # Description
        ('Description', {
            'fields': ('description',)
        }),
        
        # Status & Statistics
        ('Status & Statistics', {
            'fields': (
                'is_active',
                'get_events_count'
            )
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
    
    def icon_preview(self, obj):
        """
        Display category icon in list view.
        
        Args:
            obj (Category): Category instance
        
        Returns:
            str: HTML with icon or placeholder
        """
        if obj.icon:
            return format_html(
                '<span style="font-size: 24px;">{}</span>',
                obj.icon
            )
        return format_html(
            '<span style="color: #ccc;">No icon</span>'
        )
    
    # Set column header
    icon_preview.short_description = 'Icon'
    
    def is_active_badge(self, obj):
        """
        Display active status as a colored badge.
        
        Args:
            obj (Category): Category instance
        
        Returns:
            str: HTML badge showing active status
        """
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 10px; border-radius: 3px;">✓ Active</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6c757d; color: white; '
                'padding: 3px 10px; border-radius: 3px;">✗ Inactive</span>'
            )
    
    # Set column header
    is_active_badge.short_description = 'Status'
    
    def get_events_count(self, obj):
        """
        Display number of events in category.
        
        Shows count with a link to filter events by category.
        
        Args:
            obj (Category): Category instance
        
        Returns:
            str: HTML with event count
        """
        count = obj.events.filter(status='published').count()
        
        if count > 0:
            # Link to events filtered by this category
            url = f'/admin/events/event/?category__id__exact={obj.id}'
            return format_html(
                '<a href="{}" style="color: #007bff;">{} events</a>',
                url,
                count
            )
        else:
            return format_html(
                '<span style="color: #6c757d;">0 events</span>'
            )
    
    # Set column header
    get_events_count.short_description = 'Events'
    
    def get_queryset(self, request):
        """
        Optimize queryset with event count annotation.
        
        Uses annotation to efficiently count events in a single query.
        
        Args:
            request: HTTP request
        
        Returns:
            QuerySet: Optimized queryset with event counts
        """
        queryset = super().get_queryset(request)
        
        # Annotate with event count for efficient display
        queryset = queryset.annotate(
            total_events=Count('events')
        )
        
        return queryset
    
    # Custom admin actions
    actions = ['activate_categories', 'deactivate_categories']
    
    def activate_categories(self, request, queryset):
        """
        Bulk action to activate selected categories.
        
        Args:
            request: HTTP request
            queryset: Selected categories
        """
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} category(ies) were successfully activated.'
        )
    activate_categories.short_description = 'Activate selected categories'
    
    def deactivate_categories(self, request, queryset):
        """
        Bulk action to deactivate selected categories.
        
        Args:
            request: HTTP request
            queryset: Selected categories
        """
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} category(ies) were successfully deactivated.'
        )
    deactivate_categories.short_description = 'Deactivate selected categories'