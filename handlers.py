import logging
import json

from jsonschema import validate

from django_ws_app.response import Response, SuccessResponse
from django_ws_app.message_types import MessageTypes
from django_ws_app.manager import Manager

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

schema = {
    "type": "object",
    "properties": {
        "request": {"type": "string"},
    },
    "required": ["request", "data"],
}

def send_group(channel: str, response: Response):
    """Send group"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(channel, {
        "type": "send_payload_event",
        "payload_type": MessageTypes.DATA.value,
        "payload_data": json.dumps(response.get_obj(), default=str),
    })

def get_handler_name(message):
    """get handler name"""
    return message["request"].replace(" ", "_").lower()

class AbstractHandler(object):
    """AbstractHandler object"""

    def connect(self):
        """Handler for connect"""

    def disconnect(self):
        """Handler for disconnect"""

    def __init__(self, consumer):
        self.consumer = consumer

    def get_user(self):
        """Get user"""
        return self.consumer.scope["user"]

    def handle_message(self, message):
        """handle message"""
        validate(instance=message, schema=schema)
        handler = getattr(self, get_handler_name(message), None)
        if handler and hasattr(handler, 'action'):
            if 'data' in message:
                handler(message["data"])
            else:
                handler()

    def send(self, data: Response) -> None:
        """Send format response to this client"""
        return self.consumer.send_payload(MessageTypes.DATA.value, data.get_obj())

    def send_group(self, room: str, data: Response) -> None:
        """Send format message to group with type INFO"""
        send_group(room, data)

def action(func):
    """Decorator for incoming requests"""
    def wrapper(*args):
        return func(*args)
    wrapper.action = True
    return wrapper

class Handlers():
    """Manager WS Server"""
    _handlers = []

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Handlers, cls).__new__(cls)
        return cls.instance

    def register(self, handler):
        """Register new handler"""
        text = f"Register new handler {handler}"
        logging.info(text)
        self._handlers.append(handler)

    def get_handlers(self):
        """Get handlers"""
        return self._handlers

class BaseHandler(AbstractHandler):
    """BaseHandler"""

    def connect(self):
        """Handler for connect"""

    def disconnect(self):
        """Handler for disconnect"""
        for room in self.consumer.rooms:
            self.send_event_count_person(room)

    def get_count_clients(self, room):
        """Get count person in channel"""
        manager = Manager()
        return manager.get_count_auth_clients(room)

    def send_event_count_person(self, room):
        """Handle event from client 'count person'"""
        return self.send_group(
            room,
            SuccessResponse("COUNT PERSON", {"count": self.get_count_clients(room)}),
        )

    @action
    def whoiam(self, *args):
        """Handle event from client 'who i am'"""
        return self.send(
            SuccessResponse("WHOIAM", {"user": self.consumer.scope["user"]})
        )

    @action
    def join_room(self, room):
        """Handle event from client 'join room'"""
        self.consumer.add_room(room)
        self.send(SuccessResponse("JOIN ROOM", {"room": room}))
        self.send_event_count_person(room)

    @action
    def leave_room(self, room):
        """Handle event from client 'leave room'"""
        self.consumer.remove_room(room)
        self.send(SuccessResponse("LEAVE ROOM", {"room": room}))
        self.send_event_count_person(room)
