from django.contrib import admin
from django.urls import path,include
from Shopify import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                  path('store/', include('store.urls')),
                  path('admin/', admin.site.urls),
                  path('', views.home, name="home"),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
