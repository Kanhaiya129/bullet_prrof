from django.db import models
from django.contrib.auth.models import User


# DropDown List items for gender field
GENDER_CHOICES = (
    ("male", "Male"),
    ("female", "Femal"),
    ("other", "Other"),
)


class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, blank=False)
    profile_pic = models.ImageField(blank=True, upload_to="media")
    passcode = models.IntegerField()
    address = models.TextField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    geo_location = models.CharField(max_length=150, null=True, blank=True, default=None)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profile"
