from django.contrib import admin
from authentication.models import (
    UserProfile,
    AccountVerification,
    ForgotPasswordAndPasscode,
)
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


@admin.register(AccountVerification)
class AccountVerificationAdmin(admin.ModelAdmin):
    list_display = ["user", "token"]


@admin.register(ForgotPasswordAndPasscode)
class ForgotPasswordAndPasscodeAdmin(admin.ModelAdmin):
    list_display = ["user", "token"]


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)


admin.site.unregister(User)  # Unregister the default User admin
admin.site.register(User, CustomUserAdmin)  # Register the custom User admin

admin.site.site_header = "Buller Proof"
admin.site.site_title = "Bullet Proof"
admin.site.index_title = "Welcome to the Bullet Proof"
