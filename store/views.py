from django.shortcuts import render, redirect, get_object_or_404
from .models import Product,variation,ReviewRating
from category.models import Category
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from .form import Reviewform
from django.contrib import messages
# Create your views here.

def store(request,category_slug=None):
    category = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category,slug=category_slug)
        products = Product.objects.filter(category=categories,is_available=True).order_by('id')
        paginator = Paginator(products,6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        paginator = Paginator(products,6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products':paged_products,
        'product_count':product_count
    }
    return render (request,'store.html',context)


## Dynamically displaying  product details into product details page 

def product_details(request, category_slug, product_slug):
    single_product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)

    product_variation_color = variation.objects.color().filter(product=single_product)
    product_variation_size = variation.objects.size().filter(product=single_product)

    context = {
        'single_product': single_product,
        'product_variation_color':product_variation_color,
        'product_variation_size':product_variation_size
    }
    return render(request, 'product_details.html', context)


## logic for search functionality

def search(request):
    products = []  # Initialize to avoid UnboundLocalError

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword),
                is_available=True
            ).order_by('-created_date')

    context = {
        'products': products,
        'product_count': len(products),  # Optional: if you want to show result count
        'keyword': request.GET.get('keyword', '')
    }

    return render(request, 'store.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ReviewRating
from .form import Reviewform

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER', '/')

    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = Reviewform(request.POST, instance=review)
            if form.is_valid():
                form.save()
                messages.success(request, 'Thank You! Your review has been updated.')
                return redirect(url)
            else:
                messages.error(request, 'There was an error updating your review.')
                return redirect(url)

        except ReviewRating.DoesNotExist:
            form = Reviewform(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank You! Your review has been submitted.')
                return redirect(url)
            else:
                messages.error(request, 'There was an error submitting your review.')
                return redirect(url)

    return redirect(url)  # <== This line ensures the view always returns a response

