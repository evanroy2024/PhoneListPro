from django.urls import path
from .views import dashboard , upload_questions
from . import views 

app_name = 'plpapp'

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('upload/', upload_questions, name='upload_questions'),
    path('list-questions/', views.list_questions, name='list_questions'),
    path('upload-user-contacts/', views.upload_user_contacts, name='upload_user_contacts'),
    path('list-user-contacts/', views.list_user_contacts, name='list_user_contacts'),
    path('upload-poltakers/', views.upload_poltakers, name='upload_poltakers'),
    path('list-poltakers/', views.list_poltakers, name='list_poltakers'),

    path('profile/', views.view_profile, name='view_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-email/', views.change_email, name='change_email'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('analytics/', views.analytics_view, name='analytics_view'),

    path('notifications/', views.notifications_view, name='notifications'),
    path('help-center/', views.help_center_view, name='help_center'),
    path('settings/', views.user_settings_view, name='user_settings'),
    path('delete-account/', views.delete_account_view, name='delete_account'),

]


