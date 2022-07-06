from django.contrib import admin
from .models import *

class OrderPaymentInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields=('payment','user','product','quantity','product_price','ordered')
    extra=0


class orderAdmin(admin.ModelAdmin):
    list_display= ['order_number','fullName','phone','email','city','orderTotal','is_ordered','created_at']
    list_filter = ['status','is_ordered']
    search_fields=['order_number','first_name','last_name','phone','email']
    list_per_page=20
    inlines=[OrderPaymentInline]
    
admin.site.register(Order,orderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct)