from django.contrib import admin
from django.urls import path, include
from .views import home, login_view, logged_in, logout_view, register_view
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("", home, name="home"),
    path("login/", login_view, name="login"),
    path('logged-in/', logged_in, name='logged-in'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('check-availability/', views.check_availability, name='check_availability'),
]