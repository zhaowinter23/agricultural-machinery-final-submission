from django.contrib import admin
from django.urls import path, include
from tracks import views as track_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', track_views.home, name='home'),
    path('tracks/', include('tracks.urls')),
]
