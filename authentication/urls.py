from django.urls import path
from .views import (
    RegistrationView,
    UserLoginView,
    verify,
    reset_password_check,
    reset_password_form,
    UserSocialLoginView,
    PasscodeLoginView,
    ForgotPasswordView,
)

urlpatterns = [
    path("register", RegistrationView.as_view(), name="registraion"),
    path("verify/<str:uid>/<str:token>", verify, name="verify_email"),
    path("login", UserLoginView.as_view(), name="login"),
    path("passcode_login", PasscodeLoginView.as_view(), name="passcode_login"),
    path("social_login", UserSocialLoginView.as_view(), name="social_login"),


    path("reset_password", ForgotPasswordView.as_view(), name="reset_password"),
    path("reset_password_check/<str:uid>/<str:token>", reset_password_check, name="verify_email"),
    path("reset_password_form/<str:uid>/<str:token>", reset_password_form, name="verify_email"),
    
]
