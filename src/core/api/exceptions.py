from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response: Response = exception_handler(exc, context)

    # If response is handled by the default handler, return it
    if response:
        return response

    # Prepare the response data
    body_data = {
        'success': False,
        'message': str(exc.__class__.__name__),
        'error': str(exc)
    }

    # Create a custom response with the renderer explicitly set
    if isinstance(exc, ObjectDoesNotExist):
        response = Response(
            data=body_data,
            status=status.HTTP_404_NOT_FOUND
        )
    elif isinstance(exc, ValueError) or isinstance(exc, KeyError) or isinstance(exc, IntegrityError):
        response = Response(
            data=body_data,
            status=status.HTTP_400_BAD_REQUEST
        )
    else:
        response = Response(
            data=body_data,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Set the renderer for the response if we're in an API context
    if hasattr(context.get('request', None), 'accepted_renderer'):
        response.accepted_renderer = context['request'].accepted_renderer
        response.accepted_media_type = context['request'].accepted_media_type
        response.renderer_context = context
    else:
        # For non-API views (like admin), use JSONRenderer
        renderer = JSONRenderer()
        response.accepted_renderer = renderer
        response.accepted_media_type = "application/json"
        response.renderer_context = { }

    return response