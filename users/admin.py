from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "role", "specialty", "gender", "is_active")
    search_fields = ("username", "specialty")
    list_filter = ("role", "gender", "is_active")
