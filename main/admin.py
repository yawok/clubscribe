from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from main import models

admin.site.register(models.Club)
admin.site.register(models.Venue)
admin.site.register(models.Membership)

@admin.register(models.Event)
class EventAdmin(OSMGeoAdmin):
    list_display = ["name", "slug"]