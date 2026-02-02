from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('products/', views.products_view, name='products'),
    path('orders/', views.orders_view, name='orders'),
    path('orders/delete/<int:order_id>/', views.delete_order, name='delete_order'),
    path('users/create/', views.create_user, name='create_user'),
    path('vendors/approve/<int:vendor_id>/', views.approve_vendor, name='approve_vendor'),
    path('vendors/reject/<int:vendor_id>/', views.reject_vendor, name='reject_vendor'),
    path('vendors/', views.vendors_view, name='vendors'),
    path('vendors/delete/<int:vendor_id>/', views.delete_vendor, name='delete_vendor'),
    path('products/approve/<int:product_id>/', views.approve_product, name='approve_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('orders/<int:order_id>/status/', views.change_order_status, name='change_order_status'),
    path('users/<int:user_id>/toggle-active/', views.toggle_user_active, name='toggle_user_active'),
    path('users/', views.users_view, name='users'),
    path('payments/', views.payments_view, name='payments'),
]
