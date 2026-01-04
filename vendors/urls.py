from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('register/', views.vendor_register, name='register'),
    path('dashboard/', views.vendor_dashboard, name='dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    path('register/', views.vendor_register, name='vendor_register'),
    path('dashboard/', views.vendor_dashboard, name='dashboard'),
    path('sell-now/', views.sell_now, name='sell_now'),
    path('add-product/', views.add_product, name='add_product'),
    
]
