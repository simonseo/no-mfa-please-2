"""mfa_mirror URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, include
from mfa_user.views import home, get_started

# if route string is empty like below, it adds urls to the root
# path('', include('mfa_user.urls')), 
urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('user/', include('mfa_user.urls')),
    path('get-started/', get_started),
]
