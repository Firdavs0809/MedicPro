import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()

class SimpleJWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query = parse_qs(scope.get("query_string", b"").decode())
        token = query.get("token", [None])[0]

        if token:
            try:
                UntypedToken(token)
                payload = jwt.decode(token, settings.SIMPLE_JWT["SIGNING_KEY"] if "SIGNING_KEY" in settings.SIMPLE_JWT else settings.SECRET_KEY,
                                     algorithms=["HS256"], options={"verify_aud": False})
                user_id = payload.get("user_id")
                if user_id:
                    try:
                        user = await User.objects.aget(id=user_id)
                        scope["user"] = user
                    except User.DoesNotExist:
                        pass
            except (InvalidToken, TokenError, jwt.PyJWTError):
                pass

        return await super().__call__(scope, receive, send)
