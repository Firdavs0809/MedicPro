from core.celery import app
from .models import Payment
from orders.models import OrderStatus
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import random
import time


def notify(group: str, payload: dict):
    """
    Send a WebSocket push event to a channel group.
    """
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        group,
        {"type": "push.event", "data": payload}
    )


@app.task
def process_fake_payment(payment_id: int, force: str | None = None):
    """
    Fake payment processing task.
    Simulates payment delay, randomly approves or cancels,
    then notifies client + worker via WebSocket.
    """
    try:
        p = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return

    # Simulate gateway delay
    time.sleep(2)

    # Decide outcome
    outcome = force if force in ["success", "canceled"] else random.choice(["success", "canceled"])
    p.status = outcome
    p.save(update_fields=["status"])

    order = p.order

    if outcome == "success":
        order.status = OrderStatus.PAID
        order.save(update_fields=["status"])

        # Notify client
        notify(f"client_{order.client_id}", {
            "event": "payment_success",
            "order_id": order.id
        })

        # Notify worker if assigned
        if order.worker_id:
            notify(f"worker_{order.worker_id}", {
                "event": "new_paid_order",
                "order_id": order.id
            })

    else:
        order.status = OrderStatus.CANCELED
        order.save(update_fields=["status"])

        # Notify client only
        notify(f"client_{order.client_id}", {
            "event": "payment_canceled",
            "order_id": order.id
        })
