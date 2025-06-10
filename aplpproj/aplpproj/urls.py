"""
URL configuration for aplpproj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('mainapp.urls')),  # Replace 'myapp' with your app name\
    path('plpapp/', include('plpapp.urls')),  # Replace 'myapp' with your app name\
    path('poltaker/', include('poltakerapp.urls')),  # Replace 'myapp' with your app name\
    path('surveyapp/', include('surveyapp.urls')),  # Replace 'myapp' with your app name\
    path('guideapp/', include('guideapp.urls')),  # Replace 'myapp' with your app name\
    path('admin/', admin.site.urls),
] 
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
