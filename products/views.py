from urllib import request
import requests
import time 
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, Payment, Product, Cart, CartItem, OrderItem
from vendors.models import Vendor
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

import hashlib
import base64

@login_required 
def esewa_payment(request, order_id):
    """Initiate eSewa payment"""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    
    # Build return URLs
    success_url = request.build_absolute_uri(
        reverse('products:esewa_success')
    )
    failure_url = request.build_absolute_uri(
        reverse('products:esewa_failure')
    )
    
    # Calculate signature (required for eSewa)
    total_amount = str(order.total_amount)
    transaction_uuid = str(order.id)
    product_code = settings.ESEWA_MERCHANT_CODE
    
    # Create signature string
    signature_string = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    
    # In production, you would generate a proper HMAC signature
    # For testing, we can use a simple hash
    signature = hashlib.md5(signature_string.encode()).hexdigest()
    
    context = {
        "amount": total_amount,
        "tax_amount": "0",
        "total_amount": total_amount,
        "transaction_uuid": transaction_uuid,
        "product_code": product_code,
        "product_service_charge": "0",
        "product_delivery_charge": "0",
        "success_url": success_url,
        "failure_url": failure_url,
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "signature": signature,
        "esewa_url": settings.ESEWA_API_URL,
    }

    return render(request, "products/esewa_redirect.html", context)


@csrf_exempt
def esewa_success(request):
    """Handle eSewa success callback"""
    try:
        # Get parameters from eSewa
        data = request.POST if request.method == 'POST' else request.GET
        
        transaction_uuid = data.get('transaction_uuid')
        transaction_code = data.get('transaction_code')
        total_amount = data.get('total_amount')
        status = data.get('status')
        
        print(f"eSewa success callback: uuid={transaction_uuid}, code={transaction_code}, amount={total_amount}, status={status}")
        
        if transaction_uuid and status == 'COMPLETE':
            # Get the order
            order = Order.objects.get(id=transaction_uuid)
            
            # Mark order as paid
            order.is_paid = True
            order.payment_method = "esewa"
            order.save()
            
            # Create payment record
            Payment.objects.create(
                order=order,
                payment_method="esewa",
                transaction_id=transaction_code,
                amount=order.total_amount,
                status="success"
            )
            
            # Move cart items to OrderItems
            cart = Cart.objects.get(user=order.buyer)
            cart_items = CartItem.objects.filter(cart=cart)
            
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    vendor=item.product.vendor,
                    quantity=item.quantity,
                    price=item.product.price
                )
            
            # Clear cart
            cart_items.delete()
            
            return render(request, "products/payment_success.html", {"order": order})
        else:
            return render(request, "products/payment_failed.html", {
                "error": f"Payment not completed. Status: {status}"
            })
            
    except Exception as e:
        print(f"Error in esewa_success: {str(e)}")
        return render(request, "products/payment_failed.html", {
            "error": f"Error processing payment: {str(e)}"
        })


@csrf_exempt
def esewa_failure(request):
    """Handle eSewa failure callback"""
    return render(request, "products/payment_failed.html", {
        "error": "Payment was cancelled or failed"
    })

@login_required
def test_esewa_initiate(request):
    """Test eSewa payment initiation"""
    if request.method == "POST":
        amount = request.POST.get("amount", "10")
        order_id = request.POST.get("order_id", f"test_{request.user.id}")
        
        # Create a test order
        order = Order.objects.create(
            buyer=request.user,
            total_amount=amount,
            payment_method="esewa",
            is_paid=False
        )
        
        return redirect("products:esewa_payment", order_id=order.id)
    
    return redirect("products:checkout")


