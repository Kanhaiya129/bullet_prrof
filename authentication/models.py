from django.db import models
from django.contrib.auth.models import User


# DropDown List items for gender field
GENDER_CHOICES = (
    ("male", "Male"),
    ("female", "Femal"),
    ("other", "Other"),
)

TYPE = (("1", "Normal"), ("2", "Social"))


class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, blank=False)
    profile_pic = models.ImageField(blank=True, null=True, upload_to="media")
    passcode = models.CharField(max_length=20)
    address = models.TextField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    geo_location = models.CharField(max_length=150, null=True, blank=True, default=None)
    is_deleted = models.BooleanField(default=False)

    social_media_type = models.CharField(max_length=25, blank=True, null=True)
    social_media_id = models.CharField(max_length=200, blank=True, null=True)
    login_type = models.CharField(max_length=25, blank=True, null=True, choices=TYPE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.user.username

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profile"


class AccountVerification(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, blank=False)
    uid = models.CharField(max_length=150)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Account Verification"
        verbose_name_plural = "Account Verification"

class ForgotPasswordAndPasscode(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, blank=False)
    uid = models.CharField(max_length=150)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reset Password And Passcode"
        verbose_name_plural = "Reset Password And Passcode"