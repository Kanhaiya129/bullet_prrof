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
from fcm_django.models import FCMDevice
import base64
import uuid
import secrets
import string
from django.db.models import Q


class RegistrationSerializer(serializers.ModelSerializer):
    login_type = serializers.CharField(required=True)
    passcode = serializers.CharField(required=True)
    # address = serializers.CharField(required=False)
    # gender = serializers.CharField(required=False)
    # geo_location = serializers.CharField(required=False)
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message=("Email already exists"),
            )
        ],
    )
    name = serializers.CharField(required=True)
    # profile_picture = serializers.CharField(required=False)
    # phone_number = serializers.CharField(required=False,
    #     validators=[
    #         UniqueValidator(
    #             queryset=UserProfile.objects.all(),
    #             message=("Mobile Number Already Exists"),
    #         )
    #     ],
    # )
    username = serializers.CharField()
    # slug = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            "login_type",
            "username",
            "email",
            "password",
            "name",
            "passcode",
            # "address",
            # "gender",
            # "phone_number",
            # "geo_location",
            # "profile_picture",
            # "slug",
        ]

    def create(self, validated_data):
        filename = None
        if "profile_picture" in validated_data and "profile_picture" != "":
            base64_data = validated_data.get("profile_picture")
            filename = f"public/bullet_proof/profile_pic/{str(uuid.uuid4())}.png"

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
            "slug": validated_data["slug"] if "slug" in validated_data else None,
            "phone_number": validated_data["phone_number"] if "phone_number" in validated_data else None,
            "passcode": urlsafe_base64_encode(force_bytes(validated_data["passcode"])),
            "address": validated_data["address"] if "address" in validated_data else None,
            "gender": validated_data["gender"] if "gender" in validated_data else None,
            "geo_location":validated_data["geo_location"] if "geo_location" in validated_data else None,
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
                {"error": ["Please enter valid login type"]}
            )
        if UserProfile.objects.filter(
            user__email=attrs.get("email"),
            login_type="2",
            user__is_active=True,
        ).exists():
            user_detail = UserProfile.objects.get(user_email=attrs.get("email"))
            raise serializers.ValidationError(
                {
                    "error": [f"You already registred with {user_detail.social_media_type}. So please login with {user_detail.social_media_type}"]
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
                {"error": ["No user exist with this email"]}
            )

        # If the user is not active or deleted
        if not User.objects.get(email=attrs.get("email")).is_active:
            user = User.objects.get(email=attrs.get("email"))
            request = self.context.get("request")
            send_user_activation_mail(request, user)
            raise serializers.ValidationError(
                {"error": ["Account not verified please verify your account"]}
            )

        username = User.objects.get(email=attrs.get("email")).username
        user = authenticate(username=username, password=attrs.get("password"))

        if user is not None:
            if UserProfile.objects.filter(user=user, is_deleted=True).exists():
                raise serializers.ValidationError(
                    {"error": ["Account is disabled By Admin"]}
                )
            return attrs
        else:
            raise serializers.ValidationError({"error": "Invalid ID or password"})


class SocialLoginSerializer(serializers.Serializer):
    login_type = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    platform_id = serializers.CharField(required=True)
    platform_type = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        fields = [
            "login_type",
            "email",
            "name",
            "platform_id",
            "platform_type",
            "password",
        ]

    def validate(self, attrs):
        if attrs.get("login_type") == "1":
            raise serializers.ValidationError(
                {"error": ["Please enter valid login type"]}
            )
        if UserProfile.objects.filter(
            user__email=attrs.get("email"), is_deleted=True
        ).exists():
            raise serializers.ValidationError({"error": ["Account is disabled by admin"]})
        if UserProfile.objects.filter(
            user__email=attrs.get("email"), login_type="1"
        ).exists():
            user_detail = UserProfile.objects.get(user_email=attrs.get("email"))
            raise serializers.ValidationError(
                {
                    "error": [f"You already registred with standard login. So please login with Standard"]
                }
            )
        return super().validate(attrs)

    def create(self, validated_data):
        if not User.objects.filter(email=validated_data.get("email")).exists():
            filename = None
            if "profile_picture" in validated_data and "profile_picture" != "":
                base64_data = validated_data.get("profile_picture")
                filename = f"public/bullet_proof/profile_pic/{str(uuid.uuid4())}.png"

                # Decode and save the Base64 data to S3
                image_data = base64.b64decode(base64_data.encode())
                image_file = ContentFile(image_data, name=filename)
                default_storage.save(filename, image_file)

            user_details = {
                "username": validated_data["email"].split("@")[0],
                "email": validated_data["email"],
                "password": make_password(
                    "".join(
                        secrets.choice(string.digits + string.punctuation)
                        for _ in range(12)
                    )
                ),
                "first_name": validated_data["name"],
            }
            extra_detail = {
                "profile_pic": filename,
                "passcode": None,
                "address": None,
                "gender": None,
                "slug": None,
                "geo_location": None,
                "platform_id": validated_data["platform_id"],
                "platform_type": validated_data["platform_type"],
                "login_type": validated_data["login_type"],
            }
            with transaction.atomic():
                user = User.objects.create(**user_details)
                user.is_active = True
                user.save()
                UserProfile.objects.create(user=user, **extra_detail)
            return user
        else:
            user = User.objects.get(email=validated_data.get("email"))
            return user


class PasscodeLoginSerializer(serializers.Serializer):
    userId = serializers.CharField(required=True)
    passcode = serializers.IntegerField(required=True)

    class Meta:
        fields = ["userId", "passcode"]

    def validate(self, attrs):
        userId = attrs.get("userId")
        passcode = attrs.get("passcode")
        decode_passcode = urlsafe_base64_encode(force_bytes(passcode))
        user_detail_obj = UserProfile.objects.filter(
            user_id=userId, passcode=decode_passcode
        )
        if user_detail_obj.exists():
            return super().validate(attrs)
        raise serializers.ValidationError({"error": ["Invalid Credential"]})


class CheckUserSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    slug = serializers.CharField(required=False)
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=False)

    class Meta:
        fields = ["name", "username", "slug", "email", "phone_number"]

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        if UserProfile.objects.filter(
            Q(user__username=attrs.get("username"))
            | Q() if phone_number is None else Q(phone_number=phone_number)
            | Q(user__email=attrs.get("email"))
        ).exists(): 
            raise serializers.ValidationError(
                {"error": ["duplication of username or email or mobile number"]}
            )
        return super().validate(attrs)


