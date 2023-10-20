from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework import status
from authentication.models import UserProfile
from authentication.views import user_data
from userprofile.serializer import UpdateUserProfileSerializer, ChangePasswordSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


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
            response = {"code":200, "message": "Password updated successfully", "data":user_data(self.request.user)}
            return Response(response, status=status.HTTP_200_OK)
        # sending failure response
        return Response(
            {"code": 400, "errors": serializer_class.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
