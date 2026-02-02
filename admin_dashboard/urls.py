from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('products/', views.products_view, name='products'),
    path('orders/', views.orders_view, name='orders'),
    path('orders/delete/<int:order_id>/', views.delete_order, name='delete_order'),
    path('users/', views.users_view, name='users'),
    path('payments/', views.payments_view, name='payments'),
]
