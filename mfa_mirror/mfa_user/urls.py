from django.urls import path, include
from django.conf.urls import url
from mfa_user import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('logout/', views.logout),
    path('generate/', views.generate),
    # change confirmation route to modern pattern
    url(r'confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.confirm, name='email-confirmation'),
]
