from django.contrib import admin
from django.urls import path,include
from Shopify import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                  path('', views.home, name="home"),
                  path('securelogintoadmin/', admin.site.urls),
                  path('store/', include('store.urls')),
                  path('cart/', include('cart.urls')),
                  path('accounts/', include('accounts.urls')),
                  path('orders/', include('orders.urls')),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
