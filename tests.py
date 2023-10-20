from django.test import TestCase
from django_ws_app.response import Response, SuccessResponse, FailedResponse

class ResponseTestCase(TestCase):
    def test_response(self):
        """Response bases identity"""
        success = SuccessResponse(response="", data={"test": "test"})
        failed = FailedResponse(response="", data={"test": "test"})

        self.assertEqual(success.__class__.__bases__, failed.__class__.__bases__)
