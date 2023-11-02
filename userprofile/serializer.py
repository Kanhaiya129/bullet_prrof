from rest_framework import serializers
from authentication.models import UserProfile
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    username = serializers.CharField()

    class Meta:
        model = UserProfile
        fields = [
            "address",
            "gender",
            "geo_location",
            "username",
            "slug",
            "name",
        ]

    def update(self, instance, validated_data):
        instance.user.username = validated_data.get("username")
        instance.user.first_name = validated_data.get("name")
        try:
            instance.save()
            instance.user.save()
        except:
            raise serializers.ValidationError(
                {"error": ["This username already taken"]}
            )
        return super().update(instance, validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    # Serializer fields for old and new passwords
    current_password = serializers.CharField(
        max_length=255,
        style={"input_type": "password", "write_only": True},
        required=True,
    )
    new_password = serializers.CharField(
        max_length=255,
        style={"input_type": "password", "write_only": True},
        required=True,
    )
    confirm_password = serializers.CharField(
        max_length=255,
        style={"input_type": "password", "write_only": True},
        required=True,
    )

    class Meta:
        fields = ["current_password", "new_password", "confirm_password"]

    def validate(self, attrs):
        user = self.context["request"].user
        current_password = attrs.get("current_password")
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")
        matchcheck = check_password(current_password, user.password)
        if not matchcheck:
            raise serializers.ValidationError("Current password is not valid")
        # Check if the old password and new password are the same
        if confirm_password != new_password:
            raise serializers.ValidationError(
                "Your confirm password must be same to new password"
            )
        # Check if the old password and new password are the same
        if current_password == new_password:
            raise serializers.ValidationError(
                {"error": ["You can't set a new password same as current password"]}
            )
        return attrs


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username", "email", "first_name"]


class ListUserSerializer(serializers.ModelSerializer):
    user = UserDataSerializer()

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "profile_pic",
            "address",
            "phone_number",
            "gender",
            "geo_location",
            "slug",
            "platform_type",
            "platform_id",
            "user"
        ]
