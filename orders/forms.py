from dataclasses import field
from django import forms
from .models import *


class OrderForm(forms.ModelForm):
    class Meta:
        model=Order
        fields=['first_name','last_name','phone','email','address','city','state','pinCode','orderNote']