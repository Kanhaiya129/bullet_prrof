from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework import status
from authentication.serializers import (
    RegistrationSerializer,
    UserLoginSerializer,
    SocialLoginSerializer,
    PasscodeLoginSerializer,
    PasswordResetSerializer,
)
from rest_framework.decorators import api_view
from authentication.models import AccountVerification, UserProfile, ForgotPasswordAndPasscode
from django.utils.encoding import force_str
from rest_framework.authtoken.models import Token
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site

from fcm_django.models import FCMDevice
from services.send_email import send_user_activation_mail, send_user_resetpassword_mail


def user_data(user_obj):
    data = {
        "id": user_obj.user.id,
        "first_name": user_obj.user.first_name,
        "last_name": user_obj.user.last_name,
        "email": user_obj.user.email,
        "profile_pic": user_obj.profile_pic.url if user_obj.profile_pic else None,
        "passcode": user_obj.passcode,
        "address": user_obj.address,
        "gender": user_obj.gender,
        "geo_location": user_obj.geo_location,
    }
    return data


# Create your views here.
class RegistrationView(APIView):
    def post(self, request, format=None):
        # try:
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


class UserLoginView(APIView):
    # Class bases view for user Login
    def post(self, request, format=None):
        serializer = UserLoginSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            # If email and password are correct and user is is_active
            user_obj = User.objects.get(email=serializer.data.get("email"))
            user_detail_obj = UserProfile.objects.get(user=user_obj)
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
                    "data": {"token": token.key, "user": user_data(user_detail_obj)},
                },
                status=status.HTTP_200_OK,
            )
        # Return errors from serializer
        return Response({"status": False, "message": serializer.errors, "data": None})


class UserSocialLoginView(APIView):
    # Social Login
    def post(self, request, format=None):
        serializer = SocialLoginSerializer(data=request.data)

        if serializer.is_valid():
            user_obj = serializer.data
            user_detail = UserProfile.objects.get(user=user_obj)

            # Deleting any previous stored token
            token, _ = Token.objects.get_or_create(user=user_obj)
            return Response(
                {
                    "status": True,
                    "message": "Login Successfully",
                    "data": {"token": token.key, "user": user_data(user_detail)},
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": False,
                "message": serializer.errors,
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasscodeLoginView(APIView):
    # Class bases view for user Login
    def post(self, request, format=None):
        serializer = PasscodeLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get("email")
            user_detail_obj = UserProfile.objects.get(user__email=email)

            # Deleting any previous stored token
            Token.objects.filter(user=user_detail_obj.user).delete()
            if "fcm_token" in request.data:
                # Set FCM token for user
                fcm_device = FCMDevice()
                fcm_device.registration_id = request.data["fcm_token"]
                fcm_device.type = request.data["device_type"]
                fcm_device.user = user_detail_obj.user
                fcm_device.save()

            # Genrate Token if given username and password verify
            token, _ = Token.objects.get_or_create(user=user_detail_obj.user)
            return Response(
                {
                    "status": True,
                    "message": "Authentication Successful",
                    "data": {"token": token.key, "user": user_data(user_detail_obj)},
                },
                status=status.HTTP_200_OK,
            )
        # Return errors from serializer
        return Response(
            {"status": False, "message": "Please provide passcode", "data": None},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ForgotPasswordView(APIView):
    """
    This class view will handle the send otp api for mobile app users
    """

    def post(self, request):
        try:
            if not User.objects.filter(
                email=request.data["email"], is_staff=False
            ).exists():
                # sending failure response
                response = {
                    "status": False,
                    "message": "Invalid email",
                    "data": None,
                }
                return Response(
                    data=response,
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            # check if user exists
            user = User.objects.get(email=request.data["email"], is_staff=False)
            if user:
                send_user_resetpassword_mail(
                    request, user
                )  # Send email for verify email
                # send response with success
                response = {
                    "status": True,
                    "message": "password Reset link has been sent to your registered email address",
                    "data": None,
                }
                return Response(
                    data=response,
                    status=status.HTTP_200_OK,
                )
            else:
                # sending failure response
                response = {
                    "status": False,
                    "message": "User with given email does not exists",
                    "data": None,
                }
                return Response(
                    data=response,
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except:
            response = {
                "status": False,
                "message": "Please Provide Email",
                "data": None,
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)


def reset_password_check(request, uid, token):
    try:
        uid_decode = force_str(urlsafe_base64_decode(uid))
        user = ForgotPasswordAndPasscode.objects.filter(user_id=uid_decode)
        if user.exists():
            user= user.first()
            if default_token_generator.check_token(user.user, token):
                user.user.set_password(request.POST.get("confirm_password"))
                user.user.save()
                user.delete()
                return render(request, "admin/reset_successfully.html")
            else:
                return render(request, "admin/reset_expire_link.html")
        else:
                return render(request, "admin/reset_expire_link.html")
    except (TypeError, ValueError, OverflowError, AccountVerification.DoesNotExist):
        return render(request, "admin/reset_expire_link.html")
    
def reset_password_form(request, uid, token):
    try:
        uid_decode = force_str(urlsafe_base64_decode(uid))
        user = ForgotPasswordAndPasscode.objects.filter(user_id=uid_decode)
        if user.exists():
            user= user.first()
            if default_token_generator.check_token(user.user, token):
                # Send uid and token to the reset_password.html template
                return render(request, "email/reset_password.html", {'uid': uid, 'token': token})
            else:
                    print("###############")
                    return render(request, "admin/reset_expire_link.html")
        else:
            print("@@@@@@@@@@")
            return render(request, "admin/reset_expire_link.html")
    except (TypeError, ValueError, OverflowError, AccountVerification.DoesNotExist):
        return render(request, "admin/reset_expire_link.html")


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
            return render(request, "admin/reset_expire_link.html")
    except (TypeError, ValueError, OverflowError, AccountVerification.DoesNotExist):
        return render(request, "admin/reset_expire_link.html")
