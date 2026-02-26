"""
Views for the Categories app.

This module contains API views for category management:
- CategoryListView: List all active categories
- CategoryDetailView: Get single category details

All views are public (no authentication required) since categories
are reference data available to all users.

Author: Event Planet Team
Created: 2026-02-15
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Count, Q
from django.utils import timezone
from .models import Category
from .serializers import (
    CategoryListSerializer,
    CategoryDetailSerializer
)


class CategoryListView(generics.ListAPIView):
    """
    API view to list all active categories.
    
    Returns a list of all active categories with event counts.
    Categories are ordered alphabetically by name.
    
    Endpoint: GET /api/categories/
    
    Query Parameters:
        - active_only (bool): Filter only categories with active events (optional)
        - has_events (bool): Filter only categories with events (optional)
    
    Response (Success - 200):
        {
            "success": true,
            "data": [
                {
                    "id": 1,
                    "name": "Technology & Science",
                    "slug": "technology-science",
                    "icon": "💻",
                    "events_count": 42
                },
                {
                    "id": 2,
                    "name": "Sports & Fitness",
                    "slug": "sports-fitness",
                    "icon": "⚽",
                    "events_count": 28
                },
                ...
            ]
        }
    
    Permissions:
        - AllowAny: Public endpoint, no authentication required
    
    Examples:
        GET /api/categories/
        GET /api/categories/?active_only=true
        GET /api/categories/?has_events=true
    """
    
    # Use list serializer for minimal data
    serializer_class = CategoryListSerializer
    
    # Public endpoint - no authentication required
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Get queryset with optimized event counting.
        
        Uses annotation to efficiently count events for each category
        in a single database query.
        
        Returns:
            QuerySet: Categories with annotated event counts
        
        Filters:
            - Only active categories
            - Optional: Only categories with events
            - Optional: Only categories with active events
        """
        queryset = Category.objects.filter(is_active=True)
        
        # Annotate with event count (published events only)
        queryset = queryset.annotate(
            events_count=Count(
                'events',
                filter=Q(events__status='published')
            )
        )
        
        # Optional filter: only categories with events
        if self.request.query_params.get('has_events') == 'true':
            queryset = queryset.filter(events_count__gt=0)
        
        # Optional filter: only categories with active events
        if self.request.query_params.get('active_only') == 'true':
            now = timezone.now()
            queryset = queryset.annotate(
                active_events_count=Count(
                    'events',
                    filter=Q(
                        events__status='published',
                        events__end_datetime__gte=now
                    )
                )
            ).filter(active_events_count__gt=0)
        
        return queryset.order_by('name')
    
    def list(self, request, *args, **kwargs):
        """
        List all categories with custom response format.
        
        Args:
            request: HTTP request object
        
        Returns:
            Response: Formatted response with category list
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class CategoryDetailView(generics.RetrieveAPIView):
    """
    API view to get single category details.
    
    Returns detailed information about a specific category,
    including statistics and description.
    
    Endpoint: GET /api/categories/{id}/
    
    Path Parameters:
        - id: Category ID or slug
    
    Response (Success - 200):
        {
            "success": true,
            "data": {
                "id": 1,
                "name": "Technology & Science",
                "slug": "technology-science",
                "icon": "💻",
                "description": "Events about technology, science, and innovation",
                "is_active": true,
                "events_count": 42,
                "active_events_count": 15,
                "created_at": "2026-02-15T10:00:00Z",
                "updated_at": "2026-02-15T10:00:00Z"
            }
        }
    
    Response (Error - 404):
        {
            "success": false,
            "error": {
                "message": "Category not found",
                "status_code": 404
            }
        }
    
    Permissions:
        - AllowAny: Public endpoint, no authentication required
    
    Examples:
        GET /api/categories/1/
        GET /api/categories/technology-science/
    """
    
    # Use detail serializer for full information
    serializer_class = CategoryDetailSerializer
    
    # Public endpoint
    permission_classes = [AllowAny]
    
    # Allow lookup by ID or slug
    lookup_field = 'pk'
    
    def get_queryset(self):
        """
        Get queryset with event statistics.
        
        Returns:
            QuerySet: Categories with annotated statistics
        """
        now = timezone.now()
        
        return Category.objects.filter(
            is_active=True
        ).annotate(
            # Total published events count
            events_count=Count(
                'events',
                filter=Q(events__status='published')
            ),
            # Active (upcoming) events count
            active_events_count=Count(
                'events',
                filter=Q(
                    events__status='published',
                    events__end_datetime__gte=now
                )
            )
        )
    
    def get_object(self):
        """
        Get category by ID or slug.
        
        Allows fetching category by either primary key or slug.
        
        Returns:
            Category: Category instance
        
        Raises:
            Http404: If category not found
        """
        queryset = self.get_queryset()
        lookup_value = self.kwargs.get(self.lookup_field)
        
        # Try to get by ID first
        try:
            lookup_value = int(lookup_value)
            return queryset.get(pk=lookup_value)
        except (ValueError, TypeError):
            # If not a valid integer, try slug
            return queryset.get(slug=lookup_value)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve category details with custom response format.
        
        Args:
            request: HTTP request object
        
        Returns:
            Response: Formatted response with category details
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'data': serializer.data
        })