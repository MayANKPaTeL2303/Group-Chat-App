import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'groupchat.settings')
django.setup()  # Required before importing anything from Django apps

from chat import routing as chat_routing  # Import after django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # ✅ Use get_asgi_application directly
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat_routing.websocket_urlpatterns
        )
    ),
})
