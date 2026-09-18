from django.contrib import admin
from .models import Track, TrackPoint


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(TrackPoint)
class TrackPointAdmin(admin.ModelAdmin):
    list_display = ['track', 'sequence', 'gps_time', 'longitude', 'latitude', 'speed', 'working_status']
    list_filter = ['track', 'working_status']
    raw_id_fields = ['track']
