from django.shortcuts import render
from .models import CartItem,Cart

# Create your views here.

def cart(request):
    
    return render(request,'cart.html')