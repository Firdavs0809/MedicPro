import hashlib
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Payment, PaymentStatus
from orders.models import Order, OrderStatus

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class ClickInitiatePayment(APIView):
    """
    Step 1: Client calls this endpoint with { "order_id": <id> }
    → We create a Payment if needed and return pay_url to redirect to Click
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")
        try:
            order = Order.objects.get(id=order_id, client=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        # Create payment record if not exists
        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={"amount": order.price}
        )
        merchant_trans_id = str(order.id)

        pay_url = (
            f"https://my.click.uz/services/pay"
            f"?service_id={settings.CLICK_SERVICE_ID}"
            f"&merchant_id={settings.CLICK_MERCHANT_ID}"
            f"&amount={order.price}"
            f"&transaction_param={merchant_trans_id}"
        )

        return Response({
            "pay_url": pay_url,
            "merchant_trans_id": merchant_trans_id,
            "order_id": order.id,
        })


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def click_callback(request):
    data = request.POST

    click_trans_id = data.get("click_trans_id")
    service_id = data.get("service_id")
    merchant_trans_id = data.get("merchant_trans_id")  # our order id
    amount = data.get("amount")
    action = data.get("action")  # 0=check, 1=payment
    sign_string = data.get("sign_string")

    # 🔐 Verify signature (Click requires strict concat)
    string_to_sign = (
        f"{click_trans_id}{service_id}{settings.CLICK_SECRET_KEY}"
        f"{merchant_trans_id}{amount}{action}"
    )
    calculated_sign = hashlib.md5(string_to_sign.encode()).hexdigest()

    if calculated_sign != sign_string:
        return Response({"error": -1, "error_note": "Invalid sign"}, status=400)

    # 🔎 Find order + payment
    try:
        order = Order.objects.get(id=merchant_trans_id)
        payment = order.payment
    except (Order.DoesNotExist, Payment.DoesNotExist):
        return Response({"error": -5, "error_note": "Order not found"}, status=404)

    # 💡 Prevent double processing
    if payment.status == PaymentStatus.SUCCESS:
        return Response({"error": 0, "error_note": "Already paid"})

    if action == "0":  # ✅ CHECK phase
        return Response({"error": 0, "error_note": "Success"})

    if action == "1":  # 💰 PAYMENT phase
        payment.status = PaymentStatus.SUCCESS
        payment.click_trans_id = click_trans_id
        payment.save(update_fields=["status", "click_trans_id"])

        order.status = OrderStatus.PAID
        order.save(update_fields=["status"])

        # 🔔 WebSocket push (notify client + worker if needed)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"client_{order.client.id}",
            {
                "type": "push.event",
                "data": {
                    "event": "payment_success",
                    "order_id": order.id
                }
            }
        )
        if order.worker_id:
            async_to_sync(channel_layer.group_send)(
                f"worker_{order.worker_id}",
                {
                    "type": "push.event",
                    "data": {
                        "event": "new_paid_order",
                        "order_id": order.id
                    }
                }
            )

        return Response({"error": 0, "error_note": "Payment successful"})

    return Response({"error": -3, "error_note": "Unknown action"}, status=400)
