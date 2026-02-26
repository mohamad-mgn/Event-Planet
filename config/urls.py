"""
URL Configuration for Event Planet project.

This module defines the main URL routing for the entire project.
It includes:
- Admin interface routes
- API routes for all apps
- API documentation (Swagger/ReDoc)
- Static and media file serving (development only)

The API is versioned and all endpoints are prefixed with /api/

Author: Event Planet Team
Created: 2026-02-15
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

# ----------------------------------------------------------------------
# URL Patterns
# ----------------------------------------------------------------------
urlpatterns = [
    # ----------------------------------------------------------------------
    # Admin interface
    # ----------------------------------------------------------------------
    # Django admin panel for managing data
    # Access at: http://localhost:8000/admin/
    path('admin/', admin.site.urls),
    
    # ----------------------------------------------------------------------
    # API Documentation
    # ----------------------------------------------------------------------
    # OpenAPI schema endpoint (JSON format)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Swagger UI - Interactive API documentation
    # Access at: http://localhost:8000/api/docs/
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # ReDoc UI - Alternative API documentation
    # Access at: http://localhost:8000/api/redoc/
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # ----------------------------------------------------------------------
    # API Endpoints
    # ----------------------------------------------------------------------
    # All API endpoints are prefixed with /api/
    
    # Accounts API - Authentication, user management, OTP
    # Includes: /api/accounts/auth/, /api/accounts/profile/, etc.
    path('api/accounts/', include('apps.accounts.urls')),
    
    # Categories API - Event category management
    # Includes: /api/categories/
    path('api/categories/', include('apps.categories.urls')),
    
    # Events API - Event creation, management, stages
    # Includes: /api/events/, /api/events/public/, etc.
    path('api/events/', include('apps.events.urls')),
    
    # Registrations API - Event registration management
    # Includes: /api/registrations/create/, /api/registrations/my-registrations/
    path('api/registrations/', include('apps.registrations.urls')),
    
    # Feedback API - Event feedback and ratings
    # Includes: /api/feedback/create/, /api/feedback/event/<id>/
    path('api/feedback/', include('apps.feedback.urls')),
]

# ----------------------------------------------------------------------
# Static and Media files (Development only)
# ----------------------------------------------------------------------
# Serve static and media files during development
# In production, these should be served by a web server (Nginx, Apache)
if settings.DEBUG:
    # Serve media files (user uploads)
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    
    # Serve static files (CSS, JS, images)
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
    
    # Django Debug Toolbar (only in development)
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# ----------------------------------------------------------------------
# Admin site customization
# ----------------------------------------------------------------------
# Customize admin panel header and title
admin.site.site_header = 'Event Planet Admin'
admin.site.site_title = 'Event Planet Admin Portal'
admin.site.index_title = 'Welcome to Event Planet Admin'