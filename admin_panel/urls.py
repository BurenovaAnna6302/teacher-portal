from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Главная и авторизация
    path('', views.dashboard, name='dashboard'),
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('check-admin-code/', views.check_admin_code, name='check_admin_code'),

    # Статистика
    path('statistics/', views.statistics, name='statistics'),
    path('statistics/<int:survey_id>/', views.survey_statistics, name='survey_statistics'),

    # Управление мероприятиями
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:event_id>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:event_id>/delete/', views.event_delete, name='event_delete'),

    # Управление новостями
    path('news/', views.news_list, name='news_list'),
    path('news/create/', views.news_create, name='news_create'),
    path('news/<int:news_id>/edit/', views.news_edit, name='news_edit'),
    path('news/<int:news_id>/delete/', views.news_delete, name='news_delete'),

    # Управление методическими материалами
    path('materials/', views.materials_list, name='materials_list'),
    path('materials/create/', views.material_create, name='material_create'),
    path('materials/<int:material_id>/edit/', views.material_edit, name='material_edit'),
    path('materials/<int:material_id>/delete/', views.material_delete, name='material_delete'),

    # Управление документами
    path('documents/', views.documents_list, name='documents_list'),
    path('documents/create/', views.documents_create, name='documents_create'),
    path('documents/<int:document_id>/edit/', views.documents_edit, name='documents_edit'),
    path('documents/<int:document_id>/delete/', views.documents_delete, name='documents_delete'),

    # Управление опросами
    path('surveys/', views.surveys_list, name='surveys_list'),
    path('surveys/create/', views.survey_create, name='survey_create'),
    path('surveys/<int:survey_id>/edit/', views.survey_edit, name='survey_edit'),
    path('surveys/<int:survey_id>/delete/', views.survey_delete, name='survey_delete'),
    path('surveys/<int:survey_id>/questions/create/', views.question_create, name='question_create'),
    path('surveys/<int:survey_id>/questions/<int:question_id>/edit/', views.question_edit, name='question_edit'),
    path('surveys/<int:survey_id>/questions/<int:question_id>/delete/', views.question_delete, name='question_delete'),
    path('surveys/<int:survey_id>/status/<str:new_status>/', views.change_survey_status, name='change_survey_status'),
    # Управление успешными практиками
    path('practices/', views.practices_list, name='practices_list'),
    path('practices/create/', views.practice_create, name='practice_create'),
    path('practices/<int:practice_id>/edit/', views.practice_edit, name='practice_edit'),
    path('practices/<int:practice_id>/delete/', views.practice_delete, name='practice_delete'),
    # Помощь и поддержка
    path('help/', views.help, name='help'),
    path('change-admin-password/', views.change_admin_password, name='change_admin_password'),
    # Демо данные
    path('create-demo/', views.create_demo_data, name='create_demo_data'),
]