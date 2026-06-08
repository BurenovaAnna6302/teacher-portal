from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    path('', views.surveys_list, name='surveys'),
    path('api/', views.surveys_list_api, name='surveys_api'),
    path('<int:survey_id>/', views.survey_detail, name='survey_detail'),
    path('<int:survey_id>/submit/', views.submit_survey, name='submit_survey'),
    path('<int:survey_id>/results/', views.survey_results, name='survey_results'),
]