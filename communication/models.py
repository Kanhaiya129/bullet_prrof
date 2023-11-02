from django.db import models
from django.contrib.auth.models import User

class FriendUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, blank=False, related_name="user")
    friend = models.ForeignKey(User, null=False, on_delete=models.CASCADE, blank=False, related_name="friend")
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invited_friends")
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.username}-with-{self.friend.username}"

    class Meta:
        verbose_name = "User Friend"
        verbose_name_plural = "User Friends"

class BlockUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, blank=False, related_name="user_block")
    blocked_user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, blank=False, related_name="block_user")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.username}-block-{self.friend.username}"

    class Meta:
        verbose_name = "Block User"
        verbose_name_plural = "Block Users"

class ChatRoomUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_rooms")
    chat_room_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.chat_room_id

    class Meta:
        verbose_name = "Chat Room"
        verbose_name_plural = "Chat Rooms"