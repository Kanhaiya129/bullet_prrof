from django.urls import path
from .views import (
    UserProfileView,
    UserChangePasswordView
)

urlpatterns = [
    path('change-password/',UserChangePasswordView.as_view(),name='change-password'),
    path("user_profile", UserProfileView.as_view(), name="user_profile"),
 
]