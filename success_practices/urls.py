from django.urls import path
from . import views

app_name = 'success_practices'

urlpatterns = [
    path('', views.practices_list, name='practices_list'),
    path('api/', views.practices_list_api, name='practices_api'),
    path('<int:practice_id>/', views.practice_detail, name='practice_detail'),
]