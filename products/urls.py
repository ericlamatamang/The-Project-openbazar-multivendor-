from django.urls import path
from .views import product_list
from . import views
from django.contrib.auth.models import User
from products.models import Product  # your Product model


app_name = 'products'   # 🔴 REQUIRED
urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),

    path('cart/', views.cart_detail, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),

    path('checkout/', views.checkout, name='checkout'),
    path('process-payment/<int:order_id>/', views.process_payment, name='process_payment'),
    path('payment-success/<int:order_id>/', views.payment_success, name='payment_success'),

    path('vendor/products/', views.vendor_products, name='vendor_products'),
    path('add/', views.add_product, name='add_product'),
    path('vendor/products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('vendor/products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    
    # eSewa URLs
    path("pay/esewa/<int:order_id>/", views.esewa_payment, name="esewa_payment"),
    path("esewa/success/", views.esewa_success, name="esewa_success"),
    path("esewa/failure/", views.esewa_failure, name="esewa_failure"),
    path('test-esewa/', views.test_esewa_initiate, name='test_esewa_initiate'),
    # eSewa URLs
    path('esewa-simple/<int:order_id>/', views.esewa_simple, name='esewa_simple'),
    path('esewa/verify/', views.esewa_verify, name='esewa_verify'),
    
    # Khalti URLs
    path("khalti-demo/<int:order_id>/", views.khalti_demo, name="khalti_demo"),
    path("khalti-success/<int:order_id>/", views.khalti_success, name="khalti_success"),
    path("khalti/verify/", views.khalti_verify, name="khalti_verify"),
    path('khalti/initiate/<int:order_id>/', views.khalti_initiate, name='khalti_initiate'),
    path('verify-khalti/', views.verify_khalti_keys, name='verify_khalti'),
    path('khalti-simple/<int:order_id>/', views.khalti_simple, name='khalti_simple'),
]