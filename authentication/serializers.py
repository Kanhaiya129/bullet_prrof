from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from authentication.models import UserProfile
from django.db import transaction
from django.contrib.auth import authenticate



class RegistrationSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(required=True)
    passcode = serializers.IntegerField(required=True)
    address = serializers.CharField(required=True)
    gender = serializers.CharField(required=True)
    geo_location = serializers.CharField()
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message=("Email already exists"),
            )
        ],
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "password",
            "last_name",
            "profile_pic",
            "passcode",
            "address",
            "gender",
            "geo_location",
        ]

    def create(self, validated_data):
        user_details = {
            "username": validated_data["email"].split("@")[0],
            "email": validated_data["email"],
            "password": make_password(validated_data["password"]),
            "first_name": validated_data["first_name"],
            "last_name": validated_data["last_name"],
        }
        extra_detail = {
            "profile_pic": validated_data["profile_pic"],
            "passcode": validated_data["passcode"],
            "address": validated_data["address"],
            "gender": validated_data["gender"],
            "geo_location": validated_data["geo_location"],
        }
        with transaction.atomic():
            user = User.objects.create(**user_details)
            user.is_active = False
            user.save()
            UserProfile.objects.create(user=user, **extra_detail)

        return user

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
                {"errors": "No user exist with this email"}
            )

        # If the user is not active or deleted
        if not User.objects.get(email=attrs.get("email")).is_active:
            raise serializers.ValidationError(
                {
                    "errors": "Account not verified please verify your account"
                }
            )

        username = User.objects.get(email=attrs.get("email")).username
        user = authenticate(username=username, password=attrs.get("password"))

        if user is not None:
            if UserProfile.objects.filter(user=user, is_deleted=True).exists():
                raise serializers.ValidationError(
                    {"errors": "Account is disabled By Admin"}
                )
            return attrs
        else:
            raise serializers.ValidationError({"errors": "Invalid ID or password"})