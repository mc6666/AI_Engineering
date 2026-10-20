from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='frontend:index', permanent=False)),
    path('accounts/', include('accounts.urls')),
    path('front/', include('frontend.urls')),
    path('front/purchase/', include('purchase.urls')),
    path('front/sales/', include('sales.urls')),
    path('front/inventory/', include('inventory.urls')),
    path('back/', include('backend.urls')),
    path('django-admin/', admin.site.urls),
]
