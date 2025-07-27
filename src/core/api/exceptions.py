from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

def custom_exception_handler(exc, context):

    # Call REST framework's default exception handler first
    response: Response = exception_handler(exc, context)

    # If response is handled by the default handler, return it
    if response:
        return response

    # If the exception is not handled, we can customize the response
    body_data = {
                'success': False,
                'message': str(exc.__class__.__name__),
                'error': str(exc)
            }

    if isinstance(exc, ObjectDoesNotExist):
        return Response(
            data=body_data,
            status=status.HTTP_404_NOT_FOUND
        )
    elif isinstance(exc, ValueError) or isinstance(exc, KeyError) or isinstance(exc, IntegrityError):
        return Response(
            data=body_data,
            status=status.HTTP_400_BAD_REQUEST
        )
    else:
        return Response(
            data=body_data,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )