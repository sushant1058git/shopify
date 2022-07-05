from django.forms import ModelForm
from orders.models import Order

class checkoutForm(ModelForm):
    class Meta:
        model=Order
        fields=['first_name','last_name','phone','email','address','city','state','orderNote','pinCode']
    