from itertools import product
from pyexpat import model
from ssl import ALERT_DESCRIPTION_UNSUPPORTED_EXTENSION
from statistics import variance
from django.db import models
from accounts.models import Account
from cart.models import Variation
from store.models import Product


STATUS=(
        ('New','New'),
        ('Accepted','Accepted'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled')
    )

class Payment(models.Model):
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    paymentId=models.CharField(max_length=100)
    paymentMethod=models.CharField(max_length=50)
    amountPaid=models.CharField(max_length=50)
    orderStatus=models.CharField(max_length=50)
    orderPlacedOn=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.paymentId
    
class Order(models.Model):
    user=models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL, blank=True,null=True)
    order_number=models.CharField(max_length=20)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    phone=models.CharField(max_length=12)
    email=models.EmailField(max_length=100)
    address=models.CharField(max_length=80)
    country=models.CharField(max_length=80)
    city=models.CharField(max_length=80)
    state=models.CharField(max_length=80)
    pinCode=models.CharField(max_length=20)
    orderNote=models.TextField(blank=True)
    orderTotal=models.FloatField()
    tax=models.FloatField()
    status=models.CharField(max_length=10,choices=STATUS,default='New')
    ip=models.CharField(max_length=20,blank=True)
    is_ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.user)
    
    def fullName(self):
        return f'{self.first_name} {self.last_name}'
    
    
class OrderProduct(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    user=models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variation=models.ForeignKey(Variation,on_delete=models.CASCADE)
    color=models.CharField(max_length=50)
    size=models.CharField(max_length=50)
    quantity=models.IntegerField()
    product_price=models.FloatField()
    ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.order)
    
    
    