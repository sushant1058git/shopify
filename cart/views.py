from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


def _get_cart_id(request):  # getting cartId with this private function '_'
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    current_user=request.user
    product = Product.objects.get(id=product_id)  # get the product
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                    variation_value__iexact=value)
                    product_variation.append(variation)

                except:
                    pass
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            # existing variation --> database
            # current product variation --->list
            # item id--->database
            id = []
            ex_var_list = []
            for item in cart_item:
                existing_variation = item.variation.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)  # cart_item Id

            if product_variation in ex_var_list:
                # Increase the cart item quantity
                index = ex_var_list.index(product_variation)
                cart_item_id = id[index]
                cartitem = CartItem.objects.get(product=product, id=cart_item_id)
                print(cartitem)
                cartitem.quantity += 1
                cartitem.save()

            else:
                item = CartItem.objects.create(
                    product=product,
                    quantity=1,
                    user=current_user,
                )
                if len(product_variation) > 0:
                    item.variation.clear()
                    item.variation.add(*product_variation)
                    item.save()

        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )
            if len(product_variation) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
            cart_item.save()
        return redirect('cart')

    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                    variation_value__iexact=value)
                    product_variation.append(variation)

                except:
                    pass

        try:
            cart = Cart.objects.get(cart_id=_get_cart_id(request))  # get the cart using the cart_id present in the session.
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_get_cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists

        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            # existing variation --> database
            # current product variation --->list
            # item id--->database
            id = []
            ex_var_list = []
            for item in cart_item:
                existing_variation = item.variation.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)  # cart_item Id

            if product_variation in ex_var_list:
                # Increase the cart item quantity
                index = ex_var_list.index(product_variation)
                cart_item_id = id[index]
                cartitem = CartItem.objects.get(product=product, id=cart_item_id)
                print(cartitem)
                cartitem.quantity += 1
                cartitem.save()

            else:
                item = CartItem.objects.create(
                    product=product,
                    quantity=1,
                    cart=cart,
                )
                if len(product_variation) > 0:
                    item.variation.clear()
                    item.variation.add(*product_variation)
                    item.save()

        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            if len(product_variation) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
            cart_item.save()
        return redirect('cart')


def remove_cart(request, product_id, item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.filter(product=product, user=request.user, id=item_id)
        else:
            cart = Cart.objects.get(cart_id=_get_cart_id(request))
            cart_item = CartItem.objects.filter(product=product, cart=cart, id=item_id)
        for cart_item in cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
    except:
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, item_id):
    product = Product.objects.get(id=product_id)
    # product.delete() # This will delete from database
    if request.user.is_authenticated:
        cart_item = CartItem.objects.filter(product=product, user=request.user, id=item_id)
    else:
        cart = Cart.objects.get(cart_id=_get_cart_id(request))
        cart_item = CartItem.objects.filter(product=product, cart=cart, id=item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_item=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_item = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_get_cart_id(request))
            cart_item = CartItem.objects.filter(cart=cart, is_active=True)
        for item in cart_item:
            total += (item.product.price * item.quantity)
            quantity += item.quantity
        tax = (.02 * total)
        taxes=round(tax,2)
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'cart_item': cart_item,
        'quantity': quantity,
        'grand_total': grand_total,
        'tax': taxes

    }
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_item=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_item = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_get_cart_id(request))
            cart_item = CartItem.objects.filter(cart=cart, is_active=True)
        for item in cart_item:
            total += (item.product.price * item.quantity)
            quantity += item.quantity
        tax = (.02 * total)
        taxes=round(tax,2)
        grand_total = total + tax
    

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'cart_item': cart_item,
        'quantity': quantity,
        'grand_total': grand_total,
        'tax': taxes

    }
    return render(request, 'store/checkout.html', context)