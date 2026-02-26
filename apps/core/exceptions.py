"""
Custom exception handler for Event Planet API.

This module provides a custom exception handler that formats all API errors
in a consistent structure. It ensures that all error responses follow
the same pattern for easier client-side handling.

Standard error response format:
{
    "success": false,
    "error": {
        "message": "Human-readable error message",
        "details": {...},  // Detailed error information
        "status_code": 400
    }
}

Author: Event Planet Team
Created: 2026-02-15
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that formats errors consistently.
    
    This handler wraps Django REST Framework's default exception handler
    and formats all error responses in a consistent structure.
    
    Args:
        exc: The exception instance raised
        context: Dictionary with 'view' and 'request' keys
    
    Returns:
        Response: Formatted error response with consistent structure
    
    Error Response Format:
        {
            "success": false,
            "error": {
                "message": "Main error message",
                "details": {
                    "field_name": ["Error for this field"],
                    ...
                },
                "status_code": 400
            }
        }
    """
    
    # Call REST framework's default exception handler first
    # This gets the standard error response
    response = exception_handler(exc, context)
    
    # If response is None, the exception wasn't handled by DRF
    # This could be a server error or unexpected exception
    if response is None:
        return Response({
            'success': False,
            'error': {
                'message': 'Internal server error occurred',
                'details': str(exc),
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Format the error response in our custom structure
    custom_response = {
        'success': False,
        'error': {
            'message': get_error_message(response.data),
            'details': response.data,
            'status_code': response.status_code
        }
    }
    
    return Response(custom_response, status=response.status_code)


def get_error_message(error_data):
    """
    Extract a human-readable error message from error data.
    
    This function tries to get the most relevant error message from
    the error data structure. It handles different error formats:
    - Simple string errors
    - Dict with 'detail' key
    - Dict with multiple field errors
    - List of errors
    
    Args:
        error_data: Error data from DRF exception handler
    
    Returns:
        str: Human-readable error message
    
    Examples:
        >>> get_error_message("Not found")
        "Not found"
        
        >>> get_error_message({"detail": "Invalid token"})
        "Invalid token"
        
        >>> get_error_message({"email": ["This field is required"]})
        "Validation failed"
    """
    
    # If error_data is a simple string, return it
    if isinstance(error_data, str):
        return error_data
    
    # If error_data has a 'detail' key (common for many DRF errors)
    if isinstance(error_data, dict) and 'detail' in error_data:
        return str(error_data['detail'])
    
    # If error_data is a dict with field errors
    if isinstance(error_data, dict):
        # Try to get the first error message from any field
        for key, value in error_data.items():
            if isinstance(value, list) and len(value) > 0:
                return f"{key}: {value[0]}"
            elif isinstance(value, str):
                return f"{key}: {value}"
        
        # If we can't extract a specific message, return generic one
        return "Validation failed"
    
    # If error_data is a list
    if isinstance(error_data, list) and len(error_data) > 0:
        return str(error_data[0])
    
    # Default fallback message
    return "An error occurred"