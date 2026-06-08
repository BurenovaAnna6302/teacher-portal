from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('team/', views.team_view, name='team'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
]