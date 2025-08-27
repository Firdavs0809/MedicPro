import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from orders.routing import websocket_urlpatterns as order_ws
from users.auth_ws import SimpleJWTAuthMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": SimpleJWTAuthMiddleware(
        URLRouter(order_ws)
    ),
})
