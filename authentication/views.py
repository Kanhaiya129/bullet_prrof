from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework import status
from authentication.serializers import RegistrationSerializer, UserLoginSerializer
from authentication.models import AccountVerification, UserProfile
from django.utils.encoding import force_str
from rest_framework.authtoken.models import Token
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

from fcm_django.models import FCMDevice
from services.send_email import send_user_activation_mail


# Create your views here.
class RegistrationView(APIView):
    def post(self, request, format=None):
        try:
            if UserProfile.objects.filter(
                user__email=request.data["email"], is_deleted=True
            ).exists():
                return Response(
                    {
                        "status": False,
                        "message": "Account is disabled by admin",
                        "data": None,
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            # Passing our data in the seriealizer
            serializer = RegistrationSerializer(data=request.data)

            if serializer.is_valid():
                user = serializer.save()  # Throws error if data is empty or not correct
                send_user_activation_mail(request, user)  # Send email for verify email
                return Response(
                    {
                        "status": True,
                        "message": "User Registered Successfully, Please Check Email to verify You Account",
                        "data": None,
                    },
                    status=status.HTTP_201_CREATED,
                )

            # All serializer error stores in errors
            response = {"status": False, "errors": serializer.errors, "data": None}
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"message": f"Something Went Wrong {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserLoginView(APIView):
    # Class bases view for user Login
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            # If email and password are correct and user is is_active
            user_obj = User.objects.get(email=serializer.data.get("email"))

            # Deleting any previous stored token
            Token.objects.filter(user=user_obj).delete()

            if "fcm_token" in request.data:
                # Set FCM token for user
                fcm_device = FCMDevice()
                fcm_device.registration_id = request.data["fcm_token"]
                fcm_device.type = request.data["device_type"]
                fcm_device.user = user_obj
                fcm_device.save()

            # Genrate Token if given username and password verify
            token, _ = Token.objects.get_or_create(user=user_obj)
            return Response(
                {
                    "status": True,
                    "message": "Authentication Successful",
                    "data": {"token": token.key},
                },
                status=status.HTTP_200_OK,
            )
        # Return errors from serializer
        return Response({"status": False, "message": serializer.errors, "data": None})


def verify(request, uid, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = AccountVerification.objects.get(user_id=uid)
        if default_token_generator.check_token(user.user, token):
            user.user.is_active = True
            user.user.save()
            user.delete()
            return render(request, "admin/verify_email.html")
        else:
            return render(request, "admin/expired_link.html")
    except (TypeError, ValueError, OverflowError, AccountVerification.DoesNotExist):
        return render(request, "admin/expired_link.html")
