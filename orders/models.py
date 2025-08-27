from django.db import models
from django.conf import settings

class OrderStatus(models.TextChoices):
    CREATED = "created", "Created"
    PAID = "paid", "Paid"
    CANCELED = "canceled", "Canceled"
    ACCEPTED = "accepted", "Accepted"

class Order(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="client_orders")
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="worker_orders", null=True, blank=True)

    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    required_specialty = models.CharField(max_length=64, blank=True, default="")
    required_gender = models.CharField(max_length=10, blank=True, default="any")

    status = models.CharField(max_length=16, choices=OrderStatus.choices, default=OrderStatus.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order#{self.id} {self.title} [{self.status}]"