@login_required
def buy_now(request):
    products = Product.objects.filter(is_approved=True)
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
    foods_bakery = Product.objects.filter(category='Foods & Bakery', is_approved=True)
    crochet = Product.objects.filter(category='Crochet', is_approved=True)
    fashion_clothes = Product.objects.filter(category='Fashion (Clothes)', is_approved=True)

    return render(request, 'products/product_list.html', {
        'foods_bakery': foods_bakery,
        'crochet': crochet,
        'fashion_clothes': fashion_clothes,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_approved=True)
    return render(request, 'products/product_detail.html', {'product': product})


@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'products/cart.html', {'cart': cart})

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # Get quantity from POST
    quantity = int(request.POST.get('quantity', 1))

    # Safety limit (important)
    quantity = max(1, min(quantity, 15))

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
    )

    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity
        # Optional: cap total at 15
        cart_item.quantity = min(cart_item.quantity, 15)

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
def vendor_orders(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    orders = OrderItem.objects.filter(vendor=vendor).order_by('-order__created_at')
    return render(request, 'vendors/vendor_orders.html', {"orders": orders})


@login_required
def add_product(request):
    if request.method == "POST":
        vendor = Vendor.objects.get(user=request.user)

        # Prevent vendors that are not approved from adding products
        if not getattr(vendor, 'is_approved', False):
            # show a simple page or redirect to vendor dashboard with message
            from django.contrib import messages
            messages.warning(request, "Your vendor account is pending approval. You cannot add products yet.")
            return redirect('vendors:dashboard')

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
def edit_product(request, product_id):
    vendor = get_object_or_404(Vendor, user=request.user)
    product = get_object_or_404(Product, id=product_id, vendor=vendor)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.description = request.POST.get('description')
        product.category = request.POST.get('category')

        if request.FILES.get('image'):
            product.image = request.FILES['image']

        product.save()
        return redirect('products:vendor_products')

    return render(request, 'products/edit_product.html', {'product': product})



@login_required
def delete_product(request, product_id):
    vendor = get_object_or_404(Vendor, user=request.user)
    product = get_object_or_404(Product, id=product_id, vendor=vendor)

    if request.method == 'POST':
        product.delete()
        return redirect('products:vendor_products')

    return render(request, 'products/delete_product.html', {'product': product})


# ======================
# CHECKOUT & PAYMENT
# ======================
@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items.exists():
        return redirect("products:cart")

    total = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        # create order
        order = Order.objects.create(
            buyer=request.user,
            total_amount=total,
            payment_method=payment_method,
            is_paid=False
        )

        if payment_method == "khalti":
            return redirect("products:khalti_simple", order_id=order.id)
        elif payment_method == "esewa":
            return redirect("products:esewa_simple", order_id=order.id)  # Updated this line
        elif payment_method == "cod":
            # Cash on Delivery
            order.is_paid = True
            order.save()
            
            # Create payment record
            Payment.objects.create(
                order=order,
                payment_method="cod",
                amount=order.total_amount,
                status="pending"
            )
            
            # Move cart items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    vendor=item.product.vendor,
                    quantity=item.quantity,
                    price=item.product.price
                )
            
            # Clear cart
            cart_items.delete()
            
            return redirect("products:payment_success", order_id=order.id)

    return render(request, "products/checkout.html", {
        "cart_items": cart_items,
        "total": total
    })

@login_required
def process_payment(request, order_id):
    """Process non-online payments (like COD)"""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)

    # Create payment record
    Payment.objects.create(
        order=order,
        payment_method=order.payment_method,
        amount=order.total_amount,
        status="success"
    )

    # Move cart items to OrderItems
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            vendor=item.product.vendor,
            quantity=item.quantity,
            price=item.product.price
        )

    cart_items.delete()  # clear cart

    order.is_paid = True
    order.save()

    return render(request, 'products/payment_success.html', {'order': order})


# ======================
# KHALTI INTEGRATION
# ======================

@login_required
def khalti_demo(request, order_id):
    """Show Khalti payment page"""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    return render(request, "products/khalti_demo.html", {
        "order": order,
        "KHALTI_PUBLIC_KEY": settings.KHALTI_PUBLIC_KEY
    })


@login_required
def khalti_initiate(request, order_id):
    """Initiate Khalti payment using official V2 API"""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)

    url = "https://a.khalti.com/api/v2/epayment/initiate/"
    payload = {
        "return_url": request.build_absolute_uri(reverse("products:khalti_success")),
        "website_url": "http://127.0.0.1:8000/",
        "amount": int(order.total_amount * 100),  # Rs -> paisa
        "purchase_order_id": str(order.id),
        "purchase_order_name": f"Order #{order.id}",
    }

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)
    return JsonResponse(response.json())


