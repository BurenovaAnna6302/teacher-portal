from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    # Главная страница новостей (HTML)
    path('', views.news_list, name='news'),

    # Детальная страница новости
    path('<int:news_id>/', views.news_detail, name='news_detail'),

    # API для AJAX-запросов (JSON)
    path('api/', views.news_list_api, name='news_api'),
]