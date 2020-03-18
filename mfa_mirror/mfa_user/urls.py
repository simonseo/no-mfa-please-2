from django.urls import path, include
from mfa_user import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('logout/', views.logout),
    path('generate/', views.generate),
]
