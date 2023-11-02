import base64
import json
import uuid
from django.core import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework import status
from authentication.models import UserProfile
from authentication.views import user_data
from userprofile.serializer import (
    UpdateUserProfileSerializer,
    ChangePasswordSerializer,
    ListUserSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.generics import ListAPIView
from services.pagination import CustomPagination
from authentication.views import user_data


class UserProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if UserProfile.objects.filter(user=request.user).exists():
            # Returns the above values only when user login token is valid
            return Response(
                {
                    "code": 200,
                    "message": "User Data Fetched Successfully",
                    "data": user_data(self.request.user),
                },
                status=status.HTTP_200_OK,
            )
        response = {
            "code": 400,
            "message": "User profile data does not exists",
            "data": None,
        }
        # Returns the above values only when user login token is valid
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user = request.user
        user_detail_obj = UserProfile.objects.filter(
            user__username=user.username
        ).first()
        filename = None
        if "profile_picture" in request.data and "profile_picture" != "":
            base64_data = request.data.get("profile_picture")
            if base64_data:
                filename = f"public/bullet_proof/profile_pic/{str(uuid.uuid4())}.png"

                # Decode and save the Base64 data to S3
                image_data = base64.b64decode(base64_data.encode())
                image_file = ContentFile(image_data, name=filename)
                default_storage.save(filename, image_file)
                user_detail_obj.profile_pic = filename
                user_detail_obj.save()

        serializer = UpdateUserProfileSerializer(user_detail_obj, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "code": 200,
                    "message": "Record updated successfully",
                    "data": user_data(user),
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "code": 400,
                "message": serializer.errors,
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserChangePasswordView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer_class = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        if serializer_class.is_valid():
            # Set New Password & Save it
            self.request.user.set_password(request.data.get("new_password"))
            self.request.user.save()
            # sending success response
            response = {
                "code": 200,
                "message": "Password updated successfully",
                "data": user_data(self.request.user),
            }
            return Response(response, status=status.HTTP_200_OK)
        # sending failure response
        return Response(
            {"code": 400, "errors": serializer_class.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = ListUserSerializer

    def get(self, request):
        userprofile_data = UserProfile.objects.all().exclude(
            user__username=request.user, user__is_superuser=True
        )
        page = self.paginate_queryset(userprofile_data)
        serializer = self.serializer_class(page, many=True)
        result = self.get_paginated_response(serializer.data)
        data = result.data
        response = {
            "status": True,
            "message": "All User fetch Successfully",
            "data": data,
        }
        return Response(data=response, status=status.HTTP_200_OK)


class GetUserByMobileNumberView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = ListUserSerializer

    def get(self, request):
        mobile_no = request.query_params.get("mobile_no")
        user_profiles = UserProfile.objects.filter(
            phone_number__startswith=mobile_no
        ).exclude(user__username=request.user, user__is_superuser=True)
        page = self.paginate_queryset(user_profiles)
        serializer = self.serializer_class(page, many=True)
        result = self.get_paginated_response(serializer.data)
        data = result.data
        response = {
            "status": True,
            "message": "Mobile User fetch Successfully",
            "data": data,
        }
        return Response(data=response, status=status.HTTP_200_OK)


class GetUserByNameView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = ListUserSerializer

    def get(self, request):
        name = request.query_params.get("name")
        user_profiles = UserProfile.objects.filter(
            user__first_name__startswith=name).exclude(user__username=request.user, user__is_superuser=True)
        page = self.paginate_queryset(user_profiles)
        serializer = self.serializer_class(page, many=True)
        result = self.get_paginated_response(serializer.data)
        data = result.data
        response = {
            "status": True,
            "message": "Retrive User by name fetch successfully",
            "data": data,
        }
        return Response(data=response, status=status.HTTP_200_OK)
