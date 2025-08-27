from django.db import models
from django.conf import settings
from orders.models import Order, OrderStatus

class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SUCCESS = "success", "Success"
    CANCELED = "canceled", "Canceled"

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=16, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    click_trans_id = models.CharField(max_length=50, blank=True, null=True)
    merchant_trans_id = models.CharField(max_length=50, blank=True, null=True)


    def __str__(self):
        return f"Payment#{self.id} -> Order#{self.order_id} [{self.status}]"
