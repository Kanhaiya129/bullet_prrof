from django.urls import path
from .views import RegistrationView, UserLoginView, verify

urlpatterns = [
    path('register', RegistrationView.as_view(), name="registraion"),
    path('verify/<str:uid>/<str:token>', verify, name="verify_email"),
    path("login/", UserLoginView.as_view(), name="login"),

]