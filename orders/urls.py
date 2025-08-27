from django.urls import path
from .views import OrderCreateView, OrderHistoryView, OrderAssignView

urlpatterns = [
    path("orders/", OrderHistoryView.as_view(), name="orders_history"),
    path("orders/create/", OrderCreateView.as_view(), name="orders_create"),
    path("orders/<int:pk>/assign/", OrderAssignView.as_view(), name="orders_assign"),
]
