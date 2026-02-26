"""
Views for the Feedback app.

This module contains API views for feedback management:
- FeedbackCreateView: Create new feedback
- FeedbackListView: List event feedbacks
- MyFeedbacksView: List user's feedbacks
- FeedbackDetailView: Get feedback details
- FeedbackUpdateView: Update feedback
- FeedbackDeleteView: Delete feedback
- OrganizerResponseView: Add organizer response
- EventFeedbackStatsView: Get event feedback statistics

Author: Event Planet Team
Created: 2026-02-15
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from .models import Feedback
from .serializers import (
    FeedbackSerializer,
    FeedbackCreateSerializer,
    FeedbackListSerializer,
    FeedbackUpdateSerializer,
    OrganizerResponseSerializer
)
from apps.core.permissions import IsParticipant, IsEventOrganizer
from apps.events.models import Event


class FeedbackCreateView(generics.CreateAPIView):
    """
    API view to create new feedback.
    
    Allows participants to provide feedback for events they attended.
    
    Endpoint: POST /api/feedback/create/
    
    Request Body:
        {
            "event_id": 1,
            "rating": 5,
            "review": "Great event! Loved the organization."
        }
    
    Response (Success - 201):
        {
            "success": true,
            "message": "Feedback submitted successfully",
            "data": {...}
        }
    
    Permissions:
        - IsAuthenticated
        - IsParticipant: User must have participant role
    """
    
    serializer_class = FeedbackCreateSerializer
    permission_classes = [IsAuthenticated, IsParticipant]
    
    def create(self, request, *args, **kwargs):
        """Create feedback with custom response."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        feedback = serializer.save()
        
        # Return full feedback data
        feedback_serializer = FeedbackSerializer(feedback)
        
        return Response({
            'success': True,
            'message': 'Feedback submitted successfully',
            'data': feedback_serializer.data
        }, status=status.HTTP_201_CREATED)


