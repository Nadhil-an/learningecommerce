from django.shortcuts import render,redirect
from .models import CartItem,Cart
from store.models import Product
from django.http import HttpResponse


# Create your views here.

def __cart_id(request):
    #creating a session key for user
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request,product_id):
    product = Product.objects.get(id=product_id) # getting the product id
    session_key = __cart_id(request)

    #checking the cart is there any cart with this session
    try:
        cart = Cart.objects.get(cart_id=session_key)
    except:
        cart = Cart.objects.create(
            cart_id = session_key
        )
    cart.save()
    
     #checking product already exists
    try:
        cart_item = CartItem.objects.get(product=product,cart=cart)
        cart_item.quantity +=1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            cart = cart,
            quantity = 1,
        )
        cart_item.save()

    return redirect('cart')


def cart(request):
    
    quantity = 0
    cart_items = []
    total = 0
    
    
    session_key = __cart_id(request)
    try:
        cart = Cart.objects.get(cart_id = session_key)
        cart_item = CartItem.objects.filter(cart=cart,is_active=True)

        for cart_items in cart_item:
            total += (cart_items.product.price * cart_items.quantity)
            quantity += cart_items.quantity
        tax = total * 0.02

        grandtotal = total + tax
    except:
        pass

    context = {
        'cart_item' :cart_item,
        'quantity': quantity,
        'total':total,
        'grandtotal':grandtotal,
        'tax':tax
    }


    
    return render(request,'cart.html',context)