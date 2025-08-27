# consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class OrdersConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        
        if user.is_anonymous:
            await self.close()
        else:
            self.group_name = f"client_{user.id}"  # Changed from user_ to client_
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def push_event(self, event):
        """Handle push.event type messages"""
        await self.send_json({
            "type": event["data"]["event"],
            "data": event["data"]
        })

    async def payment_status(self, event):
        await self.send_json({
            "type": "payment_status", 
            "status": event["status"],
            "order_id": event["order_id"],
        })