from django.contrib.auth import views as auth_views
from django.urls import include, path
from .views import (
    register_view,
    login_view,
    logout_view,
    profile_view,
    edit_profile_view,
)

app_name = "accounts"

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("profile/edit/", edit_profile_view, name="edit_profile"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('vendors/', include('vendors.urls')),

]
