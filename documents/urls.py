from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.documents_list, name='documents'),
    path('api/', views.documents_list_api, name='documents_api'),
]