from rest_framework import generics
from rest_framework.response import Response


class CustomResponseMixin:
    """
    Mixin to customize API responses with a standard structure.
    It provides methods to format successful and error responses.
    The response structure is as follows:
    - For success:
        {
            "success": true,
            "message": <SUCCESS_MESSAGE>,
            "data": <response_data>
        }
    - For error:
        {
            "success": false,
            "message": <ERROR_MESSAGE>",
            "error": <error_data>
        }
    CAUTION: This mixin is only functional for the exceptions handled by DRF.
             It does not handle exceptions raised outside the DRF scope.
             For the rest, you should use a custom exception handler.
    """

    SUCCESS_MESSAGE = "OK"
    ERROR_MESSAGE = "NOT OK"

    def success_response(self, response: Response):
        response_data = {
            'success': True,
            'message': self.SUCCESS_MESSAGE,
            'data': response.data,
        }
        response.data = response_data
        return response

    def error_response(self, response: Response):
        response_data = {
            'success': False,
            'message': self.ERROR_MESSAGE,
            'error': response.data,
        }
        response.data = response_data
        return response

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)

        if response.status_code < 400:
            response = self.success_response(response=response)
        else:
            response = self.error_response(response=response)
        return response


class UserFilterMixin:
    """
    Mixin to filter querysets based on the authenticated user.
    Requires a 'user_field' attribute to specify the related path to the user.
    """
    user_field = 'user'

    def get_queryset(self):
        qs = super().get_queryset()

        if not self.user_field:
            return qs

        filter_kwargs = {
            self.user_field: self.request.user # noqa
        }
        return qs.filter(**filter_kwargs)


class BaseAPIView(UserFilterMixin, CustomResponseMixin, generics.GenericAPIView):
    ...