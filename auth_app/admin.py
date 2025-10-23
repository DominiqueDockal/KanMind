from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for the custom User model.

    Displays email, fullname, staff and active status.
    Supports filtering, searching, and custom add/change fields grouping.
    """

    model = User
    list_display = ("email", "fullname", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    ordering = ("email",)
    search_fields = ("email", "fullname")

    # Defines how fields are grouped in the user change view
    fieldsets = (
        (None, {"fields": ("email", "fullname", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )

    # Defines form fields for the admin add user page
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "fullname", "password1", "password2", "is_staff", "is_active")},
        ),
    )




