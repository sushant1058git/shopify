from django.shortcuts import render,get_object_or_404
from .models import Product
from category.models import Category
from cart.models import Cart,CartItem
from cart.views import _get_cart_id
from django.core.paginator import EmptyPage,Paginator,PageNotAnInteger

def store(request, category_slug=None ):
    category = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        products = Product.objects.filter(category = categories, is_available=True)
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products': paged_product,
        'product_count': product_count
    }
    return render(request, 'store/store.html', context)


def product_details(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug = product_slug)
        is_in_cart = CartItem.objects.filter(cart__cart_id = _get_cart_id(request), product= single_product).exists()

    except Exception as e:
        raise e
    context = {
        'single_product':single_product,
        'is_in_cart': is_in_cart
    }
    return render(request, 'store/product_details.html', context)