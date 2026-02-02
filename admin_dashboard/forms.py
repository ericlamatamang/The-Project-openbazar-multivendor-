from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from products.models import Product
from vendors.models import Vendor

User = get_user_model()


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=False)
    is_staff = forms.BooleanField(required=False, initial=False, label='Staff')
    is_superuser = forms.BooleanField(required=False, initial=False, label='Superuser')
    vendor = forms.BooleanField(required=False, initial=False, label='Vendor account')

    class Meta:
        model = User
        fields = ('username', 'email', 'is_staff', 'is_superuser', 'vendor', 'password1', 'password2')


class ProductApprovalForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'category', 'price', 'vendor', 'description', 'is_approved')


class VendorApprovalForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ('is_approved',)
