from django.urls import path
from . import views

urlpatterns = [
    path('geojson/<int:pk>/', views.track_geojson, name='track_geojson'),
    path('geojson/', views.all_tracks_geojson, name='all_tracks_geojson'),
    path('query/', views.track_query, name='track_query'),
    path('statistics/', views.statistics, name='statistics'),
    path('statistics/export/', views.export_statistics, name='export_statistics'),
    path('statistics/chart-data/', views.stats_chart_data, name='stats_chart_data'),
    path('analysis/<int:pk>/', views.track_analysis, name='track_analysis'),
    path('stats/<int:pk>/', views.track_stats_api, name='track_stats_api'),
    path('import/', views.track_import, name='track_import'),
    path('delete/<int:pk>/', views.track_delete, name='track_delete'),
    path('users/', views.user_management, name='user_management'),
]
