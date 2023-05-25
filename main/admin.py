from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.gis.admin import OSMGeoAdmin
from main import models

admin.site.register(models.Club)
admin.site.register(models.Venue)
admin.site.register(models.Membership)
admin.site.register(models.Merchant)
admin.site.register(models.SubscriptionPlan)
admin.site.register(models.Customer)


@admin.register(models.Event)
class EventAdmin(OSMGeoAdmin):
    list_display = ["name", "slug"]


@admin.register(models.User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": ("email", "password"),
            },
        ),
        (
            "Personal Information",
            {
                "fields": ("first_name", "last_name"),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "permissions",
                )
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "date_joined",
                    "last_login",
                ),
            },
        ),
    )
    add_fieldsets = (
        None,
        {
            "classes": ("wide"),
            "fields": (
                "email",
                "password1",
                "password2",
            ),
        },
    )

    list_display = ("first_name", "last_name", "email", "is_staff")
    search_fields = ("first_name", "last_name", "email")
    ordering = ("first_name", "last_name")