from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from .models import CustomUser


class CustomUserAdmin(DefaultUserAdmin):
    # list display
    list_display = (
        "email",
        "kakao_oid",
        "username",
        "is_active",
        "is_staff",
        "last_login",
    )
    list_filter = ("is_active", "is_staff")
    search_fields = ("email", "name")
    ordering = ("email",)

    # detail display
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("name",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important dates",
            {
                "fields": (
                    "last_login",
                    "created_at",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "password1", "password2"),
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
