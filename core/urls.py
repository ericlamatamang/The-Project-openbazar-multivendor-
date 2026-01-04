from django.urls import path
from .views import home

urlpatterns = [
    path('', home, name='home'),  # '' means this is the main page
]
