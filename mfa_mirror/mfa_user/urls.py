from django.urls import path, include
from django.conf.urls import url
from django.views.generic import RedirectView
from mfa_user import views


urlpatterns = [
    path('', RedirectView.as_view(url='/user/register/')),
    path('register/', views.Register.as_view()),
    # path('login/', views.Login.as_view()),
    # path('logout/', views.Logout.as_view()),
    path('generate/', views.Generate.as_view()),
    # change confirmation route to modern pattern
    url(r'confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.Confirm.as_view(), name='email-confirmation'),
]
