from rest_framework import serializers
from .models import Order

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "title", "description", "price", "required_specialty", "required_gender"]

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["client"] = request.user
        return super().create(validated_data)

class OrderSerializer(serializers.ModelSerializer):
    client_username = serializers.CharField(source="client.username", read_only=True)
    worker_username = serializers.CharField(source="worker.username", read_only=True)

    class Meta:
        model = Order
        fields = ["id","title","description","price","required_specialty","required_gender",
                  "status","client","worker","client_username","worker_username","created_at"]
        read_only_fields = ["client","status","created_at"]
