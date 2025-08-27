from rest_framework import generics, permissions, mixins, status
from rest_framework.response import Response
from .models import Order, OrderStatus
from .serializers import OrderCreateSerializer, OrderSerializer
from .permissions import IsClient, IsWorker, IsAdmin
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def notify_group(group, payload):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(group, {"type": "push.event", "data": payload})

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsClient]

    def perform_create(self, serializer):
        order = serializer.save()
        # Workerlar guruhiga broadcast: specialty + gender bo‘yicha
        group = f"workers_{order.required_specialty}_{order.required_gender}"
        notify_group(group, {"event": "new_order", "order_id": order.id, "title": order.title})
        # Clientga ham qabul qilindi deb ack
        notify_group(f"client_{order.client_id}", {"event": "order_created", "order_id": order.id})

class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.all().order_by("-created_at")

        if user.role == "client":
            return qs.filter(client=user)
        elif user.role == "worker":
            specialty = user.specialty or ""
            gender = user.gender or "any"
            return qs.filter(required_specialty=specialty).filter(required_gender__in=[gender, "any"])
        elif user.role == "admin":
            return qs
        return Order.objects.none()

class OrderAssignView(generics.UpdateAPIView):
    """Worker buyurtmani o‘ziga olishi (ACCEPT)."""
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsWorker]

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        order.worker = request.user
        order.status = OrderStatus.ACCEPTED
        order.save(update_fields=["worker", "status"])
        # Clientga xabar
        notify_group(f"client_{order.client_id}", {"event": "order_accepted", "order_id": order.id, "worker": request.user.username})
        return Response(OrderSerializer(order).data)
