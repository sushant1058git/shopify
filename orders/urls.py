from django.urls import path
from . import views

urlpatterns = [
             path('place_oders/', views.place_orders, name='place_orders'),
             path('postpayment/', views.postpayment, name='postpayment'),
             
              ]
