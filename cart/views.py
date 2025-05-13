from django.shortcuts import render,redirect,get_object_or_404
from .models import CartItem,Cart
from store.models import Product
from django.http import HttpResponse


# Create your views here.
def __cart_id(request):
    """
    Creates or retrieves a session-based cart ID for an anonymous user.
    """
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()  # Create a session if it doesn't exist
    return cart


def add_cart(request, product_id):
    """
    Adds a product to the user's cart. If the user is logged in, it associates
    the product with the logged-in user's cart. If the user is not logged in,
    it associates the product with a session cart.
    """
    # Get the product using the product ID
    product = Product.objects.get(id=product_id)
    session_key = __cart_id(request)

    # Get or create a session cart
    try:
        cart = Cart.objects.get(cart_id=session_key)
    except Cart.DoesNotExist:
        # Create a new cart if it doesn't exist
        cart = Cart.objects.create(cart_id=session_key)
        cart.save()

    # If the user is logged in, merge guest cart items into the user's cart
    if request.user.is_authenticated:
        guest_cart_items = CartItem.objects.filter(cart=cart, user=None)
        
        for item in guest_cart_items:
            try:
                # Try to find an existing item in the user's cart
                existing_item = CartItem.objects.get(product=item.product, user=request.user)
                existing_item.quantity += item.quantity  # Merge quantities
                existing_item.save()
                item.delete()  # Remove the item from the guest cart
            except CartItem.DoesNotExist:
                # If the item does not exist for the user, associate it with the user
                item.user = request.user
                item.cart = None
                item.save()

        # Now, add the product for the logged-in user
        try:
            cart_item = CartItem.objects.get(product=product, user=request.user)
            cart_item.quantity += 1  # Increment the quantity if the item exists
            cart_item.save()
        except CartItem.DoesNotExist:
            # Create a new cart item if it doesn't exist
            CartItem.objects.create(
                product=product,
                user=request.user,
                quantity=1,
                cart=cart  # Ensure cart is set for logged-in user
            )
    else:
        # If the user is not logged in (anonymous user)
        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += 1  # Increment the quantity if the item exists
            cart_item.save()
        except CartItem.DoesNotExist:
            # Create a new cart item if it doesn't exist
            CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=1
            )

    return redirect('cart')  # Redirect to the cart page




def remove_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.filter(product=product, user=request.user).first()
        else:
            cart = Cart.objects.get(cart_id=__cart_id(request))
            cart_item = CartItem.objects.filter(product=product, cart=cart).first()

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    return redirect('cart')


def remove_button(request,product_id):
    
    product = get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        cart_item = get_object_or_404(product=product,cart=cart)
    else:
        cart = Cart.objects.get(cart_id=__cart_id(request))
        cart_item = cart_item.objects.get(product=product,cart=cart)
    cart_item.delete()

    
   
    return render('cart')


def cart(request):
    
    quantity = 0
    cart_items = []
    total = 0
    cart_item = []
    grandtotal = 0
    tax=0
    session_key = __cart_id(request) 
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.filter(user=request.user,is_active=True)
        else:
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