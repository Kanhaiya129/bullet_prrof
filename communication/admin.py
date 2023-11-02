from django.contrib import admin
from .models import FriendUser

@admin.register(FriendUser)
class FriendUserAdmin(admin.ModelAdmin):
    list_display=["user","friend","status"]