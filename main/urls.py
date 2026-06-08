# main/urls.py
from django.urls import path
from . import views

app_name = 'main'  # ← ЭТА СТРОКА ОБЯЗАТЕЛЬНА!

urlpatterns = [
    path('', views.index_view, name='index'),
    path('contact/', views.contact_view, name='contact_form'),
]