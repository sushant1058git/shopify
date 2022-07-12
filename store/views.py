from email import message
from math import prod
from django.shortcuts import redirect, render,get_object_or_404
from .models import Product, ProductGallery, ReviewRating
from category.models import Category
from cart.models import Cart,CartItem
from cart.views import _get_cart_id
from django.core.paginator import EmptyPage,Paginator,PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def store(request, category_slug=None ):
    category = None
    products = None
    # if request.method=='POST':
    #     size=request.POST.getlist('size')
    #     print(size)
    #     min_price=request.POST.get('min_price')
    #     max_price=request.POST.get('max_price')
        
    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        products = Product.objects.filter(category = categories, is_available=True)
        paginator = Paginator(products, 12)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 12)
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
        
        #Get all review for given product
        list_of_all_review=ReviewRating.objects.filter(product_id=single_product.id,status=True)
        #Get Product Gallery
        gallery=ProductGallery.objects.filter(product=single_product.id)

    except Exception as e:
        raise e
    context = {
        'single_product':single_product,
        'is_in_cart': is_in_cart,
        # 'colour':colour,
        'list_of_all_review':list_of_all_review,
        'gallery':gallery
    }
    return render(request, 'store/product_details.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword != '':
            products = Product.objects.filter(Q(product_name__icontains = keyword) | Q(product_description__icontains=keyword))
            product_count = products.count()
        else:
            return redirect('home')
        context={
            'products': products,
            'product_count':product_count
        }
    return render(request, 'store/store.html', context)

@login_required(login_url='login')
def reviewproducts(request,product_id):
    context={}
    context['single_product'] = Product.objects.get(id=product_id)
    if request.method=='POST':
        try:
            # import pdb;pdb.set_trace()
            review=ReviewRating.objects.get(user_id=request.user.id,product_id=product_id)
            form=ReviewForm(request.POST,instance=review)
            form.save()
            messages.success(request,'Your review is updated')
            return redirect('store')
        except:
            form=ReviewForm(request.POST)
            if form.is_valid():
                new_form=form.save(commit=False)
                new_form.user=request.user
                new_form.product_id=product_id
                new_form.ip = request.META.get('REMOTE_ADDR')
                new_form.save()
                messages.success(request,'Your review is submitted')
                return redirect('store')
            else:
                print(form.errors)
                messages.eroor(request,'Your review could not be submitted')
                return redirect('store')
        
        
    return render(request, 'store/reviewproduct.html',context)