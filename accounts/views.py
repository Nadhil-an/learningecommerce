from django.shortcuts import render,redirect,get_object_or_404
from . forms import RegistrationForm,UserForm,UserProfileForm
from .models import Account,UserProfile
from order.models import Order
from cart.views import Cart,CartItem
from django.contrib import auth,messages
from django.contrib.auth.decorators import login_required


## verification email
from django.contrib.sites.shortcuts import  get_current_site
from django.template.loader import render_to_string
from django.utils.http import  urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import  EmailMessage
from django.http import HttpResponseRedirect
from django.urls import reverse

from cart.views import __cart_id



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

            #activation required
            current_site = get_current_site(request)
            mail_subject = 'please activate your account'
            message      = render_to_string('account_activation_email.html',{
                'user'   :user,
                'domain' :current_site,
                'uid'    :urlsafe_base64_encode(force_bytes(user.pk)),
                'token'  :default_token_generator.make_token(user),
            })

            to_email    = email
            send_email  = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            return HttpResponseRedirect(reverse('login') + f'?command=verification&email={email}')  

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
            try:
                cart = Cart.objects.get(cart_id=__cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    for item in cart_item:
                        item.user = user
                        item.save()
            except:
                pass
            
            auth.login(request,user)
            messages.success(request,'login Successfull')
            return redirect('home')
        else:
            messages.error(request,'Invalid login credentials')
            return redirect('login')
    return render(request, 'login.html')




@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out')
    return redirect ('login')

def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):

        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active =True
        user.save()
        messages.success(request,'Congratulation! Your Account is activated.')
        return redirect('login')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register')

@login_required(login_url= 'login')
def dashboard(request):
    userprofile, created = UserProfile.objects.get_or_create(user=request.user)
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    order_count = orders.count()

    context = {
        'user': request.user,
        'order_count': order_count,
        'userprofile': userprofile 

    }
 
    return render(request, 'dashboard.html', context)

def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email__exact=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent.')
            return redirect('login')  # Redirect to login or another confirmation page
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgotpassword')

    return render(request, 'forgotpassword.html')


def reset_validation(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,'Please reset your password')
        return redirect('resetpassword')
    else:
        messages.error(request,'This link is expired')
        return redirect('login')
    
def resetpassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            if uid:
                user = Account.objects.get(pk=uid)
                user.set_password(password)
                user.save()
                messages.success(request, 'Password reset successfully')
                return redirect('login')  # <-- Redirect after success
            else:
                messages.error(request, 'Session expired. Try the link again.')
                return redirect('forgotPassword')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('resetpassword')
    
    return render(request, 'resetpassword.html')


@login_required(login_url='login')
def checkout(request):
    return render(request,'checkout.html')
    
def myorders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders' :orders
    }
    return render(request,'myorder.html',context)

@login_required
def editprofile(request):
    userprofile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated.')
            return redirect('editprofile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile 
    }
    return render(request, 'editprofile.html', context)

@login_required
def changepassword(request):
    if request.method == 'POST':
        current_password = request.POST.get('currentpassword')
        new_password = request.POST.get('newpassword')
        confirm_password = request.POST.get('confirmpassword')

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                #auth.logout(request)
                messages.success(request,'Password updated sucessfully')
                return redirect('changepassword')
            else:
                messages.error(request,'Please enter valid password')
                return redirect('changepassword')
        else:
            messages.error(request,'Password does not match')
            return redirect('changepassword')
    return render(request,'changepassword.html')