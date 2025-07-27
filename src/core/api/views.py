from rest_framework import generics
from rest_framework.response import Response


class CustomGenericAPIView(generics.GenericAPIView):
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


class BaseAPIView(CustomGenericAPIView):
    ...