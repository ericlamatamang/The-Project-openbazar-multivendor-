from django.urls import path
from .views import product_list
from . import views
from django.contrib.auth.models import User
from products.models import Product  # your Product model


app_name = 'products'   # 🔴 REQUIRED
app_name = "checkout"

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path("cart/", views.cart_detail, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/update/<int:item_id>/", views.update_cart, name="update_cart"),
    path('', views.product_list, name='product_list'),
    path('vendor/products/', views.vendor_products, name='vendor_products'),
    path('add/', views.add_product, name='add_product'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment-success/<int:order_id>/', views.payment_success, name='payment_success'),

]
 