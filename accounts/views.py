from django.shortcuts import render,redirect
from . forms import RegistrationForm
from .models import Account
from django.contrib import auth,messages

# Create your views here.


## user register functionality
def register(request):
    if request.method == 'POST':
        form=RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
            user.phone_number = phone_number
            user.save()
            messages.success(request,'Registration Successfull')
            return redirect('register')
    else:
        form = RegistrationForm()

    context = {
        'form' : form,
        }
    return render(request,'register.html',context)



### login functionality
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email,password=password)
        if user is not None:
            auth.login(request,user)
            messages.success(request,'login Successfull')
            return redirect('home')
        else:
            messages.error(request,'Invalid login credentials')
            return redirect('login')
    return render(request,'login.html')




def logout(request):
    return render(render,'logout.html')