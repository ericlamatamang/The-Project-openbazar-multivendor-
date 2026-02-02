from django.db import models
from django.contrib.auth.models import User

# ======================
# PRODUCT
# ======================
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Foods & Bakery', 'Foods & Bakery'),
        ('Crochet', 'Crochet'),
        ('Fashion (Clothes)', 'Fashion (Clothes)'),
    ]

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='products/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vendor = models.ForeignKey("vendors.Vendor", on_delete=models.CASCADE, null=True, blank=True)
    is_approved = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# ======================
# CART
# ======================
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.product.price * self.quantity


# ======================
# ORDER
# ======================
class Order(models.Model):
    PAYMENT_CHOICES = (
        ('esewa', 'eSewa'),
        ('khalti', 'Khalti'),
        ('cod', 'Cash on Delivery'),
    )

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    is_paid = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} by {self.buyer.username}"


# ======================
# ORDER ITEM
# ======================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    vendor = models.ForeignKey("vendors.Vendor", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


# ======================
# PAYMENT
# ======================
class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
