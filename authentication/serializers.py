from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from authentication.models import UserProfile


class RegisterSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(required=True)
    passcode = serializers.IntegerField(required=True)
    address = serializers.CharField(required=True)
    gender = serializers.CharField(required=True)
    geo_location = serializers.CharField()

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "password" "last_name",
            "profile_pic",
            "passcode",
            "address",
            "gender",
            "geo_location",
        ]

    def create(self, validated_data):
        user_details = {
            "username": validated_data["email"],
            "email": validated_data["email"],
            "password": make_password(validated_data["password"]),
            "first_name": validated_data["first_name"],
            "last_name": validated_data["last_name"],
        }
        user = User.objects.create(**user_details)
        user.is_active = False
        user.save()

        extra_detail = {
            "profile_pic": validated_data["profile_pic"],
            "passcode": validated_data["passcode"],
            "address": validated_data["address"],
            "gender": validated_data["gender"],
            "geo_location": validated_data["geo_location"],
        }

        return UserProfile.objects.create(user=user, **extra_detail)
