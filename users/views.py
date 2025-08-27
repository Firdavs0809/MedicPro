from rest_framework import generics, permissions
from .serializers import RegisterSerializer, UserSerializer
from django.contrib.auth import get_user_model
from .permissions import IsAdmin

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class AdminUserListView(generics.ListAPIView):
    """Admin boshqa foydalanuvchilarni ko‘ra olishi kerak."""
    permission_classes = [IsAdmin]
    serializer_class = UserSerializer
    queryset = User.objects.all()
