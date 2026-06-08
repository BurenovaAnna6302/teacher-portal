from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/upload-photo/', views.upload_photo, name='upload_photo'),
    path('profile/remove-photo/', views.remove_photo, name='remove_photo'),
    path('favorites/', views.favorites, name='favorites'),
    path('favorites/add/', views.add_to_favorites, name='add_to_favorites'),
    # ИСПРАВЛЕНО: параметр называется favorite_id (ID записи избранного)
    path('favorites/remove/<int:favorite_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('favorites/clear/', views.clear_favorites, name='clear_favorites'),
    path('favorites/check/<int:material_id>/', views.check_favorite, name='check_favorite'),
    path('favorites/list/', views.get_favorites_list, name='favorites_list'),
    path('favorites/stats/', views.get_favorites_stats, name='favorites_stats'),
    path('help/', views.help, name='help'),
]