class SetPasscodeSerializer(serializers.Serializer):
    new_passcode = serializers.IntegerField(required=True)
    confirm_passcode = serializers.IntegerField(required=True)
    fcm_token = serializers.CharField(required=True)

    class Meta:
        fields = ["new_passcode", "confirm_passcode", "fcm_token"]

    def update(self, instance, validated_data):
        instance.passcode = urlsafe_base64_encode(
            force_bytes(validated_data["new_passcode"])
        )
        instance.save()
        return instance

    def validate(self, attrs):
        if attrs.get("new_passcode") != attrs.get("confirm_passcode"):
            raise serializers.ValidationError(
                {"error": ["Your confirm passcode must be same to new passcode"]}
            )
        return super().validate(attrs)

class ChangePasscodeSerializer(serializers.Serializer):
    new_passcode = serializers.CharField(required=True)
    confirm_passcode = serializers.CharField(required=True)

    class Meta:
        fields = ["new_passcode", "confirm_passcode"]

    def validate(self, attrs):
        user = self.context.get("user")
        new_password = attrs.get("new_passcode")
        confirm_passcode = attrs.get("confirm_passcode")
        user = UserProfile.objects.filter(user__username=user).first()
        decode_new_passcode=urlsafe_base64_encode(force_bytes(new_password))
        if user.passcode == decode_new_passcode:
            raise serializers.ValidationError({"error":["Unable to change your Passcode"]})
        if new_password != confirm_passcode:
            raise serializers.ValidationError({"error":["Your confirm passcode must be same to new passcode"]})
        return decode_new_passcode
