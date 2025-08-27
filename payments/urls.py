from django.urls import path
from .views import ClickInitiatePayment, click_callback

urlpatterns = [
    path("click/initiate/", ClickInitiatePayment.as_view(), name="click_initiate"),
    path("click/callback/", click_callback, name="click_callback"),
]