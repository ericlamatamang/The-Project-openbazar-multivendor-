from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse

from django.conf import settings
import json

# Import assumed project models
from products.models import Product, Order, OrderItem, Payment
from django.contrib.auth import get_user_model
from .models import ActivityLog

User = get_user_model()


@staff_member_required
def dashboard(request):
    """Dashboard overview view aggregated via Django ORM efficiently."""
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_users = User.objects.filter(is_active=True).count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    # total revenue from paid orders
    total_revenue = (
        Order.objects.filter(is_paid=True).aggregate(total=Sum('total_amount'))['total'] or 0
    )

    orders_today = Order.objects.filter(created_at__gte=today_start).count()
    pending_orders = Order.objects.filter(is_paid=False).count()
    # Product model may or may not have `stock` field; handle gracefully
    try:
        low_stock = Product.objects.filter(stock__lte=5).count()
    except Exception:
        low_stock = 0

    # Recent activity & recent orders/users
    # prefetch order items with product and vendor to minimize queries
    recent_qs = (
        Order.objects.select_related('buyer')
        .prefetch_related('items__product', 'items__vendor')
        .order_by('-created_at')[:10]
    )
    # normalize recent orders for template (project may use different field names)
    recent_orders = []
    for o in recent_qs:
        if hasattr(o, 'buyer'):
            user_name = getattr(o.buyer, 'get_full_name', None)
            if callable(user_name):
                user_name = o.buyer.get_full_name() or o.buyer.username
            else:
                user_name = getattr(o.buyer, 'username', str(o.buyer))
        else:
            user_name = 'N/A'

        # derive status from available flags
        if getattr(o, 'is_completed', False):
            status = 'delivered'
        elif getattr(o, 'is_paid', False):
            status = 'paid'
        else:
            status = 'pending'

        # collect product names and vendor names from order items
        items_list = []
        product_names = []
        vendor_names = []
        for it in getattr(o, 'items').all():
            prod_name = getattr(it.product, 'name', None) or getattr(it.product, 'title', None) or '—'
            # vendor may be on order item or on product
            vend = None
            if getattr(it, 'vendor', None):
                vend = str(it.vendor)
            else:
                vend = str(getattr(it.product, 'vendor', '') or '')

            product_names.append(prod_name)
            if vend:
                vendor_names.append(vend)
            items_list.append({'product': prod_name, 'vendor': vend or '—'})

        recent_orders.append({
            'id': o.id,
            'user_name': user_name,
            'total_amount': getattr(o, 'total_amount', 0),
            'status': status,
            'items': items_list,
            'product_list': product_names,
            'vendor_list': vendor_names,
        })

    recent_users = User.objects.order_by('-date_joined')[:8]

    # Charts data
    last_7 = []
    for i in range(6, -1, -1):
        day = today_start - timedelta(days=i)
        day_end = day + timedelta(days=1)
        count = Order.objects.filter(created_at__gte=day, created_at__lt=day_end).count()
        last_7.append({'date': day.date().isoformat(), 'orders': count})

    # Monthly revenue (last 6 months)
    six_months_ago = today_start - timedelta(days=30 * 5)
    # monthly revenue — simple placeholder (can be enhanced)
    monthly = Order.objects.filter(created_at__gte=six_months_ago).values('created_at').annotate(total=Sum('total_amount'))

    # Product category distribution — Product.category is a CharField here
    category_qs = Product.objects.values('category').annotate(count=Count('id')).order_by('-count')

    # Order status distribution derived from flags
    status_qs = [
        {'status': 'pending', 'count': Order.objects.filter(is_paid=False).count()},
        {'status': 'paid', 'count': Order.objects.filter(is_paid=True, is_completed=False).count()},
        {'status': 'delivered', 'count': Order.objects.filter(is_completed=True).count()},
    ]

    # Admin activity
    activities = ActivityLog.objects.select_related('user')[:12]

    # prepare JSON-serializable chart payloads
    chart_orders_last7_json = json.dumps(last_7)
    status_qs_json = json.dumps(status_qs)

    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'orders_today': orders_today,
        'pending_orders': pending_orders,
        'low_stock': low_stock,
        'recent_orders': recent_orders,
        'recent_users': recent_users,
        'chart_orders_last7': last_7,
        'chart_orders_last7_json': chart_orders_last7_json,
        'category_qs': list(category_qs),
        'status_qs': list(status_qs),
        'status_qs_json': status_qs_json,
        'activities': activities,
    }

    return render(request, 'admin_dashboard/dashboard.html', context)


@staff_member_required
def products_view(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'admin_dashboard/products.html', {'products': products})


@staff_member_required
def orders_view(request):
    orders = Order.objects.select_related('buyer').all().order_by('-created_at')
    # normalize to simple dicts for template safety
    orders_list = []
    for o in orders:
        buyer_name = getattr(o.buyer, 'username', str(o.buyer)) if hasattr(o, 'buyer') else 'N/A'
        orders_list.append({
            'id': o.id,
            'buyer_name': buyer_name,
            'total_amount': getattr(o, 'total_amount', 0),
            'status': ('delivered' if getattr(o, 'is_completed', False) else ('paid' if getattr(o, 'is_paid', False) else 'pending')),
            'created_at': getattr(o, 'created_at', None),
        })
    return render(request, 'admin_dashboard/orders.html', {'orders': orders_list})


@staff_member_required
def users_view(request):
    users = User.objects.order_by('-date_joined')
    return render(request, 'admin_dashboard/users.html', {'users': users})


@staff_member_required
def payments_view(request):
    payments = []
    try:
        payments = Payment.objects.select_related('order', 'order__buyer').order_by('-created_at')
    except Exception:
        payments = []

    return render(request, 'admin_dashboard/payments.html', {'payments': payments})


@staff_member_required
def delete_order(request, order_id):
    """Delete an order (POST only). Logs the action in ActivityLog and redirects back.

    This view only deletes the Order object. It is protected by staff_member_required
    and requires a POST request to avoid accidental deletes.
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect(reverse('admin_dashboard:home'))

    order = get_object_or_404(Order, id=order_id)
    # Log before deleting to preserve info
    ActivityLog.objects.create(user=request.user, action=f"Deleted order #{order.id}")
    order.delete()
    messages.success(request, f'Order #{order_id} deleted.')
    return redirect(reverse('admin_dashboard:home'))
