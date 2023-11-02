from django.urls import path
from .views import (
    UserProfileView,
    UserChangePasswordView,
    UserView,
    GetUserByMobileNumberView,
    GetUserByNameView
)

urlpatterns = [
    path('change-password/',UserChangePasswordView.as_view(),name='change-password'),
    path("user_profile", UserProfileView.as_view(), name="user_profile"),
    
    #users
    path("user", UserView.as_view(), name="user"),
    path("getByMobileNo", GetUserByMobileNumberView.as_view(), name="getByMobileNo"),
    path("getByName", GetUserByNameView.as_view(), name="getByName"),
]