from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Profile
from products.views import Cart 
from vendors.models import Vendor
# If you have an Order model, import it
# from orders.models import Order


def register_view(request):
    if request.method == "POST":
        # Get form data
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        username = email
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        phone = request.POST.get("phone", "")
        address = request.POST.get("address", "")

        # Validation
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("accounts:register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "User with this email already exists.")
            return redirect("accounts:register")

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Create profile
        profile, created = Profile.objects.get_or_create(user=user)
        profile.phone = phone
        profile.address = address
        profile.save()

        # Automatically log in user
        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect("accounts:profile")

    return render(request, "accounts/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("email")  # using email as username
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Invalid credentials.")
            return redirect("accounts:login")

    return render(request, "accounts/login.html")


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("accounts:login")

@login_required
def profile_view(request):
    orders = []  # Replace with your actual orders query

    # Check if user has a Vendor instance
    try:
        vendor = request.user.vendor_account  # Use the related_name from Vendor model
        is_vendor = True

        # Get products for this vendor
        products = Product.objects.filter(vendor=vendor)
    except Vendor.DoesNotExist:
        vendor = None
        is_vendor = False
        products = []

    return render(request, "accounts/profile.html", {
        "orders": orders,
        "is_vendor": is_vendor,
        "products": products
    })

@login_required
def edit_profile_view(request):
    profile = request.user.profile

    if request.method == "POST":
        # Update profile fields
        profile.phone = request.POST.get("phone", profile.phone)
        profile.address = request.POST.get("address", profile.address)

        # Update user fields
        user = profile.user
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)

        # Save image if uploaded
        if "image" in request.FILES:
            profile.image = request.FILES["image"]

        # Save both user and profile
        user.save()       # ✅ Save user fields
        profile.save()    # ✅ Save profile fields

        messages.success(request, "Profile updated successfully!")
        return redirect("accounts:profile")

    return render(request, "accounts/edit_profile.html", {"profile": profile})