@csrf_exempt
def khalti_success(request, order_id):
    """
    Khalti success callback.
    This handles the redirect back from Khalti after payment
    """
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    
    # Get payment details from query parameters
    pidx = request.GET.get("pidx")
    
    if pidx:
        # Verify payment with Khalti lookup API
        url = "https://a.khalti.com/api/v2/epayment/lookup/"
        headers = {
            "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        payload = {"pidx": pidx}

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if data.get("status") == "Completed":
            # ✅ Mark order as paid
            order.is_paid = True
            order.payment_method = "khalti"
            order.save()

            # ✅ Create payment record
            Payment.objects.create(
                order=order,
                payment_method="khalti",
                transaction_id=pidx,
                amount=order.total_amount,
                status="success"
            )

            # ✅ Move cart items to OrderItems for vendors
            cart = Cart.objects.get(user=order.buyer)
            cart_items = CartItem.objects.filter(cart=cart)
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    vendor=item.product.vendor,
                    quantity=item.quantity,
                    price=item.product.price
                )

            # ✅ Clear cart
            cart_items.delete()

            return render(request, "products/payment_success.html", {"order": order})

    # Payment failed or verification failed
    return render(request, "products/payment_failed.html")


@csrf_exempt
def khalti_verify(request):
    """Verify Khalti payment - WITH TEST CREDENTIALS BYPASS"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            token = data.get("token")
            amount = data.get("amount")
            order_id = data.get("order_id")
            mobile = data.get("mobile", "")  # Get mobile from frontend
            pin = data.get("pin", "")  # Get PIN from frontend
            
            print(f"Khalti verify called: order={order_id}, mobile={mobile}")
            
            if not order_id:
                return JsonResponse({
                    "success": False, 
                    "error": "Order ID is required"
                })
            
            # Get the order
            try:
                order = Order.objects.get(id=order_id, buyer=request.user)
                print(f"Order found: {order.id}, amount: {order.total_amount}")
            except Order.DoesNotExist:
                return JsonResponse({
                    "success": False, 
                    "error": "Order not found"
                })
            
            # ✅ TEST MODE: Accept payment if mobile is 9800000000 and PIN is 1111
            # This bypasses the real Khalti API for testing
            if mobile == "9800000000" and pin == "1111":
                # ✅ Mark order as paid
                order.is_paid = True
                order.payment_method = "khalti"
                order.save()
                
                # ✅ Create payment record
                Payment.objects.create(
                    order=order,
                    payment_method="khalti",
                    transaction_id=f"test_txn_{order.id}_{int(time.time())}",
                    amount=order.total_amount,
                    status="success"
                )
                
                # ✅ Move cart items to OrderItems
                try:
                    cart = Cart.objects.get(user=order.buyer)
                    cart_items = CartItem.objects.filter(cart=cart)
                    
                    for item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            vendor=item.product.vendor,
                            quantity=item.quantity,
                            price=item.product.price
                        )
                    
                    # ✅ Clear cart
                    cart_items.delete()
                    print(f"Cart cleared for order {order.id}")
                    
                except Exception as e:
                    print(f"Error moving cart items: {str(e)}")
                
                return JsonResponse({
                    "success": True, 
                    "redirect_url": reverse("products:payment_success", kwargs={"order_id": order.id}),
                    "message": "Payment successful using test credentials!"
                })
            else:
                return JsonResponse({
                    "success": False, 
                    "error": "Invalid test credentials. Use mobile: 9800000000, PIN: 1111"
                })
                
        except Exception as e:
            print(f"Error in khalti_verify: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                "success": False, 
                "error": f"Server error: {str(e)}"
            })
    
    return JsonResponse({"success": False, "error": "Invalid request method"})
# ======================
# PAYMENT SUCCESS
# ======================

@login_required
def payment_success(request, order_id):
    """Show payment success page"""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    return render(request, "products/payment_success.html", {"order": order})


# Helper function for cart
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
            'cart_item_id': item.id,
        })
        total += total_price

    return items, total

@login_required
def verify_khalti_keys(request):
    """View to verify Khalti keys are working"""
    import requests
    from django.conf import settings
    
    context = {
        'public_key': settings.KHALTI_PUBLIC_KEY,
        'secret_key': settings.KHALTI_SECRET_KEY[:10] + "..." if settings.KHALTI_SECRET_KEY else "Not set",
        'public_key_length': len(settings.KHALTI_PUBLIC_KEY) if settings.KHALTI_PUBLIC_KEY else 0,
        'secret_key_length': len(settings.KHALTI_SECRET_KEY) if settings.KHALTI_SECRET_KEY else 0,
        'public_key_prefix': settings.KHALTI_PUBLIC_KEY[:4] if settings.KHALTI_PUBLIC_KEY else "N/A",
    }
    
    # Try to test the key with Khalti API
    try:
        test_url = "https://khalti.com/api/v2/payment/verify/"
        headers = {
            "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        
        # Make a dummy request to test the key
        response = requests.post(test_url, json={"token": "dummy", "amount": 1000}, headers=headers, timeout=5)
        context['api_test_status'] = response.status_code
        context['api_test_response'] = response.json() if response.status_code != 200 else "Key is valid"
        
    except Exception as e:
        context['api_test_error'] = str(e)
    
    return render(request, 'products/verify_khalti.html', context)

@login_required
def khalti_simple(request, order_id):
    """Simple Khalti payment page with test credentials"""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    return render(request, "products/khalti_simple.html", {
        "order": order
    })
    

@login_required
def esewa_simple(request, order_id):
    """Simple eSewa payment page with test credentials"""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    return render(request, "products/esewa_simple.html", {
        "order": order
    })

@csrf_exempt
def esewa_verify(request):
    """Verify eSewa payment - with test credentials bypass"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            mobile = data.get("mobile", "")
            pin = data.get("pin", "")
            order_id = data.get("order_id")
            
            print(f"eSewa verify called: order={order_id}, mobile={mobile}")
            
            if not order_id:
                return JsonResponse({
                    "success": False, 
                    "error": "Order ID is required"
                })
            
            # Get the order
            try:
                order = Order.objects.get(id=order_id, buyer=request.user)
                print(f"Order found: {order.id}, amount: {order.total_amount}")
            except Order.DoesNotExist:
                return JsonResponse({
                    "success": False, 
                    "error": "Order not found"
                })
            
            # ✅ TEST MODE: Accept payment if mobile is 9800000000 and PIN is 1111
            if mobile == "9800000000" and pin == "1111":
                # ✅ Mark order as paid
                order.is_paid = True
                order.payment_method = "esewa"
                order.save()
                
                # ✅ Create payment record
                Payment.objects.create(
                    order=order,
                    payment_method="esewa",
                    transaction_id=f"esewa_test_{order.id}_{int(time.time())}",
                    amount=order.total_amount,
                    status="success"
                )
                
                # ✅ Move cart items to OrderItems
                try:
                    cart = Cart.objects.get(user=order.buyer)
                    cart_items = CartItem.objects.filter(cart=cart)
                    
                    for item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            vendor=item.product.vendor,
                            quantity=item.quantity,
                            price=item.product.price
                        )
                    
                    # ✅ Clear cart
                    cart_items.delete()
                    print(f"Cart cleared for order {order.id}")
                    
                except Exception as e:
                    print(f"Error moving cart items: {str(e)}")
                
                return JsonResponse({
                    "success": True, 
                    "redirect_url": reverse("products:payment_success", kwargs={"order_id": order.id}),
                    "message": "eSewa payment successful using test credentials!"
                })
            else:
                return JsonResponse({
                    "success": False, 
                    "error": "Invalid test credentials. Use mobile: 9800000000, PIN: 1111"
                })
                
        except Exception as e:
            print(f"Error in esewa_verify: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                "success": False, 
                "error": f"Server error: {str(e)}"
            })
    
    return JsonResponse({"success": False, "error": "Invalid request method"})