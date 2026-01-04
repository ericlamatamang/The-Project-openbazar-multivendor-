from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vendor
from products.models import Product  # Correct import
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

