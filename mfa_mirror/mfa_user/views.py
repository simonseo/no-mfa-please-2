from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password

# Create your views here.
def register(request):
    return render(request, 'register.html')