from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # Главная страница мероприятий (HTML)
    path('', views.events_list, name='events'),

    # Детальная страница мероприятия
    path('<int:event_id>/', views.event_detail, name='event_detail'),

    # API для AJAX-запросов (JSON)
    path('api/', views.events_list_api, name='events_api'),
]