from django.contrib import admin
from .models import FriendUser, BlockUser

@admin.register(FriendUser)
class FriendUserAdmin(admin.ModelAdmin):
    list_display=["user","friend","status"]


@admin.register(BlockUser)
class BlockUserAdmin(admin.ModelAdmin):
    list_display=["user","blocked_user"]