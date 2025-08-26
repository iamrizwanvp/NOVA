from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, OTP, PasswordResetSession


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = ["email", "username", "is_active", "is_staff", "date_joined"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal", {"fields": ("username",)}),  # removed profile_picture from here
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Important Dates", {"fields": ("date_joined", "last_login")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2"),
        }),
    )
    search_fields = ["email", "username"]
    list_filter = ["is_active", "is_staff", "date_joined"]
    readonly_fields = ("date_joined", "last_login")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "nickname"]
    search_fields = ["user__email", "nickname"]


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ["email", "otp", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["email"]


@admin.register(PasswordResetSession)
class PasswordResetSessionAdmin(admin.ModelAdmin):
    list_display = ["user", "is_verified", "created_at"]
    list_filter = ["is_verified", "created_at"]
    search_fields = ["user__email"]
