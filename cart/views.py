from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product
from .models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist


def _get_cart_id(request):    #getting cartId
    cart = request.session.session_key
    if not cart:
        cart= request.session.create()
    return cart


def add_cart(request,product_id):
    product = Product.objects.get(id=product_id)    # get the product
    try:
        cart = Cart.objects.get(cart_id = _get_cart_id(request))    # get the cart using the cart id present in the session.
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _get_cart_id(request)
        )
    cart.save()

    try:
        cart_item = CartItem.objects.get(product=product)
        cart_item.quantity += 1
        cart_item.save()

    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            quantity =1,
            cart = cart,
        )
        cart_item.save()
    # print(cart_item.product, cart_item.quantity)
    return redirect('cart')


def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id = _get_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product = product, cart = cart)
    if cart_item.quantity >1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart')

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id = _get_cart_id(request))
    product = Product.objects.get(id = product_id)
    # product.delete() # This will delete from database
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')

def cart(request, total = 0 , quantity=0, cart_item = None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_get_cart_id(request))
        cart_item = CartItem.objects.filter(cart=cart, is_active=True)
        for item in cart_item:
            total += (item.product.price * item.quantity)
            quantity += item.quantity
        tax = (.02 * total)
        grand_total = total+tax

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'cart_item': cart_item,
        'quantity': quantity,
        'grand_total': grand_total,
        'tax':tax

    }
    return render(request, 'store/cart.html', context)
