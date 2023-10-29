from django.urls import path
from .views import (
    RegistrationView,
    UserLoginView,
    verify,
    reset_password_check,
    reset_password_form,
    reset_passcode_check,
    reset_passcode_form,
    UserSocialLoginView,
    PasscodeLoginView,
    ForgotPasswordView,
    VerifyPasscode,
    CheckUserView,
    SetPassCodeView,
    ForgotPasscodeView,
    LogoutView,
    ChangePasscodeView
)

urlpatterns = [
    path("register", RegistrationView.as_view(), name="registraion"),
    path("verify/<str:uid>/<str:token>", verify, name="verify_email"),
    path("login", UserLoginView.as_view(), name="login"),
    path("social-login", UserSocialLoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),


    # Passcode Login, verify, set, change
    path("set-passcode", SetPassCodeView.as_view(), name="passcode_login"),
    path("passlogin", PasscodeLoginView.as_view(), name="passcode_login"),
    path("verifypasscode", VerifyPasscode.as_view(), name="verifypasscode"),
    path("change-passcode", ChangePasscodeView.as_view(), name="change-passcode"),


    # Reset Passcode
    path("reset_passcode", ForgotPasscodeView.as_view(), name="reset_passcode"),
    path("reset_passcode_check/<str:uid>/<str:token>", reset_passcode_check, name="reset_passcode_check"),
    path("reset_passcode_form/<str:uid>/<str:token>", reset_passcode_form, name="reset_passcode_form"),

    path("check-user", CheckUserView.as_view(), name="check-user"),
    path("social_login", UserSocialLoginView.as_view(), name="social_login"),

    # Reset password
    path("reset_password", ForgotPasswordView.as_view(), name="reset_password"),
    path("reset_password_check/<str:uid>/<str:token>", reset_password_check, name="reset_password_check"),
    path("reset_password_form/<str:uid>/<str:token>", reset_password_form, name="reset_password_form"),
    
]
