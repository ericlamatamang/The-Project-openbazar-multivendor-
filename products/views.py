from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, Product, Cart, CartItem , OrderItem
from vendors.models import Vendor  # correct Vendor import
from .models import Product  # local import only


@login_required
def buy_now(request):
    products = Product.objects.all()
    return render(request, 'products/list.html', {'products': products})


@login_required
def sell_now(request):
    vendor = Vendor.objects.filter(user=request.user).first()

    if not vendor:
        return redirect('vendor_register')

    if not vendor.is_approved:
        return render(request, 'vendors/pending.html')

    return redirect('vendor_dashboard')

def product_list(request):
    foods_bakery = Product.objects.filter(category='Foods & Bakery')
    crochet = Product.objects.filter(category='Crochet')
    fashion_clothes = Product.objects.filter(category='Fashion (Clothes)')

    return render(request, 'products/product_list.html', {
        'foods_bakery': foods_bakery,
        'crochet': crochet,
        'fashion_clothes': fashion_clothes,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/product_detail.html', {'product': product})


@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'products/cart.html', {'cart': cart})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('products:cart')


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('products:cart')


@login_required
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > 0:
        item.quantity = quantity
        item.save()
    else:
        item.delete()

    return redirect('products:cart')

@login_required
def vendor_products(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    products = Product.objects.filter(vendor=vendor)

    return render(request, 'products/vendor_products.html', {
        'products': products
    })

@login_required
def add_product(request):
    if request.method == "POST":
        vendor = Vendor.objects.get(user=request.user)

        Product.objects.create(
            name=request.POST["name"],
            category=request.POST.get("category"), 
            price=request.POST["price"],
            description=request.POST["description"],
            image=request.FILES.get("image"),
            vendor=vendor,  # ✅ IMPORTANT
        )

        return redirect("products:product_list")

    return render(request, "products/add_product.html")

@login_required
def checkout(request):
    cart_items, cart_total = get_cart_items(request)

    if request.method == "POST":
        payment_method = request.POST.get('payment_method')
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=cart_total,
            payment_method=payment_method,
            is_paid=False
        )

        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['total_price']
            )

        # Clear DB cart instead of session
        CartItem.objects.filter(cart__user=request.user).delete()

        return redirect('checkout:payment_success', order_id=order.id)

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'products/checkout.html', context)

# ======================
# PAYMENT SUCCESS VIEW
# ======================
@login_required
def payment_success(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    # For now, just mark order as paid
    order.is_paid = True
    order.save()

    return render(request, 'payment_success.html', {'order': order})

# Example: Assume you have a simple Cart session system
def get_cart_items(request):
    """
    Fetch cart items from the database for the logged-in user.
    Returns a list of items and the total amount.
    """
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items_qs = CartItem.objects.filter(cart=cart)

    items = []
    total = 0
    for item in cart_items_qs:
        total_price = item.product.price * item.quantity
        items.append({
            'product': item.product,
            'quantity': item.quantity,
            'total_price': total_price,
            'cart_item_id': item.id,  # useful if you want to update/remove in template
        })
        total += total_price

    return items, total

@login_required
def process_payment(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    
    payment_method = request.POST.get('payment_method')
    amount = order.total_amount

    # Create payment object
    payment = Payment.objects.create(
        order=order,
        payment_method=payment_method,
        amount=amount,
        status='pending'
    )

    if payment_method == 'esewa':
        # Redirect to eSewa payment URL with amount, order_id, and callback
        return redirect(esewa_payment_url(payment))
    elif payment_method == 'khalti':
        return redirect(khalti_payment_url(payment))
    else:
        # Cash on Delivery
        payment.status = 'success'
        payment.save()
        order.is_paid = True
        order.save()
        return redirect('products:payment_success', order_id=order.id)

@login_required
def payment_success(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    order.is_paid = True
    order.save()

    return render(request, 'products/payment_success.html', {'order': order})
