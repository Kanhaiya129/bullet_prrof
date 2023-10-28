import base64
import uuid
from rest_framework import serializers
from authentication.models import UserProfile
from django.contrib.auth.hashers import check_password
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    username = serializers.CharField()

    class Meta:
        model = UserProfile
        fields = [
            "profile_pic",
            "address",
            "gender",
            "geo_location",
            "username",
            "slug",
            "name",
        ]

    def update(self, instance, validated_data):
        filename = None
        if "profile_picture" in validated_data and "profile_picture" != "":
            base64_data = validated_data.get("profile_picture")
            filename = f"public/bullet_proof/profile_pic/{str(uuid.uuid4())}.png"

            # Decode and save the Base64 data to S3
            image_data = base64.b64decode(base64_data.encode())
            image_file = ContentFile(image_data, name=filename)
            default_storage.save(filename, image_file)

        # Set the 'username' and 'first_name' attributes of the related 'User' model
        instance.profile_pic = filename
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
