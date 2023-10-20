import pytest
import json

from channels.auth import SessionMiddleware, CookieMiddleware

from channels.testing import WebsocketCommunicator
from django_ws_app.consumers import Consumer

from channels.db import database_sync_to_async

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken



@pytest.mark.asyncio
@pytest.mark.django_db
async def test_my_consumer():
    communicator = WebsocketCommunicator(CookieMiddleware(SessionMiddleware(Consumer.as_asgi())), "/ws/")
    connected, subprotocol = await communicator.connect()
    assert connected

    print(subprotocol)

    response = await communicator.receive_from()
    assert response == '["0", "WHOAREYOU"]'

    bob = await database_sync_to_async(User.objects.create)(username='bob')
    refresh = RefreshToken.for_user(bob)

    await communicator.send_to(text_data=json.dumps(['0', refresh.access_token], default=str))
    response = await communicator.receive_from()

    assert response == '["0", "SUCCESS"]'

    await communicator.disconnect()
