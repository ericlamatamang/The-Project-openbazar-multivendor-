from django.contrib import admin
from .models import Order, OrderItem, Product, Cart, CartItem

# -------------------
# Product Admin
# -------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'vendor', 'image')
    list_filter = ('category',)
    search_fields = ('name', 'category')
    fields = ('name', 'category', 'price', 'vendor', 'image', 'description')
    

# -------------------
# Cart Admin
# -------------------
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'total_price')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'total_price')
    inlines = [CartItemInline]

# -------------------
# CartItem Admin (optional if you want a separate view)
# -------------------
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'cart')
    list_filter = ('cart__user',)
    search_fields = ('cart__user__username', 'product__name')
    ordering = ('cart__user', 'product')

    def user(self, obj):
        return obj.cart.user
    user.admin_order_field = 'cart__user'
    user.short_description = 'User'

# -------------------
# Order & OrderItem Admin
# -------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'payment_method', 'is_paid', 'created_at')
    list_filter = ('payment_method', 'is_paid')
    search_fields = ('user__username',)
    ordering = ('-created_at',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('product__name', 'order__user__username')
