"""
Models for the Categories app.

This module defines the Category model for event categorization.
Categories help users find and filter events based on type.

Categories are predefined and managed by administrators.
Each event must belong to exactly one category.

Author: Event Planet Team
Created: 2026-02-15
"""

from django.db import models
from django.utils.text import slugify
from apps.core.models import TimeStampedModel


class Category(TimeStampedModel):
    """
    Category model for event classification.
    
    Categories organize events into logical groups (e.g., Sports, Music, Education).
    Each category has a name, slug, icon, and optional description.
    
    Fields:
        name: Category name (e.g., "Technology & Science")
        slug: URL-friendly version of name (auto-generated)
        icon: Emoji or icon for visual representation
        description: Optional detailed description
        is_active: Whether category is available for use
    
    Inherited from TimeStampedModel:
        created_at: Category creation timestamp
        updated_at: Last update timestamp
    
    Examples:
        >>> tech = Category.objects.create(
        ...     name="Technology & Science",
        ...     icon="💻",
        ...     description="Tech events, conferences, hackathons"
        ... )
        >>> print(tech.slug)
        'technology-science'
    """
    
    # Category name (unique)
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Category Name',
        help_text='Unique name for the category (e.g., Technology & Science)'
    )
    
    # URL-friendly slug (auto-generated from name)
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name='Slug',
        help_text='URL-friendly version of name (auto-generated)'
    )
    
    # Icon or emoji for visual representation
    icon = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Icon',
        help_text='Emoji or icon character (e.g., 💻, 🎨, ⚽)'
    )
    
    # Optional description
    description = models.TextField(
        blank=True,
        verbose_name='Description',
        help_text='Detailed description of this category'
    )
    
    # Active status (allows soft deactivation)
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active',
        help_text='Whether this category is available for use'
    )
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']  # Alphabetical ordering
        indexes = [
            models.Index(fields=['name']),  # Index for faster lookups
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        """
        String representation of category.
        
        Returns:
            str: Category name with icon (if available)
        
        Examples:
            >>> str(category)
            '💻 Technology & Science'
        """
        if self.icon:
            return f"{self.icon} {self.name}"
        return self.name
    
    def save(self, *args, **kwargs):
        """
        Override save method to auto-generate slug.
        
        Automatically creates a URL-friendly slug from the category name
        if slug is not provided.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        
        Examples:
            >>> category = Category(name="Technology & Science")
            >>> category.save()
            >>> print(category.slug)
            'technology-science'
        """
        # Auto-generate slug from name if not provided
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Call parent save method
        super().save(*args, **kwargs)
    
    @property
    def events_count(self):
        """
        Get number of events in this category.
        
        Returns count of active (published) events only.
        
        Returns:
            int: Number of published events in this category
        
        Examples:
            >>> category.events_count
            42
        
        Note:
            This is a property that executes a database query.
            For performance, consider using annotations when
            retrieving multiple categories.
        """
        return self.events.filter(status='published').count()
    
    @property
    def active_events_count(self):
        """
        Get number of active events (not finished or archived).
        
        Returns:
            int: Number of active events in this category
        
        Examples:
            >>> category.active_events_count
            15
        """
        from django.utils import timezone
        return self.events.filter(
            status='published',
            end_datetime__gte=timezone.now()
        ).count()
    
    def get_popular_events(self, limit=5):
        """
        Get most popular events in this category.
        
        Returns events sorted by views count or registration count.
        
        Args:
            limit (int): Maximum number of events to return (default: 5)
        
        Returns:
            QuerySet: Popular events in this category
        
        Examples:
            >>> popular = category.get_popular_events(limit=10)
            >>> for event in popular:
            ...     print(event.title, event.views_count)
        """
        return self.events.filter(
            status='published'
        ).order_by('-views_count')[:limit]