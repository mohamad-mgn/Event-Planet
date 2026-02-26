"""
Views for the Events app.

This module contains API views for event management:
- EventListView: List all published events
- EventDetailView: Get single event details
- EventCreateView: Create new event (organizers only)
- EventUpdateView: Update event (owner only)
- EventDeleteView: Delete event (owner only)
- MyEventsView: List user's organized events
- EventPublishView: Publish event
- EventCloseView: Close event registration

Author: Event Planet Team
Created: 2026-02-15
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Q, Count
from django.utils import timezone
from .models import Event
from .serializers import (
    EventSerializer,
    EventListSerializer,
    EventCreateSerializer,
    EventUpdateSerializer
)
from apps.core.permissions import IsOrganizer, IsEventOrganizer


class EventListView(generics.ListAPIView):
    """
    API view to list all published events.
    
    Public endpoint that shows all published events with filtering
    and search capabilities.
    
    Endpoint: GET /api/events/public/
    
    Query Parameters:
        - category: Filter by category ID
        - search: Search in title and description
        - is_online: Filter online/offline events (true/false)
        - upcoming: Show only upcoming events (true/false)
        - status: Filter by status (published/closed/finished)
    
    Response (Success - 200):
        {
            "success": true,
            "data": [
                {
                    "id": 1,
                    "title": "Tech Conference 2026",
                    "slug": "tech-conference-2026",
                    "category": {...},
                    "organizer_name": "John Doe",
                    "start_datetime": "2026-03-15T10:00:00Z",
                    ...
                },
                ...
            ]
        }
    
    Permissions:
        - AllowAny: Public endpoint
    """
    
    serializer_class = EventListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Get queryset with filters.
        
        Returns:
            QuerySet: Filtered events
        """
        queryset = Event.objects.filter(
            status='published'
        ).select_related(
            'category',
            'organizer'
        ).order_by('-start_datetime')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Search in title and description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Filter by online/offline
        is_online = self.request.query_params.get('is_online')
        if is_online == 'true':
            queryset = queryset.filter(is_online=True)
        elif is_online == 'false':
            queryset = queryset.filter(is_online=False)
        
        # Filter upcoming events
        if self.request.query_params.get('upcoming') == 'true':
            queryset = queryset.filter(
                start_datetime__gte=timezone.now()
            )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """List events with custom response format."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class EventDetailView(generics.RetrieveAPIView):
    """
    API view to get single event details.
    
    Returns complete event information including stages,
    attributes, and results.
    
    Endpoint: GET /api/events/{id}/
    
    Response (Success - 200):
        {
            "success": true,
            "data": {
                "id": 1,
                "title": "Tech Conference 2026",
                "description": "...",
                "organizer": {...},
                "category": {...},
                "stages": [...],
                "attribute_values": [...],
                ...
            }
        }
    
    Permissions:
        - AllowAny: Public endpoint
    """
    
    serializer_class = EventSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Get queryset with related data."""
        return Event.objects.filter(
            status__in=['published', 'closed', 'finished']
        ).select_related(
            'category',
            'organizer'
        ).prefetch_related(
            'stages',
            'stages__roles',
            'attribute_values',
            'attribute_values__attribute',
            'results'
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve event and increment view count."""
        instance = self.get_object()
        
        # Increment view count
        instance.increment_views()
        
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class EventCreateView(generics.CreateAPIView):
    """
    API view to create new event.
    
    Only organizers can create events.
    
    Endpoint: POST /api/events/create/
    
    Request Body:
        {
            "title": "My Event",
            "description": "Event description",
            "category_id": 1,
            "start_datetime": "2026-03-15T10:00:00Z",
            "end_datetime": "2026-03-15T18:00:00Z",
            "location": "Tehran",
            "is_online": false,
            "capacity": 100
        }
    
    Response (Success - 201):
        {
            "success": true,
            "message": "Event created successfully",
            "data": {...}
        }
    
    Permissions:
        - IsAuthenticated
        - IsOrganizer: User must have organizer role
    """
    
    serializer_class = EventCreateSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]
    
    def create(self, request, *args, **kwargs):
        """Create event with custom response."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        
        # Return full event data
        event_serializer = EventSerializer(event)
        
        return Response({
            'success': True,
            'message': 'Event created successfully',
            'data': event_serializer.data
        }, status=status.HTTP_201_CREATED)


class EventUpdateView(generics.UpdateAPIView):
    """
    API view to update event.
    
    Only event organizer can update.
    
    Endpoints:
        PUT /api/events/{id}/update/
        PATCH /api/events/{id}/update/
    
    Permissions:
        - IsAuthenticated
        - IsEventOrganizer: User must be event organizer
    """
    
    serializer_class = EventUpdateSerializer
    permission_classes = [IsAuthenticated, IsEventOrganizer]
    lookup_field = 'pk'
    
    def get_queryset(self):
        """Get user's events only."""
        return Event.objects.filter(organizer=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """Update event with custom response."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        
        # Return full event data
        event_serializer = EventSerializer(event)
        
        return Response({
            'success': True,
            'message': 'Event updated successfully',
            'data': event_serializer.data
        })


class EventDeleteView(generics.DestroyAPIView):
    """
    API view to delete event.
    
    Only event organizer can delete.
    Only draft events can be deleted.
    
    Endpoint: DELETE /api/events/{id}/delete/
    
    Response (Success - 200):
        {
            "success": true,
            "message": "Event deleted successfully"
        }
    
    Permissions:
        - IsAuthenticated
        - IsEventOrganizer
    """
    
    permission_classes = [IsAuthenticated, IsEventOrganizer]
    lookup_field = 'pk'
    
    def get_queryset(self):
        """Get user's draft events only."""
        return Event.objects.filter(
            organizer=self.request.user,
            status='draft'
        )
    
    def destroy(self, request, *args, **kwargs):
        """Delete event with custom response."""
        instance = self.get_object()
        instance.delete()
        
        return Response({
            'success': True,
            'message': 'Event deleted successfully'
        })


class MyEventsView(generics.ListAPIView):
    """
    API view to list user's organized events.
    
    Shows all events created by the authenticated user.
    
    Endpoint: GET /api/events/my-events/
    
    Response (Success - 200):
        {
            "success": true,
            "data": [...]
        }
    
    Permissions:
        - IsAuthenticated
        - IsOrganizer
    """
    
    serializer_class = EventListSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]
    
    def get_queryset(self):
        """Get user's events."""
        return Event.objects.filter(
            organizer=self.request.user
        ).select_related(
            'category',
            'organizer'
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """List user's events."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class EventPublishView(APIView):
    """
    API view to publish event.
    
    Changes event status from draft to published.
    
    Endpoint: POST /api/events/{id}/publish/
    
    Response (Success - 200):
        {
            "success": true,
            "message": "Event published successfully",
            "data": {...}
        }
    
    Permissions:
        - IsAuthenticated
        - IsEventOrganizer
    """
    
    permission_classes = [IsAuthenticated, IsEventOrganizer]
    
    def post(self, request, pk):
        """Publish event."""
        try:
            event = Event.objects.get(pk=pk, organizer=request.user)
        except Event.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'message': 'Event not found',
                    'status_code': 404
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if can transition to published
        if not event.can_transition_to('published'):
            return Response({
                'success': False,
                'error': {
                    'message': f'Cannot publish event with status: {event.status}',
                    'status_code': 400
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Publish event
        event.publish()
        
        # Return updated event data
        serializer = EventSerializer(event)
        
        return Response({
            'success': True,
            'message': 'Event published successfully',
            'data': serializer.data
        })


class EventCloseView(APIView):
    """
    API view to close event registration.
    
    Changes event status from published to closed.
    
    Endpoint: POST /api/events/{id}/close/
    
    Permissions:
        - IsAuthenticated
        - IsEventOrganizer
    """
    
    permission_classes = [IsAuthenticated, IsEventOrganizer]
    
    def post(self, request, pk):
        """Close event registration."""
        try:
            event = Event.objects.get(pk=pk, organizer=request.user)
        except Event.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'message': 'Event not found',
                    'status_code': 404
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if can close
        if not event.can_transition_to('closed'):
            return Response({
                'success': False,
                'error': {
                    'message': f'Cannot close event with status: {event.status}',
                    'status_code': 400
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Close registration
        event.close_registration()
        
        serializer = EventSerializer(event)
        
        return Response({
            'success': True,
            'message': 'Event registration closed successfully',
            'data': serializer.data
        })