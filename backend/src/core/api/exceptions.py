import logging

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # If response is handled by the default handler, return it
    if response is not None:
        return response

    # Exception details stay in the logs (and Sentry); clients get a generic message.
    # The body is wrapped into the standard envelope by CustomResponseMixin.
    if isinstance(exc, ObjectDoesNotExist):
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    if isinstance(exc, IntegrityError):
        logger.warning('Integrity error in %s: %s', context.get('view').__class__.__name__, exc)
        return Response(
            {'detail': 'The request conflicts with existing data.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    logger.exception('Unhandled error in %s', context.get('view').__class__.__name__, exc_info=exc)
    return Response({'detail': 'Internal server error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
