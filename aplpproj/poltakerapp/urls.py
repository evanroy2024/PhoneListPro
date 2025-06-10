from django.urls import path
from . import views

app_name = 'poltakerapp'

urlpatterns = [
    path('login/', views.poltaker_login, name='poltaker_login'),
    path('dashboard/', views.poltaker_dashboard, name='poltaker_dashboard'),
    path('surveys/', views.polltaker_surveys, name='polltaker_survyes'),
    path('survey/<str:survey_token>/contacts/', views.survey_contacts, name='survey_contacts'),
    path('survey/<int:survey_id>/<int:contact_id>/start/', views.start_survey, name='start_survey'),

    path('profile/', views.edit_poltaker_profile, name='edit_poltaker_profile'),
]
