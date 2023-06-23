class Manager():
    """Manager WS Server"""
    consumers = []

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Manager, cls).__new__(cls)
        return cls.instance

    def add_consumer(self, consumer):
        """Add consumer"""
        self.consumers.append({
            "user": consumer.scope["user"],
            "consumer": consumer
        })

    def remove_consumer(self, consumer):
        """Remove consumer"""
        self.consumers.remove({
            "user": consumer.scope["user"],
            "consumer": consumer
        })

    def get_auth_clients(self):
        """Get list users connected to WebSocket"""
        seen_clients = set()
        clients = []
        for obj in self.consumers:
            if obj["user"].id and obj["user"].id not in seen_clients:
                clients.append(obj)
                seen_clients.add(obj["user"].id)
        return clients

    def get_auth_clients_room(self, room):
        """Get auth clients for room"""
        return [client for client in self.get_auth_clients() if room in client["consumer"].rooms]

    def get_count_auth_clients(self, room):
        """Get count auth clients"""
        return len(self.get_auth_clients_room(room))
