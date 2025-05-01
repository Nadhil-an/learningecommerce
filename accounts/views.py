from django.shortcuts import render
from . forms import RegistrationForm

# Create your views here.

def register(request):
    form = RegistrationForm()
    context = {
        'form' : form
    }
    return render(request,'register.html',context)

def login(request):
    return render(request,'login.html')

def logout(request):
    return render(render,'logout.html')