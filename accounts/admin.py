
from django.contrib import admin
from .models import Profile

admin.site.register(Profile)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_vendor')

class VendorAdmin(admin.ModelAdmin):
    list_display = ('user', 'store_name')
