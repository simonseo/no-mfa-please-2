from django.urls import path, include
from mfa_user import views

urlpatterns = [
    path('register/', views.register),
]
