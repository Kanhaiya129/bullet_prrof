from rest_framework import serializers
from .models import FriendUser, BlockUser
from authentication.models import UserProfile
from django.contrib.auth.models import User


class BlockUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockUser
        fields = ["id", "blocked_user"]


class FriendInvitationSerializer(serializers.ModelSerializer):
    friend_name = serializers.CharField(source="user.first_name")
    friend_image = serializers.SerializerMethodField()

    class Meta:
        model = FriendUser
        fields = ("id", "friend", "friend_name", "friend_image")

    def get_friend_image(self, obj):
        # Define how to get the friend's profile picture URL
        user_obj = UserProfile.objects.get(user=obj.user)
        if user_obj.profile_pic:
            return user_obj.profile_pic.url
        return None


class FriendSuggestionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id")  # Access user ID
    name = serializers.CharField(source="user.first_name")  # Access user name
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile  # Specify the model
        fields = ("id", "name", "profile_picture")

    def get_profile_picture(self, obj):
        # Define how to get the user's profile picture URL
        if obj.profile_pic:
            return obj.profile_pic.url
        return None


class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "username",
            "email",
            "profile_picture",
            "phone_number",
            "online_status",
        )

    def get_profile_picture(self, obj):
        # Define how to get the user's profile picture URL
        if obj.profile_pic:
            return obj.profile_pic.url
        return None
