# urls.py
from django.urls import path
from . import views

app_name = 'guideapp'

urlpatterns = [
    # other urls
    path('guide/', views.guide_page, name='guide'),
]
