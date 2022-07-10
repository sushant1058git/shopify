from ast import Or
from asyncio import FastChildWatcher
import json
from pyexpat.errors import messages
from time import strftime
from django.http import HttpResponse,JsonResponse
from django.shortcuts import redirect, render
from cart.models import *
from .forms import *
import datetime
from django.contrib import messages


# Create your views here.
def place_orders(request,quantity=0,total=0):
    current_user=request.user
    cart_item=CartItem.objects.filter(user=current_user)
    cart_count=cart_item.count()
    if cart_count < 1:
        return redirect('store')
    
    tax = 0
    grand_total = 0
    
    for item in cart_item:
        total += (item.product.price * item.quantity)
        quantity += item.quantity
        
    tax = (.02 * total)
    taxes=round(tax,2)
    grand_total = total + tax
    
    if request.method=='POST':
        # import pdb;pdb.set_trace()
        form=OrderForm(request.POST)
        if form.is_valid():
            data=Order()
            data.user=current_user
            data.first_name=form.cleaned_data['first_name']
            data.last_name=form.cleaned_data['last_name']
            data.phone=form.cleaned_data['phone']
            data.city=form.cleaned_data['city']
            data.email=form.cleaned_data['email']
            data.address=form.cleaned_data['address']
            data.state=form.cleaned_data['state']
            data.pinCode=form.cleaned_data['pinCode']
            data.orderNote=form.cleaned_data['orderNote']
            data.orderTotal=grand_total
            data.tax=tax
            data.ip=request.META.get('REMOTE_ADDR')
            data.save()
            #Generata order no.
            year=int(datetime.date.today().strftime('%Y'))
            date=int(datetime.date.today().strftime('%d'))
            month=int(datetime.date.today().strftime('%m'))
            d=datetime.date(year,month,date)
            current_date=d.strftime('%Y%m%d')#20220625
            order_number=current_date + str(data.id) #data.id is id 
            data.order_number=order_number
            data.save()
            order=Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
            context={
                'order':order,
                'cart_item':cart_item,
                'total':total,
                'tax':taxes,
                'grand_total':grand_total
                
            }
            return render(request,'orders/payment.html',context)
        else:
            print(form.errors)
            return redirect('checkout')
        
def postpayment(request):
    body=json.loads(request.body)
    order=Order.objects.get(user=request.user,is_ordered=False,order_number=body['order_ID'])
    #store transaction details inside payment model
    payment=Payment(
        user=request.user,
        paymentId=body['transID'],
        amountPaid=order.orderTotal,
        orderStatus=body['status'],
        
    )
    payment.save()
    order.payment=payment
    order.is_ordered=True
    order.save()
    
    #Move cart itemsss to order product table
    cart_item=CartItem.objects.filter(user=request.user)
    for item in cart_item:
        orderedproduct=OrderProduct()
        orderedproduct.order_id=order.id
        orderedproduct.payment=payment
        orderedproduct.user_id=request.user.id
        orderedproduct.product_id=item.product_id
        orderedproduct.quantity=item.quantity
        orderedproduct.product_price=item.product.price
        orderedproduct.ordered=True
        orderedproduct.save()
        cart_item=CartItem.objects.get(id=item.id)
        product_variation=cart_item.variation.all()
        orderedproduct=OrderProduct.objects.get(id=orderedproduct.id)
        orderedproduct.variation.set(product_variation)
        orderedproduct.save()
        
        #Reduce quantity of sold product from inventory
        product=Product.objects.get(id=item.product_id)
        product.stock -=item.quantity
        product.save()
    #clear card once order is placed
    CartItem.objects.filter(user=request.user).delete()
    
    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.paymentId,
    }
    return JsonResponse(data)
            
def payment_successful(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(paymentId=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.paymentId,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/payment_successful.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
    
