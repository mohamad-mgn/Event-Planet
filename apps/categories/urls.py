"""
URL configuration for Categories app.

This module defines URL patterns for category-related endpoints.

Endpoints:
    - GET /api/categories/ - List all categories
    - GET /api/categories/{id}/ - Get category details

All endpoints are public (no authentication required).

Author: Event Planet Team
Created: 2026-02-15
"""

from django.urls import path
from .views import (
    CategoryListView,
    CategoryDetailView
)

# App namespace for URL reversing
app_name = 'categories'

urlpatterns = [
    # ----------------------------------------------------------------------
    # Category listing endpoint
    # ----------------------------------------------------------------------
    
    # List all active categories
    # GET /api/categories/
    # Public endpoint - no authentication required
    # Optional query params: ?has_events=true, ?active_only=true
    path(
        '',
        CategoryListView.as_view(),
        name='category-list'
    ),
    
    # ----------------------------------------------------------------------
    # Category detail endpoint
    # ----------------------------------------------------------------------
    
    # Get single category details
    # GET /api/categories/{id}/
    # GET /api/categories/{slug}/
    # Public endpoint - no authentication required
    # Supports lookup by ID or slug
    path(
        '<str:pk>/',
        CategoryDetailView.as_view(),
        name='category-detail'
    ),
]