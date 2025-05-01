from django.shortcuts import render,get_object_or_404
from .models import Product
from category.models import Category
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
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
    context = {
        'single_product': single_product,
    }
    return render(request, 'product_details.html', context)


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
