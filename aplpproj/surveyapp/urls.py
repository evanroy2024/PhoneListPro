from django.urls import path

app_name = 'surveyapp'
from . import views

urlpatterns = [
    path('create/', views.create_survey, name='create_survey'),
    path('surveys/', views.all_surveys_view, name='all_surveys'),
    path('surveys/<int:survey_id>/delete/', views.delete_survey_view, name='delete_survey'),
    path('survey/<int:survey_id>/download/csv/', views.download_survey_csv, name='download_survey_csv'),
    path('survey/<int:survey_id>/download/pdf/', views.download_survey_pdf, name='download_survey_pdf'),
    path('survey/<int:survey_id>/responses/', views.survey_response_view, name='survey_response_view'),

    
]