class FeedbackListView(generics.ListAPIView):
    """
    API view to list feedbacks for an event.
    
    Public endpoint showing all published feedbacks for an event.
    
    Endpoint: GET /api/feedback/event/{event_id}/
    
    Query Parameters:
        - rating: Filter by rating (1-5)
        - min_rating: Minimum rating filter
    
    Response (Success - 200):
        {
            "success": true,
            "data": [...]
        }
    
    Permissions:
        - AllowAny: Public endpoint
    """
    
    serializer_class = FeedbackListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Get published feedbacks for event."""
        event_id = self.kwargs.get('event_id')
        
        queryset = Feedback.objects.filter(
            event_id=event_id,
            is_published=True
        ).select_related('participant', 'event').order_by('-created_at')
        
        # Filter by rating
        rating = self.request.query_params.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)
        
        # Filter by minimum rating
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """List event feedbacks."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class MyFeedbacksView(generics.ListAPIView):
    """
    API view to list user's feedbacks.
    
    Shows all feedbacks submitted by the authenticated user.
    
    Endpoint: GET /api/feedback/my-feedbacks/
    
    Response (Success - 200):
        {
            "success": true,
            "data": [...]
        }
    
    Permissions:
        - IsAuthenticated
        - IsParticipant
    """
    
    serializer_class = FeedbackListSerializer
    permission_classes = [IsAuthenticated, IsParticipant]
    
    def get_queryset(self):
        """Get user's feedbacks."""
        return Feedback.objects.filter(
            participant=self.request.user
        ).select_related('event').order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """List user's feedbacks."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class FeedbackDetailView(generics.RetrieveAPIView):
    """
    API view to get feedback details.
    
    Shows full details of a specific feedback.
    
    Endpoint: GET /api/feedback/{id}/
    
    Response (Success - 200):
        {
            "success": true,
            "data": {...}
        }
    
    Permissions:
        - AllowAny: Public endpoint (for published feedbacks)
    """
    
    serializer_class = FeedbackSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Get published feedbacks or user's own feedbacks."""
        if self.request.user.is_authenticated:
            # Authenticated users can see their own feedbacks
            return Feedback.objects.filter(
                Q(is_published=True) | Q(participant=self.request.user)
            ).select_related('event', 'participant')
        else:
            # Anonymous users can only see published feedbacks
            return Feedback.objects.filter(
                is_published=True
            ).select_related('event', 'participant')
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve feedback details."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class FeedbackUpdateView(generics.UpdateAPIView):
    """
    API view to update feedback.
    
    Allows participants to update their feedback.
    
    Endpoints:
        PUT /api/feedback/{id}/update/
        PATCH /api/feedback/{id}/update/
    
    Permissions:
        - IsAuthenticated
        - IsParticipant (own feedbacks only)
    """
    
    serializer_class = FeedbackUpdateSerializer
    permission_classes = [IsAuthenticated, IsParticipant]
    
    def get_queryset(self):
        """Get user's feedbacks only."""
        return Feedback.objects.filter(participant=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """Update feedback."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        feedback = serializer.save()
        
        # Return full feedback data
        feedback_serializer = FeedbackSerializer(feedback)
        
        return Response({
            'success': True,
            'message': 'Feedback updated successfully',
            'data': feedback_serializer.data
        })


class FeedbackDeleteView(generics.DestroyAPIView):
    """
    API view to delete feedback.
    
    Allows participants to delete their feedback.
    
    Endpoint: DELETE /api/feedback/{id}/delete/
    
    Response (Success - 200):
        {
            "success": true,
            "message": "Feedback deleted successfully"
        }
    
    Permissions:
        - IsAuthenticated
        - IsParticipant (own feedbacks only)
    """
    
    permission_classes = [IsAuthenticated, IsParticipant]
    
    def get_queryset(self):
        """Get user's feedbacks only."""
        return Feedback.objects.filter(participant=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """Delete feedback."""
        instance = self.get_object()
        instance.delete()
        
        return Response({
            'success': True,
            'message': 'Feedback deleted successfully'
        })


class OrganizerResponseView(APIView):
    """
    API view for organizer to respond to feedback.
    
    Allows event organizers to add responses to participant feedback.
    
    Endpoint: POST /api/feedback/{id}/respond/
    
    Request Body:
        {
            "organizer_response": "Thank you for your feedback..."
        }
    
    Response (Success - 200):
        {
            "success": true,
            "message": "Response added successfully",
            "data": {...}
        }
    
    Permissions:
        - IsAuthenticated
        - IsEventOrganizer (event owner only)
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """Add organizer response."""
        feedback = get_object_or_404(Feedback, pk=pk)
        
        # Check if user is event organizer
        if feedback.event.organizer != request.user:
            return Response({
                'success': False,
                'error': {
                    'message': 'You do not have permission to respond to this feedback.',
                    'status_code': 403
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Add response
        serializer = OrganizerResponseSerializer(
            feedback,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        feedback = serializer.save()
        
        # Return updated feedback
        feedback_serializer = FeedbackSerializer(feedback)
        
        return Response({
            'success': True,
            'message': 'Response added successfully',
            'data': feedback_serializer.data
        })


class EventFeedbackStatsView(APIView):
    """
    API view to get event feedback statistics.
    
    Returns aggregated statistics for event feedbacks.
    
    Endpoint: GET /api/feedback/event/{event_id}/stats/
    
    Response (Success - 200):
        {
            "success": true,
            "data": {
                "total_feedbacks": 42,
                "average_rating": 4.5,
                "rating_distribution": {...},
                "positive_count": 35,
                "neutral_count": 5,
                "negative_count": 2
            }
        }
    
    Permissions:
        - AllowAny: Public endpoint
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request, event_id):
        """Get event feedback statistics."""
        event = get_object_or_404(Event, id=event_id)
        
        # Get published feedbacks
        feedbacks = Feedback.objects.filter(
            event=event,
            is_published=True
        )
        
        # Calculate statistics
        total_feedbacks = feedbacks.count()
        
        if total_feedbacks == 0:
            return Response({
                'success': True,
                'data': {
                    'total_feedbacks': 0,
                    'average_rating': 0,
                    'rating_distribution': {
                        '5': 0, '4': 0, '3': 0, '2': 0, '1': 0
                    },
                    'positive_count': 0,
                    'neutral_count': 0,
                    'negative_count': 0
                }
            })
        
        # Average rating
        avg_rating = feedbacks.aggregate(Avg('rating'))['rating__avg']
        
        # Rating distribution
        rating_dist = {
            '5': feedbacks.filter(rating=5).count(),
            '4': feedbacks.filter(rating=4).count(),
            '3': feedbacks.filter(rating=3).count(),
            '2': feedbacks.filter(rating=2).count(),
            '1': feedbacks.filter(rating=1).count(),
        }
        
        # Sentiment counts
        positive_count = feedbacks.filter(rating__gte=4).count()
        neutral_count = feedbacks.filter(rating=3).count()
        negative_count = feedbacks.filter(rating__lte=2).count()
        
        return Response({
            'success': True,
            'data': {
                'total_feedbacks': total_feedbacks,
                'average_rating': round(avg_rating, 2),
                'rating_distribution': rating_dist,
                'positive_count': positive_count,
                'neutral_count': neutral_count,
                'negative_count': negative_count
            }
        })