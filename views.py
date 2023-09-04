import os
from django.http import HttpResponseNotFound
from rest_framework.views import APIView, Response

class WebsocketGateway(APIView):
    def get(self, request):
        base = os.environ.get('SITE_NAME', default=False)
        if not base: return HttpResponseNotFound()
        base = base.replace('http://', 'ws://')
        base = base.replace('https://', 'wss://')
        return Response(f'{base}')
