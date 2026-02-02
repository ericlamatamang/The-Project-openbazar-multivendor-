"""
URL configuration for openbazar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.views import home


urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('admin_dashboard.urls')),
    path('', include('core.urls')),  # connect main page
    path('products/', include('products.urls')),
    path("accounts/", include("accounts.urls")),
    path('profile/', home, name='profile'),  # User profile page
    path('edit-profile/', home, name='edit_profile'),  # Edit profile page
    path('products/', include('products.urls', namespace='products')),
    path('vendors/', include('vendors.urls')),

]
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)