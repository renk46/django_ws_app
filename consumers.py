"""Module contain"""
import traceback
import json

from asgiref.sync import async_to_sync

from channels.generic.websocket import WebsocketConsumer
from channels.auth import login

from django_ws_app.manager import Manager
from django_ws_app.handlers import Handlers, BaseHandler
from django_ws_app.message_types import MessageTypes
from django_ws_app.exceptions import InvalidData, InvalidToken, InvalidCredentials
from django_ws_app.utils import str_to_class
from django_ws_app.authenticators import AuthenticatorInterface

from django.conf import settings


class BaseConsumer(WebsocketConsumer):
    """Chat consumer"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rooms = []

    def connect(self):
        self.accept()
        manager = Manager()
        manager.add_consumer(self)

    def disconnect(self, code):
        manager = Manager()
        manager.remove_consumer(self)

    def send_payload_event(self, event):
        """Send to client payload event"""
        self.send_payload(event["payload_type"], json.loads(event["payload_data"]))

    def send_payload(self, _type, payload):
        """Send to client payload"""
        self.send(text_data=json.dumps([_type, payload], default=str))

    def add_room(self, room):
        """Add room"""
        async_to_sync(self.channel_layer.group_add)(room, self.channel_name)
        self.rooms.append(room)

    def remove_room(self, room):
        """Remove room"""
        async_to_sync(self.channel_layer.group_discard)(room, self.channel_name)
        if room in self.rooms:
            self.rooms.remove(room)


class AuthConsumer(BaseConsumer):
    """Consumer for authentication from WebSocket"""

    def connect(self):
        super(AuthConsumer, self).connect()
        self.check_is_session_authenticated_response()

    def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            if len(data) < 2:
                raise InvalidData()
            if MessageTypes.AUTH.value == data[0]:
                self.handle_auth_context(data[1])
            else:
                super(AuthConsumer, self).receive(text_data, bytes_data)
        except InvalidData:
            self.close()
            traceback.print_exc()

    def send_response(self, message):
        """Send format response to this client"""
        self.send_payload(MessageTypes.AUTH.value, message)

    def find_user(self, data):
        """Find user in authenticator"""
        module_settings = getattr(settings, "EVENT_SUBSCRIPTION_SERVER", None)
        attr = getattr(
            module_settings, "DEFAULT_AUTHENTICATOR", "django_ws_app.authenticators.JWTAuthenticator"
        ) if module_settings else "django_ws_app.authenticators.JWTAuthenticator"
        authenticator: AuthenticatorInterface = str_to_class(attr)()
        return authenticator.find_user(data)

    def add_user_to_group(self, user):
        """Add user to group"""
        async_to_sync(self.channel_layer.group_add)(str(user.id), self.channel_name)

    def handle_auth_context(self, message):
        """Handler for incoming messages"""
        manager = Manager()
        try:
            manager.remove_consumer(self)
            user = self.find_user(message)
            async_to_sync(login)(self.scope, user)
            manager.add_consumer(self)
            self.auth_success()
            self.add_user_to_group(user)
        except InvalidCredentials:
            self.auth_error()
        except InvalidToken:
            self.auth_error()

    def check_is_session_authenticated_response(self):
        """Check session authentication"""
        if self.scope["user"].is_authenticated:
            self.auth_success()
        else:
            self.auth_unknown()

    def auth_error(self):
        """Send error response to client"""
        self.send_response("TOKENEXPIRED")

    def auth_success(self):
        """Send success response to client"""
        self.send_response("SUCCESS")

    def auth_unknown(self):
        """Send auth unknown response to client"""
        self.send_response("WHOAREYOU")


class Consumer(AuthConsumer):
    """Consumer data layer WebSocket"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handlers = [handler(self) for handler in Handlers().get_handlers()]

    def connect(self):
        super(Consumer, self).connect()
        for handler in self.handlers:
            try:
                handler.connect()
            except Exception:  # pylint: disable=W0718
                traceback.print_exc()

    def disconnect(self, code):
        super(Consumer, self).disconnect(code)
        for handler in self.handlers:
            try:
                handler.disconnect()
            except Exception:  # pylint: disable=W0718
                traceback.print_exc()

    def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            if len(data) < 2:
                raise InvalidData()
            if MessageTypes.DATA.value == data[0]:
                self.handle_message(data[1])
            else:
                super(Consumer, self).receive(text_data, bytes_data)
        except InvalidData:
            self.close()
            traceback.print_exc()

    def handle_message(self, message):
        """Handle data message from WebSocket"""
        for handler in self.handlers:
            try:
                handler.handle_message(message)
            except Exception:  # pylint: disable=W0718
                traceback.print_exc()


Handlers().register(BaseHandler)
