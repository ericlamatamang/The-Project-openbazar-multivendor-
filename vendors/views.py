from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vendor
from products.models import Order, OrderItem, Product  # Correct import
from .forms import VendorForm
from django.contrib import messages

@login_required
def vendor_register(request):

    if Vendor.objects.filter(user=request.user).exists():
        return redirect('vendors:dashboard')

    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.user = request.user
            vendor.is_approved = False   # 🔥 IMPORTANT
            vendor.save()

            messages.info(
                request,
                "Your vendor request has been submitted and is awaiting admin approval."
            )
            return redirect('vendors:dashboard')
    else:
        form = VendorForm()

    return render(request, 'vendors/register.html', {'form': form})

@login_required
def vendor_dashboard(request):
    vendor = get_object_or_404(Vendor, user=request.user)

    # Only show products if approved
    products = Product.objects.filter(vendor=vendor) if vendor.is_approved else []

    return render(request, 'vendors/dashboard.html', {
        'vendor': vendor,
        'products': products,
    })
    
@login_required
def add_product(request):
    try:
        vendor = request.user.vendor_account
    except Vendor.DoesNotExist:
        messages.error(request, "You are not a vendor.")
        return redirect("accounts:profile")

    # 🔥 BLOCK PENDING VENDORS
    if not vendor.is_approved:
        messages.warning(
            request,
            "Your vendor account is pending approval. You cannot add products yet."
        )
        return redirect("vendors:dashboard")

    if request.method == "POST":
        Product.objects.create(
            vendor=vendor,
            name=request.POST.get("name"),
            price=request.POST.get("price"),
            stock=request.POST.get("stock"),
            description=request.POST.get("description"),
            image=request.FILES.get("image"),
        )

        messages.success(request, "Product added successfully!")
        return redirect("vendors:dashboard")

    return render(request, "vendors/add_product.html")

@login_required
def sell_now(request):
    # Check if the user is already a vendor
    if Vendor.objects.filter(user=request.user).exists():
        # Already a vendor → go to vendor dashboard
        return redirect('vendors:dashboard')
    
    # Not a vendor → show registration form
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.user = request.user
            vendor.save()
            return redirect('vendors:dashboard')
    else:
        form = VendorForm()
    
    return render(request, 'vendors/register.html', {'form': form})

@login_required
def vendor_orders(request):
    vendor = request.user.vendor_account

    # Get all order items that belong to this vendor
    order_items = OrderItem.objects.filter(vendor=vendor).select_related(
        "order", "product", "order__buyer"
    ).order_by('-order__created_at')  # optional: newest first

    return render(request, "vendors/vendor_orders.html", {
        "order_items": order_items
    })

@login_required
def complete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Optional: check if this order belongs to this vendor
    vendor = request.user.vendor_account
    if not OrderItem.objects.filter(order=order, product__vendor=vendor).exists():
        messages.error(request, "You cannot approve this order.")
        return redirect("vendors:vendor_orders")

    order.is_completed = True  # Mark complete
    order.save()
    messages.success(request, "Order marked as completed!")
    return redirect("vendors:vendor_orders")

@login_required
def complete_order_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, vendor=request.user.vendor_account)
    item.is_completed = True
    item.save()

    # Check if all items of the order are completed
    order = item.order
    if not order.items.filter(is_completed=False).exists():
        order.is_completed = True
        order.save()

    return redirect("vendors:vendor_orders")
