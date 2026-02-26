"""
Views for the Registrations app.

This module contains API views for registration management:
- RegistrationCreateView: Create new registration
- MyRegistrationsView: List user's registrations
- RegistrationDetailView: Get registration details
- CancelRegistrationView: Cancel registration
- CheckInView: Check in participant (organizers only)

Author: Event Planet Team
Created: 2026-02-15
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Registration
from .serializers import (
    RegistrationSerializer,
    RegistrationCreateSerializer,
    RegistrationListSerializer,
    CancelRegistrationSerializer,
    CheckInSerializer
)
from apps.core.permissions import IsParticipant, IsEventOrganizer


class RegistrationCreateView(generics.CreateAPIView):
    """
    API view to create new registration.
    
    Allows participants to register for events.
    
    Endpoint: POST /api/registrations/create/
    
    Request Body:
        {
            "event_id": 1,
            "notes": "Any questions or special requirements"
        }
    
    Response (Success - 201):
        {
            "success": true,
            "message": "Registration successful",
            "data": {...}
        }
    
    Permissions:
        - IsAuthenticated
        - IsParticipant: User must have participant role
    """
    
    serializer_class = RegistrationCreateSerializer
    permission_classes = [IsAuthenticated, IsParticipant]
    
    def create(self, request, *args, **kwargs):
        """Create registration with custom response."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registration = serializer.save()
        
        # Return full registration data
        registration_serializer = RegistrationSerializer(registration)
        
        return Response({
            'success': True,
            'message': 'Registration successful',
            'data': registration_serializer.data
        }, status=status.HTTP_201_CREATED)


class MyRegistrationsView(generics.ListAPIView):
    """
    API view to list user's registrations.
    
    Shows all registrations for the authenticated user.
    
    Endpoint: GET /api/registrations/my-registrations/
    
    Query Parameters:
        - status: Filter by status (confirmed/cancelled/pending)
        - upcoming: Show only upcoming events (true/false)
    
    Response (Success - 200):
        {
            "success": true,
            "data": [...]
        }
    
    Permissions:
        - IsAuthenticated
        - IsParticipant
    """
    
    serializer_class = RegistrationListSerializer
    permission_classes = [IsAuthenticated, IsParticipant]
    
    def get_queryset(self):
        """Get user's registrations with filters."""
        queryset = Registration.objects.filter(
            participant=self.request.user
        ).select_related('event', 'event__category').order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter upcoming events
        if self.request.query_params.get('upcoming') == 'true':
            from django.utils import timezone
            queryset = queryset.filter(
                event__start_datetime__gte=timezone.now()
            )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """List user's registrations."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class RegistrationDetailView(generics.RetrieveAPIView):
    """
    API view to get registration details.
    
    Shows full details of a specific registration.
    
    Endpoint: GET /api/registrations/{id}/
    
    Response (Success - 200):
        {
            "success": true,
            "data": {...}
        }
    
    Permissions:
        - IsAuthenticated
        - IsParticipant (own registrations only)
    """
    
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated, IsParticipant]
    
    def get_queryset(self):
        """Get user's registrations only."""
        return Registration.objects.filter(
            participant=self.request.user
        ).select_related('event', 'participant')
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve registration details."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class CancelRegistrationView(generics.UpdateAPIView):
    """
    API view to cancel registration.
    
    Allows participants to cancel their registration.
    
    Endpoint: POST /api/registrations/{id}/cancel/
    
    Request Body:
        {
            "cancellation_reason": "Cannot attend due to..."
        }
    
    Response (Success - 200):
        {
            "success": true,
            "message": "Registration cancelled successfully",
            "data": {...}
        }
    
    Permissions:
        - IsAuthenticated
        - IsParticipant (own registrations only)
    """
    
    serializer_class = CancelRegistrationSerializer
    permission_classes = [IsAuthenticated, IsParticipant]
    
    def get_queryset(self):
        """Get user's registrations only."""
        return Registration.objects.filter(
            participant=self.request.user
        )
    
    def update(self, request, *args, **kwargs):
        """Cancel registration."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        registration = serializer.save()
        
        # Return updated registration
        registration_serializer = RegistrationSerializer(registration)
        
        return Response({
            'success': True,
            'message': 'Registration cancelled successfully',
            'data': registration_serializer.data
        })


class CheckInView(APIView):
    """
    API view to check in participants.
    
    Allows event organizers to mark participants as checked in.
    
    Endpoint: POST /api/registrations/{id}/check-in/
    
    Response (Success - 200):
        {
            "success": true,
            "message": "Participant checked in successfully",
            "data": {...}
        }
    
    Permissions:
        - IsAuthenticated
        - IsEventOrganizer (event owner only)
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """Check in participant."""
        registration = get_object_or_404(Registration, pk=pk)
        
        # Check if user is event organizer
        if registration.event.organizer != request.user:
            return Response({
                'success': False,
                'error': {
                    'message': 'You do not have permission to check in participants for this event.',
                    'status_code': 403
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check in participant
        serializer = CheckInSerializer(registration, data={})
        serializer.is_valid(raise_exception=True)
        registration = serializer.save()
        
        # Return updated registration
        registration_serializer = RegistrationSerializer(registration)
        
        return Response({
            'success': True,
            'message': 'Participant checked in successfully',
            'data': registration_serializer.data
        })