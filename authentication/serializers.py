from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from authentication.models import UserProfile
from django.db import transaction
from django.contrib.auth import authenticate
from services.send_email import send_user_activation_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import base64
import uuid

class RegistrationSerializer(serializers.ModelSerializer):
    login_type = serializers.CharField(required=True)
    passcode = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    gender = serializers.CharField(required=True)
    geo_location = serializers.CharField()
    email = serializers.EmailField(required=True)
    name = serializers.CharField(required=True)
    profile_picture = serializers.CharField()
    mobile_no = serializers.CharField()
    username = serializers.CharField()
    slug = serializers.CharField()

    class Meta:
        model = User
        fields = [
            "login_type",
            "username",
            "email",
            "password",
            "name",
            "password",
            "passcode",
            "address",
            "gender",
            "mobile_no",
            "geo_location",
            "profile_picture",
            "slug",
        ]

    def create(self, validated_data):
        base64_data = validated_data.get("profile_picture")
        filename = f'public/bullet_proof/profile_pic/{str(uuid.uuid4())}.png'

        # Decode and save the Base64 data to S3
        image_data = base64.b64decode(base64_data.encode())
        image_file = ContentFile(image_data, name=filename)
        default_storage.save(filename, image_file)
        # Get the full S3 URL

        user_details = {
            "username": validated_data["username"],
            "email": validated_data["email"],
            "password": make_password(validated_data["password"]),
            "first_name": validated_data["name"],
        }
        extra_detail = {
            "profile_pic": filename,
            "slug": validated_data["slug"],
            "phone_number": validated_data["mobile_no"],
            "passcode": urlsafe_base64_encode(force_bytes(validated_data["passcode"])),
            "address": validated_data["address"],
            "gender": validated_data["gender"],
            "geo_location": validated_data["geo_location"],
            "login_type": validated_data["login_type"],
        }
        with transaction.atomic():
            user = User.objects.create(**user_details)
            user.is_active = False
            user.save()
            UserProfile.objects.create(user=user, **extra_detail)
        return user
    
    def validate(self, attrs):
        if attrs.get("login_type") == "2":
            raise serializers.ValidationError(
                {"error": "Please enter valid login type"}
            )
        if UserProfile.objects.filter(
            user__email=attrs.get("email"),
            login_type="2",
            user__is_active=True,
        ).exists():
            user_detail = UserProfile.objects.get(user_email=attrs.get("email"))
            raise serializers.ValidationError(
                {
                    "error": f"You already registred with {user_detail.social_media_type}. So please login with {user_detail.social_media_type}"
                }
            )
        return super().validate(attrs)


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        max_length=255, style={"input_type": "password", "write_only": True}
    )

    class Meta:
        model = User
        fields = ["email", "password"]

    def validate(self, attrs):
        # If entered email doesn't exist
        if not User.objects.filter(email=attrs.get("email")).exists():
            raise serializers.ValidationError(
                {"error": "No user exist with this email"}
            )

        # If the user is not active or deleted
        if not User.objects.get(email=attrs.get("email")).is_active:
            user = User.objects.get(email=attrs.get("email"))
            request = self.context.get("request")
            send_user_activation_mail(request, user)
            raise serializers.ValidationError(
                {"error": "Account not verified please verify your account"}
            )

        username = User.objects.get(email=attrs.get("email")).username
        user = authenticate(username=username, password=attrs.get("password"))

        if user is not None:
            if UserProfile.objects.filter(user=user, is_deleted=True).exists():
                raise serializers.ValidationError(
                    {"error": "Account is disabled By Admin"}
                )
            return attrs
        else:
            raise serializers.ValidationError({"error": "Invalid ID or password"})


class SocialLoginSerializer(serializers.Serializer):
    login_type = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    social_media_id = serializers.CharField(required=True)
    social_media_type = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        fields = [
            "login_type",
            "email",
            "first_name",
            "last_name",
            "social_media_id",
            "social_media_type",
            "password",
        ]

    def validate(self, attrs):
        if attrs.get("login_type") == "1":
            raise serializers.ValidationError(
                {"error": "Please enter valid login type"}
            )
        if UserProfile.objects.filter(
            user__email=attrs.get("email"), is_deleted=True
        ).exists():
            raise serializers.ValidationError({"error": "Account is disabled by admin"})
        if UserProfile.objects.filter(
            user__email=attrs.get("email"), login_type="1"
        ).exists():
            user_detail = UserProfile.objects.get(user_email=attrs.get("email"))
            raise serializers.ValidationError(
                {
                    "error": f"You already registred with standard login. So please login with Standard"
                }
            )
        return super().validate(attrs)

    def create(self, validated_data):
        if not User.objects.filter(email=validated_data.get("email")).exists():
            user_details = {
                "username": validated_data["email"].split("@")[0],
                "email": validated_data["email"],
                "password": make_password(validated_data["password"]),
                "first_name": validated_data["first_name"],
                "last_name": validated_data["last_name"],
            }
            extra_detail = {
                "profile_pic": validated_data["profile_pic"],
                "passcode": urlsafe_base64_encode(
                    force_bytes(validated_data["passcode"])
                ),
                "address": validated_data["address"],
                "gender": validated_data["gender"],
                "geo_location": validated_data["geo_location"],
                "social_media_id": validated_data["social_media_id"],
                "social_media_type": validated_data["social_media_type"],
                "login_type": validated_data["login_type"],
            }
            with transaction.atomic():
                user = User.objects.create(**user_details)
                user.is_active = False
                user.save()
                UserProfile.objects.create(user=user, **extra_detail)
            return user
        else:
            user = User.objects.get(email=validated_data.get("email"))
            return user


class PasscodeLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    passcode = serializers.IntegerField(required=True)

    class Meta:
        fields = ["email", "passcode"]

    def validate(self, attrs):
        email = attrs.get("email")
        passcode = attrs.get("passcode")
        decode_passcode = urlsafe_base64_encode(force_bytes(passcode))
        if UserProfile.objects.filter(
            user__email=email, passcode=decode_passcode
        ).exists():
            return super().validate(attrs)
        raise serializers.ValidationError("Invalid Credential")
